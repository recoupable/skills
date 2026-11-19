"""Assembly of already-created synthetic normalization exports; no import replay."""
import copy
import csv
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('normalization_handoff_fixtures', Path(__file__).with_name('test_catalog_handoff.py'))
base = importlib.util.module_from_spec(spec); spec.loader.exec_module(base)
assembly = base.export
producer = assembly.normalization


class NormalizationHandoffTests(unittest.TestCase):
    def setUp(self):
        self.fixture = base.HandoffTests(); self.fixture.setUp(); self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        self.source, self.ledger = self.root/'private-source.csv', self.root/'private-ledger.csv'
        self.row = {'Track Title':'PRIVATE_TITLE','ISRC':'PRIVATE_ISRC','Period Start':'2024-01-01',
            'Period End':'2024-03-31','Currency':'USD','Gross':'3.0049','Net':'2.0049','Deductions':'-1',
            'Rights Type':'master','Income Type':'streaming','Account ID':'PRIVATE_ACCOUNT',
            'Statement ID':'PRIVATE_STATEMENT','Transaction ID':'PRIVATE_TRANSACTION','Row Type':'detail'}

    def normalize(self, append=False, rows=None):
        with self.source.open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(self.row));writer.writeheader();writer.writerows([self.row] if rows is None else rows)
        # Fixture setup only. Assembly below is explicitly guarded from executing this.
        return producer.normalizer.normalize('distributor',self.source,self.ledger,append=append)

    def export(self, receipt, source=True, controls=None):
        directory=self.root/'normalization'
        producer.build(receipt['receipt'],self.ledger,receipt['row_receipt'],directory,'2026-11-18',self.source if source else None,controls)
        self.fixture.add('normalization',directory)
        return directory

    def build(self):
        with patch.object(producer.normalizer,'normalize',side_effect=AssertionError('no import replay')), patch.object(producer.validator,'validate',side_effect=AssertionError('no ledger replay')), patch.object(producer,'project',side_effect=AssertionError('no financial recomputation')):
            self.fixture.build()
        return json.loads((self.fixture.output/'normalization/workpaper.json').read_text())

    def test_exact_whole_scope_preserved_without_replay(self):
        directory=self.export(self.normalize())
        before={p.name:p.read_bytes() for p in directory.iterdir()}
        result=self.build();original=json.loads(before['workpaper.json'])
        self.assertEqual(result['controls'],original['controls']);self.assertEqual(result['schedules'],original['schedules'])
        self.assertEqual(result['producer_hashes'],json.loads(before['manifest.json'])['helper_hashes'])
        self.assertEqual(before,{p.name:p.read_bytes() for p in directory.iterdir()})
        self.assertEqual(result['schedules']['written-lines'][0]['owner_net_amount'],'2.0049')
        self.assertEqual(result['controls']['readiness'],'review_required')
        self.assertIsNone(result['controls']['recovered_cash'])
        self.assertEqual(result['controls']['historical_receipt_to_ledger_byte_binding'],'not_provided_by_normalizer; current supplied bytes hashed here')
        self.assertEqual(set(result['schedules']),set(producer.FIELDS))

    def test_append_held_new_rows_never_include_baseline_money(self):
        self.row.update(Net='99000',Gross='99001');self.normalize()
        self.row.update(Net='2.0049',Gross='3.0049',**{'Transaction ID':'NEW','Row Type':'held'})
        directory=self.export(self.normalize(append=True));result=self.build()
        self.assertEqual(result['schedules'],json.loads((directory/'workpaper.json').read_text())['schedules'])
        self.assertTrue(result['controls']['appended_supplied'])
        self.assertEqual(result['schedules']['written-lines'][0]['row_status'],'held')
        self.assertEqual(result['controls']['full_ledger_financial_controls'],'unknown')
        check=next(r for r in result['schedules']['checks'] if r['check']=='append_baseline')
        self.assertEqual(check['status'],'unknown_not_bound_by_receipt')
        total=next(r for r in result['schedules']['totals'] if r['basis']=='newly_written_only' and r['field']=='owner_net_amount')
        self.assertEqual(total['observed_amount'],'2.0049');self.assertEqual(len(total['line_refs']),1)
        text=(self.fixture.output/'normalization/workpaper.json').read_text()
        self.assertNotIn('99000',text)

    def test_unknown_currency_amounts_optional_hashes_remain_null(self):
        self.row.update(Currency='',Net='',Gross='',Deductions='')
        directory=self.export(self.normalize(),source=False);result=self.build()
        self.assertEqual(result['schedules'],json.loads((directory/'workpaper.json').read_text())['schedules'])
        row=result['schedules']['written-lines'][0]
        self.assertIsNone(row['currency']);self.assertIsNone(row['owner_net_amount'])
        self.assertTrue(row['currency_ref'].startswith('currency:'))
        self.assertIsNone(result['controls']['original_source_sha256']);self.assertIsNone(result['controls']['additional_controls_sha256'])
        self.assertEqual(result['controls']['freshness'],'unknown')
        self.assertTrue(any(r['status']=='no_observed_amounts' for r in result['schedules']['checks']))

    def test_duplicate_only_empty_new_schedule_and_fixed_csv_headers(self):
        self.normalize();directory=self.export(self.normalize(append=True));result=self.build()
        self.assertEqual(result['schedules']['written-lines'],[])
        self.assertEqual(result['schedules']['rows'][0]['disposition'],'duplicate')
        with (self.fixture.output/'normalization/written-lines.csv').open() as stream:
            reader=csv.DictReader(stream);self.assertEqual(reader.fieldnames,list(producer.FIELDS['written-lines']));self.assertEqual(list(reader),[])
        self.assertEqual(result['schedules'],json.loads((directory/'workpaper.json').read_text())['schedules'])

    def test_each_helper_pin_and_control_type_tampering_refused(self):
        directory=self.export(self.normalize());path=directory/'manifest.json';original=path.read_bytes()
        for name in producer.FIELDS: self.assertTrue((directory/(name+'.csv')).is_file())
        for name in assembly.normalization_contract.HELPERS:
            with self.subTest(helper=name):
                data=json.loads(original);data['helper_hashes'][name]='0'*64;path.write_text(json.dumps(data));self.fixture.rehash(directory)
                with self.assertRaises(ValueError):self.build()
                self.assertFalse(self.fixture.output.exists());path.write_bytes(original)
        path.write_bytes(original)
        workpaper=directory/'workpaper.json';saved=workpaper.read_bytes()
        for key,value in [('appended_supplied',1),('ledger_held_rows',True),('schema_version',1),('readiness','ready'),('freshness','current_as_supplied')]:
            with self.subTest(field=key):
                data=json.loads(saved);data['controls'][key]=value;workpaper.write_text(json.dumps(data))
                manifest=json.loads(original);manifest[key]=value;path.write_text(json.dumps(manifest));self.fixture.rehash(directory)
                with self.assertRaises(ValueError):self.build()
                self.assertFalse(self.fixture.output.exists())
        path.write_bytes(original);workpaper.write_bytes(saved)

    def test_hash_mismatch_csv_disagreement_and_manifest_control_disagreement(self):
        directory=self.export(self.normalize());saved={p:p.read_bytes() for p in directory.iterdir()}
        for mode in ('member','csv','control'):
            with self.subTest(mode=mode):
                if mode in ('member','csv'):
                    p=directory/'written-lines.csv';p.write_text(p.read_text().replace('2.0049','2.0050'))
                    if mode=='csv':self.fixture.rehash(directory)
                else:
                    p=directory/'manifest.json';m=json.loads(p.read_text());m['receipt_status_supplied']='partial';p.write_text(json.dumps(m));self.fixture.rehash(directory)
                with self.assertRaises(ValueError):self.build()
                self.assertFalse(self.fixture.output.exists())
                for p,raw in saved.items():p.write_bytes(raw)
                self.fixture.rehash(directory)

    def test_private_extensions_dropped_and_known_scope_prose_rejected(self):
        directory=self.export(self.normalize());p=directory/'workpaper.json';data=json.loads(p.read_text())
        data['private']={'path':'/PRIVATE_PATH','token':'SECRET_TOKEN','finite':0.125}
        data['controls']['private']='SECRET_CONTROL';data['schedules']['rows'][0]['private']='SECRET_ROW'
        p.write_text(json.dumps(data));self.fixture.rehash(directory);self.build()
        text=''.join(p.read_text() for p in self.fixture.output.rglob('*') if p.is_file())
        for value in ('PRIVATE','SECRET',str(self.root)):self.assertNotIn(value,text)
        shutil.rmtree(self.fixture.output)
        data['schedules']['checks'][0]['scope']='PRIVATE_SCOPE_PROSE';p.write_text(json.dumps(data));self.fixture.rehash(directory)
        with self.assertRaises(ValueError):self.build()

    def test_four_selected_exports_new_session_provenance(self):
        directory=self.export(self.normalize());self.fixture.financial('entitlement');self.fixture.financial('remittance');self.fixture.case()
        self.build();index=json.loads((self.fixture.output/'handoff.json').read_text())
        self.assertEqual(index['excluded_stages'],[]);self.assertEqual(len(index['exports']),4)
        self.assertFalse(index['publication_authorized']);self.assertEqual(index['cross_stage_money_rollup'],'not_calculated')
        entry=next(r for r in index['exports'] if r['kind']=='normalization')
        record=json.loads((self.fixture.output/entry['workpaper']).read_text())
        original=json.loads((directory/'workpaper.json').read_text())
        self.assertEqual(entry['input_manifest_sha256'],assembly.sha((directory/'manifest.json').read_bytes()))
        for key in ('receipt_sha256','ledger_sha256','row_receipt_sha256','source_version_ref','transform_ref','parser_ref'):
            self.assertEqual(record['controls'][key],original['controls'][key])
        self.assertEqual(index['normalization_contract_sha256'],assembly.sha((base.SCRIPTS/'_normalization_handoff.py').read_bytes()))

    def test_unselected_normalization_not_read_and_duplicate_selection_refused(self):
        directory=self.export(self.normalize());saved=(directory/'workpaper.json').read_bytes();entry=self.fixture.entries.pop()
        self.fixture.financial('entitlement');(directory/'workpaper.json').write_text('PRIVATE_INVALID')
        self.fixture.build();index=json.loads((self.fixture.output/'handoff.json').read_text())
        self.assertIn('normalization',index['excluded_stages']);self.assertFalse((self.fixture.output/'normalization').exists())
        shutil.rmtree(self.fixture.output);(directory/'workpaper.json').write_bytes(saved);self.fixture.entries=[entry,entry]
        with self.assertRaises(ValueError):self.build()

    def test_existing_amount_mismatch_remains_mismatch(self):
        receipt=self.normalize()
        with self.ledger.open(newline='') as stream:
            reader=csv.DictReader(stream);columns=reader.fieldnames;rows=list(reader)
        rows[0]['owner_net_amount']='999'
        with self.ledger.open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=columns);writer.writeheader();writer.writerows(rows)
        directory=self.export(receipt);result=self.build()
        self.assertEqual(result['controls']['artifact_consistency'],'mismatch')
        self.assertEqual(result['schedules'],json.loads((directory/'workpaper.json').read_text())['schedules'])
        self.assertTrue(any(r['check']=='mismatch' for r in result['schedules']['totals']))

    def test_invalid_association_preserves_withheld_totals_and_status(self):
        receipt=self.normalize()
        with self.ledger.open(newline='') as stream:
            reader=csv.DictReader(stream);columns=reader.fieldnames;rows=list(reader)
        rows[0]['transform_id']='0'*64
        with self.ledger.open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=columns);writer.writeheader();writer.writerows(rows)
        self.export(receipt);result=self.build()
        self.assertEqual(result['controls']['artifact_consistency'],'mismatch')
        totals=[r for r in result['schedules']['totals'] if r['basis']=='newly_written_only']
        self.assertTrue(totals)
        self.assertTrue(all(r['observed_amount'] is None and not r['line_refs'] and r['check']=='unsupported_association_or_value' for r in totals))

    def test_additional_controls_are_supplied_claims_only(self):
        receipt=self.normalize();controls=self.root/'controls.json'
        controls.write_text(json.dumps({'evidence_refs':['PRIVATE_CONTROL_EVIDENCE'],'totals':[{'currency':'USD','field':'owner_net_amount','amount':'2.0049'}]}))
        self.export(receipt,controls=controls);result=self.build()
        check=next(r for r in result['schedules']['checks'] if r['check']=='additional_controls_vs_supplied_source_totals')
        self.assertEqual(check['status'],'matches_supplied_claims_only')
        self.assertTrue(check['evidence_refs'][0].startswith('evidence:'))
        self.assertEqual(result['controls']['additional_controls_sha256'],assembly.sha(controls.read_bytes()))
        self.assertEqual(result['controls']['source_authenticity'],'not_verified')

    def test_unknown_checks_cannot_be_promoted_by_self_consistent_wire(self):
        import io
        directory=self.export(self.normalize());p=directory/'workpaper.json';saved=p.read_bytes()
        for check in ('source_totals','append_baseline','source_authenticity_current_rights_and_completeness'):
            with self.subTest(check=check):
                self.fixture.output=self.root/('handoff-'+check)
                data=json.loads(saved);rows=data['schedules']['checks']
                next(row for row in rows if row['check']==check)['status']='matches'
                p.write_text(json.dumps(data))
                stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=producer.FIELDS['checks'])
                writer.writeheader();writer.writerows({k:producer.common.cell(v) for k,v in row.items()} for row in rows)
                (directory/'checks.csv').write_text(stream.getvalue(),newline='');self.fixture.rehash(directory)
                with self.assertRaises(ValueError):self.build()
                self.assertFalse(self.fixture.output.exists())

    def rewrite_workpaper(self, directory, data):
        (directory/'workpaper.json').write_text(json.dumps(data))
        for name,rows in data['schedules'].items():
            with (directory/(name+'.csv')).open('w',newline='') as stream:
                writer=csv.DictWriter(stream,fieldnames=producer.FIELDS[name]);writer.writeheader()
                writer.writerows({key:producer.common.cell(value) for key,value in row.items()} for row in rows)
        path=directory/'manifest.json';manifest=json.loads(path.read_text());manifest.update(data['controls'])
        path.write_text(json.dumps(manifest));self.fixture.rehash(directory)

    def test_headline_controls_cannot_contradict_rehashed_schedules(self):
        directory=self.export(self.normalize());original=json.loads((directory/'workpaper.json').read_text())
        for kind in ('count','total','withheld','check','validator_false_ok','validator_false_error','false_mismatch'):
            with self.subTest(kind=kind):
                self.fixture.output=self.root/('handoff-'+kind)
                data=copy.deepcopy(original);schedules=data['schedules']
                if kind=='count':
                    schedules['counts'][0]['supplied']+=1;schedules['counts'][0]['check']='mismatch'
                elif kind in ('total','withheld'):
                    row=next(r for r in schedules['totals'] if r['basis']=='newly_written_only')
                    if kind=='total':row.update(supplied_amount='999',check='mismatch')
                    else:row.update(observed_amount=None,line_refs=[],check='unsupported_association_or_value')
                elif kind=='check':
                    next(r for r in schedules['checks'] if r['check']=='original_source_bytes')['status']='mismatch'
                elif kind=='validator_false_ok':
                    next(r for r in schedules['checks'] if r['check']=='existing_ledger_validator')['status']='errors_found'
                elif kind=='validator_false_error':data['controls']['ledger_validator_status']='errors_found'
                else:data['controls']['artifact_consistency']='mismatch'
                self.rewrite_workpaper(directory,data)
                before={p.name:p.read_bytes() for p in directory.iterdir()}
                with self.assertRaises(ValueError):self.build()
                self.assertFalse(self.fixture.output.exists())
                self.assertEqual(before,{p.name:p.read_bytes() for p in directory.iterdir()})

    def test_validator_check_missing_or_duplicated_refused(self):
        directory=self.export(self.normalize());original=json.loads((directory/'workpaper.json').read_text())
        for duplicate in (False,True):
            with self.subTest(duplicate=duplicate):
                self.fixture.output=self.root/('handoff-'+str(duplicate))
                data=copy.deepcopy(original);checks=data['schedules']['checks']
                row=next(r for r in checks if r['check']=='existing_ledger_validator')
                if duplicate:checks.append(copy.deepcopy(row))
                else:checks.remove(row)
                self.rewrite_workpaper(directory,data)
                with self.assertRaises(ValueError):self.build()
                self.assertFalse(self.fixture.output.exists())

    def test_held_baseline_does_not_conflate_eligibility_with_consistency(self):
        self.row['Net']='';self.normalize()
        self.row.update(Net='2.0049',**{'Transaction ID':'SECOND'})
        directory=self.export(self.normalize(append=True));result=self.build()
        self.assertEqual(result['controls']['receipt_status_supplied'],'ok')
        self.assertEqual(result['controls']['ledger_validator_status'],'errors_found')
        self.assertEqual(result['controls']['ledger_held_rows'],1)
        self.assertEqual(result['controls']['artifact_consistency'],'no_detected_mismatch_within_supported_checks')
        self.assertEqual(result['controls']['readiness'],'review_required')
        self.assertEqual(result['schedules'],json.loads((directory/'workpaper.json').read_text())['schedules'])
        self.assertEqual(result['schedules']['written-lines'][0]['row_status'],'ready')

    def test_normalization_report_caveats_require_selected_scope(self):
        self.fixture.case();self.fixture.build()
        self.assertNotIn('Normalization source and written totals', (self.fixture.output/'report.md').read_text())
        self.fixture.output=self.root/'with-normalization'
        self.export(self.normalize());self.build()
        self.assertIn('Normalization source and written totals', (self.fixture.output/'report.md').read_text())

    def test_standalone_cli_uses_only_saved_workpaper(self):
        self.export(self.normalize());self.fixture.selection.write_text(json.dumps({'schema_version':'1','exports':self.fixture.entries}))
        self.source.unlink();self.ledger.unlink()  # Assembly has no original-source dependency.
        result=subprocess.run([sys.executable,str(base.SCRIPTS/'assemble-catalog-handoff.py'),'--selection',str(self.fixture.selection),'--output-directory',str(self.fixture.output)],capture_output=True,text=True,cwd=self.root)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads((self.fixture.output/'normalization/workpaper.json').read_text())['controls']['readiness'],'review_required')


if __name__=='__main__':unittest.main()
