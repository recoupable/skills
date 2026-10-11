#!/usr/bin/env python3
"""Build a manual-review queue from the file manifest and royalty ledger.

Produces:
- findings/manual-review-queue.md: human-readable checklist of every file
  that did not contribute financial data, with provider, period, currency,
  rights-type hint, and a one-line action.
- workpapers/ingest-coverage.json: machine-readable coverage summary used
  to drive top-line ingest reporting (e.g. "X of Y files contributed
  financial data; Z files require manual review").

Coverage is computed by intersecting the file manifest with the source_file
column of normalized/royalty-ledger.csv. Files with parse_status='parsed'
that are absent from the ledger are flagged (parsed_but_unused) — they
were expected to contribute but did not, often because the normalizer
returned partial/empty status.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def load_manifest(workspace: Path) -> list[dict]:
    manifest_path = workspace / "workpapers" / "file-manifest.json"
    if not manifest_path.is_file():
        raise SystemExit(
            f"Missing file manifest: {manifest_path}. Run scripts/build-file-manifest.py first."
        )
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    return list(data.get("files", []))


def load_ledger_source_files(workspace: Path) -> set[str]:
    ledger_path = workspace / "normalized" / "royalty-ledger.csv"
    if not ledger_path.is_file():
        return set()
    sources: set[str] = set()
    with ledger_path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            value = (row.get("source_file") or "").strip()
            if not value:
                continue
            sources.add(value)
            # Also add the path-relative form, since source_file in the ledger
            # is sometimes absolute and sometimes relative.
            for prefix in (str(workspace) + "/", str(workspace.resolve()) + "/"):
                if value.startswith(prefix):
                    sources.add(value[len(prefix):])
    return sources


def file_contributed(manifest_entry: dict, ledger_sources: set[str]) -> bool:
    rel = str(manifest_entry.get("path") or "")
    if not rel:
        return False
    if rel in ledger_sources:
        return True
    # Try common alternate forms — bare filename, source/-prefixed.
    name = str(manifest_entry.get("filename") or "")
    if name and any(src.endswith("/" + name) or src.endswith(name) for src in ledger_sources):
        return True
    return False


def queue_action(entry: dict) -> str:
    status = entry.get("parse_status")
    suffix = entry.get("suffix") or ""
    provider = entry.get("likely_provider")
    if status == "unparsed" and entry.get("size_bytes") == 0:
        return "Request reissue: file is zero bytes."
    if suffix == ".pdf":
        if provider:
            return f"Extract financial detail from PDF (provider: {provider}); add a column-map or transcribe to CSV."
        return "Read the PDF; transcribe material facts to a structured workpaper or evidence ledger entry."
    if status == "manual_review":
        return "Review file by hand; add evidence-ledger entry for any material facts."
    if status == "parsed":
        return "Re-run the normalizer with --column-map for this provider."
    return "Determine handling: provider unknown."


def build_queue_markdown(workspace: Path, queue_entries: list[dict]) -> str:
    lines = [
        "# Manual review queue",
        "",
        f"Workspace: `{workspace}`  ",
        f"Files requiring manual review: **{len(queue_entries)}**",
        "",
        "| File | Provider | Period | Rights | Currency | Status | Action |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for entry in queue_entries:
        lines.append(
            "| `{path}` | {provider} | {period} | {rights} | {currency} | {status} | {action} |".format(
                path=entry["path"],
                provider=entry.get("likely_provider") or "—",
                period=entry.get("likely_period") or "—",
                rights=entry.get("rights_type_hint") or "—",
                currency=entry.get("likely_currency") or "—",
                status=entry.get("parse_status") or "—",
                action=queue_action(entry),
            )
        )
    lines.append("")
    return "\n".join(lines)


def build_coverage(
    workspace: Path,
    manifest: list[dict],
    ledger_sources: set[str],
) -> dict:
    by_status: Counter = Counter()
    by_provider: Counter = Counter()
    contributed: list[str] = []
    parsed_but_unused: list[str] = []

    for entry in manifest:
        status = str(entry.get("parse_status") or "unknown")
        by_status[status] += 1
        provider = entry.get("likely_provider")
        if provider:
            by_provider[provider] += 1
        if file_contributed(entry, ledger_sources):
            contributed.append(str(entry["path"]))
        elif status == "parsed":
            parsed_but_unused.append(str(entry["path"]))

    total = len(manifest)
    manual_review_count = by_status.get("manual_review", 0)
    unparsed_count = by_status.get("unparsed", 0)
    return {
        "workspace": str(workspace),
        "total_files": total,
        "by_parse_status": dict(by_status),
        "by_provider": dict(by_provider),
        "contributed_to_ledger": sorted(contributed),
        "contributed_count": len(contributed),
        "parsed_but_unused": sorted(parsed_but_unused),
        "parsed_but_unused_count": len(parsed_but_unused),
        "manual_review_count": manual_review_count,
        "unparsed_count": unparsed_count,
        "summary_line": (
            f"{len(contributed)} of {total} file(s) contributed financial data; "
            f"{manual_review_count} require manual review; "
            f"{unparsed_count} unparsed."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", help="Path to deals/{deal-id}")
    parser.add_argument(
        "--queue-output",
        default=None,
        help="Path to manual-review queue markdown (default findings/manual-review-queue.md).",
    )
    parser.add_argument(
        "--coverage-output",
        default=None,
        help="Path to ingest-coverage JSON (default workpapers/ingest-coverage.json).",
    )
    args = parser.parse_args()

    workspace = Path(args.workspace)
    queue_path = (
        Path(args.queue_output)
        if args.queue_output
        else workspace / "findings" / "manual-review-queue.md"
    )
    coverage_path = (
        Path(args.coverage_output)
        if args.coverage_output
        else workspace / "workpapers" / "ingest-coverage.json"
    )

    manifest = load_manifest(workspace)
    ledger_sources = load_ledger_source_files(workspace)
    coverage = build_coverage(workspace, manifest, ledger_sources)

    review_entries = [
        entry
        for entry in manifest
        if entry.get("parse_status") in {"manual_review", "unparsed"}
        or (entry.get("parse_status") == "parsed" and not file_contributed(entry, ledger_sources))
    ]
    queue_entries = sorted(review_entries, key=lambda e: e.get("path") or "")

    queue_path.parent.mkdir(parents=True, exist_ok=True)
    coverage_path.parent.mkdir(parents=True, exist_ok=True)
    queue_path.write_text(build_queue_markdown(workspace, queue_entries), encoding="utf-8")
    coverage_path.write_text(json.dumps(coverage, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "ok",
                "workspace": str(workspace),
                "queue_output": str(queue_path),
                "coverage_output": str(coverage_path),
                "summary_line": coverage["summary_line"],
                "manual_review_count": coverage["manual_review_count"],
                "parsed_but_unused_count": coverage["parsed_but_unused_count"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
