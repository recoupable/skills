#!/usr/bin/env python3
"""Export a private, reproducible statement/remittance/receipt workpaper."""
import argparse
import csv
import importlib.util
import json
import os
import shutil
from pathlib import Path
from _finance import amount, dumps, iso_date

HERE = Path(__file__).resolve().parent


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Reuse accepted non-financial export contracts; every dependency ships in this skill.
common = load('remittance_export_common', 'build-royalty-workpaper.py')
calculator = load('remittance_export_calculator', 'reconcile-remittances.py')
FIELDS = {
    'records': ('record_ref', 'record_type', 'source_record_ref', 'source_version_ref',
                'amount', 'currency', 'period_start', 'period_end', 'date', 'reported_status',
                'reported_status_ref', 'evidence_status', 'evidence_status_ref', 'evidence_refs', 'freshness'),
    'allocations': ('allocation_ref', 'stage', 'in_completion_scope', 'from_record_ref', 'to_record_ref',
                    'from_amount', 'from_currency', 'to_amount', 'to_currency', 'fx_rate', 'adjustments',
                    'status', 'evidence_refs', 'fx_evidence_refs', 'freshness', 'calculation_basis'),
    'adjustments': ('allocation_ref', 'adjustment_ref', 'kind', 'amount', 'currency', 'evidence_refs', 'freshness'),
    'residuals': ('stage', 'side', 'record_ref', 'in_completion_scope', 'currency', 'amount', 'allocated', 'unallocated'),
    'verified-receipts': ('currency', 'amount', 'basis', 'allocation_refs'),
    'unresolved': ('allocation_ref', 'stage', 'status', 'amount', 'reason', 'freshness'),
    'evidence': common.SCHEDULE_FIELDS['evidence'],
}
STAGES = {'statement_to_remittance': ('statements', 'remittances'),
          'remittance_to_receipt': ('remittances', 'receipts')}


def alias(kind, value):
    """Typed canonical JSON aliases; raw identifiers never enter exported text."""
    return common.alias(kind, json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False))


def evidence_refs(item, key='evidence_refs'):
    values = item.get(key, [])
    return [v for v in values if isinstance(v, str) and v.strip()] if isinstance(values, list) else []


def state(states):
    values = set(states)
    return 'stale' if 'stale' in values else 'unknown' if not values or 'unknown' in values else 'current_as_supplied'


