"""Small, portable primitives for evidenced exact-decimal workpapers."""
from decimal import Decimal, InvalidOperation, getcontext
getcontext().prec = 128
from datetime import date
import json


def amount(value, label="amount"):
    if isinstance(value, (float, bool)) or value is None:
        raise ValueError(f"{label} must be an exact decimal string or integer")
    try:
        result = Decimal(value)
    except (InvalidOperation, TypeError):
        raise ValueError(f"{label} is not a decimal") from None
    if not result.is_finite():
        raise ValueError(f"{label} must be finite")
    _, digits, exponent = result.as_tuple()
    if len(digits) + max(exponent, 0) > 24 or max(-exponent, 0) > 18:
        raise ValueError(f"{label} exceeds supported range: at most 24 coefficient/integer digits and 18 fractional places")
    return result


def refs(record, label):
    values = record.get("evidence_refs")
    if not isinstance(values, list) or not values or not all(isinstance(v, str) and v.strip() for v in values):
        raise ValueError(f"{label} requires evidence_refs")
    return values


def currency(record):
    result = record.get("currency", "")
    if not isinstance(result, str) or len(result) != 3 or not result.isalpha() or result != result.upper():
        raise ValueError("currency must be an explicit uppercase three-letter code")
    return result


def iso_date(value, label):
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        raise ValueError(f"{label} requires an ISO date") from None


def unique(items, key):
    if not isinstance(items, list) or len(items) > 10000:
        raise ValueError(f"{key} collection must be a list of at most 10000 records")
    result = {}
    for item in items:
        if not isinstance(item, dict):
            raise ValueError(f"{key} records must be objects")
        identity = item.get(key)
        if not isinstance(identity, str):
            raise ValueError(f"{key} must be a string")
        if not identity or identity in result:
            raise ValueError(f"Missing or duplicate {key}: {identity}")
        result[identity] = item
    return result


def dumps(value):
    return json.dumps(value, indent=2, default=lambda v: format(v, "f") if isinstance(v, Decimal) else str(v)) + "\n"
