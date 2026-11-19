#!/usr/bin/env python3
"""Project one existing normalizer receipt, row receipt and ledger into a private workpaper."""
import argparse
from collections import Counter, defaultdict
import csv
from decimal import Decimal
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from _finance import amount, dumps, iso_date
import _normalization_workpaper_io as bounded

HERE = Path(__file__).resolve().parent


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


common = load('normalization_export_common', 'build-royalty-workpaper.py')
normalizer = load('normalization_export_normalizer', 'normalize-royalty-statement.py')
validator = load('normalization_export_validator', 'validate-normalized-ledger.py')
CLASSES = ('detail', 'held', 'control', 'footer', 'ignored', 'duplicate')
NUMERIC = ('gross_amount', 'owner_net_amount', 'deductions')
REASON_CODES = {'source:held', 'unknown:row_class', 'malformed:columns',
                'overlap:revised_transaction_requires_resolution', 'invalid:period_order'}
REASON_CODES.update(prefix + field for prefix in ('missing:', 'invalid:')
                    for field in normalizer.REQUIRED_VALUES + ('gross_amount', 'deductions', 'payment_date', 'report_date'))
FIELDS = {
    'rows': ('row_ref', 'line_ref', 'source_version_ref', 'sheet_ref', 'source_row', 'disposition', 'reason_codes', 'reason_refs'),
    'written-lines': ('line_ref', 'row_ref', 'row_status', 'currency', 'currency_ref', 'period_start', 'period_end',
                      'gross_amount', 'owner_net_amount', 'deductions', 'field_issues', 'provenance_check'),
    'counts': ('metric', 'supplied', 'observed', 'check', 'scope'),
    'totals': ('basis', 'currency', 'currency_ref', 'field', 'supplied_amount', 'observed_amount', 'check', 'line_refs'),
    'checks': ('check', 'status', 'scope', 'evidence_refs'),
}


def alias(kind, value):
    return common.alias(kind, json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False))


def read_json(raw):
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise ValueError('Duplicate JSON key')
            out[key] = value
        return out
    def invalid(value):
        raise ValueError('Nonfinite JSON value')
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


def count(value):
    if type(value) is not int or value < 0:
        raise ValueError('Counts require nonnegative JSON integers')
    return value


def digest(value):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{64}', value):
        raise ValueError('Expected SHA256 version')
    return value


def totals_map(rows):
    if not isinstance(rows, list):
        raise ValueError('Totals require a list')
    result = {}
    for row in rows:
        currency, field, value = row['currency'], row['field'], row['amount']
        if not isinstance(currency, str) or field not in NUMERIC or not isinstance(value, str) or not re.fullmatch(r'-?\d+(?:\.\d+)?', value):
            raise ValueError('Unsupported total shape')
        if (currency, field) in result:
            raise ValueError('Duplicate currency/field total')
        result[(currency, field)] = value
    return result


def safe_currency(value):
    return value if isinstance(value, str) and re.fullmatch(r'[A-Z]{3}', value) else None


