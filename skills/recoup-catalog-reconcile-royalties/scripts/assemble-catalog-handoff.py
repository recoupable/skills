#!/usr/bin/env python3
"""Assemble explicitly selected, hash-pinned local exports into a private handoff."""
import argparse
import csv
import hashlib
import importlib.util
import io
import json
import os
from decimal import Decimal, InvalidOperation
from pathlib import Path
import shutil

from _catalog_handoff_schema import CONTROLS, digest, project, require
import _normalization_handoff as normalization_contract

HERE = Path(__file__).resolve().parent
MAX_FILE = 16 * 1024 * 1024
MAX_TOTAL = 128 * 1024 * 1024
MAX_ROWS = 10000


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


royalty = load('build-royalty-workpaper')
remittance = load('build-remittance-workpaper')
case_export = load('build-catalog-report')
case_contract = load('catalog-case')
normalization = load('build-normalization-workpaper')
SCOPES = ('case', 'entitlement', 'remittance', 'normalization')
SCHEDULES = {'case': {name: case_export.FIELDS for name in case_export.COLLECTIONS},
             'entitlement': royalty.SCHEDULE_FIELDS, 'remittance': remittance.FIELDS,
             'normalization': normalization.FIELDS}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def no_links(path):
    require(not any(p.is_symlink() for p in (path, *path.parents)))


def physical(path):
    supplied = Path(path).absolute()
    # Check supplied spelling first: resolving must never hide a linked component.
    no_links(supplied)
    require(supplied.parent.is_dir())
    resolved = supplied.resolve(strict=False)
    no_links(resolved)
    return resolved


def read(path, budget, limit=MAX_FILE):
    path = physical(path)
    require(path.is_file() and path.stat().st_size <= limit)
    with path.open('rb') as stream:
        raw = stream.read(limit + 1)
    budget[0] += len(raw)
    require(len(raw) <= limit and budget[0] <= MAX_TOTAL)
    return raw


def parse(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result)
            result[key] = value
        return result
    def bad(value):
        raise ValueError('Unsupported JSON numeric token')
    def exact_float(token):
        require(len(token) <= 256)
        try:
            value = Decimal(token)
        except InvalidOperation:
            raise ValueError('Unsupported JSON numeric token') from None
        require(value.is_finite() and -128 <= value.as_tuple().exponent <= 128)
        return value
    def bounded_int(token):
        require(len(token) <= 256)
        return int(token)
    # Preserve finite private-extension tokens without binary rounding. Decimal
    # tokens are not accepted by the exact string/integer financial wire schema.
    data = json.loads(raw, object_pairs_hook=unique, parse_constant=bad, parse_float=exact_float, parse_int=bounded_int)
    def bounded(value, depth=0):
        require(depth <= 16)
        if isinstance(value, dict):
            require(len(value) <= 256)
            for key, child in value.items():
                require(len(key) <= 256)
                bounded(child, depth + 1)
        elif isinstance(value, list):
            require(len(value) <= MAX_ROWS)
            for child in value:
                bounded(child, depth + 1)
        elif isinstance(value, str):
            require(len(value) <= 65536)
    bounded(data)
    return data


def csv_rows(raw, fields):
    previous_limit = csv.field_size_limit(MAX_FILE)
    try:
        reader = csv.DictReader(io.StringIO(raw.decode('utf-8'), newline=''))
        require(reader.fieldnames == list(fields))
        rows = []
        for row in reader:
            require(len(rows) < MAX_ROWS and None not in row and all(v is not None for v in row.values()))
            rows.append(row)
        return rows
    except csv.Error:
        raise ValueError('Unsupported CSV input') from None
    finally:
        csv.field_size_limit(previous_limit)


def files(directory, manifest, names, budget):
    entries = manifest.get('files')
    require(isinstance(entries, list) and len(entries) == len(names))
    indexed = {}
    for item in entries:
        require(isinstance(item, dict) and item.get('file') in names and item['file'] not in indexed)
        indexed[item['file']] = digest(item.get('sha256'))
    require(set(indexed) == names)
    result = {}
    for name in sorted(names):
        raw = read(directory / name, budget)
        require(sha(raw) == indexed[name])
        result[name] = raw
    return result


