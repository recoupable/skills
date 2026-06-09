#!/usr/bin/env python3
"""
Catalog Value Estimator — core.
Given a set of recordings (Spotify track IDs or ISRCs), pull live streams from
the Recoup Research API (Songstats), annualize, and model gross -> NLS -> value
with labeled assumptions. Outputs estimate.json + summary.md.

Auth: env RECOUP_API_KEY (x-api-key) or RECOUP_ACCESS_TOKEN (Bearer).
See references/methodology.md for the assumption set; defaults below.
"""
import argparse, json, os, subprocess, sys, datetime as dt
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
}

def auth_header():
    k = os.environ.get("RECOUP_API_KEY")
    if k: return ["-H", f"x-api-key: {k}"]
    t = os.environ.get("RECOUP_ACCESS_TOKEN")
    if t: return ["-H", f"Authorization: Bearer {t}"]
    sys.exit("ERROR: set RECOUP_API_KEY or RECOUP_ACCESS_TOKEN (see references/recoup-api.md).")

def api_get(path, params, timeout=15):
    q = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{BASE}/{path}?{q}"
    cmd = ["curl", "-sS", "--max-time", str(timeout)] + auth_header() + [url]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    try:
        return json.loads(out)
    except Exception:
        return {}

def num(x):
    try: return float(str(x))
    except Exception: return 0.0

def id_param(ident):
    # ISRCs are 12 chars, 2 letters + alnum; Spotify ids are 22 chars base62.
    s = ident.strip()
    if len(s) == 12 and s[:2].isalpha(): return ("isrc", s)
    return ("spotify_track_id", s)

def track_current(ident):
    key, val = id_param(ident)
    j = api_get("research/track/stats", {key: val, "source": "all"})
    d = {"id": ident, "title": ident, "isrc": "", "sp": 0, "yt": 0, "sc": 0, "tt": 0,
         "labels": [], "distributors": []}
    ti = j.get("track_info", {}) or {}
    d["title"] = ti.get("title", ident)
    d["labels"] = [l.get("name") for l in ti.get("labels", []) if isinstance(l, dict)]
    d["distributors"] = [x.get("name") for x in ti.get("distributors", []) if isinstance(x, dict)]
    for ln in ti.get("links", []) or []:
        if ln.get("isrc"): d["isrc"] = ln["isrc"]; break
    for s in j.get("stats", []) or []:
        src, data = s.get("source"), s.get("data", {}) or {}
        if src == "spotify": d["sp"] = num(data.get("streams_total"))
        elif src == "youtube": d["yt"] = num(data.get("video_views_total")) + num(data.get("short_views_total"))
        elif src == "soundcloud": d["sc"] = num(data.get("streams_total"))
        elif src == "tiktok": d["tt"] = num(data.get("views_total"))
    return d

def nearest(history, target):
    """streams_total at the history point closest to target date (ISO str)."""
    if not history: return None
    tt = dt.date.fromisoformat(target)
    best, bestdiff = None, 10**9
    for h in history:
        try: dd = dt.date.fromisoformat(h["date"])
        except Exception: continue
        diff = abs((dd - tt).days)
        if diff < bestdiff: bestdiff, best = diff, num(h.get("streams_total"))
    return best

def track_history(ident, asof, years, window_days):
    key, val = id_param(ident)
    start = (asof - dt.timedelta(days=365 * years + 5)).isoformat()
    j = api_get("research/track/historic-stats",
                {key: val, "source": "spotify", "start_date": start, "end_date": asof.isoformat()},
                timeout=20)
    hist = []
    for s in j.get("stats", []) or []:
        if s.get("source") == "spotify":
            hist = s.get("data", {}).get("history", []) or []
    end_v = nearest(hist, asof.isoformat())
    ttm_start_v = nearest(hist, (asof - dt.timedelta(days=window_days)).isoformat())
    ttm = max(0.0, (end_v or 0) - (ttm_start_v or 0)) if end_v is not None else 0.0
    anniversaries = {}
    for k in range(years + 1):
        d = (asof - dt.timedelta(days=365 * k))
        v = nearest(hist, d.isoformat())
        if v is not None: anniversaries[d.year] = v
    return ttm, anniversaries

