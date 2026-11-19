"""Typed, private projection of the published normalization workpaper wire contract."""
import re
from _catalog_handoff_schema import digest, field as shared_field, require

HELPERS = ('normalize-royalty-statement.py', 'validate-normalized-ledger.py',
           'build-royalty-workpaper.py', '_finance.py', '_normalization_workpaper_io.py',
           '_royalty_archive.py', 'build-normalization-workpaper.py')
CONTROLS = ('schema_version', 'stage', 'as_of', 'receipt_status_supplied', 'controls_status_supplied',
    'ledger_control_status_supplied', 'appended_supplied', 'artifact_consistency', 'readiness',
    'freshness', 'source_authenticity', 'full_ledger_financial_controls', 'current_rights',
    'recovered_cash', 'recovery_rollup', 'ledger_validator_status', 'ledger_held_rows',
    'ledger_error_sample_count', 'source_version_ref', 'transform_ref', 'parser_ref',
    'receipt_sha256', 'ledger_sha256', 'row_receipt_sha256', 'original_source_sha256',
    'additional_controls_sha256', 'historical_receipt_to_ledger_byte_binding')
CLASSES = ('detail', 'held', 'control', 'footer', 'ignored', 'duplicate')
NUMERIC = ('gross_amount', 'owner_net_amount', 'deductions')
ENUMS = {
    'schema_version': ('1',), 'stage': ('normalization_import_controls',),
    'receipt_status_supplied': ('ok', 'partial'),
    'controls_status_supplied': ('matched', 'mismatch', 'unavailable'),
    'ledger_control_status_supplied': ('requires_duplicate_review', 'not_independently_controlled'),
    'artifact_consistency': ('mismatch', 'no_detected_mismatch_within_supported_checks'),
    'readiness': ('review_required',), 'freshness': ('unknown',),
    'source_authenticity': ('not_verified',), 'full_ledger_financial_controls': ('unknown',),
    'current_rights': ('unknown',), 'recovery_rollup': ('not_calculated',),
    'ledger_validator_status': ('ok', 'errors_found'),
    'historical_receipt_to_ledger_byte_binding': ('not_provided_by_normalizer; current supplied bytes hashed here',),
    'disposition': CLASSES, 'row_status': ('ready', 'held', 'unsupported'),
    'provenance_check': ('consistent', 'mismatch'), 'field': NUMERIC,
    'basis': ('source_detail_supplied', 'newly_written_only'),
    'metric': ('source_rows', 'written_rows', 'receipt_rows', 'ledger_total_rows', 'ledger_scope_rows',
               'economic_duplicate_rows', 'duplicate_held_rows') + CLASSES,
    'status': ('unknown_not_supplied', 'matches', 'mismatch', 'not_recomputed', 'unknown_not_bound_by_receipt',
               'not_applicable', 'not_verified', 'consistent', 'no_observed_amounts',
               'matches_supplied_claims_only', 'unavailable', 'ok', 'errors_found'),
}
CHECKS = {
    'counts': ('matches', 'mismatch', 'not_recomputed'),
    'totals': ('not_recomputed', 'matches', 'mismatch', 'unsupported_association_or_value'),
    'checks': ('original_source_bytes', 'source_totals', 'append_baseline',
        'source_authenticity_current_rights_and_completeness', 'row_receipt_identity',
        'written_row_association', 'written_totals', 'additional_controls_vs_supplied_source_totals',
        'existing_ledger_validator'),
}
CHECK_STATES = {
    'original_source_bytes': ('unknown_not_supplied', 'matches', 'mismatch'),
    'source_totals': ('not_recomputed',),
    'append_baseline': ('unknown_not_bound_by_receipt', 'not_applicable'),
    'source_authenticity_current_rights_and_completeness': ('not_verified',),
    'row_receipt_identity': ('consistent', 'mismatch'),
    'written_row_association': ('consistent', 'mismatch'),
    'written_totals': ('mismatch', 'no_observed_amounts'),
    'additional_controls_vs_supplied_source_totals': ('mismatch', 'matches_supplied_claims_only', 'unavailable'),
    'existing_ledger_validator': ('ok', 'errors_found'),
}

