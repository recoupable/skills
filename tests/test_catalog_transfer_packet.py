"""Synthetic transfer cases: no account or provider operations."""
import copy
import json
import subprocess
import sys
import unittest
import test_catalog_provider_packet as fixtures
ROOT, packet = fixtures.ROOT, fixtures.packet


class TransferTests(unittest.TestCase):
    save = fixtures.PacketTests.save
    run_packet = fixtures.PacketTests.run_packet
    def setUp(self):
        fixtures.PacketTests.setUp(self)
        self.action['payload']['operation'] = 'collection_catalog_transfer'
        self.action['payload']['scope']['subject_type'] = 'collection_mandate'
        self.action['payload']['disclosure'] = ['Supporting documents forwarded to existing claimants']
        self.mapping['profile_id'] = 'mlc-transfer'
        self.mapping['payload_sha256'] = packet.fingerprint(self.action['payload'])
        self.labels = ['registered work list', 'source member', 'effective date',
                       'authentic authority/termination evidence']
        self.mapping['required_inputs'] = {label: [{'source_id': 'source1', 'version': 'v1'}]
                                           for label in self.labels}
        self.save()

    def test_transfer_complete_packet_preserves_binding_and_boundaries(self):
        result = self.run_packet()
        self.assertEqual(result['status'], 'prepared')
        self.assertEqual(result['payload'], self.action['payload'])
        self.assertEqual(result['profile_id'], 'mlc-transfer')
        self.assertEqual(result['public_preparation_guidance_sha256'],
                         packet.fingerprint(result['public_preparation_guidance']))
        self.assertEqual(set(result['public_preparation_guidance']['required_input_guidance']), set(self.labels))
        self.assertEqual(result['field_validation'], 'not_performed')
        self.assertNotIn('public_field_checks', result)
        self.assertEqual(result['role_verification'], 'unverified')
        self.assertEqual(result['external_preflight'], 'unverified')
        for value in result['transfer_review'].values():
            self.assertEqual(value['verification'], 'unverified')
        self.assertIn('existing claimants', result['transfer_review']['document_disclosure']['requirement'])
        self.assertIn('source_release', result['transfer_review'])
        self.assertIn('target_acceptance', result['transfer_review'])
        self.assertIn('collection_tails', result['transfer_review'])
        self.assertEqual(self.case['attempts'], {})
        self.assertEqual(self.case['outcomes'], {})

    def test_transfer_each_missing_input_blocks_with_specific_guidance(self):
        for label in self.labels:
            with self.subTest(label=label):
                refs = self.mapping['required_inputs'].pop(label)
                result = self.run_packet()
                self.assertEqual(result['status'], 'blocked')
                self.assertEqual(result['missing_inputs'], [label])
                self.assertEqual(set(result['missing_input_guidance']), {label})
                self.output.unlink()
                self.mapping['required_inputs'][label] = refs

    def test_transfer_rejects_new_work_values_without_output(self):
        self.mapping['field_values'] = {'subject_id': 'synthetic-work'}
        with self.assertRaisesRegex(ValueError, 'field_values'):
            self.run_packet()
        self.assertFalse(self.output.exists())

    def test_transfer_mismatch_and_withdrawal_guards(self):
        # Exercise the shared guards against this profile, not just new work.
        for field, value in [('case_id', 'other'), ('revision', 1), ('action_id', 'other'),
                             ('payload_sha256', '0'*64), ('profile_version', 'old'),
                             ('profile_id', 'mlc-amendment'), ('role', 'songwriter_hub')]:
            old = self.mapping[field]; self.mapping[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError): self.run_packet()
            self.assertFalse(self.output.exists()); self.mapping[field] = old
        for record in [self.source, self.action]:
            for change in [{'stale': True}, {'withheld': True}, {'status': 'withdrawn'}]:
                old = copy.deepcopy(record); record.update(change)
                with self.subTest(change=change), self.assertRaises(ValueError): self.run_packet()
                self.assertFalse(self.output.exists()); record.clear(); record.update(old)
        self.mapping['required_inputs'][self.labels[0]][0]['version'] = 'old'
        with self.assertRaises(ValueError): self.run_packet()
        self.assertFalse(self.output.exists())

    def test_transfer_wrong_operation_subject_and_rights_rejected(self):
        for key, value in [('provider', 'Other'), ('operation', 'new_work_registration'),
                           ('scope', {'subject_type': 'composition', 'rights': ['composition mechanical']}),
                           ('scope', {'subject_type': 'collection_mandate', 'rights': ['master']})]:
            old = self.action['payload'][key]; self.action['payload'][key] = value
            self.mapping['payload_sha256'] = packet.fingerprint(self.action['payload'])
            with self.subTest(key=key), self.assertRaises(ValueError): self.run_packet()
            self.assertFalse(self.output.exists()); self.action['payload'][key] = old

    def test_transfer_duplicate_attempts_and_dependency_versions_rejected(self):
        for group in ['attempts', 'outcomes']:
            self.case[group]['old'] = {'id': 'old', 'action_id': 'action1', 'status': 'unknown_outcome'}
            with self.subTest(group=group), self.assertRaises(ValueError): self.run_packet()
            self.assertFalse(self.output.exists()); self.case[group].clear()
        self.case['assessments']['dep'] = {'id': 'dep', 'status': 'prepared', 'stage': 'register',
            'rule_version': '1', 'source_refs': [{'source_id': 'source1', 'version': 'old'}]}
        self.action['depends_on'] = ['dep']
        with self.assertRaises(ValueError): self.run_packet()
        self.assertFalse(self.output.exists())

    def test_transfer_unsupported_route_and_unverified_profile_source_rejected(self):
        from unittest.mock import patch
        original = packet.strict_json
        for invalid in ['route', 'source']:
            def parse(raw, **kwargs):
                value = original(raw, **kwargs)
                if isinstance(value, dict) and invalid == 'route' and 'operations' in value:
                    next(p for p in value['operations'] if p['profile_id'] == 'mlc-transfer')['documented_route'] = 'member_portal_or_eligible_cwr'
                if isinstance(value, dict) and invalid == 'source' and isinstance(value.get('sources'), list):
                    next(s for s in value['sources'] if s['id'] == 'mlc-transfer')['check_result'] = 'placeholder'
                return value
            with patch.object(packet, 'strict_json', side_effect=parse):
                with self.assertRaises(ValueError): self.run_packet()
            self.assertFalse(self.output.exists())

    def test_transfer_portable_cli_from_foreign_directory(self):
        self.save()
        for i, script in enumerate([ROOT/'scripts/prepare-provider-packet.py',
                ROOT/'skills/recoup-catalog-register-catalog/scripts/prepare-provider-packet.py']):
            output = self.root/f'transfer-{i}.json'
            result = subprocess.run([sys.executable, str(script), '--case', str(self.casefile),
                '--mapping', str(self.mapfile), '--output', str(output)], cwd=self.root,
                text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(output.read_text())['profile_id'], 'mlc-transfer')


if __name__ == '__main__': unittest.main()