def project(receipt, rowlog, ledger, source_hash=None, controls=None, controls_supplied=False):
    """Compare existing artifacts; never import sources or infer append baseline controls."""
    if receipt['parser_version'] != normalizer.PARSER_VERSION:
        raise ValueError('Unsupported normalizer version')
    version, transform = digest(receipt['source_version_id']), digest(receipt['transform_id'])
    if type(receipt['appended']) is not bool or not isinstance(receipt['source_sheet'], str):
        raise ValueError('Unsupported receipt shape')
    enums = {'status': ('ok', 'partial'), 'controls_status': ('matched', 'mismatch', 'unavailable'),
             'ledger_control_status': ('requires_duplicate_review', 'not_independently_controlled')}
    for key, allowed in enums.items():
        if receipt[key] not in allowed:
            raise ValueError('Unsupported receipt status')
    supplied_counts = receipt['row_conservation']
    if not isinstance(supplied_counts, dict):
        raise ValueError('Counts require an object')
    for value in supplied_counts.values(): count(value)
    for key in ('rows', 'ledger_total_rows'): count(receipt[key])
    source_totals, written_totals = totals_map(receipt['source_totals']), totals_map(receipt['written_totals'])
    schedules = {key: [] for key in FIELDS}
    def check(name, status, scope, refs=()):
        schedules['checks'].append({'check': name, 'status': status, 'scope': scope, 'evidence_refs': list(refs)})
    check('original_source_bytes', 'unknown_not_supplied' if source_hash is None else 'matches' if source_hash == version else 'mismatch', 'explicitly supplied source bytes only; not authenticity')
    check('source_totals', 'not_recomputed', 'source transformation/mapping and original source controls not replayed')
    check('append_baseline', 'unknown_not_bound_by_receipt' if receipt['appended'] else 'not_applicable', 'prior ledger bytes, totals and authority are not controlled by this import')
    check('source_authenticity_current_rights_and_completeness', 'not_verified', 'no account/provider access or rights conclusion')
    by_id, observed_counts = {}, Counter()
    association_ok = True
    for row in rowlog:
        disposition = row['disposition']
        if disposition not in CLASSES or not isinstance(row['ledger_line_id'], str):
            raise ValueError('Unsupported row receipt')
        position = count(row['source_row'])
        identity = row['ledger_line_id']
        if identity in by_id:
            raise ValueError('Duplicate row receipt identity')
        expected_id = 'RL-' + hashlib.sha256(f"{version}:{receipt['source_sheet']}:{position}".encode()).hexdigest()
        matches = row['source_version_id'] == version and row['source_sheet'] == receipt['source_sheet'] and identity == expected_id
        association_ok = association_ok and matches
        reasons = row['reasons']
        if not isinstance(reasons, list): raise ValueError('Reasons require a list')
        ref = alias('row', [version, receipt['source_sheet'], position])
        by_id[identity] = row
        schedules['rows'].append({'row_ref': ref, 'line_ref': alias('line', identity), 'source_version_ref': alias('source_version', version),
            'sheet_ref': alias('sheet', row['source_sheet']), 'source_row': position, 'disposition': disposition,
            'reason_codes': [value if isinstance(value, str) and value in REASON_CODES else 'other_private_reason' for value in reasons],
            'reason_refs': [alias('reason', value) for value in reasons]})
        observed_counts[disposition] += 1
    check('row_receipt_identity', 'consistent' if association_ok else 'mismatch', 'source version, sheet, position and deterministic row identity')
    new_ids = {key for key, row in by_id.items() if row['disposition'] in ('detail', 'held')}
    reader = bounded.ledger_rows(ledger, normalizer.CANONICAL_COLUMNS)
    found = Counter(); observed_totals = defaultdict(Decimal); contributors = defaultdict(list)
    ledger_count = 0; provenance_ok = association_ok; amounts_ok = True
    for row in reader:
        ledger_count += 1
        identity = row['ledger_line_id']
        if identity not in new_ids: continue
        if len(schedules['written-lines']) >= bounded.MAX_CURRENT_ROWS:
            raise ValueError('Too many retained written rows')
        found[identity] += 1
        original = by_id[identity]
        expected_status = 'ready' if original['disposition'] == 'detail' else 'held'
        matches = (row['source_version_id'] == version and row['transform_id'] == transform and
                   row['parser_version'] == receipt['parser_version'] and row['source_sheet'] == receipt['source_sheet'] and
                   row['source_row'] == str(original['source_row']) and row['row_status'] == expected_status)
        provenance_ok = provenance_ok and matches
        line_ref = alias('line', identity)
        item = {'line_ref': line_ref, 'row_ref': alias('row', [version, receipt['source_sheet'], original['source_row']]),
                'row_status': row['row_status'] if row['row_status'] in ('ready', 'held') else 'unsupported',
                'currency': safe_currency(row['currency']), 'currency_ref': alias('currency', row['currency']),
                'field_issues': [], 'provenance_check': 'consistent' if matches else 'mismatch'}
        for key in ('period_start', 'period_end'):
            try: item[key] = iso_date(row[key], key).isoformat()
            except ValueError:
                item[key] = None; item['field_issues'].append(key + ':unknown_or_invalid')
        for field in NUMERIC:
            value = row[field]
            item[field] = None
            if value:
                try:
                    parsed = amount(value)
                    item[field] = format(parsed, 'f')
                    key = (row['currency'] or 'UNKNOWN', field)
                    observed_totals[key] += parsed
                    contributors[key].append(line_ref)
                except ValueError:
                    amounts_ok = False; item['field_issues'].append(field + ':invalid')
            else: item['field_issues'].append(field + ':unknown')
        schedules['written-lines'].append(item)
    joins_ok = all(found[key] == 1 for key in new_ids)
    totals_supported = joins_ok and provenance_ok and amounts_ok
    check('written_row_association', 'consistent' if joins_ok and provenance_ok else 'mismatch', 'new detail/held row identities only; not baseline integrity')
    expected_total_count = len(new_ids) if not receipt['appended'] else receipt['ledger_total_rows']
    metrics = [('source_rows', supplied_counts.get('source_rows', 0), len(rowlog), 'row receipt'),
               ('written_rows', supplied_counts.get('written_rows', 0), len(new_ids), 'row receipt detail plus held'),
               ('receipt_rows', receipt['rows'], len(new_ids), 'row receipt detail plus held'),
               ('ledger_total_rows', receipt['ledger_total_rows'], ledger_count, 'entire supplied ledger count only'),
               ('ledger_scope_rows', expected_total_count, ledger_count, 'nonappend has only new rows; append baseline not independently known')]
    metrics += [(name, supplied_counts.get('duplicate_rows' if name == 'duplicate' else name, 0), observed_counts[name], 'row receipt disposition') for name in CLASSES]
    for name, claimed, observed, scope in metrics:
        schedules['counts'].append({'metric': name, 'supplied': claimed, 'observed': observed,
            'check': 'matches' if claimed == observed else 'mismatch', 'scope': scope})
    for name in ('economic_duplicate_rows', 'duplicate_held_rows'):
        schedules['counts'].append({'metric': name, 'supplied': supplied_counts.get(name, 0), 'observed': None,
            'check': 'not_recomputed', 'scope': 'row receipts do not distinguish all duplicate subtypes or prove baseline'})
    for (currency, field), value in source_totals.items():
        schedules['totals'].append({'basis': 'source_detail_supplied', 'currency': safe_currency(currency), 'currency_ref': alias('currency', currency),
            'field': field, 'supplied_amount': value, 'observed_amount': None, 'check': 'not_recomputed', 'line_refs': []})
    for key in sorted(set(written_totals) | set(observed_totals)):
        currency, field = key; claimed = written_totals.get(key)
        observed = format(observed_totals[key], 'f') if totals_supported and key in observed_totals else None
        status = 'unsupported_association_or_value' if not totals_supported else 'matches' if claimed is not None and observed is not None and Decimal(claimed) == Decimal(observed) else 'mismatch'
        schedules['totals'].append({'basis': 'newly_written_only', 'currency': safe_currency(currency), 'currency_ref': alias('currency', currency),
            'field': field, 'supplied_amount': claimed, 'observed_amount': observed, 'check': status,
            'line_refs': contributors[key] if totals_supported else []})
    if not amounts_ok:
        check('written_totals', 'mismatch', 'invalid nonempty value in newly written row; no observed total can be established')
    elif not written_totals and not observed_totals:
        check('written_totals', 'no_observed_amounts', 'empty is not an observed zero or passed source control')
    if controls_supplied:
        errors = normalizer.validate_source_controls(controls, {k: Decimal(v) for k, v in source_totals.items()})
        refs = controls.get('evidence_refs', []) if isinstance(controls, dict) else []
        check('additional_controls_vs_supplied_source_totals', 'mismatch' if errors else 'matches_supplied_claims_only',
              'existing validator against supplied receipt totals; not independently recomputed source or historical controls binding',
              [alias('evidence', v) for v in refs] if isinstance(refs, list) else [])
    else: check('additional_controls_vs_supplied_source_totals', 'unavailable', 'no additional controls supplied')
    return schedules


