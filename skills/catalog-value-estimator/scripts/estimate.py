#!/usr/bin/env python3
"""
Catalog Value Estimator — core.
Given recordings (Spotify track IDs / ISRCs) or whole albums (Spotify album IDs),
pull streams from the Recoup Research API, annualize, and model
gross -> NLS -> value with labeled assumptions. Outputs estimate.json + summary.md.

Flow (both modes): current counts -> seed deep historical backfill -> optionally
wait for the instant drain -> derive TTM. Counts come from track/stats (track
mode) or albums/{id}/measurements (portfolio mode); the trailing-12-month TTM
comes from the consolidated tracks/{id}/measurements series — one read that
replaces historic-stats + playcount-deltas (chat#1796). With `--wait-backfill`,
tracks the drain reaches in this run come back as `measured_365d` rather than a
short-window run-rate.

Every track in the output carries `data_source`, `captured_at`, and
`ttm_source` (measured_365d | runrate_<N>d | insufficient_window | none).

Auth: env RECOUP_API_KEY (x-api-key) or RECOUP_ACCESS_TOKEN (Bearer).
See references/methodology.md for the assumption set; defaults below.
"""
import argparse, json, os, subprocess, sys, time, datetime as dt
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

BASE = os.environ.get("RECOUP_API_BASE", "https://api.recoupable.com/api")

DEFAULTS = {
    "rates": {"spotify": 0.0035, "youtube": 0.00069, "soundcloud": 0.0030},
    "other_dsp_grossup": {"low": 0.25, "central": 0.40, "high": 0.60},  # of Spotify gross
    "distribution_fee": 0.15,
    "artist_producer_royalty": 0.25,
    "nls_band": {"low": 0.55, "central": 0.64, "high": 0.70},           # NLS as % of gross
    "multiple": {"low": 10, "central": 13, "high": 16},
    "window_days": 365,
    "trajectory_years": 5,
    "min_delta_days": 28,   # shortest capture window accepted as a TTM proxy
}

def auth_header():
    k = os.environ.get("RECOUP_API_KEY")
    if k: return ["-H", f"x-api-key: {k}"]
    t = os.environ.get("RECOUP_ACCESS_TOKEN")
    if t: return ["-H", f"Authorization: Bearer {t}"]
    sys.exit("ERROR: set RECOUP_API_KEY or RECOUP_ACCESS_TOKEN (see references/recoup-api.md).")