def build(input_path, result_path, output, as_of, evidence_path=None):
    as_of = iso_date(as_of, 'as_of').isoformat()
    data, input_hash = common.read_json(input_path, decimal_inputs=True)
    result, result_hash = common.read_json(result_path)
    expected = json.loads(dumps(calculator.reconcile(data)))
    if json.dumps(result, sort_keys=True, allow_nan=False) != json.dumps(expected, sort_keys=True, allow_nan=False):
        raise ValueError('Result differs from current calculator and input; retain historical results and choose a new version')
    supplied, evidence_hash = common.read_json(evidence_path) if evidence_path else ({'schema_version': '1', 'sources': []}, None)
    objects = {name: {item['id']: item for item in data.get(name, [])} for name in ('statements', 'remittances', 'receipts')}
    inputs = {item['allocation_id']: item for item in data.get('allocations', [])}
    all_refs = set()
    for items in objects.values():
        for item in items.values():
            all_refs.update(evidence_refs(item))
    for item in inputs.values():
        all_refs.update(evidence_refs(item))
        all_refs.update(evidence_refs(item, 'fx_evidence_refs'))
        adjustments = item.get('adjustments', [])
        if isinstance(adjustments, list):
            for adjustment in adjustments:
                if isinstance(adjustment, dict):
                    all_refs.update(evidence_refs(adjustment))
    evidence = common.evidence_rows(all_refs, supplied, as_of)
    def context(item, key='evidence_refs'):
        refs = evidence_refs(item, key)
        return {'evidence_refs': [common.alias('evidence', ref) for ref in refs],
                'freshness': common.freshness(refs, evidence)}
    schedules = {name: [] for name in FIELDS}
    object_states = {}
    for name, items in objects.items():
        for identity, item in items.items():
            ctx = context(item)
            object_states[(name, identity)] = ctx['freshness']
            # Periods belong to statement records. Edges link records, without expanding
            # all ancestor periods for each receipt or fabricating payment/usage dates.
            schedules['records'].append({
                'record_ref': alias(name, identity), 'record_type': name,
                'source_record_ref': alias('source_record', item['source_record_id']),
                'source_version_ref': alias('source_version', item['source_version']) if item.get('source_version') is not None else None,
                'amount': format(amount(item['amount']), 'f'), 'currency': item['currency'],
                'period_start': iso_date(item['period_start'], 'period_start').isoformat() if name == 'statements' else None,
                'period_end': iso_date(item['period_end'], 'period_end').isoformat() if name == 'statements' else None,
                'date': iso_date(item['date'], 'date').isoformat() if name != 'statements' else None,
                'reported_status': item.get('status') if item.get('status') in ('Paid', 'posted', 'pending', 'returned') else 'unknown_or_other',
                'reported_status_ref': alias('reported_status', item['status']) if 'status' in item else None,
                'evidence_status': 'observed' if item.get('evidence_status') == 'observed' else 'unverified_or_unknown',
                'evidence_status_ref': alias('evidence_status', item['evidence_status']) if 'evidence_status' in item else None,
                **ctx})
    scope = result['completion_scope']
    verified_contributors = {}
    for edge in result['allocations']:
        original = inputs[edge['allocation_id']]
        left, right = STAGES[edge['stage']]
        ref = alias('allocation', edge['allocation_id'])
        if edge['status'] in ('verified_receipt', 'verified_return'):
            verified_contributors.setdefault(edge['to_currency'], []).append(ref)
        ctx = context(original)
        states = [ctx['freshness'], object_states[(left, edge['from_id'])], object_states[(right, edge['to_id'])]]
        fx_refs = evidence_refs(original, 'fx_evidence_refs')
        if fx_refs:
            states.append(common.freshness(fx_refs, evidence))
        for adjustment in original.get('adjustments', []):
            adj_ctx = context(adjustment)
            states.append(adj_ctx['freshness'])
            schedules['adjustments'].append({'allocation_ref': ref, 'adjustment_ref': alias('adjustment', [edge['allocation_id'], adjustment['adjustment_id']]),
                'kind': adjustment['kind'], 'amount': format(amount(adjustment['amount']), 'f'), 'currency': adjustment['currency'], **adj_ctx})
        schedules['allocations'].append({'allocation_ref': ref, 'stage': edge['stage'], 'in_completion_scope': edge['stage'] in scope,
            'from_record_ref': alias(left, edge['from_id']), 'to_record_ref': alias(right, edge['to_id']),
            **{key: edge[key] for key in ('from_amount', 'from_currency', 'to_amount', 'to_currency', 'fx_rate', 'adjustments', 'status')},
            'evidence_refs': ctx['evidence_refs'], 'fx_evidence_refs': [common.alias('evidence', value) for value in fx_refs],
            'freshness': state(states), 'calculation_basis': 'to_amount = from_amount * fx_rate + adjustments (receiving currency)'})
    for row in result['residuals']:
        record_type = STAGES[row['stage']][0 if row['side'] == 'from' else 1]
        schedules['residuals'].append({**{key: row[key] for key in ('stage', 'side', 'currency', 'amount', 'allocated', 'unallocated')},
            'record_ref': alias(record_type, row['id']), 'in_completion_scope': row['stage'] in scope})
    for currency, value in result['verified_receipts_by_currency'].items():
        schedules['verified-receipts'].append({'currency': currency, 'amount': value,
            'basis': 'signed net of supplied verified_receipt and verified_return allocations; not recovery',
            'allocation_refs': verified_contributors[currency]})
    for item in result['unresolved']:
        original = inputs[item['allocation_id']]
        stage = original.get('stage')
        schedules['unresolved'].append({'allocation_ref': alias('allocation', item['allocation_id']),
            'stage': stage if isinstance(stage, str) and stage in STAGES else 'unsupported_or_unknown',
            'status': 'manual_review_required', 'amount': None, 'freshness': 'unknown',
            'reason': 'See matching allocation in hash-bound private result; private error prose excluded'})
    schedules['evidence'] = list(evidence.values())
    overall = common.freshness(all_refs, evidence)
    access = result['receiving_account_access']
    controls = {'schema_version': '1', 'stage': 'statement_remittance_receipt', 'as_of': as_of,
        'calculation_check': 'matches_recomputed_input', 'result_status': result['status'],
        'readiness': 'incomplete' if result['status'] != 'ok' else 'calculated_scope_only_source_review_required',
        'completion_scope': scope, 'missing_required_stages': result['missing_required_stages'],
        'unmatched_required_records': result['unmatched_required_records'],
        'unverified_allocation_refs': [alias('allocation', value) for value in result['unverified_allocation_ids']],
        'current_payable': None, 'recovered_cash': None, 'recovery_rollup': 'not_calculated',
        'source_control': 'not_verified_by_exporter', 'freshness': overall,
        'receiving_account_access': access if access in ('unknown', 'supplied_statement_only') else 'other_supplied_description',
        'receiving_account_access_ref': alias('access_description', access),
        'input_sha256': input_hash, 'result_sha256': result_hash, 'evidence_inventory_sha256': evidence_hash,
        'arithmetic_limits': result['arithmetic_limits']}
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise ValueError('Output destination already exists; choose a new version')
    output.mkdir(parents=True, mode=0o700)
    def write(name, text):
        with (output / name).open('x', encoding='utf-8') as stream:
            os.chmod(output / name, 0o600)
            stream.write(text)
    try:
        write('workpaper.json', dumps({'controls': controls, 'schedules': schedules}))
        for name, rows in schedules.items():
            with (output / (name + '.csv')).open('x', newline='', encoding='utf-8') as stream:
                os.chmod(output / (name + '.csv'), 0o600)
                writer = csv.DictWriter(stream, fieldnames=FIELDS[name])
                writer.writeheader()
                for row in rows:
                    writer.writerow({key: common.cell(value) for key, value in row.items()})
        report = ['# Statement, remittance and receipt workpaper', '',
            f"As of: {as_of}. Calculator status: {result['status']}. Supplied evidence freshness: {overall}.",
            'Requested stages: ' + ', '.join(scope) + '.',
            'Missing requested stages: ' + (', '.join(result['missing_required_stages']) or 'none') + '.',
            f"Unmatched required residual entries: {result['unmatched_required_records']}. Unverified allocations: {len(result['unverified_allocation_ids'])}.",
            'Current payable and newly recovered cash: unknown. Source authenticity and account access are not verified.', '',
            '| Schedule | Rows |', '|---|---:|']
        report += [f'| {name}.csv | {len(rows)} |' for name, rows in schedules.items()]
        report += ['', 'Verified net amounts by currency from supplied evidence (not newly recovered money):']
        report += [f"- {row['currency']}: {row['amount']}" for row in schedules['verified-receipts']] or ['- None supplied; this is not an observed zero.']
        report += ['', 'Use workpaper.json for exact decimal strings and null unknowns. CSV formula guards are display-only.',
            'Statement, remittance and receipt amounts describe successive stages of the same funds; never add stages or currencies.',
            'Adjustment totals are already included in allocation to_amount. Adjustment detail is explanatory, never additional money.',
            'Verified returns remain signed negative allocations. Posted user-reported receipts remain unverified.',
            'Unmatched residuals are not debt. Repeated residual records across stages are not additional earnings or recoveries.',
            'Totals list their exact contributing verified allocation aliases; each allocation links its source records, FX and adjustment evidence.',
            'Statement periods live on records. Follow allocation links to those periods; receipt dates are not earning periods.',
            'Empty schedules, unknown freshness, missing stages and partial results are not passed checks. An ok result covers only requested calculator scope.',
            'Hash aliases resolve against private hash-bound inputs. Source names, account references, locations, originals and error prose are excluded.',
            'Financial values and aliases remain private. Review does not authorize sharing, provider actions, publication or money movement.', '']
        write('report.md', '\n'.join(report))
        manifest = {**controls, 'originals_included': False, 'identifier_projection': 'typed_json_sha256; evidence uses utf8_sha256',
            'calculator_sha256': common.digest((HERE / 'reconcile-remittances.py').read_bytes()),
            'finance_primitives_sha256': common.digest((HERE / '_finance.py').read_bytes()),
            'export_contract_sha256': common.digest((HERE / 'build-royalty-workpaper.py').read_bytes()),
            'exporter_sha256': common.digest(Path(__file__).read_bytes()),
            'files': [{'file': p.name, 'sha256': common.digest(p.read_bytes())} for p in sorted(output.iterdir())]}
        write('manifest.json', dumps(manifest))
        return manifest
    except BaseException:
        shutil.rmtree(output)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--result', required=True)
    parser.add_argument('--output-directory', required=True)
    parser.add_argument('--as-of', required=True)
    parser.add_argument('--evidence')
    args = parser.parse_args()
    try:
        print(dumps(build(args.input, args.result, args.output_directory, args.as_of, args.evidence)), end='')
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        parser.exit(2, 'build-remittance-workpaper: input/result validation or output write failed; inspect private inputs and choose a new destination\n')


if __name__ == '__main__':
    main()
