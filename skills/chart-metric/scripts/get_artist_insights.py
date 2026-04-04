#!/usr/bin/env python3
"""
Get AI-generated noteworthy insights for an artist.

Usage:
    python get_artist_insights.py <chartmetric_id>
    python get_artist_insights.py 3380

Environment:
    CHARTMETRIC_REFRESH_TOKEN - Your Chartmetric refresh token
"""

import sys
import json
import requests
from get_token import get_token

API_BASE = "https://api.chartmetric.com/api"


def get_artist_insights(cm_id: str) -> dict:
    """Fetch noteworthy insights from Chartmetric."""
    token = get_token()
    
    response = requests.get(
        f"{API_BASE}/artist/{cm_id}/noteworthy-insights",
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
        print("Usage: python get_artist_insights.py <chartmetric_id>")
        sys.exit(1)
    
    result = get_artist_insights(sys.argv[1])
    
    if "error" in result:
        print(f"Error: {result.get('error')}")
        if "message" in result:
            print(result.get('message'))
        sys.exit(1)
    
    insights = result.get("obj", [])
    print(f"Noteworthy Insights:\n")
    for insight in insights:
        print(f"• {insight.get('text', insight)}")
        print()
