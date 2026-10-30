import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('packet', ROOT/'scripts/prepare-provider-packet.py')
packet = importlib.util.module_from_spec(spec); spec.loader.exec_module(packet)


class PacketTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.casefile=self.root/'case.json'; self.mapfile=self.root/'map.json'; self.output=self.root/'packet.json'
        self.source={'id':'source1','status':'active','version':'v1','sha256':'a'*64,'locator':'private-source'}
        self.action={'id':'action1','status':'prepared','stage':'register','rule_version':'1',
                     'source_refs':[{'source_id':'source1','version':'v1'}],
                     'payload':{'provider':'The MLC','operation':'new_work_registration','account':'synthetic-member',
                                'party':'synthetic-writer','subjects':['synthetic-work'],
                                'scope':{'subject_type':'composition','rights':['composition mechanical'],'territory':'US','effective':'2026'},
                                'disclosure':[],'costs':[]}}
        self.case={'schema_version':1,'revision':2,'case_id':'case1','workspace_id':'workspace1','history':[],
                   **{c:{} for c in packet.case_api.COLLECTIONS}}
        self.case['sources']['source1']=self.source; self.case['actions']['action1']=self.action
        labels=['work identity','writers/publishers','supported shares','mandate','current provider form']
        self.mapping={'case_id':'case1','revision':2,'action_id':'action1','payload_sha256':packet.fingerprint(self.action['payload']),
                      'profile_id':'mlc-new-work','profile_version':'2026-10-22.1','role':'member_rightsholder',
                      'required_inputs':{label:[{'source_id':'source1','version':'v1'}] for label in labels}}
        self.save()

    def save(self):
        self.casefile.write_text(json.dumps(self.case)); self.mapfile.write_text(json.dumps(self.mapping))

    def run_packet(self):
        self.save(); before=self.casefile.read_bytes(); mapping=self.mapfile.read_bytes()
        try: return packet.prepare(self.casefile,self.mapfile,self.output)
        finally:
            self.assertEqual(self.casefile.read_bytes(),before)
            self.assertEqual(self.mapfile.read_bytes(),mapping)

    def test_bound_packet_is_local_and_case_immutable(self):
        result=self.run_packet()
        self.assertEqual(result['status'],'prepared'); self.assertEqual(result['external_preflight'],'unverified')
        self.assertEqual(result['role_verification'],'unverified')
        self.assertEqual(result['payload'],self.action['payload'])
        self.assertEqual(result['case_sha256'],hashlib.sha256(self.casefile.read_bytes()).hexdigest())
        self.assertEqual(result['profile_id'],'mlc-new-work')
        self.assertTrue(result['profile_sources']); self.assertEqual(result['case_revision'],2)
        self.assertEqual(self.case['attempts'],{}); self.assertEqual(self.case['outcomes'],{})
        self.assertNotIn('authorization',result); self.assertNotIn('receipt',result)

    def test_missing_evidence_yields_blocked_artifact(self):
        del self.mapping['required_inputs']['current provider form']
        result=self.run_packet()
        self.assertEqual(result['status'],'blocked')
        self.assertEqual(result['missing_inputs'],['current provider form'])
        self.assertTrue(self.output.exists())

    def test_public_guidance_is_dated_bound_and_does_not_validate_fields(self):
        self.mapping['required_inputs'] = {}
        result = self.run_packet()
        guidance = result['public_preparation_guidance']
        self.assertEqual(guidance['checked_at'], '2026-10-30')
        self.assertEqual(result['public_preparation_guidance_sha256'], packet.fingerprint(guidance))
        self.assertEqual(set(guidance['required_input_guidance']), set(result['missing_inputs']))
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual(result['field_validation'], 'not_performed')
        self.assertEqual(result['template_retrieval'], 'not_performed_by_helper')
        self.assertIn('300 rows', guidance['required_input_guidance']['current provider form']['next_step'])
        self.assertEqual(result['missing_input_guidance'], guidance['required_input_guidance'])
        self.assertEqual(self.case['attempts'], {})

    def test_complete_mapping_keeps_guidance_without_claiming_form_validation(self):
        result = self.run_packet()
        self.assertEqual(result['missing_input_guidance'], {})
        self.assertEqual(result['field_validation'], 'not_performed')
        self.assertEqual(result['template_retrieval'], 'not_performed_by_helper')
        self.assertTrue(result['public_preparation_guidance']['required_input_guidance'])

    def test_optional_values_bind_to_existing_action_and_block_bad_fields(self):
        self.mapping['field_values'] = {'subject_id': 'synthetic-work', 'work_title': 'Example',
            'writers': [{'name': 'Example Writer', 'role': 'CA'}],
            'collection_shares': [{'party': 'Example Publisher', 'percent': 0}]}
        result = self.run_packet()
        self.assertEqual(result['status'], 'blocked')
        self.assertEqual(result['missing_inputs'], [])
        self.assertEqual(result['field_validation'], 'needs_attention')
        self.assertEqual(result['public_field_checks']['values'], self.mapping['field_values'])
        self.assertEqual(result['mapping_sha256'], hashlib.sha256(self.mapfile.read_bytes()).hexdigest())
        self.assertEqual(result['external_preflight'], 'unverified')
        self.output.unlink()
        self.mapping['field_values']['collection_shares'][0]['percent'] = 50
        result = self.run_packet()
        self.assertEqual(result['status'], 'prepared')
        self.assertEqual(result['field_validation'], 'checked_public_subset')
        self.assertEqual(result['public_field_checks']['authority_verification'], 'unverified')

    def test_field_values_cannot_check_another_subject(self):
        self.mapping['field_values'] = {'subject_id': 'other'}
        with self.assertRaises(ValueError): self.run_packet()
        self.assertFalse(self.output.exists())

    def test_portable_cli_exports_field_findings_with_blocked_exit(self):
        self.mapping['field_values'] = {'subject_id': 'synthetic-work'}
        self.save()
        for index, script in enumerate([ROOT/'scripts/prepare-provider-packet.py',
                ROOT/'skills/recoup-catalog-register-catalog/scripts/prepare-provider-packet.py']):
            output = self.root / f'fields{index}.json'
            run = subprocess.run([sys.executable, str(script), '--case', str(self.casefile),
                '--mapping', str(self.mapfile), '--output', str(output)], cwd=self.root,
                text=True, capture_output=True)
            self.assertEqual(run.returncode, 1, run.stderr)
            result = json.loads(output.read_text())
            self.assertEqual(result['field_validation'], 'needs_attention')
            self.assertEqual(len(result['public_field_checks']['findings']), 3)

    def test_cli_rejects_precision_loss_in_numeric_percent_literals(self):
        self.mapping['field_values'] = {'subject_id': 'synthetic-work', 'work_title': 'Example',
            'writers': [{'name': 'Example Writer', 'role': 'CA'}],
            'collection_shares': [{'party': 'Example Publisher', 'percent': 'RAW_TOKEN'}]}
        self.save()
        template = self.mapfile.read_text()
        for index, token in enumerate(['100.0000000000000001', '0.0099999999999999999',
                                       '1.00000000000000001e2', '9.9999999999999999e-3',
                                       '1e999999999999999999999999', '0e999999999999999999999999',
                                       '1e-999999999999999999999999']):
            for variant, script in enumerate([ROOT/'scripts/prepare-provider-packet.py',
                    ROOT/'skills/recoup-catalog-register-catalog/scripts/prepare-provider-packet.py']):
                self.mapfile.write_text(template.replace('"RAW_TOKEN"', token))
                original = self.mapfile.read_bytes()
                output = self.root / f'precision-{index}-{variant}.json'
                run = subprocess.run([sys.executable, str(script), '--case', str(self.casefile),
                    '--mapping', str(self.mapfile), '--output', str(output)], cwd=self.root,
                    text=True, capture_output=True)
                self.assertEqual(run.returncode, 2, (token, run.stdout, run.stderr))
                self.assertIn('precision', run.stderr)
                self.assertNotIn('Traceback', run.stderr)
                self.assertFalse(output.exists())
                self.assertEqual(self.mapfile.read_bytes(), original)

    def test_decimal_mapping_precision_and_existing_contract(self):
        for token in ['0.01', '100.0', '5e1', '0.5']:
            self.assertEqual(packet.strict_json(token.encode(), exact_floats=True), float(token))
        for token in ['100.0000000000000001', '0.0099999999999999999', '1e999', '1e-999']:
            with self.assertRaises(ValueError):
                packet.strict_json(token.encode(), exact_floats=True)
        # Case/profile parsing keeps its existing contract; only mapping parsing opts in.
        self.assertEqual(packet.strict_json(b'100.0000000000000001'), 100.0)
        self.assertEqual(packet.strict_json(b'2', exact_floats=True), 2)
        self.assertIs(type(packet.strict_json(b'2', exact_floats=True)), int)

    def test_quoted_exact_decimals_block_without_changing_values_or_hash(self):
        for token in ['100.0000000000000001', '0.0099999999999999999']:
            self.mapping['field_values'] = {'subject_id': 'synthetic-work', 'work_title': 'Example',
                'writers': [{'name': 'Example Writer', 'role': 'CA'}],
                'collection_shares': [{'party': 'Example Publisher', 'percent': token}]}
            result = self.run_packet()
            self.assertEqual(result['status'], 'blocked')
            self.assertEqual(result['field_validation'], 'needs_attention')
            self.assertEqual(result['public_field_checks']['values'], self.mapping['field_values'])
            self.assertEqual(result['mapping_sha256'], hashlib.sha256(self.mapfile.read_bytes()).hexdigest())
            self.output.unlink()

    def test_mapping_mismatch_rejected_without_output(self):
        for field,value in [('case_id','other'),('revision',1),('payload_sha256','0'*64),
                            ('profile_version','stale'),('profile_id','unknown'),('role','songwriter_hub')]:
            with self.subTest(field=field):
                original=self.mapping[field];self.mapping[field]=value
                with self.assertRaises(ValueError):self.run_packet()
                self.assertFalse(self.output.exists());self.mapping[field]=original
        self.mapping['required_inputs']['guessed label']=[]
        with self.assertRaises(ValueError):self.run_packet()

    def test_action_scope_and_status_rejected(self):
        for change in [{'status':'withdrawn'},{'stale':True},{'withheld':True},{'stage':'audit'}]:
            with self.subTest(change=change):
                original=copy.deepcopy(self.action);self.action.update(change)
                with self.assertRaises(ValueError):self.run_packet()
                self.action.clear();self.action.update(original)
        for field,value in [('provider','Other'),('operation','amend_existing_work'),('scope',{'subject_type':'recording','rights':['master']})]:
            original=copy.deepcopy(self.action['payload'][field]);self.action['payload'][field]=value
            self.mapping['payload_sha256']=packet.fingerprint(self.action['payload'])
            with self.assertRaises(ValueError):self.run_packet()
            self.action['payload'][field]=original

    def test_changed_payload_source_and_dependency_rejected(self):
        self.action['payload']['disclosure']=['new recipient']
        with self.assertRaises(ValueError):self.run_packet()
        self.action['payload']['disclosure']=[]
        for change in [{'status':'withdrawn'},{'version':'v2'},{'stale':True},{'withheld':True}]:
            original=copy.deepcopy(self.source);self.source.update(change)
            with self.assertRaises(ValueError):self.run_packet()
            self.source.clear();self.source.update(original)
        self.case['assessments']['dep']={'id':'dep','status':'prepared','stage':'register','rule_version':'1',
                                        'source_refs':[{'source_id':'source1','version':'old'}]}
        self.action['depends_on']=['dep']
        with self.assertRaises(ValueError):self.run_packet()

    def test_prior_attempt_or_outcome_refuses_duplicate_intake(self):
        for group in ['attempts','outcomes']:
            self.case[group]['old']={'id':'old','action_id':'action1','status':'unknown_outcome'}
            with self.assertRaises(ValueError):self.run_packet()
            self.assertFalse(self.output.exists());self.case[group].clear()

    def test_same_payload_new_action_does_not_bypass_existing_intake(self):
        other=copy.deepcopy(self.action);other['id']='previous'
        self.case['actions']['previous']=other
        self.case['attempts']['sent']={'id':'sent','action_id':'previous','status':'observed_sent'}
        with self.assertRaises(ValueError):self.run_packet()
        self.assertFalse(self.output.exists())

    def test_profile_placeholder_or_unknown_route_rejected(self):
        from unittest.mock import patch
        original=packet.strict_json
        for invalid in ['route','source']:
            def parse(raw, **kwargs):
                value=original(raw, **kwargs)
                if isinstance(value,dict) and invalid=='route' and 'operations' in value:
                    next(p for p in value['operations'] if p['profile_id']=='mlc-new-work')['documented_route']='unverified'
                if isinstance(value,dict) and invalid=='source' and isinstance(value.get('sources'),list):
                    next(s for s in value['sources'] if s['id']=='mlc-tools')['check_result']='placeholder'
                return value
            with patch.object(packet,'strict_json',side_effect=parse):
                with self.assertRaises(ValueError):self.run_packet()
            self.assertFalse(self.output.exists())

    def test_existing_output_alias_and_replay_preservation(self):
        self.output.write_text('keep')
        with self.assertRaises(ValueError):self.run_packet()
        self.assertEqual(self.output.read_text(),'keep');self.output.unlink()
        self.output.hardlink_to(self.casefile)
        with self.assertRaises(ValueError):self.run_packet()
        self.output.unlink();first=self.run_packet();before=self.output.read_bytes()
        with self.assertRaises(ValueError):packet.prepare(self.casefile,self.mapfile,self.output)
        self.assertEqual(self.output.read_bytes(),before)
        self.output=self.root/'packet2.json';second=self.run_packet()
        self.assertEqual(first,second)

    def test_canonical_and_vendored_cli_from_foreign_directory(self):
        for index,script in enumerate([ROOT/'scripts/prepare-provider-packet.py',ROOT/'skills/recoup-catalog-register-catalog/scripts/prepare-provider-packet.py']):
            result=subprocess.run([sys.executable,str(script),'--case',str(self.casefile),'--mapping',str(self.mapfile),
                                   '--output',str(self.root/f'cli{index}.json')],cwd=self.root,text=True,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(result.stdout)['status'],'prepared')


if __name__=='__main__':unittest.main()
