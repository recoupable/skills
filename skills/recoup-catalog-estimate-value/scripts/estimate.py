#!/usr/bin/env python3
"""
Catalog Value Estimator — core.
Given recordings (Spotify track IDs / ISRCs) or whole albums (Spotify album IDs),
pull streams from the Recoup Research API, annualize, and model
gross -> NLS -> value with labeled assumptions. Outputs estimate.json + summary.md.

Two measurement modes:
  • Track mode (--ids/--isrcs/--ids-file): per-track stats + historic-stats.
    Spotify counts are store-served (Apify-first) and carry provenance.
  • Portfolio mode (--album-ids/--album-ids-file): snapshot-first. Reads
    GET /research/playcounts per album (one row per track, provenance-labeled),
    optionally triggers POST /research/snapshots for uncaptured albums with --snapshot, and derives
    TTM from GET /research/track/playcount-deltas (accepted only when the
    capture window >= min_delta_days; labeled `runrate_<N>d`).

Every track in the output carries `data_source`, `captured_at`, and
`ttm_source` (measured_365d | runrate_<N>d | insufficient_window | none).

Auth: env RECOUP_API_KEY (x-api-key) or RECOUP_ACCESS_TOKEN (Bearer).
See references/methodology.md for the assumption set; defaults below.
"""
import argparse, json, os, subprocess, sys, time, datetime as dt
import math
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlsplit

BASE = os.environ.get("RECOUP_API_BASE", "https://api.recoupable.dev/api")

