#!/usr/bin/env python3
"""
Search for an artist by name in Chartmetric.

Usage:
    python search_artist.py "Artist Name"
    python search_artist.py "Drake" --limit 10

Environment:
    CHARTMETRIC_REFRESH_TOKEN - Your Chartmetric refresh token
"""

import sys
import json
import argparse
import requests
from get_token import get_token

API_BASE = "https://api.chartmetric.com/api"


def search_artist(name: str, limit: int = 5) -> dict:
    """Search for artists by name.
    
    Uses the /search endpoint with type=artists.
    """
    token = get_token()
    
    response = requests.get(
        f"{API_BASE}/search",
        headers={"Authorization": f"Bearer {token}"},
        params={"q": name, "type": "artists", "limit": limit},
        timeout=10
    )
    
    if response.status_code == 402:
        return {
            "error": "Payment Required",
            "message": "Your Chartmetric API subscription may be expired or this endpoint requires a higher tier. Check your account at chartmetric.com or contact hi@chartmetric.com"
        }
    
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser(description="Search for an artist by name")
    parser.add_argument("name", help="Artist name to search for")
    parser.add_argument("--limit", "-l", type=int, default=5, help="Number of results")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    result = search_artist(args.name, args.limit)
    
    if args.json:
        print(json.dumps(result, indent=2))
        return
    
    # Check for error responses
    if "error" in result:
        print(f"Error: {result.get('error')}")
        if "message" in result:
            print(result.get('message'))
        return
    
    artists = result.get("obj", {}).get("artists", [])
    
    if not artists:
        print(f"No artists found for '{args.name}'")
        return
    
    print(f"Found {len(artists)} artists:\n")
    for artist in artists:
        print(f"- {artist.get('name')}")
        print(f"  Chartmetric ID: {artist.get('id')}")
        if artist.get('spotify_id'):
            print(f"  Spotify ID: {artist.get('spotify_id')}")
        print()


if __name__ == "__main__":
    main()
