"""Execute the shipped recovery examples against synthetic responses only.

Use --installed-root /path/to/extracted-customer for all five packaged guides
and the packaged estimator, including from an unrelated working directory.
This is an isolated file-install fixture, not named-client discovery or live auth.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
BILLING = "https://recoup.fixture.invalid/billing"
CHECKOUT = "https://checkout.fixture.invalid/setup"
PAYMENT_ERROR = "A payment method is required. Add a card to continue."


class BillingRecoveryExamples(unittest.TestCase):
    research_reference = ROOT / "references/research-context.md"
    estimator_script = ROOT / "skills/recoup-catalog-estimate-value/scripts/estimate.py"

    def run_research(self, payload, status=402):
        text = self.research_reference.read_text()
        helper = re.search(r"research_get\(\) \{[\s\S]*?\n\}", text).group()
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "calls"
            environment = {
                **os.environ,
                "FIXTURE_BODY": json.dumps(payload),
                "FIXTURE_STATUS": str(status),
                "FIXTURE_CALLS": str(log),
            }
            mock = """
BASE=https://recoup.fixture.invalid/api
AUTH=()
curl() {
  printf '%s\\0' "$*" >> "$FIXTURE_CALLS"
  printf '%s\\n%s' "$FIXTURE_BODY" "$FIXTURE_STATUS"
}
sleep() { echo 'Unexpected retry' >&2; return 91; }
"""
            result = subprocess.run(
                ["bash", "-c", mock + helper + '\nresearch_get "metrics?id=fixture"'],
                env=environment, capture_output=True, text=True, timeout=10,
            )
            calls = [call.decode() for call in log.read_bytes().split(b"\0") if call]
            return result.returncode, result.stdout, result.stderr, calls

    def run_estimator(self, payload, status=402):
        path = self.estimator_script
        spec = importlib.util.spec_from_file_location("recovery_estimate", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.BASE = "https://recoup.fixture.invalid/api"
        response = subprocess.CompletedProcess([], 0, json.dumps(payload) + "\n" + str(status), "")
        with patch.object(module, "auth_header", return_value=[]), patch.object(
            module.subprocess, "run", return_value=response
        ) as http:
            try:
                value = module.api("research/track/stats")
            except SystemExit as error:
                code, stdout, stderr = 1, "", str(error)
            else:
                code, stdout, stderr = 0, json.dumps(value), ""
        return code, stdout, stderr, [call.args[0] for call in http.call_args_list]

    def denied(self, runner, payload):
        code, stdout, stderr, calls = runner(payload)
        self.assertNotEqual(code, 0)
        self.assertEqual(stdout, "")
        self.assertEqual(len(calls), 1, "Do not retry, follow recovery links or create a session")
        self.assertIn("recoup.fixture.invalid/api/research", str(calls[0]))
        return stderr

    def test_credit_shortfall_uses_billing_link_and_ignores_checkout(self):
        for runner in (self.run_research, self.run_estimator):
            with self.subTest(example=runner.__name__):
                error = self.denied(runner, {
                    "error": "insufficient_credits", "remaining_credits": 0,
                    "required_credits": 1, "billingUrl": BILLING, "checkoutUrl": CHECKOUT,
                })
                self.assertIn(BILLING, error)
                self.assertNotIn(CHECKOUT, error)

    def test_payment_method_gate_preserves_checkout_link(self):
        for runner in (self.run_research, self.run_estimator):
            with self.subTest(example=runner.__name__):
                error = self.denied(runner, {
                    "status": "error", "error": PAYMENT_ERROR, "checkoutUrl": CHECKOUT,
                })
                self.assertIn(CHECKOUT, error)
                self.assertNotIn("needs credits", error)

    def test_missing_credit_link_does_not_fall_back_to_card_setup(self):
        for runner in (self.run_research, self.run_estimator):
            with self.subTest(example=runner.__name__):
                error = self.denied(runner, {
                    "error": "insufficient_credits", "checkoutUrl": CHECKOUT,
                })
                self.assertIn("Check account billing", error)
                self.assertNotIn(CHECKOUT, error)

    def test_payment_gate_does_not_substitute_credit_link(self):
        for runner in (self.run_research, self.run_estimator):
            with self.subTest(example=runner.__name__):
                error = self.denied(runner, {
                    "error": PAYMENT_ERROR, "billingUrl": BILLING,
                })
                self.assertIn("Check account billing", error)
                self.assertNotIn(BILLING, error)

    def test_missing_or_malformed_links_remain_blocked(self):
        for runner in (self.run_research, self.run_estimator):
            for error, field in (("insufficient_credits", "billingUrl"), (PAYMENT_ERROR, "checkoutUrl")):
                for value in (None, "", [], {}, 7, "not-a-url", "javascript:fixture", "https://",
                              "https://@/setup", "https://:443/setup",
                              "https://billing.fixture.invalid:bad/setup"):
                    with self.subTest(example=runner.__name__, field=field, value=value):
                        message = self.denied(runner, {"error": error, field: value})
                        self.assertIn("Check account billing", message)
                        if isinstance(value, str) and value:
                            self.assertNotIn(value, message)

    def test_non_object_error_body_has_controlled_billing_fallback(self):
        for runner in (self.run_research, self.run_estimator):
            for body in (None, [], "unavailable"):
                with self.subTest(example=runner.__name__, body=body):
                    error = self.denied(runner, body)
                    self.assertIn("Check account billing", error)

    def test_successful_reads_preserve_payload_without_recovery_calls(self):
        payload = {"stats": [], "data_source": "fixture"}
        for runner in (self.run_research, self.run_estimator):
            with self.subTest(example=runner.__name__):
                code, stdout, stderr, calls = runner(payload, status=200)
                self.assertEqual(code, 0)
                self.assertEqual(json.loads(stdout), payload)
                self.assertEqual(stderr, "")
                self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--installed-root", type=Path)
    arguments, remaining = parser.parse_known_args()
    if arguments.installed_root:
        installed = arguments.installed_root.resolve()
        suite = unittest.TestSuite()
        for skill in ("recoup-content-asset-pack", "recoup-content-make-graphics",
                      "recoup-content-make-video", "recoup-content-reactive-post",
                      "recoup-content-write-caption"):
            case = type(
                "Installed_" + skill.replace("-", "_"),
                (BillingRecoveryExamples,),
                {
                    "research_reference": installed / "skills" / skill / "references/research-context.md",
                    "estimator_script": installed / "skills/recoup-catalog-estimate-value/scripts/estimate.py",
                },
            )
            suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(case))
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        raise SystemExit(0 if result.wasSuccessful() else 1)
    unittest.main(argv=[sys.argv[0], *remaining])
