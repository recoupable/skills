#!/usr/bin/env python3
"""
Get track metadata by Chartmetric ID.

Usage:
    python get_track.py <chartmetric_id>
    python get_track.py 128613854

Environment:
    CHARTMETRIC_REFRESH_TOKEN - Your Chartmetric refresh token
"""

import sys
import json
import requests
from get_token import get_token

API_BASE = "https://api.chartmetric.com/api"


def get_track(cm_id: str) -> dict:
    """Fetch track metadata from Chartmetric."""
    token = get_token()
    
    response = requests.get(
        f"{API_BASE}/track/{cm_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    
    if response.status_code == 402:
        return {"error": "Payment Required", "message": "Check your Chartmetric subscription."}
    
    if response.status_code == 404:
        return {"error": "Track not found", "chartmetric_id": cm_id}
    
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_track.py <chartmetric_id>")
        sys.exit(1)
    
    result = get_track(sys.argv[1])
    print(json.dumps(result, indent=2))
    if "error" in result:
        sys.exit(1)
