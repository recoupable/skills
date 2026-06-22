#!/usr/bin/env python3
"""Post-hoc trust enforcement for the agent-built executive dashboard.

The dashboard at ``deals/{deal-id}/DASHBOARD.html`` is written by the
agent (via recoup-catalogs dashboard mode). This script validates it
without rendering anything. It is the trust gate that lets us give
the agent full creative freedom while still keeping the deliverable
defensible.

Checks performed:

1. File exists at deals/{deal-id}/DASHBOARD.html.
2. File parses as HTML and is between 5 KB and 5 MB.
3. Every external <script src=...> is on the CDN allowlist.
4. No <iframe>, <object>, or <embed> tags.
5. No eval(, Function(, or document.write( in inline JS.
6. Required structural markers present (status, KPIs, findings,
   recommendations, evidence-trail signal).
7. Every $-claim in visible body text either matches a workpaper value
   within 5%, or lives inside an element with data-evidence /
   data-source / data-derived on it (or any ancestor).

Exits 0 (status=ok) or 1 (status=errors_found). Errors and warnings
are printed as JSON so the agent can read and fix them.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _helpers import deep_get, load_yaml  # noqa: E402


CDN_ALLOWLIST = {
    "cdn.jsdelivr.net",
    "cdnjs.cloudflare.com",
    "unpkg.com",
}
DANGEROUS_JS = (
    "eval(",
    "Function(",
    "document.write(",
    "document.writeln(",
)
VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}
ATTESTATION_ATTRS = ("data-evidence", "data-source", "data-derived")
DOLLAR_PATTERN = re.compile(r"\$\s*([\d][\d,]*(?:\.\d+)?)\s*([KkMm]?)\b")
TOLERANCE = 0.05  # 5%
MIN_BYTES = 5 * 1024
MAX_BYTES = 5 * 1024 * 1024


# Required structural markers. Each tuple is (label, list of phrases —
# at least one phrase must appear in the visible HTML body for the
# section to count as present). Case-insensitive substring match.
REQUIRED_MARKERS: list[tuple[str, tuple[str, ...]]] = [
    ("status indicator", ("ready", "review", "blocked", "review_needed", "review needed")),
    ("KPI section", ("normalized nps", "normalized nls", "net publisher share", "net label share", "ltm")),
    ("findings section", ("finding", "blocker", "open issue", "deal issue")),
    ("evidence trail", ("evidence", "source", "data-evidence", "data-source", "data-derived")),
    (
        "recommendations section",
        (
            "what you can do next",
            "recommendations",
            "next steps",
            "recommended actions",
            "what would change",
        ),
    ),
]


# --- HTML parsing ---------------------------------------------------------


class DashboardParser(HTMLParser):
    """Walks the dashboard HTML once and accumulates everything the
    validator needs: the visible text, external script URLs, banned
    element occurrences, and a per-text-node attestation context."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        # Stack of (tag_name, attestation) entries. ``attestation`` is the
        # value of the most relevant data-* attribute on this element, or
        # None if the element has none. The "current attestation" is the
        # nearest non-None entry up the stack.
        self.tag_stack: list[tuple[str, str | None]] = []
        self.in_script: bool = False
        self.in_style: bool = False

        self.script_srcs: list[str] = []
        self.has_iframe: bool = False
        self.has_object_or_embed: bool = False
        self.inline_script_text: list[str] = []
        self.visible_text_parts: list[str] = []
        # Each dollar claim recorded as (raw_text, value_float, attestation_or_None).
        self.dollar_claims: list[tuple[str, float, str | None]] = []
        self.parse_failed: bool = False
        self.parse_failure_reason: str = ""

    # --- helpers ----------------------------------------------------------
    def _attestation_in_attrs(self, attrs: list[tuple[str, str | None]]) -> str | None:
        attrs_dict = {key: value for key, value in attrs}
        for key in ATTESTATION_ATTRS:
            value = attrs_dict.get(key)
            if value:
                return f"{key}={value}"
        return None

    def _current_attestation(self) -> str | None:
        for _tag, attestation in reversed(self.tag_stack):
            if attestation:
                return attestation
        return None

    # --- HTMLParser hooks -------------------------------------------------
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag_lower = tag.lower()
        if tag_lower == "script":
            self.in_script = True
            for key, value in attrs:
                if key == "src" and value:
                    self.script_srcs.append(value)
        elif tag_lower == "style":
            self.in_style = True
        elif tag_lower == "iframe":
            self.has_iframe = True
        elif tag_lower in {"object", "embed"}:
            self.has_object_or_embed = True

        attestation = self._attestation_in_attrs(attrs)
        if tag_lower not in VOID_ELEMENTS:
            self.tag_stack.append((tag_lower, attestation))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        # <foo /> shorthand. Treat as void — don't push.
        tag_lower = tag.lower()
        if tag_lower == "iframe":
            self.has_iframe = True
        if tag_lower in {"object", "embed"}:
            self.has_object_or_embed = True

    def handle_endtag(self, tag: str) -> None:
        tag_lower = tag.lower()
        if tag_lower == "script":
            self.in_script = False
        elif tag_lower == "style":
            self.in_style = False
        # Pop the matching tag if it's at the top of the stack. Be lenient
        # about malformed nesting — scan and remove the nearest match
        # rather than crashing.
        for index in range(len(self.tag_stack) - 1, -1, -1):
            if self.tag_stack[index][0] == tag_lower:
                del self.tag_stack[index:]
                break

    def handle_data(self, data: str) -> None:
        if self.in_script:
            self.inline_script_text.append(data)
            return
        if self.in_style:
            return
        if not data.strip():
            return
        self.visible_text_parts.append(data)
        attestation = self._current_attestation()
        for match in DOLLAR_PATTERN.finditer(data):
            value = parse_dollar_value(match)
            if value is None:
                continue
            self.dollar_claims.append((match.group(0), value, attestation))


