"""Allowlisted wire projection for supported local financial workpapers (no math)."""
import re
from _finance import iso_date
from decimal import Decimal

FRESH = ('unknown', 'stale', 'current_as_supplied')
ENUMS = {
    'schema_version': ('1',), 'stage': ('contractual_entitlement', 'statement_remittance_receipt', 'statement_to_remittance', 'remittance_to_receipt', 'unsupported_or_unknown'),
    'freshness': FRESH, 'calculation_check': ('matches_recomputed_input',),
    'result_status': ('ok', 'partial'), 'source_control': ('not_verified_by_exporter',),
    'recovery_rollup': ('not_calculated',), 'calculation_status': ('calculated',),
    'basis': ('gross_amount', 'owner_net_amount', 'signed net of supplied verified_receipt and verified_return allocations; not recovery'),
    'commission_basis': ('participation',),
    'variance_direction': ('potential_underpayment', 'potential_overpayment_or_clawback', 'matched'),
    'operation': ('basis', 'participation', 'commission', 'deduction', 'reserve_withheld', 'withholding', 'reserve_released', 'reversal', 'recognized_adjustment'),
    'balance_as_of': ('unknown_not_supplied_by_calculator',),
    'calculation_basis': ('available=opening+movements; closing=max(0,available-earnings); payable=max(0,earnings-available)', 'to_amount = from_amount * fx_rate + adjustments (receiving currency)'),
    'status': ('manual_workpaper_required', 'manual_review_required', 'allocated_statement', 'verified_receipt', 'verified_return', 'user_reported_receipt_unverified'),
    'period': ('unknown_not_calculated',),
    'reason': ('See matching blocker in hash-bound private result; free text excluded', 'See matching allocation in hash-bound private result; private error prose excluded'),
    'record_type': ('statements', 'remittances', 'receipts'),
    'reported_status': ('Paid', 'posted', 'pending', 'returned', 'unknown_or_other'),
    'evidence_status': ('observed', 'unverified_or_unknown'),
    'kind': ('fee', 'withholding', 'supported_adjustment'), 'side': ('from', 'to'),
    'readiness': ('incomplete', 'calculated_scope_only_source_review_required'),
    'receiving_account_access': ('unknown', 'supplied_statement_only', 'other_supplied_description'),
    'rounding_policy': ('Exact supported arithmetic: inputs <=24 coefficient/integer digits and <=18 fractional places; <=10000 records per collection; Decimal precision 128. No per-row rounding.',),
    'arithmetic_limits': ('Inputs <=24 coefficient/integer digits and <=18 fractional places; <=10000 records per collection; Decimal precision 128.',),
}
MONEY = set('basis_amount participation_rate commission_rate expected_amount reported_amount variance amount rate opening_balance movements eligible_earnings closing_balance reported_closing_balance closing_variance potential_payable from_amount to_amount fx_rate adjustments allocated unallocated'.split())
NULLS = {'recovered_cash', 'cash_received', 'current_payable'}
DATES = {'as_of', 'period_start', 'period_end', 'date', 'checked_on'}
REFS = {'line', 'rule', 'version', 'account', 'evidence', 'statements', 'remittances', 'receipts', 'source_record', 'source_version', 'reported_status', 'evidence_status', 'allocation', 'adjustment', 'access_description'}
COMMON_CONTROLS = ('schema_version', 'stage', 'as_of', 'calculation_check', 'result_status', 'source_control', 'freshness', 'recovered_cash', 'recovery_rollup', 'input_sha256', 'result_sha256', 'evidence_inventory_sha256')
CONTROLS = {
    'entitlement': COMMON_CONTROLS + ('rounding_policy',),
    'remittance': COMMON_CONTROLS + ('readiness', 'completion_scope', 'missing_required_stages', 'unmatched_required_records', 'unverified_allocation_refs', 'current_payable', 'receiving_account_access', 'receiving_account_access_ref', 'arithmetic_limits'),
}


def require(ok):
    if not ok:
        raise ValueError('Unsupported handoff schema or inconsistent artifact')


def digest(value):
    require(isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None)
    return value


def reference(value):
    require(isinstance(value, str) and ':' in value)
    kind, suffix = value.split(':', 1)
    require(kind in REFS)
    digest(suffix)
    return value


def field(key, value):
    if key == 'as_of':
        require(isinstance(value, str))
        iso_date(value, key)
    elif key in NULLS:
        require(value is None)
    elif key in MONEY:
        require(value is None or (type(value) in (str, int) and len(str(value)) <= 256))
        if value is not None:
            normalized = str(value).strip().replace('_', '')
            require(re.fullmatch(r'[+-]?(?:\d{1,128}(?:\.\d{0,128})?|\.\d{1,128})(?:[eE][+-]?\d{1,3})?', normalized) is not None)
            parsed = Decimal(normalized)
            require(parsed.is_finite() and -128 <= parsed.as_tuple().exponent <= 128)
    elif key in DATES:
        if value is not None:
            require(isinstance(value, str))
            iso_date(value, key)
    elif key in {'currency', 'from_currency', 'to_currency'}:
        require(value == 'unknown_not_calculated' or (isinstance(value, str) and re.fullmatch('[A-Z]{3}', value) is not None))
    elif key.endswith('_sha256'):
        require(value is not None or key in {'source_sha256', 'current_sha256', 'evidence_inventory_sha256'})
        if value is not None:
            digest(value)
    elif key.endswith('_refs'):
        require(isinstance(value, list) and len(value) <= 10000)
        for item in value:
            reference(item)
    elif key.endswith('_ref'):
        if value is not None:
            reference(value)
    elif key in {'completion_scope', 'missing_required_stages'}:
        require(isinstance(value, list) and len(value) <= 2 and len(set(value)) == len(value))
        require(key != 'completion_scope' or len(value) >= 1)
        require(all(v in ('statement_to_remittance', 'remittance_to_receipt') for v in value))
    elif key == 'earnings_periods':
        require(isinstance(value, list) and len(value) <= 10000)
        for pair in value:
            require(isinstance(pair, list) and len(pair) == 2)
            for item in pair:
                field('as_of', item)
            require(iso_date(pair[0], 'period_start') <= iso_date(pair[1], 'period_end'))
    elif key in {'step', 'unmatched_required_records'}:
        require(type(value) is int and 0 <= value <= 100000)
    elif key == 'in_completion_scope':
        require(type(value) is bool)
    else:
        require(key in ENUMS and isinstance(value, str) and value in ENUMS[key])
    return value


def project(record, fields):
    require(isinstance(record, dict) and all(key in record for key in fields))
    return {key: field(key, record[key]) for key in fields}
