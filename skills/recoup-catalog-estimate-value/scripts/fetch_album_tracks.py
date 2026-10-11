#!/usr/bin/env python3
"""Resolve a Spotify album -> its track IDs (to feed estimate.py --ids).
Usage: python3 fetch_album_tracks.py --album <spotify_album_id_or_url>
Prints a comma-separated list of track IDs; ownership (label / P-line) to stderr."""
import argparse, json, os, re, subprocess, sys
BASE = os.environ.get("RECOUP_API_BASE", "https://api.recoupable.dev/api")

def auth():
    k = os.environ.get("RECOUP_API_KEY")
    if k: return ["-H", f"x-api-key: {k}"]
    t = os.environ.get("RECOUP_ACCESS_TOKEN")
    if t: return ["-H", f"Authorization: Bearer {t}"]
    sys.exit("set RECOUP_API_KEY or RECOUP_ACCESS_TOKEN")

ap = argparse.ArgumentParser(); ap.add_argument("--album", required=True); a = ap.parse_args()
m = re.search(r"album/([A-Za-z0-9]+)", a.album); album_id = m.group(1) if m else a.album
url = f"{BASE}/spotify/album?id={album_id}&market=US"
j = json.loads(subprocess.run(["curl","-sS","--max-time","15"]+auth()+[url], capture_output=True, text=True).stdout or "{}")
ids = [t["id"] for t in j.get("tracks", {}).get("items", []) if t.get("id")]
label = j.get("label", ""); cr = "; ".join(c.get("text","") for c in j.get("copyrights", []))
print(f"# album: {j.get('name','?')}  label: {label}  {cr}", file=sys.stderr)
print(f"# {len(ids)} tracks", file=sys.stderr)
print(",".join(ids))
