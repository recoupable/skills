#!/usr/bin/env python3
"""
Discover artists by filtering on metrics, geography, genre, and more.

This is the POWER endpoint - find artists matching specific criteria.

Usage:
    # Find US artists with 100K-500K Spotify monthly listeners
    python discover_artists.py --country US --spotify-listeners 100000 500000
    
    # Find TikTok-famous artists weak on Spotify (signing opportunity)
    python discover_artists.py --tiktok-followers 1000000 10000000 --spotify-listeners 0 100000
    
    # Find emerging hip-hop artists
    python discover_artists.py --genre 86 --spotify-listeners 50000 200000 --sort weekly_diff.sp_monthly_listeners
    
    # Find solo female artists in Brazil
    python discover_artists.py --country BR --band false --pronoun she/her
    
    # Find artists at a specific festival
    python discover_artists.py --festival-id 123

Metric Filters (use two values for [min, max]):
    --spotify-listeners     Spotify monthly listeners range
    --spotify-followers     Spotify followers range
    --spotify-popularity    Spotify popularity (0-100)
    --tiktok-followers      TikTok followers range
    --tiktok-likes          TikTok likes range
    --instagram-followers   Instagram followers range
    --youtube-subscribers   YouTube subscribers range
    --cpp                   Cross-Platform Performance score range

Other Filters:
    --country              2-letter country code (US, GB, BR, etc.)
    --genre                Genre ID (use list_genres.py to find IDs)
    --subgenre             Subgenre ID
    --band                 true/false - filter bands or solo artists
    --pronoun              he/him, she/her, they/them, any
    --first-release-days   Artists who debuted within X days
    --festival-id          Artists playing at specific festival

Sorting:
    --sort                 Sort column (default: latest.sp_monthly_listeners)
    --asc                  Sort ascending (default: descending)

Sort column format: <period>.<stat>
    Periods: latest, weekly_diff, monthly_diff
    Stats: sp_monthly_listeners, sp_followers, tt_followers, ig_followers, cpp, etc.

Environment:
    CHARTMETRIC_REFRESH_TOKEN - Your Chartmetric refresh token
"""

import sys
import json
import argparse
import requests
from get_token import get_token

API_BASE = "https://api.chartmetric.com/api"


