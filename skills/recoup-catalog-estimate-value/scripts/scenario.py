#!/usr/bin/env python3
"""Local dev scenario contract; delegate all money calculations to estimate.model_tracks."""
import argparse
import copy
import datetime as dt
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
CALCULATION_HASH = hashlib.sha256((HERE/'estimate.py').read_bytes()).hexdigest()
spec = importlib.util.spec_from_file_location('estimate', HERE/'estimate.py')
estimate = importlib.util.module_from_spec(spec); spec.loader.exec_module(estimate)
if hashlib.sha256((HERE/'estimate.py').read_bytes()).hexdigest() != CALCULATION_HASH:
    raise RuntimeError('Calculation source changed during import')
METHOD = 'public-estimate-spotify-rate/1'
BANDS = {'low', 'central', 'high'}
BASIS = {'cohort_id', 'period_start', 'period_end', 'currency', 'right_kind', 'unit'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def number(value, label):
    require(type(value) in {int, float} and math.isfinite(value) and value >= 0,
            f'{label} must be a finite nonnegative number')
    return value


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def fingerprint(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def run_scenario(request):
    """Return baseline and hypothetical side-by-side; never mutate observations."""
    require(hashlib.sha256((HERE/'estimate.py').read_bytes()).hexdigest() == CALCULATION_HASH,
            'Calculation source changed; reload the pinned method before evaluation')
    request = copy.deepcopy(request)
    require(isinstance(request, dict) and set(request) == {'method_version', 'observations', 'assumptions', 'spotify_rate'},
            'Request requires exact scenario fields')
    require(request['method_version'] == METHOD, 'Unsupported method version')
    observations = request['observations']; cfg = request['assumptions']
    require(isinstance(observations, dict) and set(observations) == {'basis', 'population_complete', 'coverage_notes', 'tracks'},
            'Observation envelope fields mismatch')
    basis = observations['basis']
    require(isinstance(basis, dict) and set(basis) == BASIS, 'Explicit compatible basis required')
    require(isinstance(basis['cohort_id'], str) and basis['cohort_id'].strip(), 'Explicit cohort required')
    require(basis['right_kind'] == 'master' and basis['unit'] == 'spotify_streams', 'Unsupported rights or measurement unit')
    require(isinstance(basis['currency'], str) and re.fullmatch('[A-Z]{3}', basis['currency']), 'Explicit currency required')
    try:
        start = dt.date.fromisoformat(basis['period_start']); end = dt.date.fromisoformat(basis['period_end'])
    except (TypeError, ValueError) as exc:
        raise ValueError('Explicit ISO measurement dates required') from exc
    require(start.isoformat() == basis['period_start'] and end.isoformat() == basis['period_end']
            and (end-start).days == 365, 'Only matching measured 365-day windows are supported')
    require(type(observations['population_complete']) is bool, 'Population coverage must be explicit')
    notes = observations['coverage_notes']
    require(isinstance(notes, list) and notes and all(isinstance(n,str) and n.strip() for n in notes), 'Coverage limitations required')
    tracks = observations['tracks']
    require(isinstance(tracks,list) and 0 < len(tracks) <= 10000, 'Provide 1 to 10000 recordings')
    known_total = 0
    for track in tracks:
        require(isinstance(track,dict) and set(track) == {'id','title','sp_ttm','ttm_source','basis','source_ref','captured_at'}, 'Track fields mismatch')
        require(isinstance(track['title'], str), 'Track title must remain text')
        require(track['basis'] == basis, 'Incompatible currency, period, cohort, rights or unit')
        require(isinstance(track['source_ref'],str) and track['source_ref'].strip(), 'Source reference required')
        require(isinstance(track['captured_at'],str) and track['captured_at'].strip(), 'Capture timestamp required')
        require(track['ttm_source'] in {'measured_365d','none'}, 'Run-rates/cumulative counts are outside this dev method')
        if track['ttm_source'] == 'none':
            require(track['sp_ttm'] is None, 'Unknown measurement must remain null')
        else:
            count = track['sp_ttm']
            require(type(count) is int and 0 <= count <= 9007199254740991, 'Measured streams must be safe nonnegative integers')
            known_total += count
    require(known_total <= 9007199254740991, 'Combined count exceeds interoperable integer precision')
    required = {'currency','right_kind','controlled_share','assumption_status','assumption_sources','rates',
                'other_dsp_grossup','nls_band','multiple','window_days','min_delta_days'}
    require(isinstance(cfg,dict) and set(cfg) == required, 'Supply the complete explicit assumption set; no defaults')
    require(cfg['currency'] == basis['currency'] and cfg['right_kind'] == basis['right_kind'], 'Assumption basis mismatch')
    require(cfg['assumption_status'] == 'illustrative_unverified', 'Dev scenarios must remain illustrative_unverified')
    require(isinstance(cfg['assumption_sources'],list) and cfg['assumption_sources']
            and all(isinstance(v,str) and v.strip() for v in cfg['assumption_sources']), 'Assumption provenance/rationale required')
    require(type(cfg['window_days']) is int and cfg['window_days'] == 365, 'Annual window required')
    number(cfg['controlled_share'],'controlled_share')
    require(isinstance(cfg['rates'],dict) and set(cfg['rates']) == {'spotify'}, 'Only explicit Spotify rate supported')
    for group in ('rates','other_dsp_grossup','nls_band','multiple'):
        require(isinstance(cfg[group],dict), f'{group} must be an object')
        if group != 'rates': require(set(cfg[group]) == BANDS, f'{group} requires exact bands')
        for key,value in cfg[group].items():number(value,group+'.'+key)
    override = request['spotify_rate']
    if override is not None:number(override,'spotify_rate')
    scenario_cfg = copy.deepcopy(cfg)
    if override is not None:scenario_cfg['rates']['spotify'] = override
    # Existing adopted method is the only owner of the financial arithmetic.
    baseline = estimate.model_tracks(tracks,cfg,population_complete=observations['population_complete'])
    scenario = estimate.model_tracks(tracks,scenario_cfg,population_complete=observations['population_complete'])
    for model in (baseline,scenario):
        for field in ('annual_gross','annual_nls','value'):
            require(all(v is None or math.isfinite(v) for v in model[field].values()), 'Scenario arithmetic overflow')
    result = {'method_version':METHOD,'calculation_schema':'public-estimate/2',
              'calculation_source_sha256':CALCULATION_HASH,
              'observations':observations,'observations_sha256':fingerprint(observations),
              'baseline_assumptions':cfg,'scenario_assumptions':scenario_cfg,
              'baseline':baseline,'scenario':scenario,'reset_to_baseline':override is None,
              'output_basis':'hypothetical only; not measured royalties, ownership, receivables or cash',
              'units':{'spotify_rate':basis['currency']+'/Spotify stream','annual_gross':basis['currency']+'/365 days',
                       'annual_nls':basis['currency']+'/365 days','value':basis['currency']},
              'numeric_policy':'Existing binary64 estimate arithmetic; no row rounding; compare finite outputs at relative tolerance 1e-12 and absolute tolerance 1e-9'}
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',required=True)
    args=parser.parse_args()
    try:
        with open(args.input) as stream: request=json.load(stream)
        print(json.dumps(run_scenario(request),indent=2,allow_nan=False))
        return 0
    except (ValueError,TypeError,KeyError,OSError,OverflowError) as exc:
        parser.exit(2,f'scenario: {exc}\n')


if __name__=='__main__':raise SystemExit(main())
