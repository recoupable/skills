#!/usr/bin/env python3
"""Assemble a lead's catalog data straight from the public Recoup APIs.

This is the same data the marketing valuation tool uses — no DOM scraping. It
pulls the artist's albums (names, years, track counts, **album art**) and the
per-album live play counts (store-served Spotify counts — no Songstats quota,
so no 429), then writes a lead JSON ready for render_valuation_pdf.py.

Dollar figures (est_catalog_value, per-release value) come from the valuation
model — load the catalog-value-estimator skill to fill those in, or copy the
band the marketing tool shows. This script fills everything else.

Auth: RECOUP_API_KEY (x-api-key) or RECOUP_ACCESS_TOKEN (Bearer).
Run from the skill dir:
  python3 scripts/fetch_catalog.py --artist-id 3EPASK2OUUcDo6RgfnroTK --out lead.json
  python3 scripts/fetch_catalog.py --artist "ICEBOX" --out lead.json
"""
import argparse, json, os, sys, time, urllib.request, urllib.parse

BASE = os.environ.get("RECOUP_API_BASE", "https://recoup-api.vercel.app")


def _headers():
    key = os.environ.get("RECOUP_API_KEY")
    tok = os.environ.get("RECOUP_ACCESS_TOKEN")
    if key:
        return {"x-api-key": key}
    if tok:
        return {"Authorization": "Bearer " + tok}
    sys.exit("Set RECOUP_API_KEY or RECOUP_ACCESS_TOKEN.")


def _get(path):
    req = urllib.request.Request(BASE + path, headers=_headers())
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def _img300(images):
    for im in images or []:
        if im.get("height") == 300:
            return im.get("url")
    return (images[0]["url"] if images else None)


def resolve_artist_id(name):
    d = _get("/api/spotify/search?" + urllib.parse.urlencode({"q": name, "limit": 5}))
    items = d.get("artists") or d.get("items") or d.get("results") or []
    if not items:
        sys.exit(f"No artist found for {name!r}")
    a = items[0]
    return a.get("id") or a.get("spotify_artist_id"), a.get("name", name)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--artist-id", help="Spotify artist id")
    g.add_argument("--artist", help="artist name (resolved via /api/spotify/search)")
    ap.add_argument("--out", required=True, help="output lead JSON path")
    ap.add_argument("--name", help="override artist display name")
    args = ap.parse_args()

    artist_id = args.artist_id
    name = args.name
    if args.artist and not artist_id:
        artist_id, resolved = resolve_artist_id(args.artist)
        name = name or resolved
    name = name or args.artist or artist_id

    albums = _get("/api/spotify/artist/albums?" + urllib.parse.urlencode(
        {"id": artist_id, "include_groups": "album,single", "limit": 50, "offset": 0})).get("items", [])

    releases, dormant = [], 0
    seen, uni_streams, uni_tracks = set(), 0, 0  # dedupe tracks cross-listed across albums
    for al in albums:
        aid = al.get("id")
        # Measurements are eventually consistent — an album can read empty while its
        # measurement job is still running. Retry a few times so the first run is complete.
        ms = []
        for attempt in range(3):
            try:
                ms = _get(f"/api/research/albums/{aid}/measurements").get("measurements", [])
            except Exception:
                ms = []
            if ms:
                break
            time.sleep(2)
        streams = sum(int(m.get("value") or 0) for m in ms)  # album-level total (for display)
        for m in ms:
            tid = m.get("spotify_track_id") or m.get("isrc")
            if tid and tid not in seen:
                seen.add(tid)
                uni_streams += int(m.get("value") or 0)
                uni_tracks += 1
        if streams <= 0:
            dormant += 1
        releases.append({
            "name": al.get("name"),
            "year": int((al.get("release_date") or "0")[:4] or 0) or None,
            "tracks": len(ms),
            "streams": streams,
            "image": _img300(al.get("images")),
        })

    releases.sort(key=lambda r: r.get("streams") or 0, reverse=True)
    lead = {
        "artist": name,
        "spotify_artist_url": f"https://open.spotify.com/artist/{artist_id}",
        "lifetime_streams": uni_streams,
        "tracks_measured": uni_tracks,
        "releases_measured": len(albums),
        "dormant_releases": dormant,
        "releases": releases,
        "_note": "Catalog + album art from public Recoup APIs. Fill est_catalog_value / "
                 "value_low / value_high / per-release value via the catalog-value-estimator "
                 "model (or copy the band the marketing valuation tool shows).",
    }
    with open(args.out, "w") as f:
        json.dump(lead, f, indent=2)
    print(f"Wrote {args.out}: {len(albums)} releases, {uni_tracks} tracks, "
          f"{uni_streams:,} streams, {dormant} dormant")


if __name__ == "__main__":
    main()
