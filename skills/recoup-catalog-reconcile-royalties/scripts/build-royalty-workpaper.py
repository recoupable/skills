#!/usr/bin/env python3
"""Export a hash-bound entitlement workpaper from its input and verified result."""
import argparse
import csv
import hashlib
import importlib.util
import json
import re
import shutil
from pathlib import Path
from _finance import dumps, iso_date

HERE = Path(__file__).resolve().parent


LINE_CONTEXT = ("line_ref", "rule_ref", "rule_version_ref", "currency", "period_start",
                "period_end", "evidence_refs", "freshness", "as_of")
SCHEDULE_FIELDS = {
    "entitlement-lines": LINE_CONTEXT + ("calculation_status", "basis", "basis_amount",
        "participation_rate", "commission_rate", "commission_basis", "expected_amount",
        "reported_amount", "variance", "variance_direction", "recovered_cash"),
    "calculation-bridge": tuple(key for key in LINE_CONTEXT if key != "evidence_refs") +
        ("step", "operation", "amount", "rate"),
    "recoupment-accounts": ("account_ref", "currency", "earnings_periods", "balance_as_of",
        "evidence_refs", "freshness", "as_of", "earnings_line_refs", "calculation_basis",
        "opening_balance", "movements", "eligible_earnings", "closing_balance",
        "reported_closing_balance", "closing_variance", "potential_payable", "cash_received"),
    "unresolved": ("record_ref", "status", "amount", "currency", "period", "reason", "as_of", "freshness"),
    "evidence": ("evidence_ref", "source_sha256", "current_sha256", "checked_on", "freshness"),
}


def calculator():
    spec = importlib.util.spec_from_file_location("workpaper_entitlements", HERE / "calculate-entitlements.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def alias(kind, value):
    return kind + ":" + digest(value.encode("utf-8"))


def version_alias(value):
    """Preserve the validated calculator result's JSON type in version identity."""
    return alias("version", json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False))


def read_json(path, decimal_inputs=False):
    raw = Path(path).read_bytes()
    return json.loads(raw, **({"parse_float": str} if decimal_inputs else {})), digest(raw)


def freshness(refs, evidence):
    states = {evidence[ref]["freshness"] for ref in refs}
    return "stale" if "stale" in states else "unknown" if not states or "unknown" in states else "current_as_supplied"


def evidence_rows(refs, supplied, as_of):
    if not isinstance(supplied, dict) or supplied.get("schema_version") != "1":
        raise ValueError("Evidence inventory requires schema_version '1'")
    report_date = iso_date(as_of, "as_of")
    records = supplied.get("sources")
    if not isinstance(records, list):
        raise ValueError("Evidence sources must be a list")
    inventory = {}
    for item in records:
        ref = item.get("evidence_ref")
        if not isinstance(ref, str) or not ref.strip() or ref in inventory:
            raise ValueError("Evidence references must be unique nonblank strings")
        for key in ("source_sha256", "current_sha256"):
            if item.get(key) is not None and (not isinstance(item[key], str)
                                               or not re.fullmatch(r"[0-9a-f]{64}", item[key])):
                raise ValueError("Source versions must be lowercase SHA256 values or null")
        checked = item.get("checked_on")
        if checked is not None and iso_date(checked, "checked_on") > report_date:
            raise ValueError("Evidence check cannot be after report as_of")
        inventory[ref] = item
    rows = {}
    for ref in sorted(refs):
        item = inventory.get(ref, {})
        source, current = item.get("source_sha256"), item.get("current_sha256")
        state = "unknown"
        checked = item.get("checked_on")
        same_day = checked is not None and iso_date(checked, "checked_on") == report_date
        if source and current:
            state = "stale" if source != current else "current_as_supplied" if same_day else "unknown"
        rows[ref] = {"evidence_ref": alias("evidence", ref), "source_sha256": source,
                     "current_sha256": current, "checked_on": item.get("checked_on"), "freshness": state}
    return rows


def cell(value):
    if value is None:
        return "unknown"
    text = json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else str(value)
    return "'" + text if text.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")) else text


