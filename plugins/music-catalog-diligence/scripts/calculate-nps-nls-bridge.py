#!/usr/bin/env python3
"""Calculate a reported-to-normalized NPS/NLS bridge from JSON inputs."""

from __future__ import annotations

import argparse
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path


def _to_decimal(value: object, label: str) -> Decimal:
    """Coerce a JSON-loaded number/string to Decimal.

    JSON cannot represent Decimal natively, so the input may arrive as int,
    float, or numeric string. We round-trip through `str` to preserve the
    exact textual representation the caller intended (a literal `"1.10"` stays
    `1.10`, not `1.1000000000000000888...`).
    """
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise SystemExit(f"{label} must be numeric (got {value!r}): {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bridge_json", help="JSON with reported_amount and adjustments")
    args = parser.parse_args()

    data = json.loads(Path(args.bridge_json).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("bridge JSON top level must be an object")

    reported = _to_decimal(data.get("reported_amount", 0), "`reported_amount`")
    adjustments = data.get("adjustments", [])
    if not isinstance(adjustments, list):
        raise SystemExit("`adjustments` must be a list")

    normalized = reported
    rows: list[dict[str, str]] = [
        {"label": "Reported amount", "amount": str(reported), "running_total": str(reported)}
    ]
    for index, adjustment in enumerate(adjustments):
        if not isinstance(adjustment, dict):
            raise SystemExit(
                f"adjustments[{index}] must be an object with `label` and `amount` "
                f"(got {type(adjustment).__name__})"
            )
        label = adjustment.get("label", "Unnamed adjustment")
        amount = _to_decimal(adjustment.get("amount", 0), f"adjustments[{index}].amount")
        normalized += amount
        rows.append(
            {"label": label, "amount": str(amount), "running_total": str(normalized)}
        )

    payload = {
        "status": "ok",
        "metric": data.get("metric", "NPS/NLS"),
        "reported_amount": str(reported),
        "normalized_amount": str(normalized),
        "bridge": rows,
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