DEFAULTS = {
    "currency": "USD",
    "right_kind": "master",
    "controlled_share": 1.0,
    "assumption_status": "illustrative_unverified",
    "assumption_sources": [],
    "rates": {"spotify": 0.0035, "youtube": 0.00069, "soundcloud": 0.0030},
    "other_dsp_grossup": {"low": 0.25, "central": 0.40, "high": 0.60},  # of Spotify gross
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

def api(path, params=None, body=None, timeout=20):
    url = f"{BASE}/{path}"
    if params: url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    cmd = ["curl", "-sS", "--max-time", str(timeout), "-w", "\n%{http_code}"] + auth_header()
    if body is not None:
        cmd += ["-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps(body)]
    result = subprocess.run(cmd + [url], capture_output=True, text=True)
    if result.returncode:
        sys.exit("ERROR: research request failed; no estimate produced from unavailable counts.")
    out, _, status = result.stdout.rpartition("\n")
    if status == "404": return {}
    if status == "402":
        try: j = json.loads(out)
        except (ValueError, TypeError): j = {}
        link = None
        if isinstance(j, dict):
            field = "billingUrl" if j.get("error") == "insufficient_credits" else "checkoutUrl"
            link = j.get(field)
        try:
            parsed = urlsplit(link) if isinstance(link, str) else None
            if parsed:
                parsed.port
            if not (parsed and parsed.scheme == "https" and parsed.hostname and not any(c.isspace() for c in link)):
                link = None
        except (ValueError, TypeError):
            link = None
        sys.exit(f"ERROR: research access requires billing (402). Review: {link or 'Check account billing'}")
    if not status.isdigit() or not 200 <= int(status) < 300:
        sys.exit(f"ERROR: research HTTP {status}; no estimate produced from failed requests.")
    try: j = json.loads(out)
    except (ValueError, TypeError):
        sys.exit("ERROR: invalid research response; no estimate produced.")
    return j

def num(x):
    try: return float(str(x))
    except Exception: return 0.0

def id_param(ident):
    s = ident.strip()
    if len(s) == 12 and s[:2].isalpha(): return ("isrc", s)
    return ("spotify_track_id", s)

# ---------------- TTM via snapshot deltas (shared) ----------------
def ttm_from_deltas(isrc, asof, cfg):
    """Returns (ttm, ttm_source). Accepts run-rate only when window >= min_delta_days."""
    if not isrc: return 0.0, "none"
    since = (asof - dt.timedelta(days=400)).isoformat()
    j = api("research/track/playcount-deltas", {"isrc": isrc, "since": since, "until": asof.isoformat()})
    best = None
    for d in (j.get("deltas") or []):
        if d.get("platform") == "spotify":
            days = num(d.get("days"))
            if best is None or days > num(best.get("days")): best = d
    if not best: return 0.0, "none"
    days = num(best.get("days"))
    if days < cfg["min_delta_days"]: return 0.0, "insufficient_window"
    try:
        delta = float(best["delta"])
        if not math.isfinite(delta) or delta < 0: return 0.0, "invalid_delta"
        rr = delta / days * 365
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return 0.0, "invalid_delta"
    if not math.isfinite(rr): return 0.0, "invalid_delta"
    return rr, f"runrate_{int(days)}d"

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

def nearest(history, target):
    if not history: return None
    tt = dt.date.fromisoformat(target)
    best, bestdiff = None, 10**9
    for h in history:
        try: dd = dt.date.fromisoformat(h["date"])
        except Exception: continue
        diff = abs((dd - tt).days)
        if diff < bestdiff: bestdiff, best = diff, num(h.get("streams_total"))
    return best

def track_history(d, asof, years, cfg):
    """Fills sp_ttm, ttm_source, anniversaries on dict d (track mode)."""
    key, val = id_param(d["id"])
    start = (asof - dt.timedelta(days=365 * years + 5)).isoformat()
    j = api("research/track/historic-stats",
            {key: val, "source": "spotify", "start_date": start, "end_date": asof.isoformat()},
            timeout=25)
    hist = []
    for s in j.get("stats", []) or []:
        if s.get("source") == "spotify":
            hist = s.get("data", {}).get("history", []) or []
    win_start = asof - dt.timedelta(days=cfg["window_days"])
    points = []
    for point in hist:
        try:
            date = dt.date.fromisoformat(point["date"])
            count = float(point["streams_total"])
            if math.isfinite(count) and count >= 0 and date <= asof:
                points.append((date, count))
        except (ValueError, KeyError, TypeError):
            continue
    end = min(points, key=lambda p: abs((p[0] - asof).days)) if points else None
    start = min(points, key=lambda p: abs((p[0] - win_start).days)) if points else None
    span = (end[0] - start[0]).days if end and start else 0
    if end and start and abs((end[0] - asof).days) <= 45 and abs((start[0] - win_start).days) <= 45 and span >= cfg["min_delta_days"]:
        if end[1] < start[1]:
            d["sp_ttm"], d["ttm_source"] = 0.0, "invalid_delta"
        else:
            d["sp_ttm"] = (end[1] - start[1]) * 365 / span
            d["ttm_source"] = "measured_365d" if span == 365 else f"runrate_{span}d"
            d["measurement_window"] = {"start": start[0].isoformat(), "end": end[0].isoformat(), "days": span}
    else:
        d["sp_ttm"], d["ttm_source"] = ttm_from_deltas(d.get("isrc"), asof, cfg)
    anns = {}
    for k in range(years + 1):
        dd = (asof - dt.timedelta(days=365 * k))
        v = nearest(hist, dd.isoformat())
        if v is not None: anns[dd.year] = v
    d["anniversaries"] = anns
    return d

# ---------------- portfolio (snapshot-first) mode ----------------
def album_playcounts(album_id):
    j = api("research/playcounts", {"spotify_album_id": album_id})
    return j.get("playcounts") or []

def portfolio_tracks(album_ids, asof, cfg, snapshot=True, wait_mins=6, skip_ttm=False):
    rows, missing = [], []
    for aid in album_ids:
        pc = album_playcounts(aid)
        if pc: rows += [(aid, p) for p in pc]
        else: missing.append(aid)
    if missing and snapshot:
        print(f"  {len(missing)} albums uncaptured -> POST /research/snapshots", file=sys.stderr)
        j = api("research/snapshots", body={"album_ids": missing, "schedule": "once"})
        print(f"  snapshot {j.get('snapshot_id','?')} queued, est ${j.get('estimated_cost_usd','?')}", file=sys.stderr)
        deadline = time.time() + wait_mins * 60
        while missing and time.time() < deadline:
            time.sleep(20)
            still = []
            for aid in missing:
                pc = album_playcounts(aid)
                if pc: rows += [(aid, p) for p in pc]
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
                       "sp": num(p.get("platform_displayed_play_count")), "yt": 0, "sc": 0, "tt": 0,
                       "labels": [], "distributors": [], "album_id": aid,
                       "data_source": p.get("data_source"), "captured_at": p.get("captured_at"),
                       "anniversaries": {}})
    workers = int(os.environ.get("ESTIMATE_WORKERS", "8"))
    if skip_ttm:
        for t in tracks: t["sp_ttm"], t["ttm_source"] = 0.0, "skipped"
    else:
        def fill(t):
            t["sp_ttm"], t["ttm_source"] = ttm_from_deltas(t["isrc"], asof, cfg); return t
        with ThreadPoolExecutor(max_workers=workers) as ex: list(ex.map(fill, tracks))
    return tracks, missing

