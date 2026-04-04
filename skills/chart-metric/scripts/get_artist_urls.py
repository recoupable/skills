#!/usr/bin/env python3
"""
Get artist's social and streaming service URLs.

Usage:
    python get_artist_urls.py <chartmetric_id>
    python get_artist_urls.py 3380

Environment:
    CHARTMETRIC_REFRESH_TOKEN - Your Chartmetric refresh token
"""

import sys
import json
import requests
from get_token import get_token

API_BASE = "https://api.chartmetric.com/api"


def get_artist_urls(cm_id: str) -> dict:
    """Fetch artist's social/streaming URLs from Chartmetric."""
    token = get_token()
    
    response = requests.get(
        f"{API_BASE}/artist/{cm_id}/urls",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 402:
        return {"error": "Payment Required", "message": "Check your Chartmetric subscription."}
    
    if response.status_code == 404:
        return {"error": "Artist not found", "chartmetric_id": cm_id}
    
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_artist_urls.py <chartmetric_id>")
        sys.exit(1)
    
    result = get_artist_urls(sys.argv[1])
    
    if "error" in result:
        print(f"Error: {result.get('error')}")
        if "message" in result:
            print(result.get('message'))
        sys.exit(1)
    
    urls = result.get("obj", [])
    print("Artist URLs:\n")
    
    # Handle both list and dict formats
    if isinstance(urls, list):
        for item in urls:
            if isinstance(item, dict):
                domain = item.get("domain", "unknown")
                url = item.get("url", "")
                if url:
                    print(f"- {domain}: {url}")
            else:
                print(f"- {item}")
    elif isinstance(urls, dict):
        for platform, url in urls.items():
            if url:
                print(f"- {platform}: {url}")