SCOPES = {
    'counts': ('row receipt', 'row receipt detail plus held', 'entire supplied ledger count only',
        'nonappend has only new rows; append baseline not independently known', 'row receipt disposition',
        'row receipts do not distinguish all duplicate subtypes or prove baseline'),
    'checks': ('explicitly supplied source bytes only; not authenticity',
        'source transformation/mapping and original source controls not replayed',
        'prior ledger bytes, totals and authority are not controlled by this import',
        'no account/provider access or rights conclusion',
        'source version, sheet, position and deterministic row identity',
        'new detail/held row identities only; not baseline integrity',
        'invalid nonempty value in newly written row; no observed total can be established',
        'empty is not an observed zero or passed source control',
        'existing validator against supplied receipt totals; not independently recomputed source or historical controls binding',
        'no additional controls supplied',
        'entire supplied ledger shape/values, not source controls, authenticity or rights'),
}
REFS = {'row_ref': 'row', 'line_ref': 'line', 'source_version_ref': 'source_version',
        'sheet_ref': 'sheet', 'currency_ref': 'currency', 'transform_ref': 'transform', 'parser_ref': 'parser',
        'reason_refs': 'reason', 'line_refs': 'line', 'evidence_refs': 'evidence'}


def reference(value, kind):
    require(isinstance(value, str) and value.startswith(kind + ':'))
    digest(value[len(kind) + 1:])


def project(record, fields, reason_codes, schedule=None):
    require(isinstance(record, dict) and all(key in record for key in fields))
    result = {}
    for key in fields:
        value = record[key]
        if key in REFS:
            values = value if key.endswith('_refs') else [value]
            require(isinstance(values, list) and len(values) <= 10000)
            for ref in values:
                reference(ref, REFS[key])
        elif key.endswith('_sha256'):
            require(value is not None or key in ('original_source_sha256', 'additional_controls_sha256'))
            if value is not None:
                digest(value)
        elif key in ('as_of', 'period_start', 'period_end'):
            shared_field(key, value)
        elif key in NUMERIC + ('supplied_amount', 'observed_amount'):
            require(value is None or (isinstance(value, str) and re.fullmatch(r'-?\d+(?:\.\d+)?', value) is not None))
            shared_field('amount', value)
        elif key == 'currency':
            require(value is None or (isinstance(value, str) and re.fullmatch('[A-Z]{3}', value) is not None))
        elif key in ('source_row', 'supplied', 'observed', 'ledger_held_rows', 'ledger_error_sample_count'):
            require((key == 'observed' and value is None) or (type(value) is int and value >= 0))
        elif key == 'appended_supplied':
            require(type(value) is bool)
        elif key == 'recovered_cash':
            require(value is None)
        elif key in ('reason_codes', 'field_issues'):
            allowed = set(reason_codes) | {'other_private_reason'} if key == 'reason_codes' else {
                'period_start:unknown_or_invalid', 'period_end:unknown_or_invalid',
                *(name + ':' + state for name in NUMERIC for state in ('unknown', 'invalid'))}
            require(isinstance(value, list) and len(value) <= 64)
            require(all(isinstance(item, str) and item in allowed for item in value))
        elif key in ('check', 'scope'):
            allowed = (CHECKS if key == 'check' else SCOPES).get(schedule, ())
            require(isinstance(value, str) and value in allowed)
        else:
            require(key in ENUMS and isinstance(value, str) and value in ENUMS[key])
        result[key] = value
    if schedule == 'checks':
        require(result['status'] in CHECK_STATES[result['check']])
    elif schedule == 'counts':
        supplied_only = result['metric'] in ('economic_duplicate_rows', 'duplicate_held_rows')
        require((result['observed'] is None and result['check'] == 'not_recomputed') if supplied_only else
                (type(result['observed']) is int and result['check'] in ('matches', 'mismatch')))
    elif schedule == 'totals':
        if result['basis'] == 'source_detail_supplied':
            require(result['observed_amount'] is None and not result['line_refs'] and result['check'] == 'not_recomputed')
        else:
            require(result['check'] in ('matches', 'mismatch', 'unsupported_association_or_value'))
            if result['check'] == 'unsupported_association_or_value':
                require(result['observed_amount'] is None and not result['line_refs'])
    elif schedule == 'rows':
        require(len(result['reason_codes']) == len(result['reason_refs']))
    return result
