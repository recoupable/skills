#!/usr/bin/env python3
"""
Lookup artist by Spotify ID or URL.

Usage:
    python get_artist_by_spotify.py <spotify_id>
    python get_artist_by_spotify.py 3TVXtAsR1Inumwj472S9r4
    python get_artist_by_spotify.py "https://open.spotify.com/artist/3TVXtAsR1Inumwj472S9r4"

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
    """Extract Spotify artist ID from URL or return as-is if already an ID."""
    # If it looks like a URL, extract the ID
    match = re.search(r"artist[/:]([a-zA-Z0-9]+)", url_or_id)
    if match:
        return match.group(1)
    return url_or_id


def get_artist_by_spotify(spotify_id: str) -> dict:
    """Lookup Chartmetric artist by Spotify ID.
    
    Uses the /artist/:type/:id/get-ids endpoint to lookup artist by platform ID.
    Returns the Chartmetric artist ID and other platform IDs.
    """
    token = get_token()
    
    response = requests.get(
        f"{API_BASE}/artist/spotify/{spotify_id}/get-ids",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    
    if response.status_code == 402:
        return {
            "error": "Payment Required",
            "message": "Your Chartmetric API subscription may be expired or this endpoint requires a higher tier. Check your account at chartmetric.com or contact hi@chartmetric.com"
        }
    
    if response.status_code == 404:
        return {"error": "Artist not found in Chartmetric", "spotify_id": spotify_id}
    
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_artist_by_spotify.py <spotify_id_or_url>")
        sys.exit(1)
    
    spotify_id = extract_spotify_id(sys.argv[1])
    result = get_artist_by_spotify(spotify_id)
    print(json.dumps(result, indent=2))
    if "error" in result:
        sys.exit(1)
