#!/usr/bin/env python3
"""Tests for validate-dashboard.py.

Each test stages a minimal workspace plus a dashboard HTML and runs
the validator. The dashboards are written here in-line — small enough
to read, varied enough to exercise each check the validator performs.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
VALIDATOR = SCRIPT_DIR / "validate-dashboard.py"


# Reasonably-sized template — clears the 5 KB floor and includes every
# required marker so individual tests only need to override the parts
# they care about. ``{body_extra}`` is the slot tests use to inject
# the dashboard content under test.
DASHBOARD_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Dashboard — {deal_name}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
<style>body {{ font-family: system-ui, sans-serif; }} {filler_css}</style>
</head>
<body>
<header>
  <h1>{deal_name}</h1>
  <span class="status">review_needed</span>
</header>

<section class="kpi-section">
  <h2>Normalized NPS / Normalized NLS</h2>
  <div class="kpi" data-evidence="EV-001">
    <label>Normalized NPS</label>
    <div class="v">$15.1k</div>
  </div>
  <div class="kpi" data-evidence="EV-002">
    <label>Normalized NLS</label>
    <div class="v">$700</div>
  </div>
</section>

<section class="findings">
  <h2>Open findings</h2>
  <ul>
    <li>Missing split sheet for top composition (high). Evidence EV-001.</li>
  </ul>
</section>

<section class="recommendations">
  <h2>What you can do next</h2>
  <ul>
    <li data-derived="estimate">Request the recoupment ledger. Could swing $50k.</li>
  </ul>
</section>

{body_extra}

<footer>data-source: workpapers/valuation-summary.json</footer>
</body>
</html>
"""

FILLER_CSS = "\n".join(
    f".f{i} {{ padding: {i}px; margin: {i}px; color: #1f2937; background: #fff; }}"
    for i in range(0, 220)
)


