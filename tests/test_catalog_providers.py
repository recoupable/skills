"""Registry integrity checks; these do not execute providers or prove live coverage."""
import json
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1] / "references/catalog-providers"


class ProviderRegistryTests(unittest.TestCase):
    def test_operation_profiles_are_sourced_and_explicit_about_capability(self):
        sources = json.loads((ROOT / "sources.json").read_text())["sources"]
        ids = {item["id"] for item in sources}
        self.assertEqual(len(ids), len(sources))
        for source in sources:
            self.assertEqual(urlparse(source["url"]).scheme, "https")
            self.assertTrue(source["check_result"])
        operations = json.loads((ROOT / "operations.json").read_text())["operations"]
        profiles = {item["profile_id"] for item in operations}
        self.assertEqual(len(profiles), len(operations))
        for operation in operations:
            with self.subTest(profile=operation["profile_id"]):
                for field in ("profile_version", "provider", "operation", "subject_type", "eligible_roles", "rights", "territory_rule", "share_basis", "documented_route", "required_inputs", "preflight", "receipt", "readback"):
                    self.assertTrue(operation[field], field)
                self.assertIn(operation["stage"], {"audit", "register", "resolve_claims", "manage_delivery", "reconcile"})
                self.assertTrue(set(operation["source_ids"]).issubset(ids))
                if not operation["source_ids"]:
                    self.assertIn(operation["documented_route"], {"unresearched_account_specific_route", "issuer_route_requires_verification"})
                    self.assertTrue(operation["profile_id"].endswith("-readiness"))
                reference = (ROOT / operation["reference"]).resolve()
                self.assertTrue(reference.is_relative_to(ROOT.resolve()))
                self.assertTrue(reference.is_file())
                self.assertEqual(operation["capability"], {
                    "preparation": "evidence_packet",
                    "provider_schema_validation": "requires_current_schema_and_account_review",
                    "automated_submission": "not_implemented",
                    "authenticated_readback": "not_verified",
                    "live_operation": "not_verified"})
        corpus = json.loads((ROOT / "conformance-cases.json").read_text())
        self.assertIs(corpus["synthetic"], True)
        cases = corpus["cases"]
        self.assertEqual(len({item["id"] for item in cases}), len(cases))
        for case in cases:
            self.assertIn(case["profile_id"], profiles)
            self.assertTrue(case["inputs"])
            self.assertTrue(case["expected"])
