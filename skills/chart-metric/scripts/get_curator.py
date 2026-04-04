#!/usr/bin/env python3
"""
Get curator/playlist owner information.

Usage:
    python get_curator.py <curator_id> [--platform spotify]
    python get_curator.py 1
    python get_curator.py 1 --platform spotify

Environment:
    CHARTMETRIC_REFRESH_TOKEN - Your Chartmetric refresh token
"""

import sys
import argparse
import requests
from get_token import get_token

API_BASE = "https://api.chartmetric.com/api"


def get_curator(curator_id: str, platform: str = "spotify") -> dict:
    """Fetch curator info from Chartmetric."""
    token = get_token()
    
    response = requests.get(
        f"{API_BASE}/curator/{platform}/{curator_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 402:
        return {"error": "Payment Required", "message": "Check your Chartmetric subscription."}
    
    if response.status_code == 401:
        return {"error": "Unauthorized", "message": "This endpoint may require a higher subscription tier."}
    
    if response.status_code == 400:
        return {"error": "Bad Request", "message": "Curator ID must be a numeric Chartmetric ID."}
    
    if response.status_code == 404:
        return {"error": "Curator not found", "curator_id": curator_id}
    
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser(description="Get curator information")
    parser.add_argument("curator_id", help="Chartmetric curator ID (numeric)")
    parser.add_argument("--platform", "-p", default="spotify",
                        choices=["spotify"],
                        help="Curator platform (currently only spotify supported)")
    
    args = parser.parse_args()
    result = get_curator(args.curator_id, args.platform)
    
    if "error" in result:
        print(f"Error: {result.get('error')}")
        if "message" in result:
            print(result.get('message'))
        sys.exit(1)
    
    curator = result.get("obj", {})
    print(f"Curator: {curator.get('name', 'Unknown')}")
    print(f"  Chartmetric ID: {curator.get('id')}")
    print(f"  User ID: {curator.get('user_id')}")
    if curator.get('image_url'):
        print(f"  Image: {curator.get('image_url')}")
    if curator.get('num_playlists'):
        print(f"  Playlists: {curator.get('num_playlists')}")
    if curator.get('followers'):
        print(f"  Followers: {curator.get('followers'):,}")


if __name__ == "__main__":
    main()
