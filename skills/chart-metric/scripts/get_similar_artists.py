#!/usr/bin/env python3
"""
Get related/similar artists based on streaming data.

Two modes:
1. Basic (default): Uses /relatedartists endpoint
2. Advanced (--by-config): Uses /similar-artists/by-configurations with filters

Usage:
    # Basic related artists
    python get_similar_artists.py <chartmetric_id> [--limit 10]
    python get_similar_artists.py 3380
    python get_similar_artists.py 3380 --limit 25
    
    # Advanced with configuration filters
    python get_similar_artists.py 2762 --by-config --audience high --genre high
    python get_similar_artists.py 2762 --by-config --mood medium --musicality high

Configuration options (at least one required when using --by-config):
    --audience: high, medium, low - Similarity of Audience
    --mood: high, medium, low - Similarity of Mood
    --genre: high, medium, low - Similarity of Genre
    --musicality: high, medium, low - Similarity of Musicality

Environment:
    CHARTMETRIC_REFRESH_TOKEN - Your Chartmetric refresh token
"""

import sys
import argparse
import requests
from get_token import get_token

API_BASE = "https://api.chartmetric.com/api"


def get_related_artists(cm_id: str, limit: int = 10) -> dict:
    """Fetch related artists from Chartmetric using basic endpoint."""
    token = get_token()
    
    response = requests.get(
        f"{API_BASE}/artist/{cm_id}/relatedartists",
        headers={"Authorization": f"Bearer {token}"},
        params={"limit": limit}
    )
    
    if response.status_code == 402:
        return {"error": "Payment Required", "message": "Check your Chartmetric subscription."}
    
    if response.status_code == 401:
        return {"error": "Unauthorized", "message": "This endpoint may require authentication."}
    
    if response.status_code == 404:
        return {"error": "Artist not found", "chartmetric_id": cm_id}
    
    response.raise_for_status()
    return response.json()


def get_similar_artists_by_config(
    cm_id: str,
    limit: int = 10,
    offset: int = 0,
    audience: str = None,
    mood: str = None,
    genre: str = None,
    musicality: str = None
) -> dict:
    """
    Fetch similar artists using advanced configuration filters.
    
    At least one of audience, mood, genre, or musicality must be specified.
    Valid values: 'high', 'medium', 'low'
    """
    token = get_token()
    
    params = {"limit": limit, "offset": offset}
    if audience:
        params["audience"] = audience
    if mood:
        params["mood"] = mood
    if genre:
        params["genre"] = genre
    if musicality:
        params["musicality"] = musicality
    
    # Validate at least one config is set
    if not any([audience, mood, genre, musicality]):
        return {"error": "Invalid parameters", "message": "At least one of audience, mood, genre, or musicality is required."}
    
    response = requests.get(
        f"{API_BASE}/artist/{cm_id}/similar-artists/by-configurations",
        headers={"Authorization": f"Bearer {token}"},
        params=params
    )
    
    if response.status_code == 402:
        return {"error": "Payment Required", "message": "Check your Chartmetric subscription."}
    
    if response.status_code == 401:
        return {"error": "Unauthorized", "message": "This endpoint may require authentication."}
    
    if response.status_code == 404:
        return {"error": "Artist not found", "chartmetric_id": cm_id}
    
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser(description="Get related/similar artists")
    parser.add_argument("chartmetric_id", help="Chartmetric artist ID")
    parser.add_argument("--limit", "-l", type=int, default=10,
                        help="Number of related artists (default: 10)")
    parser.add_argument("--offset", type=int, default=0,
                        help="Offset for pagination (default: 0)")
    
    # Advanced configuration mode
    parser.add_argument("--by-config", action="store_true",
                        help="Use advanced similar-artists/by-configurations endpoint")
    parser.add_argument("--audience", choices=["high", "medium", "low"],
                        help="Similarity of audience (requires --by-config)")
    parser.add_argument("--mood", choices=["high", "medium", "low"],
                        help="Similarity of mood (requires --by-config)")
    parser.add_argument("--genre", choices=["high", "medium", "low"],
                        help="Similarity of genre (requires --by-config)")
    parser.add_argument("--musicality", choices=["high", "medium", "low"],
                        help="Similarity of musicality (requires --by-config)")
    
    args = parser.parse_args()
    
    # Use advanced endpoint if --by-config or any config option is set
    use_config = args.by_config or any([args.audience, args.mood, args.genre, args.musicality])
    
    if use_config:
        result = get_similar_artists_by_config(
            args.chartmetric_id,
            limit=args.limit,
            offset=args.offset,
            audience=args.audience,
            mood=args.mood,
            genre=args.genre,
            musicality=args.musicality
        )
    else:
        result = get_related_artists(args.chartmetric_id, args.limit)
    
    if "error" in result:
        print(f"Error: {result.get('error')}")
        if "message" in result:
            print(result.get('message'))
        sys.exit(1)
    
    # Handle different response structures
    if use_config:
        obj = result.get("obj", {})
        artists = obj.get("data", [])
        total = obj.get("total", 0)
        print(f"Similar Artists by Configuration ({len(artists)} shown, {total:,} total):\n")
    else:
        artists = result.get("obj", [])
        print(f"Related Artists ({len(artists)} found):\n")
    
    for artist in artists:
        print(f"- {artist.get('name')}")
        print(f"  Chartmetric ID: {artist.get('id')}")
        
        # Show similarity score if available (from by-config endpoint)
        if artist.get('similarity') is not None:
            print(f"  Similarity: {artist.get('similarity'):.2f}")
        
        # Show career stage if available
        if artist.get('career_stage'):
            print(f"  Career Stage: {artist.get('career_stage')}")
        
        # Show rank
        rank = artist.get('rank') or artist.get('cm_artist_rank')
        if rank:
            print(f"  CM Rank: {rank:,}")
        
        # Show Spotify data
        sp_followers = artist.get('sp_followers') or artist.get('spotify_followers')
        if sp_followers:
            print(f"  Spotify Followers: {sp_followers:,}")
        
        if artist.get('sp_monthly_listeners'):
            print(f"  Monthly Listeners: {artist.get('sp_monthly_listeners'):,}")
        
        print()


if __name__ == "__main__":
    main()