def financial(kind, manifest, contents):
    fields = SCHEDULES[kind]
    pins = {'exporter_sha256': 'build-royalty-workpaper.py' if kind == 'entitlement' else 'build-remittance-workpaper.py',
            'calculator_sha256': 'calculate-entitlements.py' if kind == 'entitlement' else 'reconcile-remittances.py',
            'finance_primitives_sha256': '_finance.py'}
    if kind == 'remittance':
        pins['export_contract_sha256'] = 'build-royalty-workpaper.py'
    projector = lambda record, columns, schedule=None: project(record, columns)
    control_fields = CONTROLS.get(kind)
    if kind == 'normalization':
        helper_hashes = {name: sha((HERE / name).read_bytes()) for name in normalization_contract.HELPERS}
        require(manifest.get('helper_hashes') == helper_hashes)
        producer_hashes = helper_hashes
        projector = lambda record, columns, schedule=None: normalization_contract.project(record, columns, normalization.REASON_CODES, schedule)
        control_fields = normalization_contract.CONTROLS
    else:
        for key, name in pins.items():
            require(manifest.get(key) == sha((HERE / name).read_bytes()))
        producer_hashes = {key: manifest[key] for key in pins}
    require(manifest.get('originals_included') is False)
    payload = parse(contents['workpaper.json'])
    controls = projector(payload['controls'], control_fields)
    require(controls == projector(manifest, control_fields))
    require(controls['stage'] == {'entitlement': 'contractual_entitlement', 'remittance': 'statement_remittance_receipt',
                                  'normalization': 'normalization_import_controls'}[kind])
    schedules = payload['schedules']
    require(isinstance(schedules, dict) and set(schedules) == set(fields))
    selected = {}
    for name, columns in fields.items():
        require(isinstance(schedules[name], list) and len(schedules[name]) <= MAX_ROWS)
        rows = [projector(row, columns, name) for row in schedules[name]]
        expected = [{key: royalty.cell(value) for key, value in row.items()} for row in rows]
        require(csv_rows(contents[name + '.csv'], columns) == expected)
        selected[name] = rows
    return {'controls': controls, 'schedules': selected, 'producer_hashes': producer_hashes}, fields


def case_index(manifest, contents):
    require(type(manifest.get('schema_version')) is int and manifest['schema_version'] == 1)
    require(manifest.get('projection') == list(case_export.FIELDS))
    require(manifest.get('scope') == 'selected_case_records' and manifest.get('originals_included') is False)
    require(type(manifest.get('revision')) is int and manifest['revision'] >= 0)
    require(isinstance(manifest.get('case_id'), str))
    def alias(value):
        return 'case:' + sha(value.encode('utf-8')) if value else ''
    schedules = {}
    for group in case_export.COLLECTIONS:
        rows = csv_rows(contents[group + '.csv'], case_export.FIELDS)
        projected = []
        for row in rows:
            item = {}
            for key, value in row.items():
                # Legacy CSV is lossy here: a literal apostrophe and an added
                # formula guard have identical wire bytes. Never guess identity.
                require(not (value.startswith("'") and value[1:].lstrip().startswith(('=', '+', '-', '@', '\t', '\r'))))
                if key in ('id', 'cause_id', 'action_id', 'rule_version', 'evidence_gap'):
                    item[key] = alias(value)
                elif key == 'source_refs':
                    refs = parse(value.encode()) if value else []
                    require(isinstance(refs, list))
                    item[key] = [{'source_id': alias(ref['source_id']), 'version': alias(ref['version'])} for ref in refs]
                elif key == 'depends_on':
                    refs = parse(value.encode()) if value else []
                    require(isinstance(refs, list))
                    item[key] = [alias(ref) for ref in refs]
                elif key == 'stage':
                    require(not value or value in case_contract.STAGES)
                    item[key] = value
                elif key == 'dimension':
                    require(not value or value in case_contract.OUTCOMES)
                    item[key] = value
                elif key == 'status':
                    allowed = case_contract.STATES.get(group, set().union(*case_contract.OUTCOMES.values()))
                    require(not value or value in allowed)
                    item[key] = value
                else:
                    require(key == 'stale' and value in ('', 'True', 'False'))
                    item[key] = None if not value else value == 'True'
            projected.append(item)
        schedules[group] = projected
    return {'controls': {'schema_version': 1, 'case_ref': alias(manifest['case_id']), 'revision': manifest['revision'],
            'case_sha256': digest(manifest.get('case_sha256')), 'scope': 'selected_case_records',
            'current_record_check': 'not_performed', 'evidence_gap_projection': 'opaque_reference'}, 'schedules': schedules}, {name: case_export.FIELDS for name in schedules}


def write(path, text):
    with path.open('x', encoding='utf-8', newline='') as stream:
        os.chmod(path, 0o600)
        stream.write(text)


