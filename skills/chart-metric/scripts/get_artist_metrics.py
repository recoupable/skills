#!/usr/bin/env python3
"""
Get artist metrics from a specific platform.

Usage:
    python get_artist_metrics.py <chartmetric_id> --source spotify
    python get_artist_metrics.py 3380 -s youtube_channel
    python get_artist_metrics.py 3380 -s instagram

Platforms (14 total):
    spotify, instagram, tiktok, twitter, facebook, youtube_channel,
    youtube_artist, soundcloud, deezer, twitch, line, melon,
    wikipedia, bandsintown

Note: Use 'youtube_channel' or 'youtube_artist', NOT 'youtube'

Environment:
    CHARTMETRIC_REFRESH_TOKEN - Your Chartmetric refresh token
"""

import json
import argparse
import requests
from get_token import get_token

API_BASE = "https://api.chartmetric.com/api"

VALID_SOURCES = [
    "spotify",
    "instagram",
    "tiktok",
    "twitter",
    "facebook",
    "youtube_channel",
    "youtube_artist",
    "soundcloud",
    "deezer",
    "twitch",
    "line",
    "melon",
    "wikipedia",
    "bandsintown",
]


def get_artist_metrics(cm_id: str, source: str) -> dict:
    """Fetch artist metrics for a specific platform."""
    token = get_token()
    
    response = requests.get(
        f"{API_BASE}/artist/{cm_id}/stat/{source}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    
    if response.status_code == 402:
        return {
            "error": "Payment Required",
            "message": "Your Chartmetric API subscription may be expired or this endpoint requires a higher tier. Check your account at chartmetric.com or contact hi@chartmetric.com"
        }
    
    if response.status_code == 404:
        return {"error": "Artist not found", "chartmetric_id": cm_id}
    
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser(description="Get artist metrics for a platform")
    parser.add_argument("chartmetric_id", help="Chartmetric artist ID")
    parser.add_argument(
        "--source", "-s", 
        required=True, 
        choices=VALID_SOURCES,
        help="Platform source"
    )
    
    args = parser.parse_args()
    result = get_artist_metrics(args.chartmetric_id, args.source)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
