#!/usr/bin/env python3
"""Validate cross-artifact consistency in a catalog deal workspace.

Rules:
1. Every entry in `scope.excluded_assets` of assumptions.yaml is either
   absent from canonical-catalog.csv OR present with `controlled_share=0`.
2. Every rights-map.csv row whose `support_level == 'conflicting'` and whose
   notes mention reversion/termination corresponds to a canonical-catalog
   row with `controlled_share=0`.
3. Every findings.json entry whose `valuation_treatment` says to exclude
   has its affected_assets reduced to `controlled_share=0` in the catalog
   (warning only — the agent may have a reason to keep the row).

Returns status='errors_found' on any rule-1 or rule-2 violation; emits a
'warnings' list for rule-3.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _helpers import deep_get, load_yaml  # noqa: E402


REVERSION_PATTERN = re.compile(r"(?i)(reverted|reversion|terminated|termination|reverts|term[\s_]?end)")
EXCLUSION_PATTERN = re.compile(r"(?i)(exclude|excluded from|do not include|holdback at 100|drop from)")


def load_canonical_catalog(workspace: Path) -> list[dict]:
    path = workspace / "normalized" / "canonical-catalog.csv"
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def load_rights_map(workspace: Path) -> list[dict]:
    path = workspace / "normalized" / "rights-map.csv"
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def load_findings(workspace: Path) -> list[dict]:
    path = workspace / "findings" / "findings.json"
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [item for item in data.get("findings", []) if isinstance(item, dict)]


def parse_share(value: str | None) -> float | None:
    if value is None:
        return None
    text = value.strip().rstrip("%")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def normalize_title(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def excluded_asset_label(entry: str) -> str:
    """Extract the title-like prefix from an assumptions.yaml exclusion string."""
    text = entry.strip()
    # Split on em-dash, en-dash, or " - " — common separators between title and reason.
    for sep in (" — ", " – ", " - "):
        if sep in text:
            text = text.split(sep, 1)[0]
            break
    # Strip trailing parenthetical year, e.g. "Coyote Moon Blues (1978)" -> "Coyote Moon Blues"
    text = re.sub(r"\s*\([^)]*\)\s*$", "", text).strip()
    return text


def find_catalog_matches(label: str, catalog: list[dict]) -> list[dict]:
    target = normalize_title(label)
    if not target:
        return []
    matches: list[dict] = []
    target_squashed = target.replace(" ", "_")
    for row in catalog:
        title_norm = normalize_title(row.get("title") or "")
        if title_norm == target:
            matches.append(row)
            continue
        asset_id = (row.get("catalog_asset_id") or "").strip().lower()
        if asset_id and (asset_id == target_squashed or asset_id == target.replace(" ", "")):
            matches.append(row)
            continue
        # Substring fallback (handles "Coyote Moon Blues" vs catalog_asset_id COYOTE_MOON)
        title_squashed = title_norm.replace(" ", "_")
        if title_norm and (title_norm.startswith(target) or target.startswith(title_norm)):
            matches.append(row)
            continue
        if asset_id and asset_id in target_squashed:
            matches.append(row)
            continue
    return matches


def validate_excluded_assets(
    excluded: list[str],
    catalog: list[dict],
) -> tuple[list[dict], list[dict]]:
    errors: list[dict] = []
    unmatched: list[dict] = []
    for entry in excluded:
        if not isinstance(entry, str) or not entry.strip():
            continue
        label = excluded_asset_label(entry)
        matches = find_catalog_matches(label, catalog)
        if not matches:
            unmatched.append({"excluded_label": label, "raw": entry})
            continue
        for row in matches:
            share = parse_share(row.get("controlled_share"))
            if share is not None and share != 0:
                errors.append(
                    {
                        "rule": "excluded_asset_with_nonzero_controlled_share",
                        "excluded_label": label,
                        "catalog_asset_id": row.get("catalog_asset_id"),
                        "title": row.get("title"),
                        "controlled_share": share,
                    }
                )
    return errors, unmatched


def validate_reverted_rights(
    rights: list[dict],
    catalog: list[dict],
) -> list[dict]:
    catalog_by_id = {(row.get("catalog_asset_id") or "").strip(): row for row in catalog}
    seen_ids: set[str] = set()
    errors: list[dict] = []
    for row in rights:
        asset_id = (row.get("catalog_asset_id") or "").strip()
        support = (row.get("support_level") or "").strip().lower()
        notes = row.get("notes") or ""
        if not asset_id:
            continue
        if support not in {"conflicting", "missing"}:
            continue
        if not REVERSION_PATTERN.search(notes):
            continue
        if asset_id in seen_ids:
            continue
        seen_ids.add(asset_id)
        catalog_row = catalog_by_id.get(asset_id)
        if catalog_row is None:
            continue
        share = parse_share(catalog_row.get("controlled_share"))
        if share is not None and share != 0:
            errors.append(
                {
                    "rule": "reverted_or_terminated_rights_with_nonzero_controlled_share",
                    "catalog_asset_id": asset_id,
                    "title": catalog_row.get("title"),
                    "support_level": support,
                    "rights_notes": notes,
                    "controlled_share": share,
                }
            )
    return errors


def validate_excluded_findings(
    findings: list[dict],
    catalog: list[dict],
) -> list[dict]:
    catalog_by_id = {(row.get("catalog_asset_id") or "").strip(): row for row in catalog}
    warnings: list[dict] = []
    for finding in findings:
        treatment = finding.get("valuation_treatment") or ""
        if not EXCLUSION_PATTERN.search(treatment):
            continue
        affected = finding.get("affected_assets") or []
        if not isinstance(affected, list):
            continue
        for asset in affected:
            asset_id = str(asset).strip()
            if not asset_id:
                continue
            row = catalog_by_id.get(asset_id)
            if row is None:
                continue
            share = parse_share(row.get("controlled_share"))
            if share is None or share == 0:
                continue
            warnings.append(
                {
                    "rule": "excluding_finding_targets_nonzero_share_asset",
                    "finding_id": finding.get("finding_id"),
                    "catalog_asset_id": asset_id,
                    "controlled_share": share,
                    "valuation_treatment": treatment[:200],
                }
            )
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", help="Path to deals/{deal-id}")
    args = parser.parse_args()

    workspace = Path(args.workspace)
    assumptions_path = workspace / "assumptions.yaml"
    catalog = load_canonical_catalog(workspace)
    rights = load_rights_map(workspace)
    findings = load_findings(workspace)

    excluded: list[str] = []
    if assumptions_path.is_file():
        assumptions = load_yaml(assumptions_path)
        raw_excluded = deep_get(assumptions, "scope.excluded_assets") or []
        if isinstance(raw_excluded, list):
            excluded = [str(item) for item in raw_excluded if item is not None]

    excluded_errors, unmatched = validate_excluded_assets(excluded, catalog)
    rights_errors = validate_reverted_rights(rights, catalog)
    finding_warnings = validate_excluded_findings(findings, catalog)

    errors = excluded_errors + rights_errors
    warnings = finding_warnings
    status = "ok" if not errors else "errors_found"

    payload = {
        "status": status,
        "workspace": str(workspace),
        "excluded_asset_violations": excluded_errors,
        "unmatched_excluded_labels": unmatched,
        "reverted_rights_violations": rights_errors,
        "exclusion_finding_warnings": warnings,
        "summary": {
            "excluded_in_assumptions": len(excluded),
            "catalog_rows": len(catalog),
            "rights_rows": len(rights),
            "findings": len(findings),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }
    print(json.dumps(payload, indent=2))
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