def build(input_path, result_path, output, as_of, evidence_path=None):
    iso_date(as_of, "as_of")
    data, input_hash = read_json(input_path, decimal_inputs=True)
    result, result_hash = read_json(result_path)
    expected = json.loads(dumps(calculator().calculate(data)))
    # JSON identity must distinguish booleans, numbers and exact decimal strings.
    if json.dumps(result, sort_keys=True, allow_nan=False) != json.dumps(expected, sort_keys=True, allow_nan=False):
        raise ValueError("Result differs from current calculator and input; regenerate or retain as historical evidence")
    supplied, evidence_hash = read_json(evidence_path) if evidence_path else ({"schema_version": "1", "sources": []}, None)
    all_refs = set()
    def collect(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "evidence_refs" and isinstance(child, list):
                    all_refs.update(ref for ref in child if isinstance(ref, str) and ref.strip())
                elif key in {"rules", "lines", "adjustments", "recoupment_accounts", "movements"}:
                    collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)
    collect(data)
    evidence = evidence_rows(all_refs, supplied, as_of)
    def context(item):
        refs = item["evidence_refs"]
        return {"evidence_refs": [alias("evidence", ref) for ref in refs],
                "freshness": freshness(refs, evidence), "as_of": as_of}
    lines, bridges, accounts, unresolved = [], [], [], []
    input_lines = {line["line_id"]: line for line in data.get("lines", [])}
    rules = {rule["rule_id"]: rule for rule in data.get("rules", [])}
    calculated = {line["line_id"]: line for line in result["lines"]}
    for line in result["lines"]:
        source = input_lines[line["line_id"]]
        rule = rules[line["rule_id"]]
        common = {"line_ref": alias("line", line["line_id"]), "rule_ref": alias("rule", line["rule_id"]),
                  "rule_version_ref": version_alias(line["rule_version"]),
                  "currency": line["currency"], "period_start": line["period_start"],
                  "period_end": line["period_end"], **context(line)}
        lines.append({**common, "calculation_status": line["status"], "basis": rule["basis"],
                      "basis_amount": source[rule["basis"]], "participation_rate": rule["participation_rate"],
                      "commission_rate": rule["commission_rate"], "commission_basis": "participation",
                      **{key: line[key] for key in ("expected_amount", "reported_amount", "variance", "variance_direction", "recovered_cash")}})
        # Evidence is stored once per line; bridge rows resolve it via line_ref.
        bridge_context = {key: value for key, value in common.items() if key != "evidence_refs"}
        for index, step in enumerate(line["bridge"]):
            bridges.append({**bridge_context, "step": index, "operation": step["operation"],
                            "amount": step["amount"], "rate": step.get("rate")})
    for account in result["recoupment_accounts"]:
        periods = sorted({(calculated[key]["period_start"], calculated[key]["period_end"]) for key in account["earnings_line_ids"]})
        accounts.append({"account_ref": alias("account", account["account_id"]),
                         "currency": account["currency"], "earnings_periods": periods,
                         "balance_as_of": "unknown_not_supplied_by_calculator", **context(account),
                         "earnings_line_refs": [alias("line", key) for key in account["earnings_line_ids"]],
                         "calculation_basis": "available=opening+movements; closing=max(0,available-earnings); payable=max(0,earnings-available)",
                         **{key: account[key] for key in ("opening_balance", "movements", "eligible_earnings", "closing_balance", "reported_closing_balance", "closing_variance", "potential_payable", "cash_received")}})
    for blocker in result["blockers"]:
        kind = "line" if "line_id" in blocker else "account"
        unresolved.append({"record_ref": alias(kind, blocker[kind + "_id"]),
                           "status": "manual_workpaper_required", "amount": None,
                           "currency": "unknown_not_calculated", "period": "unknown_not_calculated",
                           "reason": "See matching blocker in hash-bound private result; free text excluded",
                           "as_of": as_of, "freshness": "unknown"})
    schedules = {"entitlement-lines": lines, "calculation-bridge": bridges, "recoupment-accounts": accounts,
                 "unresolved": unresolved, "evidence": list(evidence.values())}
    overall = freshness(all_refs, evidence)
    controls = {"schema_version": "1", "stage": "contractual_entitlement", "as_of": as_of,
                "calculation_check": "matches_recomputed_input", "result_status": result["status"],
                "source_control": "not_verified_by_exporter", "freshness": overall,
                "recovered_cash": None, "recovery_rollup": "not_calculated",
                "rounding_policy": result["rounding_policy"],
                "input_sha256": input_hash, "result_sha256": result_hash, "evidence_inventory_sha256": evidence_hash}
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise ValueError("Output destination already exists; choose a new version")
    output.mkdir(parents=True, mode=0o700)
    try:
        (output / "workpaper.json").write_text(dumps({"controls": controls, "schedules": schedules}), encoding="utf-8")
        for name, rows in schedules.items():
            fields = SCHEDULE_FIELDS[name]
            with (output / (name + ".csv")).open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                for row in rows:
                    writer.writerow({key: cell(value) for key, value in row.items()})
        report = ["# Royalty entitlement workpaper", "", "Scope: supplied fixed-rate entitlement and recoupment calculations only.",
                  "Normalization, source control totals, remittance and bank matching are not checked by this export.",
                  f"As of: {as_of}. Calculation result: {result['status']}. Evidence freshness: {overall}.",
                  "The calculation matches the hash-bound input; this is not verification of the supplied facts or terms.", "",
                  "| Schedule | Rows |", "|---|---:|"]
        report += [f"| {name}.csv | {len(rows)} |" for name, rows in schedules.items()]
        report += ["", "Exact decimals and null unknowns are authoritative in workpaper.json; CSV formula guards are display-only.",
                   "Bridge rows are intermediate steps, not additive earnings. Recoupment uses the same entitlement lines.",
                   "Do not add line variances, recoupment payable, adjustments or later cash as separate recoveries.",
                   "No shared-cause monetary recovery total is calculated. Potential variance is neither accepted debt nor recovered cash.",
                   "Empty schedules mean no supplied calculated records, not a passed check. Unresolved amounts remain unknown.",
                   "Missing/old evidence checks remain unknown; differing supplied source versions are stale. No live freshness was verified.",
                   "Source references and record IDs are SHA256 aliases; resolve them against the hash-bound private inputs.",
                   "Source paths, names, account details, source prose and originals are excluded. Financial values remain private.",
                   "Report review grants no permission to share, publish, contact providers or move money.", ""]
        (output / "report.md").write_text("\n".join(report), encoding="utf-8")
        manifest = {**controls, "originals_included": False, "identifier_projection": "sha256_aliases",
                    "calculator_sha256": digest((HERE / "calculate-entitlements.py").read_bytes()),
                    "finance_primitives_sha256": digest((HERE / "_finance.py").read_bytes()),
                    "exporter_sha256": digest(Path(__file__).read_bytes()),
                    "files": [{"file": path.name, "sha256": digest(path.read_bytes())} for path in sorted(output.iterdir())]}
        (output / "manifest.json").write_text(dumps(manifest), encoding="utf-8")
        return manifest
    except BaseException:
        # Only this invocation's exclusively created directory is removed.
        # Failed schedules must not masquerade as a completed report or block retry.
        shutil.rmtree(output)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Original calculate-entitlements input JSON")
    parser.add_argument("--result", required=True, help="Saved calculate-entitlements result JSON")
    parser.add_argument("--output-directory", required=True, help="New private directory, never overwritten")
    parser.add_argument("--as-of", required=True, help="Report date YYYY-MM-DD; does not assert evidence freshness")
    parser.add_argument("--evidence", help="Optional version inventory; see references/royalty-workpaper-export.md")
    args = parser.parse_args()
    try:
        print(dumps(build(args.input, args.result, args.output_directory, args.as_of, args.evidence)), end="")
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        parser.exit(2, f"build-royalty-workpaper: {exc}\n")


if __name__ == "__main__":
    main()
