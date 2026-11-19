"""Synthetic existing-normalizer receipts only; exports never invoke an import."""
import copy
from contextlib import contextmanager
import csv
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tracemalloc
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'skills/recoup-catalog-review-deal/scripts'
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location('normalization_workpaper_tests', SCRIPTS / 'build-normalization-workpaper.py')
export = importlib.util.module_from_spec(spec); spec.loader.exec_module(export)


class NormalizationWorkpaperTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source, self.ledger, self.output = [self.root/name for name in ('source.csv', 'ledger.csv', 'out')]
        self.row = {'Track Title': 'PRIVATE_TITLE', 'ISRC': 'PRIVATE_ISRC', 'Period Start': '2024-01-01',
            'Period End': '2024-03-31', 'Currency': 'USD', 'Gross': '100.0001', 'Net': '97.0001', 'Deductions': '-3',
            'Rights Type': 'master', 'Income Type': 'streaming', 'Account ID': 'PRIVATE_ACCOUNT', 'Statement ID': 'PRIVATE_STATEMENT',
            'Transaction ID': 'PRIVATE_TRANSACTION', 'Row Type': 'detail'}

    @contextmanager
    def guard_input_streams(self):
        limits={self.receipt_path:export.bounded.MAX_JSON_BYTES+1,
                self.rows_path:export.bounded.MAX_JSONL_RECORD_BYTES+1,
                self.ledger:export.bounded.CHUNK,self.source:export.bounded.CHUNK,
                self.root/'controls.json':export.bounded.MAX_JSON_BYTES+1}
        observed={'opens':[], 'reads':[]}
        original_open=Path.open
        class Guard:
            def __init__(self,stream,path):self.stream,self.path=stream,path
            def __enter__(self):return self
            def __exit__(self,*args):return self.stream.__exit__(*args)
            def read(self,size=-1):return self.consume('read',size)
            def readline(self,size=-1):return self.consume('readline',size)
            def readlines(self,*args):raise AssertionError('unbounded input readlines')
            def __iter__(self):return self
            def __next__(self):
                line=self.readline()
                if not line:raise StopIteration
                return line
            def consume(self,method,size):
                observed['reads'].append((self.path,method,size))
                if not isinstance(size,int) or size<=0 or size>limits[self.path]:
                    raise AssertionError('unbounded input stream read')
                return getattr(self.stream,method)(size)
            def __getattr__(self,name):return getattr(self.stream,name)
        def opened(path,*args,**kwargs):
            mode=args[0] if args else kwargs.get('mode','r')
            stream=original_open(path,*args,**kwargs)
            if path in limits and 'r' in mode:
                observed['opens'].append(path)
                return Guard(stream,path)
            return stream
        with patch.object(Path,'open',opened):yield observed

    def normalize(self, rows=None, append=False, controls=None):
        rows = [self.row] if rows is None else rows
        with self.source.open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(self.row)); writer.writeheader(); writer.writerows(rows)
        path = None
        if controls is not None:
            path = self.root/'controls.json'; path.write_text(json.dumps(controls))
        self.receipt = export.normalizer.normalize('distributor', self.source, self.ledger, append=append, controls_path=path)
        self.receipt_path = Path(self.receipt['receipt']); self.rows_path = Path(self.receipt['row_receipt'])
        return self.receipt

    def build(self, source=True, controls=None):
        before = [p.read_bytes() for p in (self.receipt_path, self.ledger, self.rows_path, self.source)]
        manifest = export.build(self.receipt_path, self.ledger, self.rows_path, self.output, '2026-11-18', self.source if source else None, controls)
        self.assertEqual(before, [p.read_bytes() for p in (self.receipt_path, self.ledger, self.rows_path, self.source)])
        expected = {name+'.csv' for name in export.FIELDS} | {'workpaper.json', 'report.md'}
        self.assertEqual({r['file'] for r in manifest['files']}, expected)
        self.assertEqual(len(manifest['files']), len(expected))
        self.assertEqual({p.name for p in self.output.iterdir()}, expected | {'manifest.json'})
        for row in manifest['files']:
            self.assertEqual(row['sha256'], export.common.digest((self.output/row['file']).read_bytes()))
        for name,path in [('receipt',self.receipt_path),('ledger',self.ledger),('row_receipt',self.rows_path)]:
            self.assertEqual(manifest[name+'_sha256'], export.common.digest(path.read_bytes()))
        return json.loads((self.output/'workpaper.json').read_text())

    def check(self, p, name):
        return next(r for r in p['schedules']['checks'] if r['check']==name)['status']

    def rewrite_ledger(self, change):
        with self.ledger.open(newline='') as f:
            reader=csv.DictReader(f); fields=reader.fieldnames; rows=list(reader)
        change(rows)
        with self.ledger.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

    def test_exact_new_totals_links_byte_bindings_and_limits(self):
        self.normalize(); p=self.build(); c=p['controls']; s=p['schedules']
        self.assertEqual(c['controls_status_supplied'],'unavailable')
        self.assertEqual(c['freshness'],'unknown'); self.assertEqual(c['full_ledger_financial_controls'],'unknown')
        self.assertEqual(c['readiness'],'review_required'); self.assertIsNone(c['recovered_cash'])
        self.assertEqual(c['artifact_consistency'],'no_detected_mismatch_within_supported_checks')
        self.assertEqual(s['written-lines'][0]['owner_net_amount'],'97.0001')
        self.assertEqual(s['written-lines'][0]['period_start'],'2024-01-01')
        self.assertEqual(s['written-lines'][0]['row_ref'],s['rows'][0]['row_ref'])
        totals=[r for r in s['totals'] if r['basis']=='newly_written_only' and r['field']=='owner_net_amount']
        self.assertEqual(totals[0]['observed_amount'],'97.0001')
        self.assertEqual(totals[0]['line_refs'],[s['written-lines'][0]['line_ref']])
        self.assertTrue(all(r['observed_amount'] is None and r['check']=='not_recomputed' for r in s['totals'] if r['basis']=='source_detail_supplied'))
        self.assertEqual(self.check(p,'original_source_bytes'),'matches')

    def test_appended_baseline_is_never_in_written_totals(self):
        self.normalize()
        self.row.update(Net='2.0049', Gross='3.0049', **{'Transaction ID':'SECOND'})
        self.normalize(append=True); p=self.build()
        self.assertEqual(len(p['schedules']['written-lines']),1)
        total=next(r for r in p['schedules']['totals'] if r['basis']=='newly_written_only' and r['field']=='owner_net_amount')
        self.assertEqual(total['observed_amount'],'2.0049')
        self.assertEqual(self.check(p,'append_baseline'),'unknown_not_bound_by_receipt')
        self.assertEqual(p['controls']['full_ledger_financial_controls'],'unknown')
        self.assertNotIn('99.0050',(self.output/'workpaper.json').read_text())

    def test_baseline_change_cannot_be_claimed_detected_or_controlled(self):
        self.normalize(); self.row['Transaction ID']='SECOND'; self.normalize(append=True)
        self.rewrite_ledger(lambda rows: rows[0].update(owner_net_amount='500'))
        p=self.build()
        self.assertEqual(self.check(p,'append_baseline'),'unknown_not_bound_by_receipt')
        self.assertEqual(p['controls']['full_ledger_financial_controls'],'unknown')
        self.assertEqual(p['controls']['artifact_consistency'],'no_detected_mismatch_within_supported_checks')

    def test_exact_duplicate_has_no_new_money(self):
        self.normalize(); self.normalize(append=True); p=self.build()
        self.assertEqual(p['schedules']['rows'][0]['disposition'],'duplicate')
        self.assertEqual(p['schedules']['written-lines'],[])
        self.assertEqual([r for r in p['schedules']['totals'] if r['basis']=='newly_written_only'],[])
        self.assertEqual(self.check(p,'written_totals'),'no_observed_amounts')

    def test_economic_duplicate_and_revised_overlap_remain_visible(self):
        self.normalize(); self.row['Track Title']='PRIVATE_DIFFERENT_TITLE'; self.normalize(append=True)
        p=self.build()
        metric=next(r for r in p['schedules']['counts'] if r['metric']=='economic_duplicate_rows')
        self.assertEqual(metric['supplied'],1); self.assertIsNone(metric['observed'])
        self.assertEqual(p['controls']['receipt_status_supplied'],'partial')
        self.assertEqual(p['controls']['ledger_control_status_supplied'],'requires_duplicate_review')
        shutil.rmtree(self.output)
        self.row['Net']='95'; self.normalize(append=True); p=self.build()
        self.assertEqual(p['schedules']['rows'][0]['disposition'],'held')
        self.assertIn('overlap:revised_transaction_requires_resolution',p['schedules']['rows'][0]['reason_codes'])

    def test_missing_amount_currency_and_held_not_zero(self):
        self.row.update(Net='',Currency=''); self.normalize(); p=self.build()
        self.assertEqual(p['controls']['receipt_status_supplied'],'partial')
        line=p['schedules']['written-lines'][0]
        self.assertIsNone(line['owner_net_amount']); self.assertIsNone(line['currency'])
        self.assertIn('missing:owner_net_amount',p['schedules']['rows'][0]['reason_codes'])
        self.assertEqual(p['controls']['ledger_validator_status'],'errors_found')

    def test_control_footer_ignored_and_header_only_fixed_headers(self):
        self.normalize([{**self.row,'Row Type':kind,'Transaction ID':kind} for kind in ('control','footer','ignored')]); p=self.build()
        self.assertEqual(p['schedules']['written-lines'],[])
        self.assertEqual([r['disposition'] for r in p['schedules']['rows']],['control','footer','ignored'])
        shutil.rmtree(self.output); self.normalize([]); p=self.build()
        self.assertEqual(p['controls']['receipt_status_supplied'],'partial')
        self.assertEqual(p['controls']['ledger_validator_status'],'errors_found')
        for name,fields in export.FIELDS.items():
            with (self.output/(name+'.csv')).open() as f:self.assertEqual(next(csv.reader(f)),list(fields))

    def test_matched_supplied_controls_do_not_authenticate_source(self):
        controls={'evidence_refs':['PRIVATE_URL_SECRET'],'totals':[{'currency':'USD','field':'owner_net_amount','amount':'97.0001'}]}
        self.normalize(controls=controls); p=self.build(controls=self.root/'controls.json')
        self.assertEqual(p['controls']['controls_status_supplied'],'matched')
        self.assertEqual(self.check(p,'additional_controls_vs_supplied_source_totals'),'matches_supplied_claims_only')
        self.assertEqual(self.check(p,'source_totals'),'not_recomputed')
        self.assertEqual(p['controls']['source_authenticity'],'not_verified')
        self.assertNotIn('PRIVATE', ''.join(f.read_text() for f in self.output.iterdir()))

    def test_mismatched_controls_and_unknown_source_are_visible(self):
        controls={'evidence_refs':['synthetic:summary'],'totals':[{'currency':'USD','field':'owner_net_amount','amount':'1'}]}
        self.normalize(controls=controls); p=self.build(source=False,controls=self.root/'controls.json')
        self.assertEqual(p['controls']['controls_status_supplied'],'mismatch')
        self.assertEqual(self.check(p,'additional_controls_vs_supplied_source_totals'),'mismatch')
        self.assertEqual(self.check(p,'original_source_bytes'),'unknown_not_supplied')

    def test_tampered_written_amount_is_mismatch(self):
        self.normalize(); self.rewrite_ledger(lambda rows:rows[0].update(owner_net_amount='999'))
        p=self.build(); self.assertEqual(p['controls']['artifact_consistency'],'mismatch')
        row=next(r for r in p['schedules']['totals'] if r['basis']=='newly_written_only' and r['field']=='owner_net_amount')
        self.assertEqual(row['supplied_amount'],'97.0001');self.assertEqual(row['observed_amount'],'999')
        self.assertEqual(row['check'],'mismatch')

    def test_missing_or_wrong_provenance_written_rows_never_pass(self):
        for mode in ('missing','provenance','duplicate'):
            self.normalize()
            def mutate(rows):
                if mode=='missing':rows.clear()
                elif mode=='provenance':rows[0]['transform_id']='b'*64
                else:rows.append(copy.deepcopy(rows[0]))
            self.rewrite_ledger(mutate); p=self.build()
            self.assertEqual(self.check(p,'written_row_association'),'mismatch')
            self.assertTrue(all(r['observed_amount'] is None for r in p['schedules']['totals'] if r['basis']=='newly_written_only'))
            shutil.rmtree(self.output)

    def test_source_and_row_identity_tampering_visible(self):
        self.normalize();self.source.write_text('different source bytes')
        row=json.loads(self.rows_path.read_text());row['source_row']=999
        self.rows_path.write_text(json.dumps(row)+'\n');p=self.build()
        self.assertEqual(self.check(p,'original_source_bytes'),'mismatch')
        self.assertEqual(self.check(p,'row_receipt_identity'),'mismatch')
        self.assertEqual(p['controls']['artifact_consistency'],'mismatch')

    def test_count_tampering_and_typed_schema_rejection(self):
        self.normalize(); self.receipt['row_conservation']['source_rows']=12
        self.receipt_path.write_text(json.dumps(self.receipt));p=self.build()
        self.assertEqual(p['controls']['artifact_consistency'],'mismatch');shutil.rmtree(self.output)
        self.receipt['row_conservation']['source_rows']=True;self.receipt_path.write_text(json.dumps(self.receipt))
        with self.assertRaises(ValueError):self.build()
        self.assertFalse(self.output.exists())

    def test_privacy_arbitrary_extensions_and_reasons(self):
        self.normalize()
        self.receipt.update(input='PRIVATE_PATH',headers_seen=['PRIVATE_HEADER'],warnings=['PRIVATE_ERROR'],extra='PRIVATE_EXTENSION')
        self.receipt_path.write_text(json.dumps(self.receipt))
        row=json.loads(self.rows_path.read_text());row['reasons']=['PRIVATE_REASON'];self.rows_path.write_text(json.dumps(row)+'\n')
        p=self.build()
        self.assertEqual(p['schedules']['rows'][0]['reason_codes'],['other_private_reason'])
        self.assertNotIn('PRIVATE',''.join(f.read_text() for f in self.output.iterdir()))
        self.assertEqual(len({export.alias('version',v) for v in (1,'1',True)}),3)

    def test_separate_currency_exact_signed_subcent_and_large_values(self):
        self.normalize([{**self.row,'Net':'-0.000000000000000001'}, {**self.row,'Net':'9007199254740993','Currency':'EUR','Transaction ID':'SECOND'}])
        p=self.build();rows=[r for r in p['schedules']['totals'] if r['basis']=='newly_written_only' and r['field']=='owner_net_amount']
        self.assertEqual({r['currency']:r['observed_amount'] for r in rows},{'USD':'-0.000000000000000001','EUR':'9007199254740993'})
        with (self.output/'written-lines.csv').open() as f:self.assertTrue(next(csv.DictReader(f))['owner_net_amount'].startswith("'"))

    def test_existing_outputs_private_modes_and_write_cleanup(self):
        self.normalize();self.build()
        self.assertEqual(self.output.stat().st_mode & 0o777,0o700)
        for f in self.output.iterdir():self.assertEqual(f.stat().st_mode & 0o777,0o600)
        before=(self.output/'manifest.json').read_bytes()
        with self.assertRaises(ValueError):self.build()
        self.assertEqual(before,(self.output/'manifest.json').read_bytes());shutil.rmtree(self.output)
        with patch.object(export.csv.DictWriter,'writerow',side_effect=OSError('synthetic')):
            with self.assertRaises(OSError):self.build()
        self.assertFalse(self.output.exists());self.assertTrue(self.ledger.exists())

    def test_complete_total_links_and_linear_output_size(self):
        sizes=[]
        for n in (32,64):
            self.normalize([{**self.row,'Transaction ID':str(i)} for i in range(n)])
            p=self.build();sizes.append((self.output/'workpaper.json').stat().st_size)
            total=next(r for r in p['schedules']['totals'] if r['basis']=='newly_written_only' and r['field']=='owner_net_amount')
            self.assertEqual(len(total['line_refs']),n)
            self.assertEqual(len(set(total['line_refs'])),n)
            self.assertEqual(set(total['line_refs']),{r['line_ref'] for r in p['schedules']['written-lines']})
            shutil.rmtree(self.output)
        self.assertLess(sizes[1]/sizes[0],2.2)

    def test_invalid_nonempty_amount_with_empty_receipt_totals_is_mismatch(self):
        self.row.update(Gross='', Net='', Deductions='')
        self.normalize()
        self.assertEqual(self.receipt['source_totals'], [])
        self.assertEqual(self.receipt['written_totals'], [])
        self.rewrite_ledger(lambda rows: rows[0].update(owner_net_amount='PRIVATE_INVALID_AMOUNT'))
        p=self.build()
        self.assertEqual(self.check(p,'written_totals'),'mismatch')
        self.assertEqual(p['controls']['artifact_consistency'],'mismatch')
        self.assertIsNone(p['schedules']['written-lines'][0]['owner_net_amount'])
        self.assertEqual(p['schedules']['totals'],[])
        self.assertEqual(p['controls']['readiness'],'review_required')
        self.assertNotIn('PRIVATE_INVALID_AMOUNT',''.join(f.read_text() for f in self.output.iterdir()))

    def test_unknown_currency_supplied_totals_and_empty_are_not_zero(self):
        self.row.update(Currency='',Gross='',Net='',Deductions='')
        self.normalize();p=self.build()
        self.assertEqual(p['schedules']['totals'],[])
        self.assertEqual(self.check(p,'written_totals'),'no_observed_amounts')
        self.assertEqual(p['controls']['artifact_consistency'],'no_detected_mismatch_within_supported_checks')
        self.assertIsNone(p['schedules']['written-lines'][0]['owner_net_amount'])

    def test_old_held_baseline_and_new_ok_import_are_separate(self):
        self.row['Net']='';self.normalize()
        self.row.update(Net='2',**{'Transaction ID':'SECOND'});self.normalize(append=True)
        p=self.build()
        self.assertEqual(p['controls']['receipt_status_supplied'],'ok')
        self.assertEqual(p['controls']['ledger_validator_status'],'errors_found')
        self.assertEqual(p['controls']['ledger_held_rows'],1)
        self.assertEqual(p['controls']['artifact_consistency'],'no_detected_mismatch_within_supported_checks')
        self.assertEqual(p['controls']['readiness'],'review_required')

    def test_duplicate_json_unsupported_versions_and_destination_links_refused(self):
        self.normalize()
        original=self.receipt_path.read_bytes()
        self.receipt_path.write_text('{"status":"ok","status":"partial"}')
        with self.assertRaises(ValueError):self.build()
        self.assertFalse(self.output.exists())
        self.receipt_path.write_bytes(original)
        self.receipt['parser_version']='future/999';self.receipt_path.write_text(json.dumps(self.receipt))
        with self.assertRaises(ValueError):self.build()
        self.receipt_path.write_bytes(original)
        self.output.symlink_to(self.ledger)
        with self.assertRaises(ValueError):self.build()
        self.assertTrue(self.output.is_symlink())

    def test_input_bounds_refuse_before_output_and_unbounded_reads(self):
        self.normalize()
        original=self.receipt_path.read_bytes()
        self.receipt_path.write_text(json.dumps({**self.receipt,'warnings':['X'*(2*1024*1024)]}))
        with self.guard_input_streams() as observed:
            with self.assertRaises(ValueError):
                export.build(self.receipt_path,self.ledger,self.rows_path,self.output,'2026-11-18')
        self.assertEqual(observed,{'opens':[], 'reads':[]})
        self.assertFalse(self.output.exists());self.receipt_path.write_bytes(original)
        for name,limit in [('MAX_JSONL_RECORD_BYTES',32),('MAX_ROW_RECEIPT_BYTES',32),('MAX_LEDGER_BYTES',32),('MAX_CURRENT_ROWS',0),('MAX_FIELD_CHARS',4),('MAX_CSV_RECORD_CHARS',32),('MAX_LEDGER_ROWS',0)]:
            with self.subTest(limit=name),patch.object(export.bounded,name,limit),self.guard_input_streams():
                with self.assertRaises(ValueError):
                    export.build(self.receipt_path,self.ledger,self.rows_path,self.output,'2026-11-18')
                self.assertFalse(self.output.exists())
        row=json.loads(self.rows_path.read_text());row['reasons']=['synthetic']*65
        self.rows_path.write_text(json.dumps(row)+'\n')
        with self.assertRaises(ValueError):
            export.build(self.receipt_path,self.ledger,self.rows_path,self.output,'2026-11-18')
        self.assertFalse(self.output.exists())

    def test_large_baseline_streams_with_small_current_receipt(self):
        self.normalize();self.row.update(Net='2.0049',**{'Transaction ID':'SECOND'});self.normalize(append=True)
        with self.ledger.open(newline='') as f:
            reader=csv.DictReader(f);fields=reader.fieldnames;old,new=list(reader)
        with self.ledger.open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
            for i in range(512):
                writer.writerow({**old,'ledger_line_id':'baseline-'+str(i),'raw_values':'X'*32768})
            writer.writerow(new)
        self.receipt['ledger_total_rows']=513;self.receipt_path.write_text(json.dumps(self.receipt))
        tracemalloc.start()
        try:
            with self.guard_input_streams() as observed:
                manifest=export.build(self.receipt_path,self.ledger,self.rows_path,self.output,'2026-11-18')
            _,peak=tracemalloc.get_traced_memory()
        finally:tracemalloc.stop()
        self.assertEqual(set(observed['opens']),{self.receipt_path,self.rows_path,self.ledger})
        self.assertEqual({path for path,_,_ in observed['reads']},set(observed['opens']))
        self.assertGreater(sum(path==self.ledger for path,_,_ in observed['reads']),1)
        self.assertLess(peak,self.ledger.stat().st_size//2)
        self.assertEqual(manifest['ledger_sha256'],export.normalizer.sha256_file(self.ledger))
        p=json.loads((self.output/'workpaper.json').read_text())
        self.assertEqual(len(p['schedules']['written-lines']),1)
        self.assertEqual(p['schedules']['written-lines'][0]['owner_net_amount'],'2.0049')
        self.assertEqual(self.check(p,'append_baseline'),'unknown_not_bound_by_receipt')

    def test_wide_normalizer_source_preserves_projection_and_limits(self):
        self.row.update({'PRIVATE_COLUMN_'+str(i):'PRIVATE_VALUE' for i in range(300)})
        self.normalize()
        self.assertGreater(len(json.loads(self.rows_path.read_text())['raw_values']),256)
        p=self.build()
        self.assertEqual(p['controls']['artifact_consistency'],'no_detected_mismatch_within_supported_checks')
        self.assertEqual(p['schedules']['written-lines'][0]['owner_net_amount'],'97.0001')
        self.assertNotIn('PRIVATE',''.join(f.read_text() for f in self.output.iterdir()))
        shutil.rmtree(self.output)
        with patch.object(export.bounded,'MAX_JSONL_RECORD_BYTES',64):
            with self.assertRaises(ValueError):self.build()
        self.assertFalse(self.output.exists())
        row=json.loads(self.rows_path.read_text())
        row['raw_values']['PRIVATE_OVERSIZE']='X'*(export.bounded.MAX_FIELD_CHARS+1)
        self.rows_path.write_text(json.dumps(row)+'\n')
        with self.assertRaises(ValueError):self.build()
        self.assertFalse(self.output.exists())

    def test_stream_guard_detects_unbounded_read_regressions(self):
        self.normalize()
        for name,target in [('read_small',self.receipt_path),('read_rows',self.rows_path),('copy_hash',self.ledger)]:
            original=getattr(export.bounded,name)
            def unbounded(path,*args):
                with Path(path).open('rb') as stream:stream.read()
                return original(path,*args)
            with self.subTest(reader=name),patch.object(export.bounded,name,unbounded),self.guard_input_streams() as observed:
                with self.assertRaisesRegex(AssertionError,'unbounded input stream'):
                    export.build(self.receipt_path,self.ledger,self.rows_path,self.output,'2026-11-18')
            self.assertEqual(observed['reads'][-1],(target,'read',-1))
            self.assertFalse(self.output.exists())

    def test_snapshot_hash_and_checks_do_not_reread_changed_original(self):
        self.normalize();before=export.normalizer.sha256_file(self.ledger)
        original=export.project
        def project_then_change(*args,**kwargs):
            result=original(*args,**kwargs)
            self.ledger.write_text('changed after snapshot')
            return result
        with patch.object(export,'project',project_then_change):
            manifest=export.build(self.receipt_path,self.ledger,self.rows_path,self.output,'2026-11-18')
        self.assertEqual(manifest['ledger_sha256'],before)
        self.assertEqual(manifest['ledger_validator_status'],'ok')

    def test_export_never_calls_normalizer_import(self):
        self.normalize()
        with patch.object(export.normalizer,'normalize',side_effect=AssertionError('must not import')):
            self.build()

    def test_standalone_cli_with_local_dependencies_only(self):
        self.normalize();folder=self.root/'standalone';folder.mkdir()
        for name in ('build-normalization-workpaper.py','normalize-royalty-statement.py','validate-normalized-ledger.py','build-royalty-workpaper.py','_finance.py','_normalization_workpaper_io.py','_royalty_archive.py'):
            shutil.copyfile(SCRIPTS/name,folder/name)
        run=subprocess.run([sys.executable,str(folder/'build-normalization-workpaper.py'),'--receipt',str(self.receipt_path),
            '--ledger',str(self.ledger),'--row-receipt',str(self.rows_path),'--output-directory',str(self.output),'--as-of','2026-11-18'],
            cwd='/tmp',env={**os.environ,'PYTHONPATH':''},capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stderr);self.assertNotIn('PRIVATE',run.stdout+run.stderr)


if __name__=='__main__':unittest.main()
