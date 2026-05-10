#!/usr/bin/env python3
"""Build a markdown diligence dashboard for a catalog deal workspace.

The dashboard reads ``findings/findings.json`` and reports an overall status:

- ``blocked``       -- one or more open *blocker* findings (severity ``critical``
                       or legacy ``P0``).
- ``review_needed`` -- one or more open *high*-tier findings (severity ``high``
                       or legacy ``P1``).
- ``ready``         -- no open blockers or high-severity findings.

Severity comparison is case-insensitive. Both the canonical lowercase taxonomy
(``critical | high | medium | low``) and the legacy ``P0 | P1`` codes are
accepted so the dashboard stays compatible with older fixtures while matching
the rest of the plugin (see ``references/red-flags.md``).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


# Severities that prevent sharing until cured. Compared case-insensitively.
BLOCKER_SEVERITIES = {"critical", "p0"}

# Severities that need explicit disclosure but do not fully block sharing.
REVIEW_SEVERITIES = {"high", "p1"}


def load_json(path: Path, default: object) -> object:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def finding_severity(finding: dict[str, object]) -> str:
    """Return the finding's severity as a lowercase string for tier matching."""
    return str(finding.get("severity", "")).strip().lower()


def finding_status(finding: dict[str, object]) -> str:
    return str(finding.get("status", "")).strip().lower()


def finding_description(finding: dict[str, object]) -> str:
    """Prefer the canonical ``issue`` field; fall back to ``title`` for older fixtures."""
    for key in ("issue", "title"):
        value = finding.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "Untitled finding"


def is_open(finding: dict[str, object]) -> bool:
    """Treat findings without a status as open. Closed/resolved/deferred are not blockers."""
    status = finding_status(finding)
    return status in {"", "open", "in_progress", "in-progress"}


def summarize_findings(
    workspace: Path,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    """Return (all_findings, open_blockers, open_review_items)."""
    data = load_json(workspace / "findings" / "findings.json", {"findings": []})
    findings = data.get("findings", []) if isinstance(data, dict) else []
    typed_findings = [finding for finding in findings if isinstance(finding, dict)]
    open_blockers = [
        finding
        for finding in typed_findings
        if is_open(finding) and finding_severity(finding) in BLOCKER_SEVERITIES
    ]
    open_review = [
        finding
        for finding in typed_findings
        if is_open(finding) and finding_severity(finding) in REVIEW_SEVERITIES
    ]
    return typed_findings, open_blockers, open_review


def determine_status(
    blockers: list[dict[str, object]],
    review_items: list[dict[str, object]],
) -> str:
    if blockers:
        return "blocked"
    if review_items:
        return "review_needed"
    return "ready"


def render_finding_line(finding: dict[str, object]) -> str:
    finding_id = finding.get("finding_id", "unknown")
    severity = finding.get("severity", "unknown")
    description = finding_description(finding)
    return f"- `{severity}` `{finding_id}`: {description}"


def render_dashboard(workspace: Path) -> str:
    findings, blockers, review_items = summarize_findings(workspace)
    status = determine_status(blockers, review_items)
    lines = [
        "# Diligence Dashboard",
        "",
        f"- Workspace: `{workspace}`",
        f"- Overall status: `{status}`",
        f"- Findings: `{len(findings)}`",
        f"- Open blockers (critical/P0): `{len(blockers)}`",
        f"- Open review items (high/P1): `{len(review_items)}`",
        "",
        "## Open blockers",
        "",
    ]
    if blockers:
        lines.extend(render_finding_line(finding) for finding in blockers)
    else:
        lines.append("- None.")

    lines.extend(["", "## Open review items", ""])
    if review_items:
        lines.extend(render_finding_line(finding) for finding in review_items)
    else:
        lines.append("- None.")

    lines.extend(["", "## Next actions", ""])
    if status == "blocked":
        lines.append("- Resolve critical blockers before sharing the package.")
    elif status == "review_needed":
        lines.append(
            "- Review open high-severity findings and disclose or resolve them before sharing."
        )
    else:
        lines.append("- Run final memo citation review before sharing externally.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deal_workspace", help="Path to deals/{deal-id}")
    parser.add_argument("--output", help="Output markdown path")
    parser.add_argument(
        "--fail-on-blocked",
        action="store_true",
        help="Exit non-zero when the deal status is 'blocked' (useful for CI guardrails).",
    )
    args = parser.parse_args()

    workspace = Path(args.deal_workspace)
    output = Path(args.output) if args.output else workspace / "diligence-dashboard.md"
    output.write_text(render_dashboard(workspace), encoding="utf-8")

    _, blockers, review_items = summarize_findings(workspace)
    status = determine_status(blockers, review_items)
    print(
        json.dumps(
            {
                "status": "ok",
                "output": str(output),
                "deal_status": status,
                "open_blockers": len(blockers),
                "open_review_items": len(review_items),
            },
            indent=2,
        )
    )
    if args.fail_on_blocked and status == "blocked":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
