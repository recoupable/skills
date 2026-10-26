#!/usr/bin/env python3
"""Calculate an evidenced reported-to-normalized bridge, not contractual entitlement."""
import argparse
import json
from pathlib import Path
from _finance import amount, currency, refs, iso_date, unique, dumps


def calculate(data):
    currency(data)
    evidence = refs(data, "reported amount")
    if iso_date(data.get("period_start"), "period_start") > iso_date(data.get("period_end"), "period_end"):
        raise ValueError("Invalid period")
    reported = amount(data.get("reported_amount"), "reported_amount")
    adjustments = unique(data.get("adjustments", []), "adjustment_id")
    normalized = reported
    rows = [{"label": "Reported amount", "amount": reported, "running_total": reported, "evidence_refs": evidence}]
    for identity, adjustment in adjustments.items():
        if adjustment.get("currency", data["currency"]) != data["currency"]:
            raise ValueError("Mixed-currency adjustment requires a separate evidenced FX bridge")
        delta = amount(adjustment.get("amount"))
        normalized += delta
        rows.append({"adjustment_id": identity, "label": adjustment.get("label", identity), "amount": delta,
                     "running_total": normalized, "evidence_refs": refs(adjustment, identity)})
    return {"status": "ok", "metric": data.get("metric", "NPS/NLS"), "currency": data["currency"],
            "period_start": data["period_start"], "period_end": data["period_end"], "reported_amount": reported,
            "normalized_amount": normalized, "bridge": rows, "entitlement_calculated": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bridge_json")
    args = parser.parse_args()
    print(dumps(calculate(json.loads(Path(args.bridge_json).read_text(), parse_float=str))), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