def parse_dollar_value(match: re.Match[str]) -> float | None:
    raw = match.group(1).replace(",", "")
    try:
        value = float(raw)
    except ValueError:
        return None
    suffix = (match.group(2) or "").lower()
    if suffix == "k":
        value *= 1000
    elif suffix == "m":
        value *= 1_000_000
    return value


# --- Truth-set assembly ---------------------------------------------------


def parse_amount(value: str | None) -> float:
    if not value:
        return 0.0
    cleaned = (
        str(value)
        .replace("$", "")
        .replace(",", "")
        .replace("(", "-")
        .replace(")", "")
        .strip()
    )
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def load_json(path: Path) -> Any:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def collect_truth_values(workspace: Path) -> set[float]:
    """Build the set of $-values the agent is allowed to claim without
    needing an explicit attestation. Drawn from every primary workpaper
    that the dashboard might quote."""
    truth: set[float] = set()

    def add(value: Any) -> None:
        if isinstance(value, bool):
            return
        if isinstance(value, (int, float)):
            truth.add(float(value))
            truth.add(abs(float(value)))

    workpapers = workspace / "workpapers"

    # Valuation summary — normalized + scenarios.
    valuation = load_json(workpapers / "valuation-summary.json")
    if isinstance(valuation, dict):
        normalized = valuation.get("normalized") or {}
        if isinstance(normalized, dict):
            for key in ("nps", "nls", "ltm", "ttm", "reported_nps", "reported_nls"):
                add(normalized.get(key))
        scenarios = valuation.get("scenarios") or {}
        if isinstance(scenarios, dict):
            for scenario in scenarios.values():
                if isinstance(scenario, dict):
                    for key in ("value", "value_low", "value_high"):
                        add(scenario.get(key))

    # NPS / NLS bridges.
    for filename in ("nps-bridge.json", "nls-bridge.json"):
        bridge = load_json(workpapers / filename)
        if not isinstance(bridge, dict):
            continue
        add(bridge.get("reported_amount"))
        add(bridge.get("normalized_amount"))
        for row in bridge.get("bridge", []):
            if isinstance(row, dict):
                add(row.get("amount"))
                add(row.get("running_total"))

    # Concentration analysis — top-N entries.
    conc = load_json(workpapers / "concentration-analysis.json")
    if isinstance(conc, dict):
        add(conc.get("total"))
        concentration = conc.get("concentration") or {}
        if isinstance(concentration, dict):
            for dim_data in concentration.values():
                if isinstance(dim_data, dict):
                    for entry in dim_data.get("top_10_entries") or []:
                        if isinstance(entry, dict):
                            add(entry.get("amount"))

    # Ingest coverage — usually counts not dollars, but include defensively.
    coverage = load_json(workpapers / "ingest-coverage.json")
    if isinstance(coverage, dict):
        add(coverage.get("total_files"))

    # Royalty ledger — totals + per-rights-type + per-provider + per-asset.
    ledger_path = workspace / "normalized" / "royalty-ledger.csv"
    if ledger_path.is_file():
        try:
            with ledger_path.open(newline="", encoding="utf-8-sig") as handle:
                rows = list(csv.DictReader(handle))
        except OSError:
            rows = []
        if rows:
            grand_total = sum(parse_amount(r.get("owner_net_amount")) for r in rows)
            grand_gross = sum(parse_amount(r.get("gross_amount")) for r in rows)
            add(grand_total)
            add(grand_gross)
            by_rights: dict[str, float] = defaultdict(float)
            by_provider: dict[str, float] = defaultdict(float)
            by_asset: dict[str, float] = defaultdict(float)
            for row in rows:
                rights_key = (row.get("rights_type") or "").lower().strip()
                provider_key = (row.get("provider") or "").strip()
                asset_key = (row.get("catalog_asset_id") or "").strip()
                amount = parse_amount(row.get("owner_net_amount"))
                if rights_key:
                    by_rights[rights_key] += amount
                if provider_key:
                    by_provider[provider_key] += amount
                if asset_key:
                    by_asset[asset_key] += amount
            for value in (*by_rights.values(), *by_provider.values(), *by_asset.values()):
                add(value)

    # Anything in workpapers/*.json with numeric fields adjacent to
    # "amount" / "value" / "nps" / "nls" — be greedy. The truth set is a
    # WHITELIST, so over-collection only makes the validator more
    # permissive, never less safe.
    if workpapers.is_dir():
        for path in workpapers.rglob("*.json"):
            data = load_json(path)
            collect_numeric_recursively(data, add)

    # Assumptions.yaml — multiples, discount_rate, thresholds.
    assumptions_path = workspace / "assumptions.yaml"
    if assumptions_path.is_file():
        try:
            assumptions = load_yaml(assumptions_path)
        except OSError:
            assumptions = {}
        collect_numeric_recursively(assumptions, add)

    return truth