def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--ids"); g.add_argument("--isrcs"); g.add_argument("--ids-file")
    ap.add_argument("--asset-name", default="Catalog")
    ap.add_argument("--owner", default="")
    ap.add_argument("--asof", default=dt.date.today().isoformat())
    ap.add_argument("--config"); ap.add_argument("--out", default="./out")
    ap.add_argument("--no-trajectory", action="store_true")
    a = ap.parse_args()

    cfg = json.loads(json.dumps(DEFAULTS))
    if a.config:
        user = json.load(open(a.config)); cfg.update(user)
    asof = dt.date.fromisoformat(a.asof)
    if a.ids: idents = [x for x in a.ids.split(",") if x.strip()]
    elif a.isrcs: idents = [x for x in a.isrcs.split(",") if x.strip()]
    else: idents = [x.strip() for x in open(a.ids_file) if x.strip()]
    os.makedirs(a.out, exist_ok=True)

    years = 0 if a.no_trajectory else cfg["trajectory_years"]
    workers = int(os.environ.get("ESTIMATE_WORKERS", "6"))
    def fetch(ident):
        cur = track_current(ident)
        ttm, anns = track_history(ident, asof, max(years, 1), cfg["window_days"])
        cur["sp_ttm"] = ttm; cur["anniversaries"] = anns
        return cur
    tracks = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for i, cur in enumerate(ex.map(fetch, idents)):
            tracks.append(cur)
            print(f"  [{i+1}/{len(idents)}] {cur['title'][:34]:34}  all-time {cur['sp']:>13,.0f}  TTM {cur['sp_ttm']:>12,.0f}", file=sys.stderr)

    R = cfg["rates"]
    sp_all = sum(t["sp"] for t in tracks); yt_all = sum(t["yt"] for t in tracks)
    sc_all = sum(t["sc"] for t in tracks); tt_all = sum(t["tt"] for t in tracks)
    sp_ttm = sum(t["sp_ttm"] for t in tracks)

    def value_grid(g_sp):
        g_ytsc = (yt_all * R["youtube"] + sc_all * R["soundcloud"])
        ratio = (g_ytsc / (sp_all * R["spotify"])) if sp_all else 0.0   # preserve platform mix
        measured = g_sp + g_sp * ratio
        out = {}
        for sk, sv in cfg["other_dsp_grossup"].items():
            gross = measured + g_sp * sv
            out[sk] = {"gross": gross,
                       "nls": {nk: gross * nv for nk, nv in cfg["nls_band"].items()}}
        return out

    annual = value_grid(sp_ttm * R["spotify"])
    central_gross = annual["central"]["gross"]; central_nls = annual["central"]["nls"]["central"]
    central_value = central_nls * cfg["multiple"]["central"]
    low_value = annual["low"]["nls"]["low"] * cfg["multiple"]["low"]
    high_value = annual["high"]["nls"]["high"] * cfg["multiple"]["high"]

    # concentration (by TTM streams)
    ranked = sorted(tracks, key=lambda t: t["sp_ttm"], reverse=True)
    top1 = ranked[0]["sp_ttm"] / sp_ttm if sp_ttm else 0
    top3 = sum(t["sp_ttm"] for t in ranked[:3]) / sp_ttm if sp_ttm else 0

    # trajectory (album-level cumulative per anniversary + annual deltas)
    traj = {}
    if years:
        yrset = set()
        for t in tracks: yrset |= set(t["anniversaries"].keys())
        for y in sorted(yrset):
            cum = sum(t["anniversaries"].get(y, 0) for t in tracks)
            n = sum(1 for t in tracks if y in t["anniversaries"])
            traj[y] = {"cumulative": cum, "tracks": n}
        yk = sorted(traj)
        for i in range(1, len(yk)):
            traj[yk[i]]["annual"] = traj[yk[i]]["cumulative"] - traj[yk[i-1]]["cumulative"]

    result = {
        "asset": a.asset_name, "owner": a.owner, "as_of": a.asof, "n_tracks": len(tracks),
        "assumptions": cfg,
        "streams": {"spotify_all_time": sp_all, "youtube_all_time": yt_all,
                    "soundcloud_all_time": sc_all, "tiktok_all_time": tt_all,
                    "spotify_ttm": sp_ttm},
        "annual_gross": {k: v["gross"] for k, v in annual.items()},
        "annual_nls": {"low": annual["low"]["nls"]["low"], "central": central_nls,
                       "high": annual["high"]["nls"]["high"]},
        "value": {"low": low_value, "central": central_value, "high": high_value},
        "concentration": {"top_track": ranked[0]["title"], "top_track_share": top1, "top3_share": top3},
        "trajectory": traj,
        "tracks": [{"title": t["title"], "isrc": t["isrc"], "spotify_all_time": t["sp"],
                    "spotify_ttm": t["sp_ttm"]} for t in ranked],
        "labels": sorted({l for t in tracks for l in t["labels"] if l}),
        "distributors": sorted({d for t in tracks for d in t["distributors"] if d}),
    }
    json.dump(result, open(f"{a.out}/estimate.json", "w"), indent=2)

    # summary.md
    M = lambda x: f"{x/1e9:.2f}B" if x >= 1e9 else f"{x/1e6:.1f}M"
    D = lambda x: f"${x/1e6:.2f}M"
    lines = [f"# {a.asset_name} — Catalog Value Estimate", "",
        f"*Owner: {a.owner or 'n/a'} · As of {a.asof} · {len(tracks)} recordings · "
        f"directional model (see methodology). Streams measured live; $ figures derived from public rates.*", "",
        "## Headline", "",
        f"- **Estimated value:** {D(low_value)} – {D(high_value)} (central **{D(central_value)}**)",
        f"- **Annual (trailing-12mo) NLS:** {D(annual['low']['nls']['low'])} – {D(annual['high']['nls']['high'])} (central **{D(central_nls)}**)",
        f"- **All-time Spotify streams:** {M(sp_all)}   ·   **trailing 12 mo:** {M(sp_ttm)}",
        f"- **Concentration:** top track \"{ranked[0]['title']}\" = {top1*100:.0f}% of TTM streams; top 3 = {top3*100:.0f}%",
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
        "- Measured = Spotify/YouTube/SoundCloud; Apple/Amazon/Deezer/Tidal approximated (gross-up). Master-side only.",
        "- Every rate/deduction/multiple is an assumption — calibrate with a real statement to collapse the range."]
    open(f"{a.out}/summary.md", "w").write("\n".join(lines))
    print(f"\nWrote {a.out}/estimate.json and {a.out}/summary.md", file=sys.stderr)
    print(f"VALUE central={D(central_value)}  NLS central={D(central_nls)}  TTM={M(sp_ttm)}", file=sys.stderr)

if __name__ == "__main__":
    main()
