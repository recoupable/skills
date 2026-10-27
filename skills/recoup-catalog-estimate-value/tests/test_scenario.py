import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('scenario',ROOT/'scripts/scenario.py')
S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)
V=json.loads((ROOT/'fixtures/scenario-vectors.json').read_text())

class ScenarioTests(unittest.TestCase):
    def setUp(self):self.request=copy.deepcopy(V['request'])
    def test_method_contract_pins_existing_calculation_and_vectors(self):
        contract=json.loads((ROOT/'references/scenario-method.json').read_text())
        schema=json.loads((ROOT/'references/scenario-request.schema.json').read_text())
        self.assertEqual(contract['source_sha256'],S.CALCULATION_HASH)
        self.assertEqual(contract['method_id']+'/'+str(contract['version']),S.METHOD)
        self.assertEqual(schema['properties']['method_version']['const'],S.METHOD)
        self.assertEqual(V['method_version'],S.METHOD)
    def test_loaded_calculation_source_drift_refuses_false_provenance(self):
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/'estimate.py').write_bytes((ROOT/'scripts/estimate.py').read_bytes()+b'\n# different source\n')
            with patch.object(S,'HERE',root):
                with self.assertRaisesRegex(ValueError,'source changed'):S.run_scenario(self.request)

    def test_vectors_reconcile_and_observations_remain_immutable(self):
        before=copy.deepcopy(self.request)
        with patch.object(S.estimate,'api',side_effect=AssertionError('No network')):
            out=S.run_scenario(self.request)
        self.assertEqual(before,self.request)
        self.assertEqual(out['observations'],before['observations'])
        for model in ('baseline','scenario'):
            for field in ('annual_gross','annual_nls','value'):
                for band in S.BANDS:self.assertAlmostEqual(out[model][field][band],V['expected'][model][field])
            for field in ('status','covered_tracks','input_tracks','coverage_share'):
                self.assertEqual(out[model][field],V['expected'][field])
        self.assertEqual(out['scenario']['unknown_track_ids'],['synthetic-unknown'])
    def test_reset_and_rate_vectors_preserve_coverage(self):
        for vector in V['variants']:
            self.request['spotify_rate']=vector['spotify_rate'];out=S.run_scenario(self.request)
            for field in ('annual_gross','annual_nls','value'):
                self.assertAlmostEqual(out['scenario'][field]['central'],vector[field])
            self.assertEqual(out['scenario']['coverage_share'],.5)
            if vector['spotify_rate'] is None:
                self.assertEqual(out['baseline'],out['scenario'])
                self.assertEqual(out['baseline_assumptions'],out['scenario_assumptions'])
                self.assertTrue(out['reset_to_baseline'])
    def test_rate_linearity_nonnegative_monotonicity_and_permutation(self):
        previous=-1
        for rate in [0,.001,.002,.004,.008,.016]:
            self.request['spotify_rate']=rate;out=S.run_scenario(self.request)
            value=out['scenario']['value']['central']
            self.assertAlmostEqual(value,20*rate/.004)
            self.assertGreaterEqual(value,previous);previous=value
            self.request['observations']['tracks'].reverse()
            self.assertEqual(out['scenario'],S.run_scenario(self.request)['scenario'])
    def test_delegates_existing_method_without_double_deduction(self):
        with patch.object(S.estimate,'model_tracks',wraps=S.estimate.model_tracks) as method:
            out=S.run_scenario(self.request)
        self.assertEqual(method.call_count,2)
        self.assertEqual(out['scenario']['annual_nls']['central'],4)
    def test_unknown_and_observed_zero_stay_distinct(self):
        known=self.request['observations']['tracks'][0]
        known.update(sp_ttm=None,ttm_source='none')
        out=S.run_scenario(self.request)
        self.assertIsNone(out['scenario']['value']['central'])
        self.assertEqual(out['scenario']['status'],'insufficient_measurement')
        known.update(sp_ttm=0,ttm_source='measured_365d')
        out=S.run_scenario(self.request)
        self.assertEqual(out['scenario']['value']['central'],0)
        self.assertEqual(out['scenario']['covered_tracks'],1)
    def test_incompatible_bases_refuse(self):
        for key,value in [('currency','EUR'),('cohort_id','other'),('period_end','2026-01-02'),('right_kind','composition'),('unit','luminate_streams')]:
            request=copy.deepcopy(self.request);request['observations']['tracks'][0]['basis'][key]=value
            with self.assertRaises(ValueError):S.run_scenario(request)
    def test_wrong_window_and_unmeasured_cumulative_refuse(self):
        for source in ['runrate_30d','cumulative','measured_30d']:
            self.request['observations']['tracks'][0]['ttm_source']=source
            with self.assertRaises(ValueError):S.run_scenario(self.request)
        self.request=copy.deepcopy(V['request'])
        self.request['observations']['basis']['period_end']='2025-02-01'
        with self.assertRaises(ValueError):S.run_scenario(self.request)
    def test_bad_assumptions_versions_and_numeric_values_refuse(self):
        for value in [True,-1,float('nan'),float('inf'),'0.004']:
            self.request['spotify_rate']=value
            with self.assertRaises(ValueError):S.run_scenario(self.request)
        self.request=copy.deepcopy(V['request']);self.request['method_version']='unknown'
        with self.assertRaises(ValueError):S.run_scenario(self.request)
        self.request=copy.deepcopy(V['request']);del self.request['assumptions']['multiple']
        with self.assertRaises(ValueError):S.run_scenario(self.request)
        self.request=copy.deepcopy(V['request']);self.request['assumptions']['currency']='EUR'
        with self.assertRaises(ValueError):S.run_scenario(self.request)
    def test_duplicate_ids_and_unsafe_counts_refuse(self):
        self.request['observations']['tracks'][1]['id']='synthetic-a'
        with self.assertRaises(ValueError):S.run_scenario(self.request)
        self.request=copy.deepcopy(V['request']);self.request['observations']['tracks'][0]['sp_ttm']=2**53
        with self.assertRaises(ValueError):S.run_scenario(self.request)
    def test_structured_title_refuses_schema_mismatch(self):
        self.request['observations']['tracks'][0]['title']={}
        with self.assertRaisesRegex(ValueError,'title'):S.run_scenario(self.request)

    def test_empty_or_missing_coverage_is_not_assumed(self):
        for key,value in [('population_complete',None),('coverage_notes',[]),('tracks',[])]:
            req=copy.deepcopy(self.request);req['observations'][key]=value
            with self.assertRaises(ValueError):S.run_scenario(req)

if __name__=='__main__':unittest.main()
