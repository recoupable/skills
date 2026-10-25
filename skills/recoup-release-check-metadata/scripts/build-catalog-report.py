#!/usr/bin/env python3
"""Create a private, evidence-linked case index and CSV schedules without originals."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

COLLECTIONS = ("sources", "assessments", "findings", "actions", "attempts", "outcomes")
FIELDS = ("id", "stage", "status", "dimension", "cause_id", "action_id", "rule_version",
          "stale", "source_refs", "depends_on", "evidence_gap")


GROUP_FIELDS = {
    "sources": {"id", "status"},
    "assessments": {"id", "stage", "status", "rule_version", "stale", "source_refs", "depends_on", "evidence_gap"},
    "findings": {"id", "stage", "status", "cause_id", "rule_version", "stale", "source_refs", "depends_on", "evidence_gap"},
    "actions": {"id", "stage", "status", "rule_version", "stale", "source_refs", "depends_on", "evidence_gap"},
    "attempts": {"id", "status", "action_id", "rule_version", "stale", "source_refs", "depends_on", "evidence_gap"},
    "outcomes": {"id", "status", "dimension", "action_id", "rule_version", "stale", "source_refs", "depends_on", "evidence_gap"},
}


def project_record(group, record, include_summary):
    allowed = GROUP_FIELDS[group] | ({"summary"} if include_summary else set())
    result = {}
    for key in allowed:
        value = record.get(key)
        if key == "source_refs" and isinstance(value, list):
            result[key] = [{field: item[field] for field in ("source_id", "version")}
                           for item in value if isinstance(item, dict)
                           and all(isinstance(item.get(field), str) for field in ("source_id", "version"))]
        elif key == "depends_on" and isinstance(value, list):
            result[key] = [item for item in value if isinstance(item, str)]
        elif key == "stale" and isinstance(value, bool):
            result[key] = value
        elif isinstance(value, str):
            result[key] = value
    return result


def cell(value):
    value = json.dumps(value, ensure_ascii=False, sort_keys=True) if isinstance(value, (dict, list)) else str(value)
    # Spreadsheet display only. Source JSON remains unchanged for reproducible calculations.
    return "'" + value if value.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")) else value


def build(case_path, output, include_summary=False):
    raw = Path(case_path).read_bytes()
    case = json.loads(raw)
    if case.get("schema_version") != 1:
        raise ValueError("Unsupported catalog case schema")
    output = Path(output)
    if output.exists():
        raise ValueError("Output destination already exists; choose a new version")
    output.mkdir(parents=True, mode=0o700)
    fields = FIELDS + (("summary",) if include_summary else ())
    manifest = {"schema_version": 1, "case_id": case["case_id"], "revision": case["revision"],
                "case_sha256": hashlib.sha256(raw).hexdigest(), "projection": list(fields),
                "originals_included": False, "files": [], "scope": "selected_case_records"}
    for group in COLLECTIONS:
        records = case[group]
        destination = output / f"{group}.csv"
        with destination.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for record in records.values():
                selected = project_record(group, record, include_summary)
                writer.writerow({key: cell(selected.get(key, "")) for key in fields})
        manifest["files"].append({"file": destination.name, "rows": len(records),
                                  "sha256": hashlib.sha256(destination.read_bytes()).hexdigest()})
    report = ["# Catalog case evidence index", "", f"Case revision: {case['revision']}",
              f"Source case SHA256: `{manifest['case_sha256']}`", "",
              "This index reports saved case records. It does not certify provider acceptance,",
              "external correction or receipt of money beyond the evidence in those records.",
              "Originals, source locations, action payloads and authorization details are excluded.",
              "IDs and included evidence descriptions can still be private; review the destination.", "",
              "| Schedule | Records | Stale records |", "|---|---:|---:|"]
    for group in COLLECTIONS:
        report.append(f"| {group}.csv | {len(case[group])} | {sum(bool(r.get('stale')) for r in case[group].values())} |")
    report += ["", "Use source_refs with the authorized private case to retrieve exact source versions.",
               "Missing evidence, unknown outcomes and unchecked observations remain unresolved.",
               "No monetary rollup is inferred from findings: shared causes and conditional estimates",
               "must be reconciled in the stage's controlled accounting workpapers.", ""]
    (output / "report.md").write_text("\n".join(report), encoding="utf-8")
    manifest["files"].append({"file": "report.md", "sha256": hashlib.sha256((output / "report.md").read_bytes()).hexdigest()})
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True)
    parser.add_argument("--output-directory", required=True)
    parser.add_argument("--include-summary", action="store_true", help="Include private human summaries in the selected export")
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.case, args.output_directory, args.include_summary), indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, f"build-catalog-report: {exc}\n")


if __name__ == "__main__":
    main()
