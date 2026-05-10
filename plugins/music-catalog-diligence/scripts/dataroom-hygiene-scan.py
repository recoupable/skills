#!/usr/bin/env python3
"""Scan a data room for files that suggest seller-side concealment leaks.

Surfaces:
- Filenames suggesting working notes or admin checklists.
- File contents containing concealment-language patterns
  ("do not show buyer", "remove before sharing", etc.).

Writes:
- workpapers/dataroom-hygiene.json — machine-readable matches.
- findings/dataroom-hygiene-findings.json — proposed findings entries to merge
  into findings/findings.json (one per matched file).

Catching this pattern (e.g. DELETE_BEFORE_SHARING.txt) reframes how to read
the rest of the data room and is materially load-bearing for diligence trust
posture.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


# Strong filename signals: explicit working-doc markers that should not appear
# in a final data room. Match → emit a finding.
FILENAME_STRONG = re.compile(
    r"(?ix)"
    r"(delete[\s_-]?before|"
    r"do[\s_-]?not[\s_-]?(share|show|disclose|email|send|forward|tell|use|publish|distribute|volunteer)|"
    r"remove[\s_-]?before|"
    r"admin[\s_-]?notes?|"
    r"internal[\s_-]?(only|todo|notes?))"
)

# Weak filename signals: process markers like "DRAFT" — surfaced in the
# workpaper for context but do not by themselves emit a finding. We use
# explicit separators ([._-] or string boundary) because Python's \b treats
# underscore as a word character, so \bdraft\b would not match "_DRAFT.pdf".
FILENAME_WEAK = re.compile(
    r"(?i)"
    r"(?:[._-]|^)(draft|wip|backup|junk|scratch|todo|tmp|temp|confidential)(?:[._-]|$)"
)

# Content patterns are intrinsically strong — the language only appears in
# admin/concealment contexts. Match → emit a finding.
CONTENT_PATTERN = re.compile(
    r"(?ix)"
    r"(do[\s_-]?not[\s_-]+(show|share|volunteer|disclose|tell|send|email|forward)|"
    r"don['']?t[\s_-]+(show|share|volunteer|disclose|tell|send|forward)|"
    r"remove[\s_-]+before[\s_-]+(sharing|sending|disclosure)|"
    r"delete[\s_-]+before[\s_-]+(sharing|sending|disclosure)|"
    r"hide[\s_-]+(this|from)|"
    r"gloss[\s_-]+over|"
    r"keep[\s_-]+out[\s_-]+of[\s_-]+(the[\s_-]+)?(data[\s_-]?room|deck|memo))"
)

TEXTUAL_SUFFIXES = {".txt", ".md", ".csv", ".tsv", ".html", ".xml", ".log", ".json", ".yaml", ".yml", ".sql"}
MAX_FILE_BYTES = 5 * 1024 * 1024  # 5 MB cap to bound work on large logs


def scan_filename(path: Path) -> tuple[bool, bool]:
    """Returns (strong_match, weak_match)."""
    return bool(FILENAME_STRONG.search(path.name)), bool(FILENAME_WEAK.search(path.name))


def scan_content(path: Path) -> list[dict[str, object]]:
    if path.suffix.lower() not in TEXTUAL_SUFFIXES:
        return []
    try:
        size = path.stat().st_size
    except OSError:
        return []
    if size > MAX_FILE_BYTES:
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    matches: list[dict[str, object]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if CONTENT_PATTERN.search(line):
            preview = line.strip()
            if len(preview) > 240:
                preview = preview[:237] + "..."
            matches.append({"line": line_no, "preview": preview})
    return matches


def scan_workspace(source_dir: Path, workspace: Path) -> list[dict[str, object]]:
    matches: list[dict[str, object]] = []
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file():
            continue
        try:
            relative = str(path.relative_to(workspace))
        except ValueError:
            relative = str(path)
        filename_strong, filename_weak = scan_filename(path)
        content_matches = scan_content(path)
        if not (filename_strong or filename_weak or content_matches):
            continue
        if filename_strong or content_matches:
            strength = "high"
        else:
            strength = "weak"
        matches.append(
            {
                "path": relative,
                "filename_strong": filename_strong,
                "filename_weak": filename_weak,
                "content_matches": content_matches,
                "match_strength": strength,
            }
        )
    return matches


def proposed_findings(matches: list[dict[str, object]]) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    next_id = 1
    for match in matches:
        if match["match_strength"] == "weak":
            continue
        path = match["path"]
        snippet_count = len(match.get("content_matches") or [])
        issue_parts = [f"Data-room hygiene scan flagged {path}."]
        if match.get("filename_strong"):
            issue_parts.append("Filename matches an explicit concealment / admin-notes marker.")
        if snippet_count:
            issue_parts.append(f"Content contains {snippet_count} line(s) matching concealment-language patterns.")
        issue_parts.append(
            "If the file represents seller-side admin notes accidentally included, treat all "
            "seller-favorable representations across the data room with elevated skepticism."
        )
        findings.append(
            {
                "finding_id": f"HYG-SCAN-{next_id:03d}",
                "severity": "high",
                "category": "process_integrity",
                "affected_assets": ["data_room_trust_posture"],
                "evidence_ids": [],
                "issue": " ".join(issue_parts),
                "valuation_treatment": "Apply elevated skepticism to seller representations; counsel-only review of flagged file.",
                "follow_up": f"Read {path} in full; corroborate or refute material claims; counsel-to-counsel acknowledgment.",
                "status": "open",
                "_source_match": match,
            }
        )
        next_id += 1
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", help="Path to deals/{deal-id}")
    parser.add_argument(
        "--source-dir",
        default=None,
        help="Directory to scan. Defaults to {workspace}/source.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON path. Defaults to {workspace}/workpapers/dataroom-hygiene.json.",
    )
    parser.add_argument(
        "--findings-output",
        default=None,
        help="Proposed-findings JSON path. Defaults to {workspace}/findings/dataroom-hygiene-findings.json.",
    )
    args = parser.parse_args()

    workspace = Path(args.workspace)
    source_dir = Path(args.source_dir) if args.source_dir else workspace / "source"
    if not source_dir.is_dir():
        raise SystemExit(f"missing source directory: {source_dir}")

    output_path = Path(args.output) if args.output else workspace / "workpapers" / "dataroom-hygiene.json"
    findings_path = (
        Path(args.findings_output)
        if args.findings_output
        else workspace / "findings" / "dataroom-hygiene-findings.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    findings_path.parent.mkdir(parents=True, exist_ok=True)

    matches = scan_workspace(source_dir, workspace)
    findings = proposed_findings(matches)

    output_path.write_text(
        json.dumps(
            {
                "status": "ok",
                "workspace": str(workspace),
                "source_dir": str(source_dir),
                "match_count": len(matches),
                "matches": matches,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    findings_path.write_text(
        json.dumps({"findings": findings}, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "status": "ok",
                "workspace": str(workspace),
                "match_count": len(matches),
                "output": str(output_path),
                "findings_output": str(findings_path),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
