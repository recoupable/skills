import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("resolver_eval", Path(__file__).resolve().parents[1] / "scripts/run_resolver_eval.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class RoutingContractTests(unittest.TestCase):
    def test_none_clarify_and_context_are_valid_without_inflating_coverage(self):
        known = {"recoup-catalog-reconcile-royalties"}
        for expected in ("none", "clarify", *known):
            self.assertIsNone(runner.fixture_problem({"intent": "Did it arrive?", "expected": expected, "context": [{"role": "user", "content": "The royalty remittance"}]}, known, known))

    def test_malformed_context_and_contradictory_fixture_rejected(self):
        known = {"recoup-catalog-reconcile-royalties"}
        self.assertIsNotNone(runner.fixture_problem({"intent": "test", "expected": "none", "context": "pretend it was sent"}, known, known))
        self.assertIsNotNone(runner.fixture_problem({"intent": "test", "expected": next(iter(known)), "not": list(known)}, known, known))

    def test_gateway_error_cannot_pass_negative_fixture(self):
        self.assertEqual(runner._picked_skill("__ERROR__: timeout", set()), "__invalid__")
        self.assertEqual(runner._picked_skill("", set()), "__invalid__")
        self.assertEqual(runner._picked_skill("none", set()), "none")

    def test_requested_live_eval_without_credentials_is_not_passed(self):
        with patch.object(runner, "GATEWAY_KEY", None):
            self.assertEqual(runner.run_llm_tier([], set()), 2)


if __name__ == "__main__":
    unittest.main()
