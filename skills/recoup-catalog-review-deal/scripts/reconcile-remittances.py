#!/usr/bin/env python3
"""Reconcile evidenced statement→remittance→receipt allocations without inferring cash.

Usage: python3 scripts/reconcile-remittances.py --input allocations.json --output result.json
Amounts are signed exact decimal strings. Each FX/fee/withholding bridge is explicit.
See fixtures/finance/remittance-input.json. No banking or provider writes occur.
"""
import argparse
import json
from decimal import Decimal
from collections import defaultdict
from pathlib import Path
from _finance import amount, refs, currency, unique, dumps, iso_date


def reconcile(data):
    if not isinstance(data, dict):
        raise ValueError("Input must be a JSON object")
    if data.get("schema_version") != "1":
        raise ValueError("schema_version must be '1'")
    sets = {name: unique(data.get(name, []), "id") for name in ("statements", "remittances", "receipts")}
    for name, items in sets.items():
        unique(list(items.values()), "source_record_id")
        for identity, item in items.items():
            refs(item, identity)
            currency(item)
            amount(item.get("amount"))
            if name != "statements":
                iso_date(item.get("date"), identity + ".date")
            else:
                if iso_date(item.get("period_start"), "period_start") > iso_date(item.get("period_end"), "period_end"):
                    raise ValueError("Statement period is invalid")
    unique(data.get("allocations", []), "allocation_id")
    usage, results, errors, received = defaultdict(Decimal), [], [], defaultdict(Decimal)
    allowed = {"statement_to_remittance": ("statements", "remittances"), "remittance_to_receipt": ("remittances", "receipts")}
    scope = data.get("completion_scope", list(allowed))
    if not isinstance(scope, list) or not scope or not all(isinstance(stage, str) and stage in allowed for stage in scope) or len(scope) != len(set(scope)):
        raise ValueError("completion_scope must explicitly select one or both allocation stages")
    for allocation in data.get("allocations", []):
        try:
            identity = allocation["allocation_id"]
            stage = allocation.get("stage")
            if stage not in allowed:
                raise ValueError("Unknown allocation stage")
            left_set, right_set = allowed[stage]
            left = sets[left_set].get(allocation.get("from_id"))
            right = sets[right_set].get(allocation.get("to_id"))
            if not left or not right:
                raise ValueError("Allocation references unknown object")
            evidence = refs(allocation, identity) + refs(left, left["id"]) + refs(right, right["id"])
            from_amount, to_amount = amount(allocation.get("from_amount")), amount(allocation.get("to_amount"))
            if not from_amount or not to_amount:
                raise ValueError("Zero allocations do not establish a match")
            # Signed reversals are separate records and consume capacity of the same sign.
            for side, item, value in (("from", left, from_amount), ("to", right, to_amount)):
                capacity = amount(item["amount"])
                used_key = (stage, side, item["id"])
                if value * capacity <= 0 or abs(usage[used_key] + value) > abs(capacity):
                    raise ValueError(f"Over-allocation or wrong sign for {item['id']}")
            if left["currency"] == right["currency"]:
                fx = Decimal(1)
                if "fx_rate" in allocation and amount(allocation["fx_rate"]) != 1:
                    raise ValueError("Same-currency FX must equal 1")
            else:
                fx = amount(allocation.get("fx_rate"), "fx_rate")
                if fx <= 0:
                    raise ValueError("Cross-currency bridge needs positive FX")
                evidence += refs({"evidence_refs": allocation.get("fx_evidence_refs")}, "Cross-currency FX bridge")
            adjustments = Decimal(0)
            for adjustment in unique(allocation.get("adjustments", []), "adjustment_id").values():
                if adjustment.get("kind") not in {"fee", "withholding", "supported_adjustment"}:
                    raise ValueError("Unsupported bridge adjustment")
                if currency(adjustment) != right["currency"]:
                    raise ValueError("Bridge adjustment must be in receiving currency")
                evidence += refs(adjustment, "adjustment")
                delta = amount(adjustment.get("amount"))
                if adjustment["kind"] in {"fee", "withholding"} and delta > 0:
                    raise ValueError("Fee/withholding adjustment must be nonpositive")
                adjustments += delta
            if from_amount * fx + adjustments != to_amount:
                raise ValueError("Amounts do not reconcile exactly with the supplied FX and adjustments")
            status = "allocated_statement"
            if stage == "remittance_to_receipt":
                if right.get("status") != "posted":
                    raise ValueError("Pending/returned receipt is not posted receiving-account evidence")
                if not left.get("receiving_account_ref") or left.get("receiving_account_ref") != right.get("account_ref"):
                    raise ValueError("Receiving-account scope mismatch or unknown; resolve changed payee with evidence")
                if right.get("evidence_status") != "observed":
                    status = "user_reported_receipt_unverified"
                else:
                    status = "verified_receipt" if to_amount > 0 else "verified_return"
                    received[right["currency"]] += to_amount
            usage[(stage, "from", left["id"])] += from_amount
            usage[(stage, "to", right["id"])] += to_amount
            results.append({"allocation_id": identity, "stage": stage, "from_id": left["id"], "to_id": right["id"],
                            "from_amount": from_amount, "from_currency": left["currency"], "to_amount": to_amount,
                            "to_currency": right["currency"], "fx_rate": fx, "adjustments": adjustments,
                            "status": status, "evidence_refs": sorted(set(evidence))})
        except (ValueError, KeyError, TypeError) as exc:
            errors.append({"allocation_id": allocation.get("allocation_id"), "reason": str(exc)})
    residuals = []
    for stage, (left_set, right_set) in allowed.items():
        for side, name in (("from", left_set), ("to", right_set)):
            for identity, item in sets[name].items():
                allocated = usage[(stage, side, identity)]
                residuals.append({"stage": stage, "side": side, "id": identity, "currency": item["currency"],
                                  "amount": amount(item["amount"]), "allocated": allocated,
                                  "unallocated": amount(item["amount"]) - allocated, "evidence_refs": item["evidence_refs"]})
    remaining = [entry for entry in residuals if entry["stage"] in scope and entry["unallocated"] != 0]
    unverified = [entry["allocation_id"] for entry in results if entry["status"] == "user_reported_receipt_unverified"]
    absent_stages = [stage for stage in scope if not any(entry["stage"] == stage for entry in results)]
    return {"schema_version": "1", "status": "partial" if errors or not results or remaining or unverified or absent_stages else "ok", "allocations": results,
            "completion_scope": scope, "unverified_allocation_ids": unverified, "unmatched_required_records": len(remaining), "missing_required_stages": absent_stages,
            "arithmetic_limits": "Inputs <=24 coefficient/integer digits and <=18 fractional places; <=10000 records per collection; Decimal precision 128.",
            "unresolved": errors, "residuals": residuals, "verified_receipts_by_currency": dict(received),
            "current_payable": None, "receiving_account_access": data.get("receiving_account_access", "unknown"),
            "limitations": "Paid labels and historical credits do not establish current payable or bank receipt. Unallocated amounts are unmatched, not automatically debts."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    same_path = Path(args.input).resolve() == Path(args.output).resolve()
    try:
        if same_path:
            raise ValueError("Output cannot overwrite source input")
        result = reconcile(json.loads(Path(args.input).read_text(), parse_float=str))
    except (ValueError, TypeError, KeyError, OSError) as exc:
        result = {"status": "invalid_input", "errors": [str(exc)]}
    if not same_path:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(dumps(result))
    print(dumps(result), end="")
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
