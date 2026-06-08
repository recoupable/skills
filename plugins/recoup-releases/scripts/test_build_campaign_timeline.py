#!/usr/bin/env python3
"""Unit tests for build_campaign_timeline. Stdlib unittest; no deps."""
import datetime as dt
import unittest

import build_campaign_timeline as bct


class TimelineTests(unittest.TestCase):
    def test_dates_are_computed_from_offsets(self):
        rel = dt.date(2026, 7, 31)
        tl = bct.build_timeline(rel, "single", today=dt.date(2026, 6, 1))
        by_offset = {m["offset"]: m for m in tl["milestones"]}
        self.assertEqual(by_offset["R+0"]["date"], "2026-07-31")
        self.assertEqual(by_offset["R-28"]["date"], "2026-07-03")  # 31 Jul - 28d
        self.assertEqual(by_offset["R+7"]["date"], "2026-08-07")

    def test_tbd_has_no_dates_and_warns(self):
        tl = bct.build_timeline(None, "single")
        self.assertEqual(tl["release_date"], "TBD")
        self.assertTrue(all("date" not in m for m in tl["milestones"]))
        self.assertTrue(any("TBD" in w for w in tl["warnings"]))

    def test_dsp_lead_warning_fires_when_close(self):
        rel = dt.date(2026, 6, 15)
        tl = bct.build_timeline(rel, "single", today=dt.date(2026, 6, 1))  # 14 days
        self.assertTrue(any("DSP editorial" in w for w in tl["warnings"]))

    def test_no_lead_warning_when_far(self):
        rel = dt.date(2026, 9, 1)
        tl = bct.build_timeline(rel, "single", today=dt.date(2026, 6, 1))  # ~92 days
        self.assertFalse(any("DSP editorial" in w for w in tl["warnings"]))

    def test_album_adds_lead_single_milestone(self):
        rel = dt.date(2026, 9, 1)
        single = bct.build_timeline(rel, "single", today=dt.date(2026, 6, 1))
        album = bct.build_timeline(rel, "album", today=dt.date(2026, 6, 1))
        self.assertGreater(len(album["milestones"]), len(single["milestones"]))

    def test_bad_type_via_main_returns_2(self):
        self.assertEqual(bct.main(["--release-date", "2026-07-31", "--type", "nonsense"]), 2)


if __name__ == "__main__":
    unittest.main()
