#!/usr/bin/env python3
"""Build a JSON manifest for source files in a catalog deal workspace.

Classifies each file with parse_status, likely_provider, likely_period,
likely_currency, and rights_type_hint so downstream tools (manual-review
queue, normalizer routing, audit checklists) can act on a structured view
of the data room.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


PARSEABLE_SUFFIXES = {".csv", ".tsv", ".xlsx", ".xls", ".json"}
MANUAL_REVIEW_SUFFIXES = {".pdf", ".doc", ".docx", ".rtf"}
TEXTUAL_SUFFIXES = {".txt", ".md", ".html", ".xml", ".log", ".yaml", ".yml"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".tif", ".tiff"}


# Provider markers — first match wins. Patterns are tested case-insensitively
# against the full path under source/ to catch folder-based grouping.
PROVIDER_PATTERNS = [
    (re.compile(r"(?i)/ascap/"), "ASCAP"),
    (re.compile(r"(?i)/bmi/"), "BMI"),
    (re.compile(r"(?i)/sesac/"), "SESAC"),
    (re.compile(r"(?i)/mlc/|the[\s_-]?mlc"), "The MLC"),
    (re.compile(r"(?i)/soundexchange/|sx[\s_-]?statement"), "SoundExchange"),
    (re.compile(r"(?i)/hfa[\s_-]?legacy/|hfa_"), "HFA"),
    (re.compile(r"(?i)jasrac"), "JASRAC"),
    (re.compile(r"(?i)sacem"), "SACEM"),
    (re.compile(r"(?i)sadaic"), "SADAIC"),
    (re.compile(r"(?i)gema(?![a-z])"), "GEMA"),
    (re.compile(r"(?i)/prs/|prs[\s_-]?(export|statement)"), "PRS"),
    (re.compile(r"(?i)apra"), "APRA"),
    (re.compile(r"(?i)spotify"), "Spotify"),
    (re.compile(r"(?i)apple|itunes"), "Apple/iTunes"),
    (re.compile(r"(?i)youtube|content[\s_-]?id|yt[\s_-]"), "YouTube"),
    (re.compile(r"(?i)tunecore|distrokid|cd[\s_-]?baby|orchard|empire|stem|amuse"), "Distributor"),
    (re.compile(r"(?i)/sub_publishers/|sub[\s_-]?publisher"), "Sub-Publisher"),
]


CURRENCY_BY_PROVIDER = {
    "JASRAC": "JPY",
    "SADAIC": "ARS",
    "SACEM": "EUR",
    "GEMA": "EUR",
    "PRS": "GBP",
    "APRA": "AUD",
}


RIGHTS_TYPE_HINT_BY_PROVIDER = {
    "ASCAP": ("publishing", "performance"),
    "BMI": ("publishing", "performance"),
    "SESAC": ("publishing", "performance"),
    "The MLC": ("publishing", "mechanical"),
    "HFA": ("publishing", "mechanical"),
    "SoundExchange": ("neighboring", "radio"),
    "PRS": ("publishing", "performance"),
    "JASRAC": ("publishing", "performance"),
    "SACEM": ("publishing", "performance"),
    "SADAIC": ("publishing", "performance"),
    "GEMA": ("publishing", "performance"),
    "APRA": ("publishing", "performance"),
    "Spotify": ("master", "streaming"),
    "Apple/iTunes": ("master", "streaming"),
    "YouTube": ("master", "ugc"),
    "Distributor": ("master", "streaming"),
    "Sub-Publisher": ("publishing", "performance"),
}


PERIOD_PATTERNS = [
    (re.compile(r"(\d{4})Q([1-4])"), lambda m: f"{m.group(1)}Q{m.group(2)}"),
    (re.compile(r"(\d{4})[-_](\d{2})[-_](\d{2})"), lambda m: f"{m.group(1)}-{m.group(2)}-{m.group(3)}"),
    (re.compile(r"(\d{4})[-_](\d{2})"), lambda m: f"{m.group(1)}-{m.group(2)}"),
    (re.compile(r"(\d{4})_quarterly"), lambda m: f"{m.group(1)}"),
    (re.compile(r"(\d{4})_annual"), lambda m: f"{m.group(1)}"),
    (re.compile(r"(?<![\d-])(\d{4})(?![\d-])"), lambda m: m.group(1)),
]


# Folder-level rights-type hints when no provider matches.
FOLDER_HINTS = [
    (re.compile(r"(?i)/04_rights_documents/sample_clearances/"), ("rights_doc", "sample_clearance")),
    (re.compile(r"(?i)/04_rights_documents/split_sheets/"), ("rights_doc", "split_sheet")),
    (re.compile(r"(?i)/04_rights_documents/sync_licenses/"), ("rights_doc", "sync_license")),
    (re.compile(r"(?i)/04_rights_documents/songwriter_agreements/"), ("rights_doc", "writer_agreement")),
    (re.compile(r"(?i)/04_rights_documents/letters_of_direction/"), ("rights_doc", "letter_of_direction")),
    (re.compile(r"(?i)/04_rights_documents/terminations_reversions/"), ("rights_doc", "termination_reversion")),
    (re.compile(r"(?i)/04_rights_documents/"), ("rights_doc", "agreement")),
    (re.compile(r"(?i)/05_registrations/"), ("registration", "registration")),
    (re.compile(r"(?i)/02_catalog/"), ("catalog_metadata", "catalog")),
    (re.compile(r"(?i)/01_corporate/"), ("corporate", "corporate")),
    (re.compile(r"(?i)/06_financials/"), ("financial_summary", "summary")),
    (re.compile(r"(?i)/07_misc/"), ("misc", "misc")),
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify_provider(rel_path: str) -> str | None:
    for pattern, provider in PROVIDER_PATTERNS:
        if pattern.search(rel_path):
            return provider
    return None


def classify_period(rel_path: str) -> str | None:
    name = rel_path.rsplit("/", 1)[-1]
    folder = rel_path.rsplit("/", 1)[0] if "/" in rel_path else ""
    for haystack in (name, folder):
        for pattern, formatter in PERIOD_PATTERNS:
            match = pattern.search(haystack)
            if match:
                return formatter(match)
    return None


def classify_rights_hint(rel_path: str, provider: str | None) -> tuple[str | None, str | None]:
    if provider and provider in RIGHTS_TYPE_HINT_BY_PROVIDER:
        return RIGHTS_TYPE_HINT_BY_PROVIDER[provider]
    for pattern, (rights, doc_type) in FOLDER_HINTS:
        if pattern.search(rel_path):
            return rights, doc_type
    return None, None


def classify_parse_status(suffix: str, size_bytes: int) -> str:
    if size_bytes == 0:
        return "unparsed"
    if suffix in PARSEABLE_SUFFIXES:
        return "parsed"
    if suffix in MANUAL_REVIEW_SUFFIXES:
        return "manual_review"
    if suffix in TEXTUAL_SUFFIXES:
        return "manual_review"
    if suffix in IMAGE_SUFFIXES:
        return "manual_review"
    return "unparsed"


def classify_currency(provider: str | None) -> str | None:
    return CURRENCY_BY_PROVIDER.get(provider) if provider else None


def build_manifest(source_dir: Path) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(source_dir.parent)
        rel_str = str(rel)
        suffix = path.suffix.lower()
        size = path.stat().st_size
        provider = classify_provider("/" + rel_str)
        period = classify_period(rel_str)
        rights_type, doc_type = classify_rights_hint("/" + rel_str, provider)
        parse_status = classify_parse_status(suffix, size)
        currency = classify_currency(provider)
        entries.append(
            {
                "path": rel_str,
                "filename": path.name,
                "suffix": suffix,
                "size_bytes": size,
                "sha256": sha256_file(path),
                "parse_status": parse_status,
                "likely_provider": provider,
                "likely_period": period,
                "likely_currency": currency,
                "rights_type_hint": rights_type,
                "document_type_hint": doc_type,
            }
        )
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deal_workspace", help="Path to deals/{deal-id}")
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON path. Defaults to workpapers/file-manifest.json.",
    )
    args = parser.parse_args()

    workspace = Path(args.deal_workspace)
    source_dir = workspace / "source"
    if not source_dir.is_dir():
        raise SystemExit(f"Missing source directory: {source_dir}")

    output = Path(args.output) if args.output else workspace / "workpapers" / "file-manifest.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    files = build_manifest(source_dir)
    payload = {"deal_workspace": str(workspace), "files": files}
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    status_counts: dict[str, int] = {}
    for entry in files:
        key = str(entry["parse_status"])
        status_counts[key] = status_counts.get(key, 0) + 1

    print(
        json.dumps(
            {
                "status": "ok",
                "output": str(output),
                "files": len(files),
                "by_parse_status": status_counts,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