def discover_artists(
    country: str = None,
    genre_id: int = None,
    subgenre_id: int = None,
    band: bool = None,
    pronoun: str = None,
    first_release_days: int = None,
    festival_ids: list = None,
    spotify_listeners: tuple = None,
    spotify_followers: tuple = None,
    spotify_popularity: tuple = None,
    tiktok_followers: tuple = None,
    tiktok_likes: tuple = None,
    instagram_followers: tuple = None,
    youtube_subscribers: tuple = None,
    cpp: tuple = None,
    sort_column: str = "latest.sp_monthly_listeners",
    sort_desc: bool = True,
    limit: int = 50,
    offset: int = 0
) -> dict:
    """
    Discover artists using Chartmetric's powerful filter endpoint.
    
    Returns artists matching the specified criteria with all their metrics.
    """
    token = get_token()
    
    params = {
        "limit": limit,
        "offset": offset,
        "sortColumn": sort_column,
        "sortOrderDesc": str(sort_desc).lower()
    }
    
    # Basic filters
    if country:
        params["code2"] = country
    if genre_id:
        params["tagId"] = genre_id
    if subgenre_id:
        params["subTagId"] = subgenre_id
    if band is not None:
        params["band"] = str(band).lower()
    if pronoun:
        params["pronoun"] = pronoun
    if first_release_days:
        params["firstReleaseDaysAgo"] = first_release_days
    if festival_ids:
        params["eventIds[]"] = festival_ids
    
    # Metric range filters (need special handling for arrays)
    range_params = []
    if spotify_listeners:
        range_params.append(("sp_ml[]", spotify_listeners[0]))
        range_params.append(("sp_ml[]", spotify_listeners[1]))
    if spotify_followers:
        range_params.append(("sp_f[]", spotify_followers[0]))
        range_params.append(("sp_f[]", spotify_followers[1]))
    if spotify_popularity:
        range_params.append(("sp_p[]", spotify_popularity[0]))
        range_params.append(("sp_p[]", spotify_popularity[1]))
    if tiktok_followers:
        range_params.append(("tt_f[]", tiktok_followers[0]))
        range_params.append(("tt_f[]", tiktok_followers[1]))
    if tiktok_likes:
        range_params.append(("tt_l[]", tiktok_likes[0]))
        range_params.append(("tt_l[]", tiktok_likes[1]))
    if instagram_followers:
        range_params.append(("ig_f[]", instagram_followers[0]))
        range_params.append(("ig_f[]", instagram_followers[1]))
    if youtube_subscribers:
        range_params.append(("ytc_s[]", youtube_subscribers[0]))
        range_params.append(("ytc_s[]", youtube_subscribers[1]))
    if cpp:
        range_params.append(("cpp[]", cpp[0]))
        range_params.append(("cpp[]", cpp[1]))
    
    # Build URL with array params
    url = f"{API_BASE}/artist/list/filter"
    
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        params=params if not range_params else None
    )
    
    # If we have range params, we need to build the URL manually
    if range_params:
        from urllib.parse import urlencode
        base_query = urlencode(params)
        range_query = "&".join([f"{k}={v}" for k, v in range_params])
        full_url = f"{url}?{base_query}&{range_query}"
        response = requests.get(
            full_url,
            headers={"Authorization": f"Bearer {token}"}
        )
    
    if response.status_code == 402:
        return {"error": "Payment Required", "message": "Check your Chartmetric subscription."}
    
    if response.status_code == 401:
        return {"error": "Unauthorized", "message": "This endpoint may require a higher subscription tier."}
    
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser(
        description="Discover artists by filtering on metrics and attributes",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Basic filters
    parser.add_argument("--country", "-c", help="2-letter country code (US, GB, BR)")
    parser.add_argument("--genre", "-g", type=int, help="Genre ID")
    parser.add_argument("--subgenre", type=int, help="Subgenre ID")
    parser.add_argument("--band", choices=["true", "false"], help="Filter bands or solo")
    parser.add_argument("--pronoun", choices=["any", "he/him", "she/her", "they/them"])
    parser.add_argument("--first-release-days", type=int, help="Debuted within X days")
    parser.add_argument("--festival-id", type=int, action="append", help="Festival event ID")
    
    # Metric ranges (2 values each)
    parser.add_argument("--spotify-listeners", type=int, nargs=2, metavar=("MIN", "MAX"),
                        help="Spotify monthly listeners range")
    parser.add_argument("--spotify-followers", type=int, nargs=2, metavar=("MIN", "MAX"),
                        help="Spotify followers range")
    parser.add_argument("--spotify-popularity", type=int, nargs=2, metavar=("MIN", "MAX"),
                        help="Spotify popularity range (0-100)")
    parser.add_argument("--tiktok-followers", type=int, nargs=2, metavar=("MIN", "MAX"),
                        help="TikTok followers range")
    parser.add_argument("--tiktok-likes", type=int, nargs=2, metavar=("MIN", "MAX"),
                        help="TikTok likes range")
    parser.add_argument("--instagram-followers", type=int, nargs=2, metavar=("MIN", "MAX"),
                        help="Instagram followers range")
    parser.add_argument("--youtube-subscribers", type=int, nargs=2, metavar=("MIN", "MAX"),
                        help="YouTube subscribers range")
    parser.add_argument("--cpp", type=int, nargs=2, metavar=("MIN", "MAX"),
                        help="Cross-Platform Performance score range")
    
    # Sorting and pagination
    parser.add_argument("--sort", default="latest.sp_monthly_listeners",
                        help="Sort column (default: latest.sp_monthly_listeners)")
    parser.add_argument("--asc", action="store_true", help="Sort ascending")
    parser.add_argument("--limit", "-l", type=int, default=50, help="Results limit")
    parser.add_argument("--offset", type=int, default=0, help="Pagination offset")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    
    result = discover_artists(
        country=args.country,
        genre_id=args.genre,
        subgenre_id=args.subgenre,
        band=args.band == "true" if args.band else None,
        pronoun=args.pronoun,
        first_release_days=args.first_release_days,
        festival_ids=args.festival_id,
        spotify_listeners=tuple(args.spotify_listeners) if args.spotify_listeners else None,
        spotify_followers=tuple(args.spotify_followers) if args.spotify_followers else None,
        spotify_popularity=tuple(args.spotify_popularity) if args.spotify_popularity else None,
        tiktok_followers=tuple(args.tiktok_followers) if args.tiktok_followers else None,
        tiktok_likes=tuple(args.tiktok_likes) if args.tiktok_likes else None,
        instagram_followers=tuple(args.instagram_followers) if args.instagram_followers else None,
        youtube_subscribers=tuple(args.youtube_subscribers) if args.youtube_subscribers else None,
        cpp=tuple(args.cpp) if args.cpp else None,
        sort_column=args.sort,
        sort_desc=not args.asc,
        limit=args.limit,
        offset=args.offset
    )
    
    if args.json:
        print(json.dumps(result, indent=2))
        return
    
    if "error" in result:
        print(f"Error: {result.get('error')}")
        if "message" in result:
            print(result.get('message'))
        sys.exit(1)
    
    artists = result.get("obj", [])
    print(f"Found {len(artists)} artists:\n")
    
    for artist in artists[:30]:
        print(f"- {artist.get('name')}")
        print(f"  CM ID: {artist.get('id')}")
        
        # Show key metrics
        if artist.get('sp_monthly_listeners'):
            print(f"  Spotify Listeners: {artist.get('sp_monthly_listeners'):,}")
        if artist.get('sp_followers'):
            print(f"  Spotify Followers: {artist.get('sp_followers'):,}")
        if artist.get('tiktok_followers'):
            print(f"  TikTok Followers: {artist.get('tiktok_followers'):,}")
        if artist.get('ins_followers'):
            print(f"  Instagram Followers: {artist.get('ins_followers'):,}")
        if artist.get('code2'):
            print(f"  Country: {artist.get('code2')}")
        
        print()
    
    if len(artists) > 30:
        print(f"... and {len(artists) - 30} more (use --limit to adjust)")


if __name__ == "__main__":
    main()