def build(selection_path, output):
    budget = [0]
    raw = read(selection_path, budget, 65536)
    selection = parse(raw)
    require(selection.get('schema_version') == '1')
    entries = selection.get('exports')
    require(isinstance(entries, list) and 1 <= len(entries) <= len(SCOPES))
    output = physical(output)
    require(not output.exists() and output.parent.is_dir())
    prepared = {}
    for entry in entries:
        kind = entry.get('kind')
        require(kind in SCOPES and kind not in prepared)
        directory = physical(entry['directory'])
        require(directory.is_dir())
        require(not output.is_relative_to(directory) and not directory.is_relative_to(output))
        manifest_raw = read(directory / 'manifest.json', budget, 1024 * 1024)
        require(sha(manifest_raw) == digest(entry.get('manifest_sha256')))
        manifest = parse(manifest_raw)
        fields = SCHEDULES[kind]
        names = {name + '.csv' for name in fields} | {'report.md'} | (set() if kind == 'case' else {'workpaper.json'})
        contents = files(directory, manifest, names, budget)
        payload, fields = case_index(manifest, contents) if kind == 'case' else financial(kind, manifest, contents)
        prepared[kind] = (payload, fields, sha(manifest_raw))
    output.mkdir(mode=0o700)
    try:
        index = []
        for kind, (payload, fields, manifest_hash) in prepared.items():
            folder = output / kind
            folder.mkdir(mode=0o700)
            payload['input_manifest_sha256'] = manifest_hash
            write(folder / 'workpaper.json', royalty.dumps(payload))
            for name, rows in payload['schedules'].items():
                stream = io.StringIO(newline='')
                writer = csv.DictWriter(stream, fieldnames=fields[name])
                writer.writeheader()
                writer.writerows({key: royalty.cell(value) for key, value in row.items()} for row in rows)
                write(folder / (name + '.csv'), stream.getvalue())
            index.append({'kind': kind, 'workpaper': kind + '/workpaper.json', 'input_manifest_sha256': manifest_hash,
                          'controls': payload['controls'], 'schedules': {name: len(rows) for name, rows in payload['schedules'].items()}})
        handoff = {'schema_version': '1', 'selection_sha256': sha(raw), 'exports': index,
                   'excluded_stages': sorted(set(SCOPES) - set(prepared)),
                   'readiness': 'review_required', 'current_record_check': 'not_performed',
                   'cross_stage_money_rollup': 'not_calculated', 'originals_included': False,
                   'publication_authorized': False, 'assembler_sha256': sha(Path(__file__).read_bytes()),
                   'schema_contract_sha256': sha((HERE / '_catalog_handoff_schema.py').read_bytes())}
        if 'normalization' in prepared:
            handoff['normalization_contract_sha256'] = sha((HERE / '_normalization_handoff.py').read_bytes())
        write(output / 'handoff.json', royalty.dumps(handoff))
        report = ['# Selected catalog handoff', '', 'Private review artifact: CSV and exact JSON, not an XLSX workbook.',
                  'Read handoff.json, then each listed workpaper.json and its CSV schedules.',
                  'Input manifest hashes bind the supplied export snapshots; they do not authenticate sources or prove current records.',
                  'Use the hashes with the authorized private evidence inventory to locate original inputs and source versions.',
                  'No private paths or originals are included. The selection file stays private and is referenced only by hash.',
                  'Case identifiers and evidence-gap descriptions are opaque aliases. Resolve them against the hash-bound private case.',
                  'Case and financial exports are separate scopes; this assembly does not assert a relationship between their records.',
                  'Missing stages remain excluded, not passed. Held, unresolved, stale, rejected and unknown states retain their stage meanings.',
                  'Source dates and freshness are copied, never refreshed by assembly. Confirm current versions separately before relying on this snapshot.',
                  'No financial arithmetic is performed. Bridge steps, recoupment, statements, remittances and receipts are not additive recovery.',
                  'Report approval grants no publication, sharing, provider-action or payment authority.', '', '| Included scope | Exact record |', '|---|---|']
        report += [f"| {item['kind']} | [{item['workpaper']}]({item['workpaper']}) |" for item in index]
        report += ['', 'Excluded supported scopes: ' + (', '.join(handoff['excluded_stages']) or 'none') + '.',
                   'Normalization source and written totals overlap; held values are not eligible earnings. Never add these bases or prior-ledger amounts.',
                   'Append baseline financial controls and historical receipt-to-ledger byte binding remain unknown; assembly does not rerun any checks.',
                   'Other stage formats are unsupported in this version; never silently include them.', '']
        write(output / 'report.md', '\n'.join(report))
        manifest = {'schema_version': '1', 'scope': 'selected_catalog_handoff', 'files': [
            {'file': str(p.relative_to(output)), 'sha256': sha(p.read_bytes())} for p in sorted(output.rglob('*')) if p.is_file()]}
        write(output / 'manifest.json', royalty.dumps(manifest))
        return manifest
    except BaseException:
        shutil.rmtree(output)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--selection', required=True)
    parser.add_argument('--output-directory', required=True)
    args = parser.parse_args()
    try:
        build(args.selection, args.output_directory)
        print('Created private selected handoff; review required.')
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RecursionError):
        parser.exit(2, 'assemble-catalog-handoff: unsupported, changed or oversized input, or unavailable output; no completed handoff\n')


if __name__ == '__main__':
    main()