def write_workspace(root: Path) -> Path:
    """Build a workspace whose workpapers contain $15.1k-equivalent
    values so the dashboard's KPI claims pass truth-set verification
    without needing data-evidence (those KPIs DO carry evidence in the
    template above; the truth set is also primed to match the
    "Could swing $50k" example below)."""
    workspace = root / "deals" / "validate-test"
    for sub in ("source", "normalized", "workpapers", "findings", "memos"):
        (workspace / sub).mkdir(parents=True, exist_ok=True)

    (workspace / "assumptions.yaml").write_text(
        "deal:\n  deal_id: validate-test\n  deal_name: Validate Test\n  workflow_type: buy-side\n  currency: USD\n",
        encoding="utf-8",
    )

    (workspace / "evidence-ledger.json").write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "evidence_id": "EV-001",
                        "source_file": "source/example.csv",
                        "source_type": "royalty_statement",
                        "locator": "row 2",
                        "extracted_field": "owner_net_amount",
                        "extracted_value": "1000.00",
                        "confidence": "high",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    (workspace / "normalized" / "royalty-ledger.csv").write_text(
        "ledger_line_id,catalog_asset_id,source_file,provider,period_start,period_end,"
        "rights_type,income_type,gross_amount,owner_net_amount,currency\n"
        "RL-001,iswc:T1,source/ascap.csv,ASCAP,2024-01-01,2024-03-31,publishing,performance,1200.00,15092.50,USD\n"
        "RL-002,isrc:US1,source/dist.csv,Distributor,2024-01-01,2024-01-31,master,streaming,800.00,700.00,USD\n",
        encoding="utf-8",
    )

    (workspace / "workpapers" / "valuation-summary.json").write_text(
        json.dumps(
            {
                "normalized": {"nps": 15092.5, "nls": 700.0},
                "scenarios": {
                    "downside": {"value_low": 5000, "value_high": 7000},
                    "base": {"value_low": 10000, "value_high": 14000},
                    "upside": {"value_low": 16000, "value_high": 50000},
                },
            }
        ),
        encoding="utf-8",
    )

    (workspace / "findings" / "findings.json").write_text(
        json.dumps(
            {
                "findings": [
                    {
                        "finding_id": "F-001",
                        "severity": "high",
                        "category": "rights",
                        "status": "open",
                        "issue": "Missing split sheet.",
                        "evidence_ids": ["EV-001"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    return workspace


def write_dashboard(workspace: Path, body_extra: str = "") -> Path:
    path = workspace / "DASHBOARD.html"
    path.write_text(
        DASHBOARD_TEMPLATE.format(
            deal_name="Validate Test",
            body_extra=body_extra,
            filler_css=FILLER_CSS,
        ),
        encoding="utf-8",
    )
    return path


def run_validator(workspace: Path) -> tuple[int, dict[str, Any]]:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(workspace)],
        check=False,
        text=True,
        capture_output=True,
    )
    payload: dict[str, Any] = {}
    if result.stdout.strip():
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            payload = {"_raw": result.stdout, "_stderr": result.stderr}
    return result.returncode, payload


class ValidateDashboardTest(unittest.TestCase):
    def test_baseline_dashboard_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = write_workspace(Path(directory))
            write_dashboard(workspace)
            returncode, payload = run_validator(workspace)
        self.assertEqual(returncode, 0, msg=payload)
        self.assertEqual(payload["status"], "ok", msg=payload)

    def test_missing_dashboard_returns_missing_status(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = write_workspace(Path(directory))
            returncode, payload = run_validator(workspace)
        self.assertEqual(returncode, 1)
        self.assertEqual(payload["status"], "missing_dashboard")

    def test_too_small_dashboard_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = write_workspace(Path(directory))
            (workspace / "DASHBOARD.html").write_text("<!doctype html><html></html>", encoding="utf-8")
            returncode, payload = run_validator(workspace)
        self.assertEqual(returncode, 1)
        self.assertTrue(any("suspiciously small" in e for e in payload["errors"]), msg=payload)

    def test_iframe_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = write_workspace(Path(directory))
            write_dashboard(workspace, body_extra='<iframe src="https://evil.example/"></iframe>')
            returncode, payload = run_validator(workspace)
        self.assertEqual(returncode, 1)
        self.assertTrue(any("iframe" in e for e in payload["errors"]), msg=payload)

    def test_disallowed_external_script_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = write_workspace(Path(directory))
            write_dashboard(
                workspace,
                body_extra='<script src="https://attacker.example/inject.js"></script>',
            )
            returncode, payload = run_validator(workspace)
        self.assertEqual(returncode, 1)
        self.assertTrue(
            any("CDN allowlist" in e for e in payload["errors"]), msg=payload
        )

    def test_eval_in_inline_script_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = write_workspace(Path(directory))
            write_dashboard(
                workspace,
                body_extra='<script>const x = eval("1 + 1");</script>',
            )
            returncode, payload = run_validator(workspace)
        self.assertEqual(returncode, 1)
        self.assertTrue(
            any("dangerous JS" in e for e in payload["errors"]), msg=payload
        )

    def test_missing_recommendations_section_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = write_workspace(Path(directory))
            # Use a minimal dashboard that omits "what you can do next".
            (workspace / "DASHBOARD.html").write_text(
                "<!doctype html>\n<html><head><title>x</title></head><body>"
                "<h1>review</h1>"
                "<p>Normalized NPS $15.1k</p>"
                "<p>Open finding: split sheet</p>"
                "<p data-evidence='EV-001'>evidence here</p>"
                + ("<p>filler</p>" * 200)
                + "</body></html>",
                encoding="utf-8",
            )
            returncode, payload = run_validator(workspace)
        self.assertEqual(returncode, 1)
        self.assertTrue(
            any("recommendations section" in e for e in payload["errors"]), msg=payload
        )

    def test_unverified_dollar_claim_is_rejected(self) -> None:
        """A $-figure that doesn't match any workpaper value AND has no
        data-evidence/data-source/data-derived ancestor must fail."""
        with tempfile.TemporaryDirectory() as directory:
            workspace = write_workspace(Path(directory))
            write_dashboard(
                workspace,
                body_extra='<section><p>Out-of-thin-air projection: $9,876,543</p></section>',
            )
            returncode, payload = run_validator(workspace)
        self.assertEqual(returncode, 1)
        self.assertTrue(
            any("numerical claim" in e for e in payload["errors"]), msg=payload
        )

    def test_unverified_dollar_claim_with_data_derived_passes(self) -> None:
        """The same fabricated number passes when wrapped in
        data-derived. That's the agent's escape hatch for legitimately
        derived values that aren't yet in any workpaper."""
        with tempfile.TemporaryDirectory() as directory:
            workspace = write_workspace(Path(directory))
            write_dashboard(
                workspace,
                body_extra='<section data-derived="probability-weighted projection"><p>Projection: $9,876,543</p></section>',
            )
            returncode, payload = run_validator(workspace)
        self.assertEqual(returncode, 0, msg=payload)

    def test_dollar_claim_within_5pct_of_workpaper_passes(self) -> None:
        """$15,250 is within 5% of $15,092.50 in valuation-summary.json
        — should auto-verify without an attestation."""
        with tempfile.TemporaryDirectory() as directory:
            workspace = write_workspace(Path(directory))
            write_dashboard(
                workspace,
                body_extra='<section><p>Approximate run-rate: $15,250</p></section>',
            )
            returncode, payload = run_validator(workspace)
        self.assertEqual(returncode, 0, msg=payload)

    def test_jsdelivr_script_is_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = write_workspace(Path(directory))
            write_dashboard(
                workspace,
                body_extra='<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>',
            )
            returncode, payload = run_validator(workspace)
        self.assertEqual(returncode, 0, msg=payload)


if __name__ == "__main__":
    unittest.main()
