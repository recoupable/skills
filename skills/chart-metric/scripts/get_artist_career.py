#!/usr/bin/env python3
"""
Get artist career history.

Usage:
    python get_artist_career.py <chartmetric_id>
    python get_artist_career.py 3380

Environment:
    CHARTMETRIC_REFRESH_TOKEN - Your Chartmetric refresh token
"""

import sys
import json
import requests
from get_token import get_token

API_BASE = "https://api.chartmetric.com/api"


def get_artist_career(cm_id: str) -> dict:
    """Fetch artist career history from Chartmetric."""
    token = get_token()
    
    response = requests.get(
        f"{API_BASE}/artist/{cm_id}/career",
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
        print("Usage: python get_artist_career.py <chartmetric_id>")
        sys.exit(1)
    
    result = get_artist_career(sys.argv[1])
    print(json.dumps(result, indent=2))
    if "error" in result:
        sys.exit(1)
