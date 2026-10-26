#!/usr/bin/env python3
"""Build exact-decimal entitlement and recoupment workpapers from evidenced terms.

Usage: python3 scripts/calculate-entitlements.py --input terms.json --output result.json
Supported: explicit fixed rates/effective periods, participation-based commission,
signed supported adjustments, and separately scoped recoupment accounts. Tiered or
cross-collateralized terms require an explicit manual workpaper; no guessed terms.
Adjustment/movement currency defaults to its parent line/account only when omitted.
An explicit currency must match that parent; this helper does not convert FX.
See fixtures/finance/entitlement-input.json for the complete input shape.
"""
import argparse
import json
from decimal import Decimal
from pathlib import Path
from _finance import amount, refs, currency, iso_date, unique, dumps, same_file

ADJUSTMENTS = {"deduction", "reserve_withheld", "reserve_released", "withholding", "reversal", "recognized_adjustment"}


def calculate(data):
    if not isinstance(data, dict):
        raise ValueError("Input must be a JSON object")
    if data.get("schema_version") != "1":
        raise ValueError("schema_version must be '1'")
    rules = unique(data.get("rules", []), "rule_id")
    lines = unique(data.get("lines", []), "line_id")
    results, errors = [], []
    for line_id, line in lines.items():
        try:
            rule = rules.get(line.get("rule_id"))
            if not rule:
                raise ValueError("No explicit rule_id with evidenced terms")
            evidence = refs(line, line_id) + refs(rule, rule["rule_id"])
            if not rule.get("rule_version"):
                raise ValueError("rule_version is required")
            if rule.get("unsupported_terms"):
                raise ValueError("Manual workpaper required for unsupported terms: " + str(rule["unsupported_terms"]))
            if rule.get("adjustments_complete") is not True:
                raise ValueError("Confirm the adjustment schedule is complete; missing schedules are not zero")
            ccy = currency(line)
            start, end = iso_date(line.get("period_start"), "period_start"), iso_date(line.get("period_end"), "period_end")
            if start > end or start < iso_date(rule.get("effective_start"), "effective_start") or end > iso_date(rule.get("effective_end"), "effective_end"):
                raise ValueError("Line falls outside or spans rule effective period; split with source evidence")
            if line.get("rights_type") != rule.get("rights_type") or not rule.get("rights_type"):
                raise ValueError("Rights basis mismatch; publishing income does not establish master participation")
            if not line.get("territory") or line["territory"] not in rule.get("territories", []):
                raise ValueError("Territory is outside explicit rule scope")
            basis = rule.get("basis")
            if basis not in {"gross_amount", "owner_net_amount"}:
                raise ValueError("Rule needs an explicit gross_amount or owner_net_amount contractual basis")
            base = amount(line.get(basis), basis)
            rate = amount(rule.get("participation_rate"), "participation_rate")
            commission = amount(rule.get("commission_rate"), "commission_rate")
            if not 0 <= rate <= 1 or not 0 <= commission <= 1:
                raise ValueError("Rates must be fractions in [0,1] with their contractual basis")
            if rule.get("commission_basis") != "participation":
                raise ValueError("Unsupported commission basis; use an evidenced manual workpaper")
            already_net = rule.get("already_net_of")
            if not isinstance(already_net, list):
                raise ValueError("already_net_of must explicitly list included deductions (or [])")
            if commission and "commission" in already_net:
                raise ValueError("Would double-deduct commission already in the basis")
            participating = base * rate
            commission_amount = participating * commission
            expected = participating - commission_amount
            bridge = [{"operation": "basis", "amount": base}, {"operation": "participation", "rate": rate, "amount": participating},
                      {"operation": "commission", "rate": commission, "amount": -commission_amount}]
            for adjustment in unique(line.get("adjustments", []), "adjustment_id").values():
                kind = adjustment.get("kind")
                if kind not in ADJUSTMENTS or kind in already_net:
                    raise ValueError("Unknown or already deducted adjustment: " + str(kind))
                if "currency" in adjustment and currency(adjustment) != ccy:
                    raise ValueError("Adjustment currency differs from line; use an evidenced manual FX workpaper")
                evidence += refs(adjustment, "adjustment")
                delta = amount(adjustment.get("amount"), "adjustment.amount")
                if kind in {"deduction", "reserve_withheld", "withholding"} and delta > 0:
                    raise ValueError(f"{kind} must be nonpositive")
                if kind == "reserve_released" and delta < 0:
                    raise ValueError("reserve_released must be nonnegative")
                expected += delta
                bridge.append({"operation": kind, "amount": delta})
            reported = amount(line.get("reported_amount"), "reported_amount")
            variance = expected - reported
            results.append({"line_id": line_id, "rule_id": rule["rule_id"], "rule_version": rule["rule_version"],
                            "status": "calculated", "currency": ccy, "period_start": str(start), "period_end": str(end),
                            "expected_amount": expected, "reported_amount": reported, "variance": variance,
                            "variance_direction": "potential_underpayment" if variance > 0 else "potential_overpayment_or_clawback" if variance < 0 else "matched",
                            "recovered_cash": None, "evidence_refs": sorted(set(evidence)), "bridge": bridge})
        except (ValueError, KeyError, TypeError) as exc:
            errors.append({"line_id": line_id, "reason": str(exc), "status": "manual_workpaper_required"})
    by_id = {item["line_id"]: item for item in results}
    recoupment, allocated = [], set()
    for account in unique(data.get("recoupment_accounts", []), "account_id").values():
        try:
            identity = account["account_id"]
            evidence = refs(account, identity)
            ccy = currency(account)
            if account.get("cross_collateralization") is not False:
                raise ValueError("Cross-collateralization requires a separate reviewed manual workpaper")
            opening = amount(account.get("opening_balance"), "opening_balance")
            if opening < 0:
                raise ValueError("Opening recoupment balance cannot be negative")
            movements = Decimal(0)
            for move in unique(account.get("movements", []), "movement_id").values():
                if move.get("kind") not in {"advance", "cost", "supported_adjustment"}:
                    raise ValueError("Unsupported recoupment movement")
                if "currency" in move and currency(move) != ccy:
                    raise ValueError("Movement currency differs from recoupment account; use an evidenced manual FX workpaper")
                evidence += refs(move, "movement")
                delta = amount(move.get("amount"))
                if move["kind"] in {"advance", "cost"} and delta < 0:
                    raise ValueError("Advance/cost requires nonnegative amount; use supported_adjustment for reversal")
                movements += delta
            earnings = Decimal(0)
            line_ids = account.get("earnings_line_ids", [])
            if not line_ids or len(set(line_ids)) != len(line_ids):
                raise ValueError("Explicit nonduplicate eligible earnings_line_ids required")
            for line_id in line_ids:
                if line_id in allocated:
                    raise ValueError("Overlapping recoupment allocation: " + line_id)
                item = by_id.get(line_id)
                if not item or item["currency"] != ccy:
                    raise ValueError("Unavailable earnings or mixed currency: " + line_id)
                earnings += item["expected_amount"]
                evidence += item["evidence_refs"]
            available = opening + movements
            if available < 0:
                raise ValueError("Movements produce negative unrecouped balance; manual workpaper required")
            closing = max(Decimal(0), available - earnings)
            payable = max(Decimal(0), earnings - available)
            reported_closing = amount(account.get("reported_closing_balance"), "reported_closing_balance")
            recoupment.append({"account_id": identity, "currency": ccy, "opening_balance": opening, "movements": movements,
                              "eligible_earnings": earnings, "closing_balance": closing, "reported_closing_balance": reported_closing,
                              "closing_variance": closing - reported_closing, "potential_payable": payable,
                              "earnings_line_ids": line_ids, "evidence_refs": sorted(set(evidence)), "cash_received": None})
            allocated.update(line_ids)
        except (ValueError, KeyError, TypeError) as exc:
            errors.append({"account_id": account.get("account_id"), "reason": str(exc), "status": "manual_workpaper_required"})
    return {"schema_version": "1", "status": "partial" if errors or not results else "ok", "lines": results,
            "recoupment_accounts": recoupment, "blockers": errors,
            "rounding_policy": "Exact supported arithmetic: inputs <=24 coefficient/integer digits and <=18 fractional places; <=10000 records per collection; Decimal precision 128. No per-row rounding.",
            "limitations": "Calculates supplied rules only. Variances are potential exposure, not recognized debt or recovered cash."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    same_path = same_file(args.input, args.output)
    try:
        if same_path:
            raise ValueError("Output cannot overwrite source input")
        result = calculate(json.loads(Path(args.input).read_text(), parse_float=str))
    except (ValueError, TypeError, KeyError, OSError) as exc:
        result = {"status": "invalid_input", "errors": [str(exc)]}
    if not same_path:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(dumps(result))
    print(dumps(result), end="")
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
