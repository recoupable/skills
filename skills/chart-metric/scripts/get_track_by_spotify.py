#!/usr/bin/env python3
"""
Lookup track by Spotify ID or URL.

Usage:
    python get_track_by_spotify.py <spotify_id>
    python get_track_by_spotify.py 0VjIjW4GlUZAMYd2vXMi3b
    python get_track_by_spotify.py "https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b"

Environment:
    CHARTMETRIC_REFRESH_TOKEN - Your Chartmetric refresh token
"""

import sys
import json
import re
import requests
from get_token import get_token

API_BASE = "https://api.chartmetric.com/api"


def extract_spotify_id(url_or_id: str) -> str:
    """Extract Spotify track ID from URL or return as-is if already an ID."""
    match = re.search(r"track[/:]([a-zA-Z0-9]+)", url_or_id)
    if match:
        return match.group(1)
    return url_or_id


def get_track_by_spotify(spotify_id: str) -> dict:
    """Lookup Chartmetric track by Spotify ID."""
    token = get_token()
    
    response = requests.get(
        f"{API_BASE}/track/spotify/{spotify_id}/get-ids",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    
    if response.status_code == 402:
        return {"error": "Payment Required", "message": "Check your Chartmetric subscription."}
    
    if response.status_code == 404:
        return {"error": "Track not found in Chartmetric", "spotify_id": spotify_id}
    
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_track_by_spotify.py <spotify_id_or_url>")
        sys.exit(1)
    
    spotify_id = extract_spotify_id(sys.argv[1])
    result = get_track_by_spotify(spotify_id)
    print(json.dumps(result, indent=2))
    if "error" in result:
        sys.exit(1)