def api(path, params=None, body=None, timeout=20, soft=False):
    url = f"{BASE}/{path}"
    if params: url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    cmd = ["curl", "-sS", "--max-time", str(timeout)] + auth_header()
    if body is not None:
        cmd += ["-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps(body)]
    out = subprocess.run(cmd + [url], capture_output=True, text=True).stdout
    try: j = json.loads(out)
    except Exception: return {}
    # A 402 carries a Stripe checkoutUrl. For required reads we stop the run; for
    # best-effort calls (soft=True, e.g. the backfill seed) we hand the body back
    # so the caller can surface the link without aborting the whole estimate.
    if not soft and isinstance(j, dict) and j.get("checkoutUrl"):
        sys.exit(f"ERROR: out of credits (402). Top up at: {j['checkoutUrl']}")
    return j

def num(x):
    try: return float(str(x))
    except Exception: return 0.0

def id_param(ident):
    s = ident.strip()
    if len(s) == 12 and s[:2].isalpha(): return ("isrc", s)
    return ("spotify_track_id", s)

# ---------------- TTM from the measurements series (chat#1796) ----------------
def measurements_series(track_id):
    """Daily measured Spotify series for a track from the consolidated
    `measurements` resource — one read that replaces both `track/historic-stats`
    and `track/playcount-deltas`. `{track_id}` is provider-neutral (ISRC or
    Spotify track id, resolved server-side). Returns [{date, value, data_source}]."""
    j = api(f"research/tracks/{track_id}/measurements", {"granularity": "daily"}, timeout=25)
    return j.get("series") or []

def compute_ttm(series, asof, cfg):
    """Derive (sp_ttm, ttm_source) from one measured series: a true
    `measured_365d` diff when the series spans the trailing year, otherwise a
    short-window run-rate from the series' own span (`runrate_<N>d` when
    N >= min_delta_days). Replaces the client-side snapshot-delta math — the same
    series now carries both the Songstats backfill and the Apify snapshot points."""
    if not series: return 0.0, "none"
    try:
        dates = sorted(dt.date.fromisoformat(p["date"]) for p in series if p.get("date"))
    except Exception:
        dates = []
    if not dates: return 0.0, "none"
    win_start = asof - dt.timedelta(days=cfg["window_days"])
    end_v = nearest(series, asof.isoformat())
    start_v = nearest(series, win_start.isoformat())
    span_ok = dates[0] <= win_start + dt.timedelta(days=45) and dates[-1] >= asof - dt.timedelta(days=45)
    if end_v is not None and start_v is not None and span_ok:
        return max(0.0, end_v - start_v), "measured_365d"
    # fall back to a run-rate over the available (short) span
    days = (dates[-1] - dates[0]).days
    if days < cfg["min_delta_days"]: return 0.0, "insufficient_window"
    v0, v1 = nearest(series, dates[0].isoformat()), nearest(series, dates[-1].isoformat())
    if v0 is None or v1 is None: return 0.0, "insufficient_window"
    return max(0.0, (v1 - v0) / days * 365), f"runrate_{int(days)}d"

# ---------------- track mode ----------------
def track_current(ident):
    key, val = id_param(ident)
    j = api("research/track/stats", {key: val, "source": "all"})
    d = {"id": ident, "title": ident, "isrc": val if key == "isrc" else "", "sp": 0, "yt": 0,
         "sc": 0, "tt": 0, "labels": [], "distributors": [],
         "data_source": None, "captured_at": None}
    ti = j.get("track_info", {}) or {}
    d["title"] = ti.get("title", ident)
    d["labels"] = [l.get("name") for l in ti.get("labels", []) if isinstance(l, dict)]
    d["distributors"] = [x.get("name") for x in ti.get("distributors", []) if isinstance(x, dict)]
    for ln in ti.get("links", []) or []:
        if ln.get("isrc"): d["isrc"] = ln["isrc"]; break
    for s in j.get("stats", []) or []:
        src, data = s.get("source"), s.get("data", {}) or {}
        if src == "spotify":
            d["sp"] = num(data.get("streams_total"))
            d["data_source"] = s.get("data_source")
            d["captured_at"] = s.get("captured_at")
        elif src == "youtube": d["yt"] = num(data.get("video_views_total")) + num(data.get("short_views_total"))
        elif src == "soundcloud": d["sc"] = num(data.get("streams_total"))
        elif src == "tiktok": d["tt"] = num(data.get("views_total"))
    return d

def nearest(series, target):
    if not series: return None
    tt = dt.date.fromisoformat(target)
    best, bestdiff = None, 10**9
    for h in series:
        try: dd = dt.date.fromisoformat(h["date"])
        except Exception: continue
        diff = abs((dd - tt).days)
        if diff < bestdiff: bestdiff, best = diff, num(h.get("value"))
    return best

def track_history(d, asof, years, cfg):
    """Fills sp_ttm, ttm_source, anniversaries on dict d from the measurements
    series (provider-neutral id; one read replaces historic-stats + deltas)."""
    series = measurements_series(d.get("isrc") or d["id"])
    d["sp_ttm"], d["ttm_source"] = compute_ttm(series, asof, cfg)
    anns = {}
    for k in range(years + 1):
        dd = asof - dt.timedelta(days=365 * k)
        v = nearest(series, dd.isoformat())
        if v is not None: anns[dd.year] = v
    d["anniversaries"] = anns
    return d

# ---------------- portfolio (snapshot-first) mode ----------------
def album_measurements(album_id):
    """Latest measured count per track on an album from the `measurements`
    resource (replaces GET /research/playcounts). Items: {isrc, spotify_track_id,
    name, value, captured_at, data_source}."""
    j = api(f"research/albums/{album_id}/measurements", {"latest": "true"})
    return j.get("measurements") or []

def portfolio_tracks(album_ids, snapshot=True, wait_mins=6):
    """Current per-track counts for a catalog. Captures uncaptured albums via a
    `current` measurement-job (replaces POST /research/snapshots). TTM is filled
    separately by fill_ttm() — after the historical seed, so an instant drain
    yields measured_365d in the same run."""
    rows, missing = [], []
    for aid in album_ids:
        m = album_measurements(aid)
        if m: rows += [(aid, p) for p in m]
        else: missing.append(aid)
    if missing and snapshot:
        print(f"  {len(missing)} albums uncaptured -> POST /research/measurement-jobs (current)", file=sys.stderr)
        j = api("research/measurement-jobs", body={"scope": {"album_ids": missing}, "source": "current"})
        print(f"  capture job {j.get('id','?')} queued, est ${j.get('estimated_cost_usd','?')}", file=sys.stderr)
        deadline = time.time() + wait_mins * 60
        while missing and time.time() < deadline:
            time.sleep(20)
            still = []
            for aid in missing:
                m = album_measurements(aid)
                if m: rows += [(aid, p) for p in m]
                else: still.append(aid)
            missing = still
            print(f"  waiting on {len(missing)} albums...", file=sys.stderr)
    if missing:
        print(f"  WARNING: {len(missing)} albums still uncaptured (re-run later): {missing[:5]}...", file=sys.stderr)
    tracks, seen = [], set()
    for aid, p in rows:
        tid = p.get("spotify_track_id") or p.get("isrc")
        if not tid or tid in seen: continue
        seen.add(tid)
        tracks.append({"id": tid, "title": p.get("name", tid), "isrc": p.get("isrc", ""),
                       "sp": num(p.get("value")), "yt": 0, "sc": 0, "tt": 0,
                       "labels": [], "distributors": [], "album_id": aid,
                       "data_source": p.get("data_source"), "captured_at": p.get("captured_at"),
                       "anniversaries": {}})
    return tracks, missing

def fill_ttm(tracks, asof, cfg, skip_ttm=False):
    """Fill sp_ttm + ttm_source from each track's measurements series. Call AFTER
    the historical backfill seed so tracks the instant drain reached come back as
    measured_365d, not a short-window run-rate."""
    if skip_ttm:
        for t in tracks: t["sp_ttm"], t["ttm_source"] = 0.0, "skipped"
        return tracks
    workers = int(os.environ.get("ESTIMATE_WORKERS", "8"))
    def fill(t):
        series = measurements_series(t.get("isrc") or t["id"])
        t["sp_ttm"], t["ttm_source"] = compute_ttm(series, asof, cfg); return t
    with ThreadPoolExecutor(max_workers=workers) as ex: list(ex.map(fill, tracks))
    return tracks

# ---------------- historical backfill seeding ----------------
def seed_backfill(scope):
    """Create a *historical* measurement-job so the Songstats worker fills in each
    track's deep daily history — the instant drain then upgrades TTMs from a
    short-window run-rate to `measured_365d` (poll with `--wait-backfill`). `scope`
    is `{"album_ids":[...]}`, `{"isrcs":[...]}`, or `{"catalog_id":...}`. The job
    ranks by all-time streams and dedupes server-side (songs already carrying
    `songstats` history are skipped — no track is fetched twice). Reads no longer
    enqueue backfill, so this seed is explicit. Best-effort: any error is logged
    and never fails the estimate. Resource model: chat#1796."""
    if not scope or not any(scope.values()):
        return {"note": "no scope to seed"}
    # soft=True: the historical source is gated on a card on file, so a cardless
    # account gets a 402 + checkoutUrl. Handle it here instead of aborting the run.
    j = api("research/measurement-jobs", soft=True,
            body={"scope": scope, "source": "historical"}, timeout=30)
    if isinstance(j, dict) and j.get("checkoutUrl"):
        return {"note": "deep-history backfill needs a payment method on file (Songstats is "
                        "metered) — add one to enable it: " + j["checkoutUrl"]}
    if not j or (isinstance(j, dict) and j.get("error")):
        return {"note": "POST /research/measurement-jobs errored — deep history not seeded this run"}
    return {"enqueued": j.get("enqueued"), "skipped_already_backfilled": j.get("skipped")}


# ---------------- main ----------------
def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--ids"); g.add_argument("--isrcs"); g.add_argument("--ids-file")
    g.add_argument("--album-ids", help="comma-separated Spotify album ids (snapshot-first portfolio mode)")
    g.add_argument("--album-ids-file")
    ap.add_argument("--asset-name", default="Catalog")
    ap.add_argument("--owner", default="")
    ap.add_argument("--asof", default=dt.date.today().isoformat())
    ap.add_argument("--config"); ap.add_argument("--out", default="./out")
    ap.add_argument("--no-trajectory", action="store_true")
    ap.add_argument("--no-snapshot", action="store_true", help="portfolio mode: don't auto-trigger snapshots")
    ap.add_argument("--skip-ttm", action="store_true", help="portfolio mode: all-time only (no delta calls)")
    ap.add_argument("--no-backfill-seed", action="store_true",
                    help="don't seed deep Songstats historical backfill")
    ap.add_argument("--wait-backfill", type=int, default=0,
                    help="seconds to wait after seeding so the instant drain can upgrade "
                         "TTMs to measured_365d in this same run (0 = don't wait)")
    ap.add_argument("--wait-mins", type=int, default=6)
    a = ap.parse_args()

    cfg = json.loads(json.dumps(DEFAULTS))
    if a.config: cfg.update(json.load(open(a.config)))
    asof = dt.date.fromisoformat(a.asof)
    os.makedirs(a.out, exist_ok=True)

    def maybe_wait():
        if a.wait_backfill and not a.no_backfill_seed and not a.skip_ttm:
            print(f"  waiting {a.wait_backfill}s for the instant backfill drain...", file=sys.stderr)
            time.sleep(a.wait_backfill)

    portfolio_mode = bool(a.album_ids or a.album_ids_file)
    uncaptured = []
    if portfolio_mode:
        if a.album_ids: album_ids = [x.strip() for x in a.album_ids.split(",") if x.strip()]
        else: album_ids = [x.strip() for x in open(a.album_ids_file) if x.strip()]
        # current counts -> seed historical backfill -> (wait for instant drain) -> TTM
        tracks, uncaptured = portfolio_tracks(album_ids, snapshot=not a.no_snapshot, wait_mins=a.wait_mins)
        backfill_seed = ({"note": "skipped (--no-backfill-seed)"} if a.no_backfill_seed
                         else seed_backfill({"album_ids": album_ids}))
        print(f"  [backfill] seed -> {backfill_seed}", file=sys.stderr)
        maybe_wait()
        fill_ttm(tracks, asof, cfg, skip_ttm=a.skip_ttm)
        for i, t in enumerate(tracks):
            print(f"  [{i+1}/{len(tracks)}] {t['title'][:34]:34}  all-time {t['sp']:>13,.0f}  "
                  f"TTM {t['sp_ttm']:>12,.0f} ({t['ttm_source']})", file=sys.stderr)
        years = 0
    else:
        if a.ids: idents = [x for x in a.ids.split(",") if x.strip()]
        elif a.isrcs: idents = [x for x in a.isrcs.split(",") if x.strip()]
        else: idents = [x.strip() for x in open(a.ids_file) if x.strip()]
        years = 0 if a.no_trajectory else cfg["trajectory_years"]
        workers = int(os.environ.get("ESTIMATE_WORKERS", "6"))
        # 1. current per-track stats (resolves ISRCs) -> 2. seed backfill -> 3. wait -> 4. TTM/history
        with ThreadPoolExecutor(max_workers=workers) as ex:
            tracks = list(ex.map(track_current, idents))
        isrcs = [t["isrc"] for t in tracks if t.get("isrc")]
        backfill_seed = ({"note": "skipped (--no-backfill-seed)"} if a.no_backfill_seed
                         else seed_backfill({"isrcs": isrcs}) if isrcs else {"note": "no ISRCs resolved"})
        print(f"  [backfill] seed -> {backfill_seed}", file=sys.stderr)
        maybe_wait()
        def fetch(t):
            return track_history(t, asof, max(years, 1), cfg)
        with ThreadPoolExecutor(max_workers=workers) as ex:
            list(ex.map(fetch, tracks))
        for i, cur in enumerate(tracks):
            print(f"  [{i+1}/{len(tracks)}] {cur['title'][:34]:34}  all-time {cur['sp']:>13,.0f}  "
                  f"TTM {cur['sp_ttm']:>12,.0f} ({cur['ttm_source']})", file=sys.stderr)

    R = cfg["rates"]
    sp_all = sum(t["sp"] for t in tracks); yt_all = sum(t["yt"] for t in tracks)
    sc_all = sum(t["sc"] for t in tracks); tt_all = sum(t["tt"] for t in tracks)
    sp_ttm = sum(t["sp_ttm"] for t in tracks)

    def value_grid(g_sp):
        g_ytsc = (yt_all * R["youtube"] + sc_all * R["soundcloud"])
        ratio = (g_ytsc / (sp_all * R["spotify"])) if sp_all else 0.0
        measured = g_sp + g_sp * ratio
        out = {}
        for sk, sv in cfg["other_dsp_grossup"].items():
            gross = measured + g_sp * sv
            out[sk] = {"gross": gross, "nls": {nk: gross * nv for nk, nv in cfg["nls_band"].items()}}
        return out

    annual = value_grid(sp_ttm * R["spotify"])
    central_gross = annual["central"]["gross"]; central_nls = annual["central"]["nls"]["central"]
    central_value = central_nls * cfg["multiple"]["central"]
    low_value = annual["low"]["nls"]["low"] * cfg["multiple"]["low"]
    high_value = annual["high"]["nls"]["high"] * cfg["multiple"]["high"]

    ranked = sorted(tracks, key=lambda t: t["sp_ttm"], reverse=True)
    top1 = ranked[0]["sp_ttm"] / sp_ttm if sp_ttm else 0
    top3 = sum(t["sp_ttm"] for t in ranked[:3]) / sp_ttm if sp_ttm else 0

    traj = {}
    if years:
        yrset = set()
        for t in tracks: yrset |= set(t["anniversaries"].keys())
        for y in sorted(yrset):
            traj[y] = {"cumulative": sum(t["anniversaries"].get(y, 0) for t in tracks),
                       "tracks": sum(1 for t in tracks if y in t["anniversaries"])}
        yk = sorted(traj)
        for i in range(1, len(yk)):
            traj[yk[i]]["annual"] = traj[yk[i]]["cumulative"] - traj[yk[i-1]]["cumulative"]

    caps = [t["captured_at"] for t in tracks if t.get("captured_at")]
    provenance = {
        "mode": "portfolio_snapshot_first" if portfolio_mode else "per_track",
        "data_sources": dict(Counter(t.get("data_source") or "unknown" for t in tracks)),
        "ttm_sources": dict(Counter(t.get("ttm_source") or "unknown" for t in tracks)),
        "captured_at_min": min(caps) if caps else None,
        "captured_at_max": max(caps) if caps else None,
        "ttm_coverage_share": (sum(1 for t in tracks if t["sp_ttm"] > 0) / len(tracks)) if tracks else 0,
        "deep_history_share": (sum(1 for t in tracks if t.get("ttm_source") == "measured_365d") / len(tracks)) if tracks else 0,
        "backfill_seed": backfill_seed,
        "uncaptured_albums": uncaptured,
        "notes": "runrate_* TTM is a short-window annualization (>=%dd accepted) — noisier than measured_365d; "
                 "seasonality uncorrected. Portfolio mode measures Spotify only (yt/sc enter via gross-up)."
                 % cfg["min_delta_days"],
    }

    result = {
        "asset": a.asset_name, "owner": a.owner, "as_of": a.asof, "n_tracks": len(tracks),
        "assumptions": cfg, "provenance": provenance,
        "streams": {"spotify_all_time": sp_all, "youtube_all_time": yt_all,
                    "soundcloud_all_time": sc_all, "tiktok_all_time": tt_all,
                    "spotify_ttm": sp_ttm},
        "annual_gross": {k: v["gross"] for k, v in annual.items()},
        "annual_nls": {"low": annual["low"]["nls"]["low"], "central": central_nls,
                       "high": annual["high"]["nls"]["high"]},
        "value": {"low": low_value, "central": central_value, "high": high_value},
        "concentration": {"top_track": ranked[0]["title"] if ranked else "",
                          "top_track_share": top1, "top3_share": top3},
        "trajectory": traj,
        "tracks": [{"title": t["title"], "isrc": t["isrc"], "spotify_all_time": t["sp"],
                    "spotify_ttm": t["sp_ttm"], "ttm_source": t.get("ttm_source"),
                    "data_source": t.get("data_source"), "captured_at": t.get("captured_at")}
                   for t in ranked],
        "labels": sorted({l for t in tracks for l in t["labels"] if l}),
        "distributors": sorted({d for t in tracks for d in t["distributors"] if d}),
    }
    json.dump(result, open(f"{a.out}/estimate.json", "w"), indent=2)

    M = lambda x: f"{x/1e9:.2f}B" if x >= 1e9 else f"{x/1e6:.1f}M"
    D = lambda x: f"${x/1e6:.2f}M"
    ttm_mix = ", ".join(f"{k}: {v}" for k, v in provenance["ttm_sources"].items())
    src_mix = ", ".join(f"{k}: {v}" for k, v in provenance["data_sources"].items())
    lines = [f"# {a.asset_name} — Catalog Value Estimate", "",
        f"*Owner: {a.owner or 'n/a'} · As of {a.asof} · {len(tracks)} recordings · "
        f"directional model (see methodology). Streams measured; $ figures derived from public rates.*", "",
        "## Headline", "",
        f"- **Estimated value:** {D(low_value)} – {D(high_value)} (central **{D(central_value)}**)",
        f"- **Annual (trailing-12mo) NLS:** {D(annual['low']['nls']['low'])} – {D(annual['high']['nls']['high'])} (central **{D(central_nls)}**)",
        f"- **All-time Spotify streams:** {M(sp_all)}   ·   **trailing 12 mo:** {M(sp_ttm)}",
        f"- **Concentration:** top track \"{ranked[0]['title'] if ranked else '—'}\" = {top1*100:.0f}% of TTM streams; top 3 = {top3*100:.0f}%",
        "", "## Provenance", "",
        f"- **Counts:** {src_mix} (captured {str(provenance['captured_at_min'])[:10]} → {str(provenance['captured_at_max'])[:10]})",
        f"- **TTM derivation:** {ttm_mix} · TTM coverage {provenance['ttm_coverage_share']*100:.0f}% of tracks",
        f"- **Deep history (measured_365d):** {provenance['deep_history_share']*100:.0f}% of tracks · "
        f"backfill seed: {provenance['backfill_seed']}",
        ""]
    if result["distributors"]:
        lines.append(f"- **Distributor(s):** {', '.join(result['distributors'])}")
    if traj:
        lines += ["", "## 5-year trajectory (Spotify)", "",
                  "| As of | Cumulative | Streams that year |", "|---|---|---|"]
        for y in sorted(traj):
            t = traj[y]; ann = t.get("annual")
            lines.append(f"| {y} | {M(t['cumulative'])} | {M(ann) if ann is not None else '—'} |")
    lines += ["", "## Value model (central)", "",
        f"Annual gross ≈ {D(central_gross)} → NLS (×{cfg['nls_band']['central']:.2f}) ≈ {D(central_nls)} "
        f"→ value (×{cfg['multiple']['central']}) ≈ {D(central_value)}.", "",
        "## Caveats", "",
        "- Counts are platform-displayed play counts (provenance-labeled per track); not royalty-bearing streams.",
        "- `runrate_*` TTM is a short-window annualization — noisier than `measured_365d`; seasonality uncorrected.",
        "- Measured = Spotify (+YouTube/SoundCloud in track mode); Apple/Amazon/Deezer/Tidal approximated (gross-up). Master-side only.",
        "- Every rate/deduction/multiple is an assumption — calibrate with a real statement to collapse the range."]
    open(f"{a.out}/summary.md", "w").write("\n".join(lines))
    print(f"\nWrote {a.out}/estimate.json and {a.out}/summary.md", file=sys.stderr)
    print(f"VALUE central={D(central_value)}  NLS central={D(central_nls)}  TTM={M(sp_ttm)}", file=sys.stderr)

if __name__ == "__main__":
    main()
