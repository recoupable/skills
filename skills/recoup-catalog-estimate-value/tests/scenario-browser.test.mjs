import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import crypto from 'node:crypto';
import {runScenario, REFERENCE_SOURCE_SHA256, METHOD_VERSION} from '../scripts/scenario.mjs';
const skill = fileURLToPath(new URL('../', import.meta.url));
const vectors = JSON.parse(fs.readFileSync(skill + 'fixtures/scenario-vectors.json', 'utf8'));
const fresh = () => structuredClone(vectors.request);
const python = requests => {
  // Serialize JS inputs first: the transport is JSON, not Python-only numeric types.
  const code = `import importlib.util,json,sys\nspec=importlib.util.spec_from_file_location('scenario',sys.argv[1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)\nresults=[]\nfor req in json.load(sys.stdin):\n try: results.append({'ok':True,'value':m.run_scenario(req)})\n except Exception as e: results.append({'ok':False})\nprint(json.dumps(results))`;
  const result = spawnSync('python3', ['-c', code, skill + 'scripts/scenario.py'], {input: JSON.stringify(requests), encoding: 'utf8', maxBuffer: 20*1024*1024, timeout: 30000});
  assert.equal(result.status, 0, result.stderr); return JSON.parse(result.stdout);
};
const normalized = result => { const copy=structuredClone(result);delete copy.execution_runtime;delete copy.calculation_source_role;return copy; };
function equivalent(actual, expected) {
  if (typeof expected === 'number') assert.ok(Math.abs(actual-expected) <= Math.max(1e-9, Math.abs(expected)*1e-12), `${actual} != ${expected}`);
  else if (expected && typeof expected === 'object') {
    assert.deepEqual(Object.keys(actual).sort(), Object.keys(expected).sort());
    for (const key of Object.keys(expected)) equivalent(actual[key],expected[key]);
  } else assert.equal(actual,expected);
}

test('source pin and deterministic vectors match unchanged Python', async () => {
  const method=JSON.parse(fs.readFileSync(skill+'references/scenario-method.json','utf8'));
  assert.equal(crypto.createHash('sha256').update(fs.readFileSync(skill+'scripts/estimate.py')).digest('hex'),REFERENCE_SOURCE_SHA256);
  assert.equal(method.source_sha256,REFERENCE_SOURCE_SHA256);
  const inputs=[fresh(),...vectors.variants.map(v=>({...fresh(),spotify_rate:v.spotify_rate}))];
  const refs=python(inputs);
  for (let i=0;i<inputs.length;i++) {
    assert.equal(refs[i].ok,true);equivalent(normalized(await runScenario(inputs[i])),refs[i].value);
  }
});

test('cross-runtime rate/share/coverage properties, reset and Unicode provenance', async () => {
  const inputs=[];
  for(let i=0;i<40;i++) {
    const q=fresh();q.spotify_rate=i%7===0?null:i/10000;
    q.assumptions.controlled_share=(i%11)/10;
    q.observations.tracks[0].sp_ttm=i*997;
    q.observations.tracks[0].title=i%2?'🎵 café \\ud800':'文字';
    if(i%5===0)q.observations.tracks[0]={...q.observations.tracks[0],sp_ttm:null,ttm_source:'none'};
    q.observations.population_complete=i%2===0;
    inputs.push(q);
  }
  const refs=python(inputs);
  for(let i=0;i<inputs.length;i++) {
    const before=structuredClone(inputs[i]);const result=await runScenario(inputs[i]);
    assert.deepEqual(inputs[i],before);assert.equal(refs[i].ok,true);equivalent(normalized(result),refs[i].value);
    if(result.reset_to_baseline)assert.deepEqual(result.baseline,result.scenario);
  }
});

