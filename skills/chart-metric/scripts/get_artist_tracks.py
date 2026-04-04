#!/usr/bin/env python3
"""
Get artist's tracks.

Usage:
    python get_artist_tracks.py <chartmetric_id>
    python get_artist_tracks.py 3380

Environment:
    CHARTMETRIC_REFRESH_TOKEN - Your Chartmetric refresh token
"""

import sys
import json
import requests
from get_token import get_token

API_BASE = "https://api.chartmetric.com/api"


def get_artist_tracks(cm_id: str) -> dict:
    """Fetch artist's tracks from Chartmetric."""
    token = get_token()
    
    response = requests.get(
        f"{API_BASE}/artist/{cm_id}/tracks",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    
    if response.status_code == 402:
        return {"error": "Payment Required", "message": "Check your Chartmetric subscription."}
    
    if response.status_code == 404:
        return {"error": "Artist not found", "chartmetric_id": cm_id}
    
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_artist_tracks.py <chartmetric_id>")
        sys.exit(1)
    
    result = get_artist_tracks(sys.argv[1])
    
    if "error" in result:
        print(f"Error: {result.get('error')}")
        if "message" in result:
            print(result.get('message'))
        sys.exit(1)
    
    tracks = result.get("obj", [])
    print(f"Found {len(tracks)} tracks:\n")
    for track in tracks[:20]:  # Limit to first 20
        print(f"- {track.get('name')}")
        print(f"  Chartmetric ID: {track.get('id')}")
        print(f"  Album: {track.get('album_names', ['N/A'])[0] if track.get('album_names') else 'N/A'}")
        print()