def build(receipt_path, ledger_path, row_receipt_path, output, as_of, source_path=None, controls_path=None):
    as_of = iso_date(as_of, 'as_of').isoformat()
    receipt_raw = bounded.read_small(receipt_path)
    receipt = read_json(receipt_raw)
    rows, row_hash = bounded.read_rows(row_receipt_path, read_json)
    controls_raw = bounded.read_small(controls_path) if controls_path else None
    source_hash = bounded.copy_hash(source_path) if source_path else None
    with tempfile.TemporaryDirectory(prefix='normalization-workpaper-check-') as directory:
        path = Path(directory) / 'ledger.csv'
        with path.open('xb') as stream:
            os.chmod(path, 0o600)
            ledger_hash = bounded.copy_hash(ledger_path, stream)
        schedules = project(receipt, rows, path, source_hash, read_json(controls_raw) if controls_raw is not None else None, controls_raw is not None)
        validation = validator.validate(path)
    schedules['checks'].append({'check': 'existing_ledger_validator', 'status': validation['status'],
        'scope': 'entire supplied ledger shape/values, not source controls, authenticity or rights', 'evidence_refs': []})
    mismatch = any(row.get('check') in ('mismatch', 'unsupported_association_or_value') for name in ('counts', 'totals') for row in schedules[name]) or any(row['status'] == 'mismatch' for row in schedules['checks'])
    control = {'schema_version': '1', 'stage': 'normalization_import_controls', 'as_of': as_of,
        'receipt_status_supplied': receipt['status'], 'controls_status_supplied': receipt['controls_status'],
        'ledger_control_status_supplied': receipt['ledger_control_status'], 'appended_supplied': receipt['appended'],
        'artifact_consistency': 'mismatch' if mismatch else 'no_detected_mismatch_within_supported_checks',
        'readiness': 'review_required', 'freshness': 'unknown', 'source_authenticity': 'not_verified',
        'full_ledger_financial_controls': 'unknown', 'current_rights': 'unknown', 'recovered_cash': None,
        'recovery_rollup': 'not_calculated', 'ledger_validator_status': validation['status'],
        'ledger_held_rows': validation['held_rows'], 'ledger_error_sample_count': len(validation['errors']),
        'source_version_ref': alias('source_version', receipt['source_version_id']),
        'transform_ref': alias('transform', receipt['transform_id']), 'parser_ref': alias('parser', receipt['parser_version']),
        'receipt_sha256': common.digest(receipt_raw), 'ledger_sha256': ledger_hash, 'row_receipt_sha256': row_hash,
        'original_source_sha256': source_hash, 'additional_controls_sha256': common.digest(controls_raw) if controls_raw is not None else None,
        'historical_receipt_to_ledger_byte_binding': 'not_provided_by_normalizer; current supplied bytes hashed here'}
    output = Path(output)
    if output.exists() or output.is_symlink(): raise ValueError('Choose a new output version')
    output.mkdir(parents=True, mode=0o700)
    def write(name, text):
        with (output / name).open('x', encoding='utf-8') as stream:
            os.chmod(output / name, 0o600); stream.write(text)
    try:
        write('workpaper.json', dumps({'controls': control, 'schedules': schedules}))
        for name, records in schedules.items():
            with (output / (name + '.csv')).open('x', newline='', encoding='utf-8') as stream:
                os.chmod(output / (name + '.csv'), 0o600)
                writer = csv.DictWriter(stream, fieldnames=FIELDS[name]); writer.writeheader()
                for row in records: writer.writerow({key: common.cell(value) for key, value in row.items()})
        report = ['# Normalization and import-controls workpaper', '',
            f"As of: {as_of}. Supplied import status: {receipt['status']}. Supplied source controls: {receipt['controls_status']}.",
            f"Artifact consistency: {control['artifact_consistency']}. Existing ledger validator: {validation['status']}.",
            f"Supplied append flag: {receipt['appended']}. Freshness, authenticity, current rights and full-ledger financial controls remain unknown/unverified.", '',
            'Row conservation compares supplied counts to row-receipt dispositions, not to independently parsed original source rows.',
            'Written totals are recomputed only for newly written detail/held rows joined by identity and provenance. Held values are not eligible earnings.',
            'Source totals and duplicate subtypes remain supplied claims. Additional controls compare only to those supplied source totals.',
            'An append receipt cannot control earlier ledger amounts or prove baseline bytes. No prior-ledger monetary total is emitted.',
            'Receipt paths are never followed. Explicit source bytes, if supplied, are hashed only, not imported or authenticated.', '',
            '| Schedule | Rows |', '|---|---:|']
        report += [f'| {name}.csv | {len(records)} |' for name, records in schedules.items()]
        report += ['', 'Unknown/held/duplicate/mismatch/unavailable states remain open review items. An ok parser or populated field does not establish completeness.',
            'Source and written totals overlap; never add them or combine currencies as income or recovery. No new payable or recovered cash is inferred.',
            'Exact JSON values and null unknowns are authoritative; CSV formula guards are display-only. Empty schedules are not passed controls.',
            'Aliases link rows, source version and transform to the private hash-bound inputs. Raw names/accounts/paths/headers/warnings/raw_values are excluded.',
            'Financial data and aliases remain private. Report review authorizes no sharing, imports, provider actions or money movement.', '']
        write('report.md', '\n'.join(report))
        dependencies = ['normalize-royalty-statement.py', 'validate-normalized-ledger.py', 'build-royalty-workpaper.py', '_finance.py', '_normalization_workpaper_io.py', '_royalty_archive.py', Path(__file__).name]
        manifest = {**control, 'originals_included': False, 'helper_hashes': {name: common.digest((HERE/name).read_bytes()) for name in dependencies},
                    'files': [{'file': path.name, 'sha256': common.digest(path.read_bytes())} for path in sorted(output.iterdir())]}
        write('manifest.json', dumps(manifest)); return manifest
    except BaseException:
        shutil.rmtree(output); raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ('receipt', 'ledger', 'row-receipt', 'output-directory', 'as-of'): parser.add_argument('--' + flag, required=True)
    parser.add_argument('--source'); parser.add_argument('--controls')
    args = parser.parse_args()
    try: print(dumps(build(args.receipt, args.ledger, args.row_receipt, args.output_directory, args.as_of, args.source, args.controls)), end='')
    except (OSError, ValueError, KeyError, TypeError, AttributeError, csv.Error, RecursionError):
        parser.exit(2, 'build-normalization-workpaper: unsupported input or output failure; inspect private originals without replacing them\n')


if __name__ == '__main__': main()
