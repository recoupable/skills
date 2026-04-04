#!/usr/bin/env python3
"""
Get artist profile by Chartmetric ID.

Usage:
    python get_artist.py <chartmetric_id>
    python get_artist.py 1234567

Environment:
    CHARTMETRIC_REFRESH_TOKEN - Your Chartmetric refresh token
"""

import sys
import json
import requests
from get_token import get_token

API_BASE = "https://api.chartmetric.com/api"


def get_artist(cm_id: str) -> dict:
    """Fetch artist profile from Chartmetric."""
    token = get_token()
    
    response = requests.get(
        f"{API_BASE}/artist/{cm_id}",
        headers={"Authorization": f"Bearer {token}"}
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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_artist.py <chartmetric_id>")
        sys.exit(1)
    
    result = get_artist(sys.argv[1])
    print(json.dumps(result, indent=2))
