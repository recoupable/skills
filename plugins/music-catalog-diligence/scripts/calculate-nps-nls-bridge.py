#!/usr/bin/env python3
"""Calculate a reported-to-normalized NPS/NLS bridge from JSON inputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bridge_json", help="JSON with reported_amount and adjustments")
    args = parser.parse_args()

    data = json.loads(Path(args.bridge_json).read_text(encoding="utf-8"))
    reported = float(data.get("reported_amount", 0))
    adjustments = data.get("adjustments", [])
    if not isinstance(adjustments, list):
        raise SystemExit("`adjustments` must be a list")

    normalized = reported
    rows = [{"label": "Reported amount", "amount": reported, "running_total": reported}]
    for adjustment in adjustments:
        label = adjustment.get("label", "Unnamed adjustment")
        amount = float(adjustment.get("amount", 0))
        normalized += amount
        rows.append({"label": label, "amount": amount, "running_total": normalized})

    payload = {
        "status": "ok",
        "metric": data.get("metric", "NPS/NLS"),
        "reported_amount": reported,
        "normalized_amount": normalized,
        "bridge": rows,
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