# ---------------- reproducible monetary scenarios ----------------
def accepted_measurement(track, cfg):
    """Apply the same minimum window to API and supplied annual measurements."""
    source = track.get("ttm_source")
    runrate = re.fullmatch(r"runrate_([0-9]+)d", source) if isinstance(source, str) else None
    accepted_source = source == "measured_365d" or (runrate is not None and int(runrate.group(1)) >= cfg["min_delta_days"])
    value = track.get("sp_ttm")
    return accepted_source and not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value) and value >= 0


def model_tracks(tracks, cfg, uncaptured=None, population_complete=True):
    """Model the measured subset; no missing count becomes estimated zero income."""
    ids = [t.get("id") for t in tracks]
    if any(not isinstance(ident, str) or not ident for ident in ids) or len(ids) != len(set(ids)):
        raise ValueError("Each observation requires a unique nonempty recording id; resolve duplicate/colliding inputs first")
    for key in ("controlled_share",):
        if not isinstance(cfg.get(key), (int, float)) or not 0 <= cfg[key] <= 1:
            raise ValueError(key + " must be between 0 and 1")
    if cfg.get("window_days") != 365:
        raise ValueError("window_days must be 365 for this annual model")
    if isinstance(cfg.get("min_delta_days"), bool) or not isinstance(cfg.get("min_delta_days"), int) or cfg["min_delta_days"] <= 0:
        raise ValueError("min_delta_days must be a positive integer")
    for group in ("rates", "other_dsp_grossup", "nls_band", "multiple"):
        for key, value in cfg[group].items():
            if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise ValueError(group + "." + key + " must be finite and nonnegative")
    if any(value > 1 for value in cfg["nls_band"].values()):
        raise ValueError("nls_band factors must not exceed 1")
    for group in ("other_dsp_grossup", "nls_band", "multiple"):
        if not cfg[group]["low"] <= cfg[group]["central"] <= cfg[group]["high"]:
            raise ValueError(group + " must have ordered low/central/high scenarios")
    if not isinstance(cfg.get("currency"), str) or len(cfg["currency"]) != 3 or not cfg["currency"].isupper():
        raise ValueError("currency must be an explicit three-letter code")
    covered = [t for t in tracks if accepted_measurement(t, cfg)]
    status = "complete_input_subset" if len(covered) == len(tracks) and tracks and not uncaptured and population_complete else "partial_subset"
    if not covered: status = "insufficient_measurement"
    if cfg.get("right_kind") != "master": status = "unsupported_right"
    supported = status not in ("insufficient_measurement", "unsupported_right")
    # Separate annual source measurements are needed for YouTube/SoundCloud. An
    # all-time ratio is not a comparable annual measurement; retain it as context only.
    spotify_gross = sum(t["sp_ttm"] for t in covered) * cfg["rates"]["spotify"]
    annual_gross, annual_nls, value = {}, {}, {}
    for band in ("low", "central", "high"):
        gross = spotify_gross * (1 + cfg["other_dsp_grossup"][band])
        net = gross * cfg["nls_band"][band] * cfg["controlled_share"]
        annual_gross[band] = gross if supported else None
        annual_nls[band] = net if supported else None
        value[band] = net * cfg["multiple"][band] if supported else None
    return {"status": status, "scope": "covered recording subset only", "currency": cfg["currency"],
            "covered_tracks": len(covered), "input_tracks": len(tracks),
            "coverage_share": len(covered) / len(tracks) if tracks else None,
            "population_complete": population_complete, "uncaptured_albums": uncaptured or [],
            "annual_gross": annual_gross, "annual_nls": annual_nls, "value": value,
            "unknown_track_ids": [t.get("id") for t in tracks if t not in covered],
            "limitations": ["Money is modeled, not reported or collected royalties.",
                            "Missing tracks/platforms are unknown, not zero; no catalog-wide extrapolation.",
                            "Rights and controlled share are assumptions, not ownership findings.",
                            "Net factors already include modeled deductions; do not deduct fees again.",
                            "A single comparable statement can calibrate one slice; residual uncertainty remains."]}


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--ids"); g.add_argument("--isrcs"); g.add_argument("--ids-file")
    g.add_argument("--album-ids"); g.add_argument("--album-ids-file")
    g.add_argument("--observations", help="offline JSON with tracks and population_complete; no account required")
    ap.add_argument("--asset-name", default="Catalog")
    ap.add_argument("--owner", default="")
    ap.add_argument("--asof", default=dt.date.today().isoformat())
    ap.add_argument("--config"); ap.add_argument("--out", default="./out")
    ap.add_argument("--no-trajectory", action="store_true")
    ap.add_argument("--snapshot", action="store_true", help="explicitly authorize snapshot creation for uncaptured albums")
    ap.add_argument("--no-snapshot", action="store_true", help="compatibility flag; snapshot creation is already opt-in")
    ap.add_argument("--skip-ttm", action="store_true")
    ap.add_argument("--wait-mins", type=int, default=6)
    a = ap.parse_args()
    cfg = json.loads(json.dumps(DEFAULTS))
    if a.config: cfg.update(json.load(open(a.config)))
    asof = dt.date.fromisoformat(a.asof)
    os.makedirs(a.out, exist_ok=True)
    uncaptured, complete = [], True
    portfolio_mode = bool(a.album_ids or a.album_ids_file)
    if a.observations:
        supplied = json.load(open(a.observations))
        tracks = supplied["tracks"]
        complete = supplied.get("population_complete") is True
        uncaptured = supplied.get("uncaptured_albums", [])
    elif portfolio_mode:
        album_ids = a.album_ids.split(",") if a.album_ids else open(a.album_ids_file).read().splitlines()
        tracks, uncaptured = portfolio_tracks(list(dict.fromkeys(x.strip() for x in album_ids if x.strip())), asof, cfg,
                                              snapshot=a.snapshot and not a.no_snapshot,
                                              wait_mins=a.wait_mins, skip_ttm=a.skip_ttm)
        # Playcount snapshots expose mapped tracks; they do not prove the requested
        # albums' complete ordered track lists. Keep population completeness unknown.
        complete = False
    else:
        raw = a.ids or a.isrcs
        idents = raw.split(",") if raw else open(a.ids_file).read().splitlines()
        idents = list(dict.fromkeys(x.strip() for x in idents if x.strip()))
        years = 0 if a.no_trajectory else cfg["trajectory_years"]
        def fetch(ident):
            return track_history(track_current(ident), asof, max(years, 1), cfg)
        with ThreadPoolExecutor(max_workers=int(os.environ.get("ESTIMATE_WORKERS", "6"))) as ex:
            tracks = list(ex.map(fetch, idents))
    try:
        model = model_tracks(tracks, cfg, uncaptured, complete)
    except (ValueError, KeyError) as error:
        ap.error(str(error))
    covered = [t for t in tracks if t.get("id") not in model["unknown_track_ids"]]
    ranked = sorted(covered, key=lambda t: t["sp_ttm"], reverse=True)
    sp_ttm = sum(t.get("sp_ttm", 0) for t in covered)
    caps = [t["captured_at"] for t in tracks if t.get("captured_at")]
    provenance = {"mode": "offline" if a.observations else "portfolio_snapshot_first" if portfolio_mode else "per_track",
                  "data_sources": dict(Counter(t.get("data_source") or "unknown" for t in tracks)),
                  "ttm_sources": dict(Counter(t.get("ttm_source") or "unknown" for t in tracks)),
                  "captured_at_min": min(caps) if caps else None, "captured_at_max": max(caps) if caps else None,
                  "ttm_coverage_share": model["coverage_share"], "uncaptured_albums": uncaptured,
                  "population_complete": complete}
    result = {"schema_version": "public-estimate/2", "asset": a.asset_name, "owner": a.owner,
              "as_of": a.asof, "n_tracks": len(tracks), "assumptions": cfg, "provenance": provenance, "model": model,
              "streams": {"spotify_all_time": sum(t.get("sp") or 0 for t in tracks), "spotify_ttm": sp_ttm if covered else None},
              "annual_gross": model["annual_gross"], "annual_nls": model["annual_nls"], "value": model["value"],
              "concentration": {"scope": "covered recording subset only", "top_track": ranked[0].get("title", "") if ranked else "",
                                "top_track_share": (ranked[0].get("sp_ttm", 0) / sp_ttm) if ranked and sp_ttm else None,
                                "top3_share": sum(t.get("sp_ttm") or 0 for t in ranked[:3]) / sp_ttm if sp_ttm else None},
              "tracks": tracks, "trajectory": {},
              "labels": sorted({label for t in tracks for label in t.get("labels", []) if label}),
              "distributors": sorted({label for t in tracks for label in t.get("distributors", []) if label})}
    with open(f"{a.out}/estimate.json", "w") as stream: json.dump(result, stream, indent=2)
    money = lambda value: "unknown" if value is None else f"{cfg['currency']} {value:,.2f}"
    lines = [f"# {a.asset_name} — Public-data scenario estimate", "",
             f"As of {a.asof}. Status: **{model['status']}**. Scope: **{model['scope']}**.",
             f"Accepted annual measurements: {model['covered_tracks']} / {model['input_tracks']} input recordings; population complete: {complete}.",
             f"Assumption status: **{cfg['assumption_status']}**. Currency: {cfg['currency']}; modeled controlled interest: {cfg['controlled_share']:.0%}.",
             "", "| Scenario | Modeled annual gross | Modeled annual net interest | Indicative value |", "|---|---|---|---|"]
    for band in ("low", "central", "high"):
        lines.append(f"| {band} | {money(model['annual_gross'][band])} | {money(model['annual_nls'][band])} | {money(model['value'][band])} |")
    lines += ["", "All-time counts are observations only; the monetary scenario uses accepted Spotify annual counts plus the explicit other-platform scenario.",
              "The net factor includes deductions exactly once, then applies the assumed controlled share. No bank receipt or receivable is inferred.", ""]
    lines += ["- " + limitation for limitation in model["limitations"]]
    with open(f"{a.out}/summary.md", "w") as stream: stream.write("\n".join(lines) + "\n")
    print(f"Wrote {a.out}/estimate.json and summary.md ({model['status']})")


if __name__ == "__main__":
    main()
