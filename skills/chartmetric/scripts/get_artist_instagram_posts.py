#!/usr/bin/env python3
"""
Get artist's top Instagram posts and reels.

Usage:
    python get_artist_instagram_posts.py <chartmetric_id>
    python get_artist_instagram_posts.py 3380

Environment:
    CHARTMETRIC_REFRESH_TOKEN - Your Chartmetric refresh token
"""

import sys
import json
import requests
from get_token import get_token

API_BASE = "https://api.chartmetric.com/api"


def get_artist_instagram_posts(cm_id: str) -> dict:
    """Fetch artist's top Instagram posts and reels."""
    token = get_token()
    
    response = requests.get(
        f"{API_BASE}/SNS/deepSocial/cm_artist/{cm_id}/instagram",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 402:
        return {"error": "Payment Required", "message": "Check your Chartmetric subscription."}
    
    if response.status_code == 404:
        return {"error": "Artist not found or no Instagram data", "chartmetric_id": cm_id}
    
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_artist_instagram_posts.py <chartmetric_id>")
        sys.exit(1)
    
    result = get_artist_instagram_posts(sys.argv[1])
    
    if "error" in result:
        print(f"Error: {result.get('error')}")
        if "message" in result:
            print(result.get('message'))
        sys.exit(1)
    
    print(json.dumps(result, indent=2))
