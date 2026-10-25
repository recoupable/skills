#!/usr/bin/env python3
"""Measure a synthetic large CSV import. Creates/deletes temporary synthetic files.

python3 tests/benchmark_finance.py --rows 2000000 --output /tmp/finance-benchmark.json
This benchmark is separate from fast unit tests. It reports process peak RSS and
source/ledger byte sizes; it does not claim performance on private provider data.
"""
import argparse
import csv
import hashlib
from decimal import Decimal
import importlib.util
import json
import resource
import sys
import tempfile
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=2000000)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.rows < 1:
        raise SystemExit("rows must be positive")
    script = Path(__file__).resolve().parents[1] / "scripts/normalize-royalty-statement.py"
    script_sha256 = hashlib.sha256(script.read_bytes()).hexdigest()
    sys.path.insert(0, str(script.parent))
    spec = importlib.util.spec_from_file_location("royalty_normalizer_benchmark", script)
    normalizer = importlib.util.module_from_spec(spec); sys.modules[spec.name] = normalizer; spec.loader.exec_module(normalizer)
    with tempfile.TemporaryDirectory(prefix="synthetic-royalty-benchmark-") as directory:
        source, output = Path(directory) / "source.csv", Path(directory) / "ledger.csv"
        with source.open("w", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["Title", "Period Start", "Period End", "Currency", "Net", "Rights Type", "Income Type"])
            for i in range(args.rows):
                writer.writerow(["Synthetic Work", "2024-01-01", "2024-03-31", "USD", ".0049", "publishing", "performance"])
        expected_total = format(Decimal(".0049") * args.rows, "f")
        controls = Path(directory) / "controls.json"
        controls.write_text(json.dumps({"evidence_refs": ["synthetic-generator:row-count-times-rate"],
                                       "totals": [{"currency": "USD", "field": "owner_net_amount", "amount": expected_total}]}))
        started = time.monotonic()
        receipt = normalizer.normalize("distributor", source, output, controls_path=controls)
        elapsed = time.monotonic() - started
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # macOS reports bytes; Linux reports KiB.
        rss_bytes = rss if sys.platform == "darwin" else rss * 1024
        result = {"synthetic": True, "rows": args.rows, "status": receipt["status"], "seconds": round(elapsed, 3),
                  "peak_rss_bytes": rss_bytes, "source_bytes": source.stat().st_size, "ledger_bytes": output.stat().st_size,
                  "source_totals": receipt["source_totals"], "row_conservation": receipt["row_conservation"],
                  "controls_status": receipt["controls_status"], "expected_owner_net": expected_total,
                  "normalizer_sha256": script_sha256,
                  "python": sys.version.split()[0], "platform": sys.platform}
        Path(args.output).write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        if receipt["status"] != "ok" or receipt["rows"] != args.rows:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
