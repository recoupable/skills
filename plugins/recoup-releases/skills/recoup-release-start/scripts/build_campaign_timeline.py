#!/usr/bin/env python3
"""Deterministic release-campaign timeline generator.

Date math must NOT be improvised by the model (latent-vs-deterministic split):
given a release date + type, this computes the exact calendar date of every
rollout milestone, and flags timing risks (e.g. the ~28-day DSP editorial pitch
window). Stdlib only.

Usage:
    python3 scripts/build_campaign_timeline.py --release-date 2026-07-31 --type single
    python3 scripts/build_campaign_timeline.py --release-date TBD --type album
"""
import argparse
import datetime as dt
import json
import sys

# (phase, day-offset-from-release, action). Negative = before release.
BASE_MILESTONES = [
    ("pre-release", -28, "Lock assets; submit DSP editorial pitch (≥4-week lead)"),
    ("pre-release", -21, "Announce + open pre-save; first teaser clip"),
    ("pre-release", -14, "Press/feature outreach; second teaser"),
    ("pre-release", -7, "Release-week content stockpiled; final reminders"),
    ("pre-release", -1, "Pre-save reminder; confirm all links live"),
    ("release-week", 0, "Release day push across all channels; email blast"),
    ("release-week", 1, "Capture day-one reactions; activate paid support"),
    ("release-week", 3, "Mid-week momentum content; pitch follow-ups"),
    ("post-release", 7, "Week-1 report; chase playlist/press adds"),
    ("post-release", 14, "Repurpose top-performing clips"),
    ("post-release", 28, "Month-1 results review vs goal metric; decide double-down/cut"),
]

# Type-specific extra milestones (added to the base set).
TYPE_EXTRAS = {
    "single": [],
    "ep": [("pre-release", -35, "Stagger lead single ~5 weeks ahead")],
    "album": [
        ("pre-release", -49, "Lead single live (~7 weeks ahead)"),
        ("pre-release", -21, "Second single / focus track"),
    ],
    "deluxe": [("pre-release", -21, "Tease the new/deluxe tracks")],
    "remix": [("pre-release", -14, "Tease the remix vs the original")],
    "collab": [("pre-release", -21, "Coordinate co-marketing with the collaborator")],
    "soundtrack": [("pre-release", -21, "Sync/placement co-promo with the title")],
    "sync-focused": [("pre-release", -28, "Prioritize sync-licensing outreach (see recoup-song-sync-brief)")],
    "catalog-reissue": [("pre-release", -21, "Anniversary hook + existing-audience reactivation (lighter discovery push)")],
}

VALID_TYPES = sorted(TYPE_EXTRAS)


def build_timeline(release_date, release_type, today=None):
    """Return the timeline dict. release_date is a date or None (TBD)."""
    release_type = (release_type or "single").lower()
    extras = TYPE_EXTRAS.get(release_type, [])
    rows = sorted(BASE_MILESTONES + extras, key=lambda r: r[1])

    milestones = []
    for phase, offset, action in rows:
        entry = {"phase": phase, "offset": f"R{offset:+d}", "action": action}
        if release_date is not None:
            entry["date"] = (release_date + dt.timedelta(days=offset)).isoformat()
        milestones.append(entry)

    warnings = []
    if release_date is None:
        warnings.append("Release date is TBD — timeline is in relative offsets only. Lock the date to get calendar dates.")
    else:
        today = today or dt.date.today()
        lead_days = (release_date - today).days
        if lead_days < 0:
            warnings.append(f"Release date {release_date.isoformat()} is in the past ({-lead_days} days ago).")
        elif lead_days < 28:
            warnings.append(
                f"Only {lead_days} days to release — under the ~28-day DSP editorial pitch window. "
                "Editorial playlist consideration is tight or closed; weight toward indie/algorithmic + paid."
            )

    return {
        "release_date": release_date.isoformat() if release_date else "TBD",
        "type": release_type,
        "generated": (today or dt.date.today()).isoformat() if release_date else dt.date.today().isoformat(),
        "milestones": milestones,
        "warnings": warnings,
    }


def parse_args(argv):
    p = argparse.ArgumentParser(description="Deterministic release-campaign timeline generator.")
    p.add_argument("--release-date", required=True, help="YYYY-MM-DD or TBD")
    p.add_argument("--type", default="single", help=f"one of: {', '.join(VALID_TYPES)}")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    if args.release_date.strip().upper() == "TBD":
        release_date = None
    else:
        try:
            release_date = dt.date.fromisoformat(args.release_date)
        except ValueError:
            print(json.dumps({"error": f"bad --release-date '{args.release_date}' (want YYYY-MM-DD or TBD)"}))
            return 2
    if args.type.lower() not in TYPE_EXTRAS:
        print(json.dumps({"error": f"unknown --type '{args.type}'", "valid_types": VALID_TYPES}))
        return 2
    print(json.dumps(build_timeline(release_date, args.type), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