test('negative contract cases refuse in both runtimes', async () => {
  const mutations=[
    q=>q.method_version='unknown',q=>delete q.assumptions.multiple,q=>q.spotify_rate=true,q=>q.spotify_rate=-1,
    q=>q.spotify_rate='0.004',q=>q.observations.population_complete=null,q=>q.observations.coverage_notes=[],
    q=>q.observations.coverage_notes=['\u0085'],q=>q.observations.tracks=[],
    q=>q.observations.tracks[0].title={},q=>q.observations.tracks[0].id='',
    q=>q.observations.tracks[1].id=q.observations.tracks[0].id,
    q=>q.observations.tracks[0].sp_ttm=2**53,q=>q.observations.tracks[0].sp_ttm=-1,
    q=>q.observations.tracks[0].sp_ttm=true,q=>q.observations.tracks[0].sp_ttm=1.2,
    q=>q.observations.tracks[1].sp_ttm=0,q=>q.observations.tracks[0].ttm_source='runrate_30d',
    q=>q.observations.tracks[0].ttm_source='cumulative',q=>q.observations.tracks[0].source_ref='',
    q=>q.observations.tracks[0].captured_at='',q=>q.observations.tracks[0].basis.currency='EUR',
    q=>q.observations.tracks[0].basis.cohort_id='other',q=>q.observations.tracks[0].basis.period_end='2026-01-02',
    q=>q.observations.basis.period_start='2025-02-30',q=>q.observations.basis.period_start='0000-01-01',
    q=>q.observations.basis.right_kind='composition',q=>q.observations.basis.unit='luminate_streams',
    q=>q.assumptions.currency='EUR',q=>q.assumptions.controlled_share=2,q=>q.assumptions.controlled_share=true,
    q=>q.assumptions.assumption_status='verified',q=>q.assumptions.assumption_sources=[],
    q=>q.assumptions.window_days=30,q=>q.assumptions.min_delta_days=true,q=>q.assumptions.min_delta_days=0,q=>q.assumptions.min_delta_days=1e21,
    q=>q.assumptions.nls_band.high=2,q=>q.assumptions.multiple.low=99,q=>q.assumptions.rates.youtube=1,
    q=>q.assumptions.rates.spotify=1e308,q=>q.observations.tracks[0].title='\ud800',
    q=>q.observations.tracks[1]={...q.observations.tracks[0],id:'second',sp_ttm:9007199254740991},
  ];
  const inputs=mutations.map(fn=>{const q=fresh();fn(q);return q;});const refs=python(inputs);
  for(let i=0;i<inputs.length;i++) {
    assert.equal(refs[i].ok,false,`Python accepted negative${i}`);
    await assert.rejects(runScenario(inputs[i]),undefined,`JS accepted negative${i}`);
  }
});

test('nonfinite/non-JSON inputs refuse before hashing', async () => {
  for(const value of [NaN,Infinity,undefined,()=>0])await assert.rejects(runScenario({...fresh(),spotify_rate:value}));
  const cyclic=fresh();cyclic.extra=cyclic;await assert.rejects(runScenario(cyclic));
});

test('snapshot isolation across async hash and output isolation', async () => {
  const q=fresh(),before=structuredClone(q),pending=runScenario(q);
  q.observations.tracks[0].sp_ttm=9999;q.assumptions.rates.spotify=99;
  const out=await pending;assert.deepEqual(out.observations,before.observations);
  out.observations.tracks[0].sp_ttm=7;assert.equal(q.observations.tracks[0].sp_ttm,9999);
  assert.equal(out.execution_runtime,'catalog-browser-scenario/1');assert.match(out.calculation_source_role,/not executed/);
});

test('bounded10000-record cohort matches reference without network', async () => {
  const q=fresh();q.observations.tracks=Array.from({length:10000},(_,i)=>({...q.observations.tracks[0],id:'recording-'+i,sp_ttm:i%7}));
  const refs=python([q]);const out=await runScenario(q);equivalent(normalized(out),refs[0].value);
  q.observations.tracks.push({...q.observations.tracks[0],id:'too-many'});await assert.rejects(runScenario(q));
});
