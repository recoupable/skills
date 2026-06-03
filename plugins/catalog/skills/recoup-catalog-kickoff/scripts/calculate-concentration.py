#!/usr/bin/env python3
"""Calculate concentration by common catalog royalty ledger dimensions.

Outputs concentration percentages (top 1, top 3, top 5, top 10) per
dimension, optionally driving an auto-emitted finding when a tripped
threshold from assumptions.yaml is detected.

Default behavior: print result to stdout. With `--output`, also write the
concentration analysis to disk. With `--assumptions`, read materiality
thresholds; with `--emit-finding-output`, write a proposed finding entry
to a file the agent can merge into findings.json.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _helpers import deep_get, load_yaml  # noqa: E402


DEFAULT_DIMENSIONS = ["catalog_asset_id", "provider", "platform_or_licensee", "territory", "income_type"]
TOP_N_BUCKETS = (1, 3, 5, 10)
DEFAULT_FINDING_DIMENSION = "catalog_asset_id"


def parse_amount(value: str | None) -> float:
    if not value:
        return 0.0
    cleaned = value.replace("$", "").replace(",", "").replace("(", "-").replace(")", "")
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def rank_dimension(rows: list[dict], dimension: str, amount_column: str) -> list[tuple[str, float]]:
    buckets: defaultdict[str, float] = defaultdict(float)
    for row in rows:
        key = (row.get(dimension) or "unknown").strip() or "unknown"
        buckets[key] += parse_amount(row.get(amount_column))
    return sorted(buckets.items(), key=lambda item: abs(item[1]), reverse=True)


def top_n_pct(ranked: list[tuple[str, float]], total: float, n: int) -> float | None:
    if total == 0 or not ranked:
        return None
    head = sum(amount for _, amount in ranked[:n])
    return round(head / total * 100, 2)


def build_concentration(
    rows: list[dict],
    dimensions: list[str],
    amount_column: str,
) -> tuple[float, dict]:
    total = sum(parse_amount(row.get(amount_column)) for row in rows)
    results: dict[str, dict] = {}
    for dimension in dimensions:
        ranked = rank_dimension(rows, dimension, amount_column)
        results[dimension] = {
            "top_1_pct": top_n_pct(ranked, total, 1),
            "top_3_pct": top_n_pct(ranked, total, 3),
            "top_5_pct": top_n_pct(ranked, total, 5),
            "top_10_pct": top_n_pct(ranked, total, 10),
            "top_10_entries": [
                {
                    "value": key,
                    "amount": amount,
                    "percent_of_total": (amount / total * 100) if total else None,
                }
                for key, amount in ranked[:10]
            ],
        }
    return total, results


def make_finding(
    threshold: float,
    dimension: str,
    pct_breakdown: dict,
    workspace_path: Path,
) -> dict | None:
    tripped: list[dict] = []
    for bucket in TOP_N_BUCKETS:
        key = f"top_{bucket}_pct"
        pct = pct_breakdown.get(key)
        if pct is None:
            continue
        if pct >= threshold:
            tripped.append({"bucket": f"top_{bucket}", "pct": pct})
    if not tripped:
        return None
    top_entries = pct_breakdown.get("top_10_entries", [])[:5]
    asset_ids = [entry["value"] for entry in top_entries]
    issue_lines = [
        f"Catalog revenue concentration exceeds the configured threshold of {threshold:.0f}% on dimension '{dimension}'.",
    ]
    for entry in tripped:
        issue_lines.append(f"  - {entry['bucket']}: {entry['pct']:.1f}% of net revenue.")
    issue_lines.append(
        "Top 5 contributors: "
        + ", ".join(f"{e['value']} ({e['percent_of_total']:.1f}%)" for e in top_entries[:5])
    )
    return {
        "finding_id": "CONC-AUTO-001",
        "severity": "high",
        "category": "valuation",
        "affected_assets": asset_ids,
        "evidence_ids": [],
        "issue": "\n".join(issue_lines),
        "valuation_treatment": (
            "Underwrite catalog as concentrated; do not apply diversified-catalog multiples without "
            "stress-testing the top contributors' decay and durability."
        ),
        "follow_up": (
            f"Cross-reference top contributors against rights-map.csv for chain-of-title and reversion exposure. "
            f"Run downside scenarios assuming the top {tripped[0]['bucket']} contributor decays 50%."
        ),
        "status": "open",
        "_source": "calculate-concentration",
        "_threshold_pct": threshold,
        "_dimension": dimension,
        "_workspace": str(workspace_path),
    }


def load_rows(ledger_csv: Path) -> list[dict]:
    with ledger_csv.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger_csv", help="Path to royalty-ledger.csv")
    parser.add_argument("--amount-column", default="owner_net_amount")
    parser.add_argument("--dimensions", nargs="*", default=DEFAULT_DIMENSIONS)
    parser.add_argument("--output", default=None, help="Write concentration JSON to this path.")
    parser.add_argument(
        "--assumptions",
        default=None,
        help="Path to assumptions.yaml. Reads materiality.concentration_threshold_percent.",
    )
    parser.add_argument(
        "--threshold-pct",
        type=float,
        default=None,
        help="Override the concentration threshold (overrides --assumptions).",
    )
    parser.add_argument(
        "--finding-dimension",
        default=DEFAULT_FINDING_DIMENSION,
        help="Dimension to evaluate against the threshold (default catalog_asset_id).",
    )
    parser.add_argument(
        "--emit-finding-output",
        default=None,
        help="When the threshold is tripped, write a proposed finding to this path.",
    )
    args = parser.parse_args()

    ledger_path = Path(args.ledger_csv)
    rows = load_rows(ledger_path)
    total, concentration = build_concentration(rows, args.dimensions, args.amount_column)

    threshold = args.threshold_pct
    threshold_source = "cli"
    if threshold is None and args.assumptions:
        assumptions = load_yaml(Path(args.assumptions))
        configured = deep_get(assumptions, "materiality.concentration_threshold_percent")
        if isinstance(configured, (int, float)):
            threshold = float(configured)
            threshold_source = "assumptions.yaml"

    finding = None
    if threshold is not None:
        breakdown = concentration.get(args.finding_dimension, {})
        workspace = ledger_path.parents[1] if len(ledger_path.parents) >= 2 else ledger_path.parent
        finding = make_finding(threshold, args.finding_dimension, breakdown, workspace)

    payload = {
        "status": "ok",
        "ledger": str(ledger_path),
        "amount_column": args.amount_column,
        "total": total,
        "threshold_pct": threshold,
        "threshold_source": threshold_source if threshold is not None else None,
        "finding_dimension": args.finding_dimension,
        "concentration": concentration,
        "tripped_threshold": finding is not None,
    }

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        payload["output_written"] = str(out_path)

    if args.emit_finding_output:
        emit_path = Path(args.emit_finding_output)
        emit_path.parent.mkdir(parents=True, exist_ok=True)
        emit_path.write_text(
            json.dumps({"findings": [finding] if finding else []}, indent=2) + "\n",
            encoding="utf-8",
        )
        payload["finding_output_written"] = str(emit_path)

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
