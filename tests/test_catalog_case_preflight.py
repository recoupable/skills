import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('catalog_case', Path(__file__).parents[1] / 'scripts/catalog-case.py')
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class ResumedPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'snapshot.json'
        payload = {'provider': 'synthetic', 'operation': 'amend', 'account': 'synthetic-account',
                   'party': 'synthetic-party', 'subjects': ['work-1'], 'scope': {'territory': 'US'},
                   'disclosure': [], 'costs': []}
        derived = {'source_refs': [], 'evidence_gap': 'Synthetic dependency chain', 'rule_version': 'test-v1'}
        self.case = {'schema_version': 1, 'case_id': '11111111-1111-4111-8111-111111111111',
                     'workspace_id': '22222222-2222-4222-8222-222222222222', 'revision': 1, 'scope': 'synthetic',
                     'sources': {'s': {'id': 's', 'version': 'v1', 'sha256': 'a' * 64, 'locator': 'synthetic.csv', 'status': 'active'}},
                     'assessments': {'a': {**derived, 'id': 'a', 'stage': 'audit', 'status': 'complete', 'source_refs': [{'source_id': 's', 'version': 'v1'}]}},
                     'findings': {'f': {**derived, 'id': 'f', 'stage': 'audit', 'status': 'open', 'cause_id': 'synthetic', 'depends_on': ['a']}},
                     'actions': {'action': {**derived, 'id': 'action', 'stage': 'register', 'status': 'authorized', 'depends_on': ['f'], 'payload': payload,
                                           'authorization': {'reference': 'synthetic instruction', 'payload_sha256': MOD.fingerprint(payload), 'scope': payload['scope'], 'valid_until': '2099-01-01T00:00:00Z'}}},
                     'attempts': {}, 'outcomes': {}}

    def preflight(self, expected):
        self.path.write_text(json.dumps(self.case))
        original = self.path.read_bytes()
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = MOD.main(['preflight', '--file', str(self.path), '--action-id', 'action'])
        self.assertEqual(code, expected, stdout.getvalue() + stderr.getvalue())
        self.assertEqual(self.path.read_bytes(), original)
        if expected == 0:
            self.assertEqual(json.loads(stdout.getvalue())['external_preflight'], 'required')
        return stderr.getvalue()

    def test_hosted_stale_assessment_cannot_leave_transitive_action_current(self):
        self.case['sources']['s']['status'] = 'withdrawn'
        self.case['assessments']['a']['stale'] = True
        self.assertIn('dependency', self.preflight(2))

    def test_unmarked_withdrawn_or_revised_evidence_blocks_preflight(self):
        for patch in ({'status': 'withdrawn'}, {'version': 'v2', 'sha256': 'b' * 64}):
            with self.subTest(patch=patch):
                original = self.case['sources']['s'].copy()
                self.case['sources']['s'].update(patch)
                self.preflight(2)
                self.case['sources']['s'] = original

    def test_current_chain_without_history_passes_and_unrelated_stale_record_does_not_block(self):
        self.case['findings']['unrelated'] = {**self.case['findings']['f'], 'id': 'unrelated', 'depends_on': [], 'stale': True}
        self.preflight(0)

    def test_missing_or_cyclic_dependency_blocks_preflight(self):
        for deps in (['missing'], ['action']):
            with self.subTest(deps=deps):
                self.case['assessments']['a']['depends_on'] = deps
                self.preflight(2)

    def test_withdrawn_action_dependency_blocks_direct_and_outcome_paths(self):
        prior = copy.deepcopy(self.case['actions']['action'])
        prior.update(id='prior', status='withdrawn', depends_on=[])
        self.case['actions']['prior'] = prior
        self.case['outcomes']['prior-outcome'] = {'id': 'prior-outcome', 'action_id': 'prior', 'dimension': 'provider_decision', 'status': 'pending',
                                                'source_refs': [], 'evidence_gap': 'Pending readback', 'rule_version': 'test-v1'}
        for dependency in ('prior', 'prior-outcome'):
            with self.subTest(dependency=dependency):
                self.case['actions']['action']['depends_on'] = [dependency]
                self.assertIn('withdrawn', self.preflight(2))

    def test_redacted_attempt_cannot_disappear_from_retry_guard(self):
        self.case['attempts']['unknown'] = {'id': 'unknown', 'status': 'unknown_outcome', 'stale': True, 'withheld': True}
        self.assertIn('Redacted', self.preflight(2))

    def test_stale_unknown_attempt_still_blocks_after_chain_is_reassessed(self):
        self.case['attempts']['unknown'] = {'id': 'unknown', 'action_id': 'action', 'payload_sha256': MOD.fingerprint(self.case['actions']['action']['payload']),
                                          'status': 'unknown_outcome', 'stale': True, 'source_refs': [], 'evidence_gap': 'timeout', 'rule_version': 'test-v1'}
        self.assertIn('Unknown outcome', self.preflight(2))

    def test_current_accepted_outcome_still_blocks_resend(self):
        self.case['outcomes']['accepted'] = {'id': 'accepted', 'action_id': 'action', 'dimension': 'provider_decision', 'status': 'accepted',
                                           'source_refs': [{'source_id': 's', 'version': 'v1'}], 'rule_version': 'test-v1'}
        self.assertIn('Do not resend', self.preflight(2))


if __name__ == '__main__':
    unittest.main()
