"""Synthetic overclaim cases: no account or provider operations."""
import copy
import json
import subprocess
import sys
import unittest
import test_catalog_provider_packet as fixtures
ROOT, packet = fixtures.ROOT, fixtures.packet


class OverclaimTests(unittest.TestCase):
    save = fixtures.PacketTests.save
    run_packet = fixtures.PacketTests.run_packet
    def setUp(self):
        fixtures.PacketTests.setUp(self)
        self.action['stage'] = 'resolve_claims'
        self.action['payload']['scope']['subject_type'] = 'composition_claim'
        self.action['payload']['operation'] = 'overclaim_resolution'
        self.action['payload']['disclosure'] = ['Existing reviewed recipient']
        self.mapping['profile_id'] = 'mlc-overclaim'
        self.action['payload']['scope'].update({'share_basis': 'documented collection convention',
            'claimed_share': '25/100', 'selected_remedy': 'request review of documented conflicting claims', 'territory': 'US', 'effective': '2026-01-01/2026-12-31'})
        self.mapping['payload_sha256'] = packet.fingerprint(self.action['payload'])
        self.labels = ['overclaim/work ID', 'competing claims', 'supporting documents', 'exact selected remedy']
        self.current = {**self.source, 'id': 'current', 'version': 'record-v2', 'sha256': 'b'*64}
        self.claimed = {**self.source, 'id': 'claimed', 'version': 'claimed-v3', 'sha256': 'c'*64}
        self.authority = {**self.source, 'id': 'authority-evidence', 'version': 'mandate-v1', 'sha256': 'd'*64}
        self.remedy = {**self.source, 'id': 'selected-remedy', 'version': 'remedy-v4', 'sha256': 'e'*64}
        for source in [self.current, self.claimed, self.authority, self.remedy]:
            self.case['sources'][source['id']] = source
        # Active evidence of an older mandate is distinct from a stale source.
        self.case['history'] = [{'records': {'sources': {'authority-evidence': copy.deepcopy(self.authority)}}}]
        self.mapping['required_inputs'] = {
            'overclaim/work ID': [{'source_id': 'source1', 'version': 'v1'}],
            'competing claims': [{'source_id': 'current', 'version': 'record-v2'},
                                 {'source_id': 'claimed', 'version': 'claimed-v3'}],
            'supporting documents': [{'source_id': 'authority-evidence', 'version': 'mandate-v1'}],
            'exact selected remedy': [{'source_id': 'selected-remedy', 'version': 'remedy-v4'}]}
        self.save()

    def test_overclaim_complete_preserves_current_claimed_and_history(self):
        import hashlib
        history = copy.deepcopy(self.case['history'])
        result = self.run_packet()
        self.assertEqual(result['status'], 'prepared')
        self.assertEqual(result['payload'], self.action['payload'])
        self.assertEqual(result['profile_id'], 'mlc-overclaim')
        self.assertEqual(result['case_sha256'], hashlib.sha256(self.casefile.read_bytes()).hexdigest())
        self.assertEqual(result['mapping_sha256'], hashlib.sha256(self.mapfile.read_bytes()).hexdigest())
        self.assertEqual(result['public_preparation_guidance_sha256'], packet.fingerprint(result['public_preparation_guidance']))
        self.assertEqual(set(result['public_preparation_guidance']['required_input_guidance']), set(self.labels))
        self.assertEqual(result['field_validation'], 'not_performed')
        self.assertNotIn('public_field_checks', result)
        self.assertNotIn('transfer_review', result)
        self.assertNotIn('amendment_review', result)
        self.assertEqual(result['role_verification'], 'unverified')
        self.assertEqual(result['external_preflight'], 'unverified')
        self.assertEqual(self.case['history'], history)
        self.assertEqual(result['evidence_sources'], self.case['sources'])
        for entry in result['required_inputs']:
            self.assertEqual(entry['source_refs'], self.mapping['required_inputs'][entry['required_input']])
            self.assertEqual(entry['semantic_verification'], 'unverified')
        for value in result['overclaim_review'].values():
            self.assertEqual(value['verification'], 'unverified')
        self.assertEqual(set(result['overclaim_review']),
                         {'selected_remedy', 'contact_authority', 'amendment_authority', 'relinquishment_authority',
                          'upload_authority', 'case_disposition', 'share_readback', 'financial_effect'})
        self.assertEqual(self.case['attempts'], {})
        self.assertEqual(self.case['outcomes'], {})
        self.assertNotIn('receipt', result)

    def test_overclaim_each_missing_input_blocks_with_specific_guidance(self):
        for label in self.labels:
            with self.subTest(label=label):
                refs = self.mapping['required_inputs'].pop(label)
                result = self.run_packet()
                self.assertEqual(result['status'], 'blocked')
                self.assertEqual(result['missing_inputs'], [label])
                self.assertEqual(set(result['missing_input_guidance']), {label})
                self.output.unlink()
                self.mapping['required_inputs'][label] = refs

    def test_overclaim_rejects_new_work_values_without_output(self):
        self.mapping['field_values'] = {'subject_id': 'synthetic-work'}
        with self.assertRaisesRegex(ValueError, 'field_values'):
            self.run_packet()
        self.assertFalse(self.output.exists())

    def test_overclaim_mismatch_and_withdrawal_guards(self):
        # Exercise the shared guards against this profile, not just new work.
        for field, value in [('case_id', 'other'), ('revision', 1), ('action_id', 'other'),
                             ('payload_sha256', '0'*64), ('profile_version', 'old'),
                             ('profile_id', 'mlc-songwriter-details'), ('role', 'songwriter_hub_user')]:
            old = self.mapping[field]; self.mapping[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError): self.run_packet()
            self.assertFalse(self.output.exists()); self.mapping[field] = old
        for record in [self.source, self.current, self.claimed, self.authority, self.remedy, self.action]:
            for change in [{'stale': True}, {'withheld': True}, {'status': 'withdrawn'}]:
                old = copy.deepcopy(record); record.update(change)
                with self.subTest(change=change), self.assertRaises(ValueError): self.run_packet()
                self.assertFalse(self.output.exists()); record.clear(); record.update(old)
        self.mapping['required_inputs'][self.labels[0]][0]['version'] = 'old'
        with self.assertRaises(ValueError): self.run_packet()
        self.assertFalse(self.output.exists())

    def test_overclaim_wrong_operation_subject_and_rights_rejected(self):
        for key, value in [('provider', 'Other'), ('operation', 'new_work_registration'),
                           ('operation', 'amend_existing_work'), ('operation', 'existing_interest_claim'),
                           ('scope', {'subject_type': 'collection_mandate', 'rights': ['composition mechanical']}),
                           ('scope', {'subject_type': 'composition_claim', 'rights': ['master']})]:
            old = self.action['payload'][key]; self.action['payload'][key] = value
            self.mapping['payload_sha256'] = packet.fingerprint(self.action['payload'])
            with self.subTest(key=key), self.assertRaises(ValueError): self.run_packet()
            self.assertFalse(self.output.exists()); self.action['payload'][key] = old

    def test_overclaim_duplicate_attempts_and_dependency_versions_rejected(self):
        for group in ['attempts', 'outcomes']:
            self.case[group]['old'] = {'id': 'old', 'action_id': 'action1', 'status': 'unknown_outcome'}
            with self.subTest(group=group), self.assertRaises(ValueError): self.run_packet()
            self.assertFalse(self.output.exists()); self.case[group].clear()
        self.case['assessments']['dep'] = {'id': 'dep', 'status': 'prepared', 'stage': 'register',
            'rule_version': '1', 'source_refs': [{'source_id': 'source1', 'version': 'old'}]}
        self.action['depends_on'] = ['dep']
        with self.assertRaises(ValueError): self.run_packet()
        self.assertFalse(self.output.exists())

    def test_overclaim_unsupported_route_and_unverified_profile_source_rejected(self):
        from unittest.mock import patch
        original = packet.strict_json
        for invalid in ['route', 'source']:
            def parse(raw, **kwargs):
                value = original(raw, **kwargs)
                if isinstance(value, dict) and invalid == 'route' and 'operations' in value:
                    next(p for p in value['operations'] if p['profile_id'] == 'mlc-overclaim')['documented_route'] = 'member_claiming_tool'
                if isinstance(value, dict) and invalid == 'source' and isinstance(value.get('sources'), list):
                    next(s for s in value['sources'] if s['id'] == 'mlc-overclaim')['check_result'] = 'placeholder'
                return value
            with patch.object(packet, 'strict_json', side_effect=parse):
                with self.assertRaises(ValueError): self.run_packet()
            self.assertFalse(self.output.exists())

    def test_overclaim_current_claimed_history_version_mismatch_rejected(self):
        for source in [self.current, self.claimed, self.authority, self.remedy]:
            version = source['version']; source['version'] = 'new-unmapped-version'
            with self.subTest(source=source['id']), self.assertRaises(ValueError): self.run_packet()
            self.assertFalse(self.output.exists()); source['version'] = version

    def test_overclaim_changed_disclosure_or_historic_source_hash_rejected(self):
        self.action['payload']['disclosure'].append('Unreviewed recipient')
        with self.assertRaises(ValueError): self.run_packet()
        self.assertFalse(self.output.exists())
        self.action['payload']['disclosure'].pop()
        self.authority['sha256'] = 'e'*64
        with self.assertRaises(ValueError): self.run_packet()
        self.assertFalse(self.output.exists())

    def test_overclaim_same_payload_action_cannot_bypass_previous_attempt(self):
        other = copy.deepcopy(self.action); other['id'] = 'previous'
        self.case['actions']['previous'] = other
        self.case['attempts']['sent'] = {'id': 'sent', 'action_id': 'previous', 'status': 'observed_sent'}
        with self.assertRaises(ValueError): self.run_packet()
        self.assertFalse(self.output.exists())

    def test_overclaim_representative_role_remains_eligible_but_unverified(self):
        self.mapping['role'] = 'authorized_member_representative'
        result = self.run_packet()
        self.assertEqual(result['status'], 'prepared')
        self.assertEqual(result['role_verification'], 'unverified')
        self.assertEqual(result['payload']['scope']['claimed_share'], '25/100')
        self.assertEqual(result['payload']['scope']['share_basis'], 'documented collection convention')
        self.assertEqual(result['payload']['scope']['territory'], 'US')
        self.assertEqual(result['payload']['scope']['effective'], '2026-01-01/2026-12-31')

    def test_overclaim_stage_or_selected_remedy_changes_rejected(self):
        self.action['stage'] = 'register'
        with self.assertRaises(ValueError): self.run_packet()
        self.assertFalse(self.output.exists()); self.action['stage'] = 'resolve_claims'
        self.action['payload']['scope']['selected_remedy'] = 'relinquish all shares'
        with self.assertRaises(ValueError): self.run_packet()
        self.assertFalse(self.output.exists())

    def test_resolution_skill_is_standalone_with_local_dependencies(self):
        import shutil
        skill = self.root/'installed-resolution'
        shutil.copytree(ROOT/'skills/recoup-catalog-resolve-claims', skill)
        self.assertTrue((skill/'scripts/mlc-public-fields.py').is_file())
        output = self.root/'standalone.json'
        result = subprocess.run([sys.executable, str(skill/'scripts/prepare-provider-packet.py'),
            '--case', str(self.casefile), '--mapping', str(self.mapfile), '--output', str(output)],
            cwd=self.root, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(output.read_text())['profile_id'], 'mlc-overclaim')

    def test_overclaim_portable_cli_from_foreign_directory(self):
        self.save()
        for i, script in enumerate([ROOT/'scripts/prepare-provider-packet.py',
                ROOT/'skills/recoup-catalog-register-catalog/scripts/prepare-provider-packet.py',
                ROOT/'skills/recoup-catalog-resolve-claims/scripts/prepare-provider-packet.py']):
            output = self.root/f'overclaim-{i}.json'
            result = subprocess.run([sys.executable, str(script), '--case', str(self.casefile),
                '--mapping', str(self.mapfile), '--output', str(output)], cwd=self.root,
                text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(output.read_text())['profile_id'], 'mlc-overclaim')


if __name__ == '__main__': unittest.main()
