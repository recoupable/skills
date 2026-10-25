import copy
import importlib.util
from pathlib import Path
import unittest
import datetime as dt
import json
import subprocess
import sys
import tempfile
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("estimate", Path(__file__).parents[1] / "scripts/estimate.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class EstimateTests(unittest.TestCase):
    def setUp(self):
        self.cfg = copy.deepcopy(MOD.DEFAULTS)

    def test_unknown_is_not_zero_money(self):
        result = MOD.model_tracks([{"id": "unknown", "sp_ttm": 0, "ttm_source": "none"}], self.cfg)
        self.assertEqual(result["status"], "insufficient_measurement")
        self.assertIsNone(result["value"]["central"])

    def test_observed_zero_counts_as_coverage(self):
        result = MOD.model_tracks([{"id": "zero", "sp_ttm": 0, "ttm_source": "measured_365d"}], self.cfg)
        self.assertEqual(result["coverage_share"], 1)
        self.assertEqual(result["value"]["central"], 0)

    def test_supplied_runrate_requires_well_formed_minimum_window(self):
        for source in ("runrate_1d", "runrate_27d", "runrate_garbage", "runrate_28", "runrate_28d_extra", "runrate_-28d", "runrate_28.5d"):
            with self.subTest(source=source):
                result = MOD.model_tracks([{"id": "short", "sp_ttm": 1000, "ttm_source": source}], self.cfg)
                self.assertEqual(result["status"], "insufficient_measurement")
                self.assertEqual(result["covered_tracks"], 0)
                self.assertIsNone(result["value"]["central"])
        result = MOD.model_tracks([{"id": "accepted", "sp_ttm": 1000, "ttm_source": "runrate_28d"}], self.cfg)
        self.assertEqual(result["status"], "complete_input_subset")

    def test_supplied_window_honors_explicit_minimum_and_rejects_invalid_config(self):
        self.cfg["min_delta_days"] = 60
        result = MOD.model_tracks([{"id": "short", "sp_ttm": 1000, "ttm_source": "runrate_30d"}], self.cfg)
        self.assertEqual(result["status"], "insufficient_measurement")
        for invalid in (0, -1, True, 28.5, "28"):
            with self.subTest(invalid=invalid):
                self.cfg["min_delta_days"] = invalid
                with self.assertRaisesRegex(ValueError, "min_delta_days"):
                    MOD.model_tracks([], self.cfg)

    def test_cli_concentration_uses_only_the_covered_subset(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "observations.json"
            source.write_text(json.dumps({"population_complete": True, "tracks": [
                {"id": "known", "title": "Known", "sp_ttm": 100, "ttm_source": "measured_365d"},
                {"id": "unknown", "title": "Unknown", "sp_ttm": 10000, "ttm_source": "none"},
                {"id": "short", "title": "Short", "sp_ttm": 20000, "ttm_source": "runrate_1d"}]}))
            run = subprocess.run([sys.executable, str(SPEC.origin), "--observations", str(source), "--out", str(root / "out")], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            result = json.loads((root / "out/estimate.json").read_text())
            self.assertEqual(result["model"]["status"], "partial_subset")
            self.assertEqual(result["streams"]["spotify_ttm"], 100)
            self.assertEqual(result["concentration"]["top_track"], "Known")
            self.assertEqual(result["concentration"]["top_track_share"], 1)
            self.assertEqual(result["concentration"]["top3_share"], 1)

    def test_partial_subset_and_no_double_deduction(self):
        self.cfg["controlled_share"] = .5
        tracks = [{"id": "known", "sp_ttm": 1000, "ttm_source": "runrate_30d", "yt": 1e12}, {"id": "missing", "sp_ttm": 0, "ttm_source": "none"}]
        result = MOD.model_tracks(tracks, self.cfg)
        self.assertEqual(result["status"], "partial_subset")
        self.assertAlmostEqual(result["annual_nls"]["central"], 1000 * .0035 * 1.4 * .64 * .5)
        self.assertEqual(result["unknown_track_ids"], ["missing"])

    def test_composition_not_modeled_as_master(self):
        self.cfg["right_kind"] = "composition"
        result = MOD.model_tracks([{"id": "work", "sp_ttm": 1000, "ttm_source": "measured_365d"}], self.cfg)
        self.assertEqual(result["status"], "unsupported_right")
        self.assertIsNone(result["annual_nls"]["central"])

    def test_unknown_population_is_partial(self):
        result = MOD.model_tracks([{"id": "one", "sp_ttm": 1, "ttm_source": "measured_365d"}], self.cfg, population_complete=False)
        self.assertEqual(result["status"], "partial_subset")

    def test_invalid_assumption_rejected(self):
        self.cfg["controlled_share"] = 5
        with self.assertRaises(ValueError): MOD.model_tracks([], self.cfg)

    def test_duplicate_population_rejected(self):
        row = {"id": "same", "sp_ttm": 100, "ttm_source": "measured_365d"}
        with self.assertRaisesRegex(ValueError, "unique"):
            MOD.model_tracks([row, row], self.cfg)

    def test_missing_delta_does_not_become_zero(self):
        with patch.object(MOD, "api", return_value={"deltas": [{"platform": "spotify", "days": 30}]}):
            count, source = MOD.ttm_from_deltas("AA0000000001", dt.date(2026, 1, 1), self.cfg)
        self.assertEqual(source, "invalid_delta")

    def test_nonannual_window_is_labeled_and_annualized(self):
        response = {"stats": [{"source": "spotify", "data": {"history": [
            {"date": "2025-01-20", "streams_total": 100},
            {"date": "2026-01-01", "streams_total": 446}]}}]}
        with patch.object(MOD, "api", return_value=response):
            row = MOD.track_history({"id": "spotify-id", "isrc": "AA0000000001"}, dt.date(2026, 1, 1), 1, self.cfg)
        self.assertEqual(row["ttm_source"], "runrate_346d")
        self.assertEqual(row["sp_ttm"], 365)


if __name__ == "__main__":
    unittest.main()