def collect_numeric_recursively(node: Any, add) -> None:
    """Walk a JSON-shaped tree and add any int/float leaves to the truth set."""
    if isinstance(node, dict):
        for value in node.values():
            collect_numeric_recursively(value, add)
    elif isinstance(node, list):
        for item in node:
            collect_numeric_recursively(item, add)
    elif isinstance(node, (int, float)) and not isinstance(node, bool):
        add(node)


def value_matches_truth(claim_value: float, truth: set[float], tolerance: float = TOLERANCE) -> bool:
    if abs(claim_value) < 1.0:
        # Treat near-zero claims as auto-verified — every truth set has
        # plenty of zero-ish values and rounding to "$0" is benign.
        return True
    for truth_value in truth:
        if truth_value == 0:
            continue
        if abs(claim_value - truth_value) / abs(truth_value) <= tolerance:
            return True
    return False


# --- External-resource and inline-JS checks --------------------------------


def host_of(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.lower()


def disallowed_script_srcs(script_srcs: list[str]) -> list[str]:
    bad: list[str] = []
    for src in script_srcs:
        host = host_of(src)
        # Allow same-origin (no host) — those are inline references to
        # files in the same workspace and won't make network calls.
        if not host:
            continue
        if host not in CDN_ALLOWLIST and not any(host.endswith("." + cdn) for cdn in CDN_ALLOWLIST):
            bad.append(src)
    return bad


def dangerous_js_hits(inline_text: str) -> list[str]:
    hits: list[str] = []
    for needle in DANGEROUS_JS:
        if needle in inline_text:
            hits.append(needle.rstrip("("))
    return hits


def missing_required_markers(visible_text: str, raw_html: str) -> list[str]:
    haystack = visible_text.lower()
    raw = raw_html.lower()
    missing: list[str] = []
    for label, phrases in REQUIRED_MARKERS:
        if any(phrase.lower() in haystack or phrase.lower() in raw for phrase in phrases):
            continue
        missing.append(label)
    return missing


# --- Top-level driver -----------------------------------------------------


def validate(workspace: Path, dashboard_path: Path | None = None) -> dict[str, Any]:
    if dashboard_path is None:
        dashboard_path = workspace / "DASHBOARD.html"

    errors: list[str] = []
    warnings: list[str] = []

    if not dashboard_path.is_file():
        return {
            "status": "missing_dashboard",
            "workspace": str(workspace),
            "dashboard": str(dashboard_path),
            "errors": [f"DASHBOARD.html not found at {dashboard_path}"],
            "warnings": [],
        }

    size = dashboard_path.stat().st_size
    if size < MIN_BYTES:
        errors.append(
            f"dashboard is suspiciously small ({size} bytes < {MIN_BYTES} byte floor) — likely empty or broken"
        )
    elif size > MAX_BYTES:
        errors.append(
            f"dashboard is suspiciously large ({size} bytes > {MAX_BYTES} byte ceiling) — likely embedded raw data"
        )

    raw_html = dashboard_path.read_text(encoding="utf-8", errors="replace")
    head = raw_html.lstrip()[:512].lower()
    if not (head.startswith("<!doctype") or head.startswith("<html")):
        errors.append("dashboard does not start with <!doctype html> or <html>")

    parser = DashboardParser()
    try:
        parser.feed(raw_html)
    except Exception as exc:  # pragma: no cover - defensive
        errors.append(f"HTML parser failed: {exc}")

    visible_text = " ".join(parser.visible_text_parts)
    inline_text = "".join(parser.inline_script_text)

    if parser.has_iframe:
        errors.append("<iframe> tag is disallowed in the dashboard")
    if parser.has_object_or_embed:
        errors.append("<object> or <embed> tags are disallowed in the dashboard")

    bad_srcs = disallowed_script_srcs(parser.script_srcs)
    if bad_srcs:
        errors.append(
            "external <script src> not in CDN allowlist: "
            + ", ".join(bad_srcs)
            + f". Allowed: {sorted(CDN_ALLOWLIST)}."
        )

    js_hits = dangerous_js_hits(inline_text)
    if js_hits:
        errors.append(
            "dangerous JS pattern(s) found in inline scripts: " + ", ".join(js_hits)
        )

    missing = missing_required_markers(visible_text, raw_html)
    if missing:
        errors.append("missing required dashboard sections: " + ", ".join(missing))

    truth = collect_truth_values(workspace)
    unverified: list[dict[str, Any]] = []
    for raw_text, value, attestation in parser.dollar_claims:
        if attestation:
            continue
        if value_matches_truth(value, truth):
            continue
        unverified.append({"text": raw_text, "value": value})
    if unverified:
        sample = unverified[:8]
        errors.append(
            f"{len(unverified)} numerical claim(s) on the dashboard do not match any workpaper "
            "value (within 5%) and have no data-evidence / data-source / data-derived ancestor. "
            f"Examples: {sample}. Either correct the number, cite the source via "
            "data-evidence='EV-NNN', or mark as derived via data-derived='<reason>'."
        )

    status = "ok" if not errors else "errors_found"
    return {
        "status": status,
        "workspace": str(workspace),
        "dashboard": str(dashboard_path),
        "size_bytes": size,
        "external_scripts": parser.script_srcs,
        "dollar_claims_seen": len(parser.dollar_claims),
        "dollar_claims_unverified": len(unverified),
        "truth_set_size": len(truth),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deal_workspace", help="Path to deals/{deal-id}")
    parser.add_argument(
        "--dashboard",
        default=None,
        help="Path to the dashboard HTML (default: {workspace}/DASHBOARD.html).",
    )
    args = parser.parse_args()

    workspace = Path(args.deal_workspace)
    dashboard = Path(args.dashboard) if args.dashboard else None
    payload = validate(workspace, dashboard)
    print(json.dumps(payload, indent=2))
    return 0 if payload["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
