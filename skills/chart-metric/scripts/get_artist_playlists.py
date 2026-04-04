#!/usr/bin/env python3
"""
Get artist playlist placements.

Usage:
    # Basic usage
    python get_artist_playlists.py <chartmetric_id>
    python get_artist_playlists.py 3380 --platform spotify --status current
    python get_artist_playlists.py 3380 --platform applemusic --status past
    
    # With filters (Spotify)
    python get_artist_playlists.py 3380 --editorial --newMusicFriday
    python get_artist_playlists.py 3380 --chart --indie
    
    # With date range and sorting
    python get_artist_playlists.py 3380 --since 2025-01-01 --sort followers --limit 50

Platforms: spotify, applemusic, deezer, amazon, youtube
Status: current, past

Spotify filters: editorial, personalized, chart, thisIs, newMusicFriday, radio,
                 fullyPersonalized, brand, majorCurator, popularIndie, indie, audiobook
                 
Apple Music filters: editorial, editorialBrand, chart, radio, musicBrand,
                     nonMusicBrand, indie, personalityArtist
                     
Deezer filters: editorial, deezerPartner, chart, hundredPercent, brand,
                majorCurator, popularIndie, indie

Environment:
    CHARTMETRIC_REFRESH_TOKEN - Your Chartmetric refresh token
"""

import sys
import argparse
import requests
from get_token import get_token

API_BASE = "https://api.chartmetric.com/api"

# Platform-specific filter support
PLATFORM_FILTERS = {
    "spotify": ["editorial", "personalized", "chart", "thisIs", "newMusicFriday",
                "radio", "fullyPersonalized", "brand", "majorCurator", 
                "popularIndie", "indie", "audiobook"],
    "applemusic": ["editorial", "editorialBrand", "chart", "radio", "musicBrand",
                   "nonMusicBrand", "indie", "personalityArtist"],
    "deezer": ["editorial", "deezerPartner", "chart", "hundredPercent", "brand",
               "majorCurator", "popularIndie", "indie"],
    "amazon": [],  # No filters for Amazon
    "youtube": []  # No filters for YouTube
}


def get_artist_playlists(
    cm_id: str,
    platform: str = "spotify",
    status: str = "current",
    since: str = None,
    until: str = None,
    limit: int = 50,
    offset: int = 0,
    sort_column: str = None,
    sort_desc: bool = True,
    filters: dict = None
) -> dict:
    """
    Fetch artist playlist placements from Chartmetric.
    
    Args:
        cm_id: Chartmetric artist ID
        platform: spotify, applemusic, deezer, amazon, youtube
        status: current or past
        since: Start date (YYYY-MM-DD)
        until: End date (YYYY-MM-DD)
        limit: Results per page
        offset: Pagination offset
        sort_column: Column to sort by
        sort_desc: Sort descending
        filters: Dict of boolean filters (editorial, indie, etc.)
    """
    token = get_token()
    
    params = {"limit": limit}
    
    if offset > 0:
        params["offset"] = offset
    if since:
        params["since"] = since
    if until:
        params["until"] = until
    if sort_column:
        params["sortColumn"] = sort_column
        # Only include sortOrderDesc when explicitly sorting
        if not sort_desc:  # API defaults to descending, so only set when ascending
            params["sortOrderDesc"] = "false"
    
    # Add filter parameters
    if filters:
        for key, value in filters.items():
            if key in PLATFORM_FILTERS.get(platform, []):
                params[key] = str(value).lower()
    
    response = requests.get(
        f"{API_BASE}/artist/{cm_id}/{platform}/{status}/playlists",
        headers={"Authorization": f"Bearer {token}"},
        params=params,
        timeout=10
    )
    
    if response.status_code == 402:
        return {"error": "Payment Required", "message": "Check your Chartmetric subscription."}
    
    if response.status_code == 401:
        return {"error": "Unauthorized", "message": "This endpoint may require a higher subscription tier."}
    
    if response.status_code == 404:
        return {"error": "Artist not found", "chartmetric_id": cm_id}
    
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser(
        description="Get artist playlist placements",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("chartmetric_id", help="Chartmetric artist ID")
    parser.add_argument("--platform", "-p", default="spotify",
                        choices=["spotify", "applemusic", "deezer", "amazon", "youtube"],
                        help="Playlist platform (default: spotify)")
    parser.add_argument("--status", "-s", default="current",
                        choices=["current", "past"],
                        help="Current or past placements (default: current)")
    
    # Date and pagination
    parser.add_argument("--since", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--until", help="End date (YYYY-MM-DD)")
    parser.add_argument("--limit", "-l", type=int, default=50, help="Results limit")
    parser.add_argument("--offset", type=int, default=0, help="Pagination offset")
    parser.add_argument("--sort", help="Sort column (followers, added_at, name, etc.)")
    parser.add_argument("--asc", action="store_true", help="Sort ascending (default: descending)")
    
    # Filter flags (all platforms)
    parser.add_argument("--editorial", action="store_true", help="Editorial playlists")
    parser.add_argument("--chart", action="store_true", help="Chart playlists")
    parser.add_argument("--indie", action="store_true", help="Indie curator playlists")
    parser.add_argument("--radio", action="store_true", help="Radio playlists")
    parser.add_argument("--brand", action="store_true", help="Brand playlists")
    parser.add_argument("--majorCurator", action="store_true", help="Major curator playlists")
    parser.add_argument("--popularIndie", action="store_true", help="Popular indie playlists")
    
    # Spotify-specific filters
    parser.add_argument("--personalized", action="store_true", help="Personalized (Spotify)")
    parser.add_argument("--thisIs", action="store_true", help="This Is playlists (Spotify)")
    parser.add_argument("--newMusicFriday", action="store_true", help="New Music Friday (Spotify)")
    parser.add_argument("--fullyPersonalized", action="store_true", help="Fully personalized (Spotify)")
    parser.add_argument("--audiobook", action="store_true", help="Audiobook playlists (Spotify)")
    
    # Apple Music filters
    parser.add_argument("--editorialBrand", action="store_true", help="Editorial brand (Apple)")
    parser.add_argument("--musicBrand", action="store_true", help="Music brand (Apple)")
    parser.add_argument("--nonMusicBrand", action="store_true", help="Non-music brand (Apple)")
    parser.add_argument("--personalityArtist", action="store_true", help="Personality/artist (Apple)")
    
    # Deezer filters
    parser.add_argument("--deezerPartner", action="store_true", help="Deezer partner")
    parser.add_argument("--hundredPercent", action="store_true", help="100% playlists (Deezer)")
    
    args = parser.parse_args()
    
    # Build filters dict from args
    filter_names = ["editorial", "chart", "indie", "radio", "brand", "majorCurator",
                    "popularIndie", "personalized", "thisIs", "newMusicFriday",
                    "fullyPersonalized", "audiobook", "editorialBrand", "musicBrand",
                    "nonMusicBrand", "personalityArtist", "deezerPartner", "hundredPercent"]
    
    filters = {}
    for name in filter_names:
        if getattr(args, name, False):
            filters[name] = True
    
    result = get_artist_playlists(
        args.chartmetric_id,
        platform=args.platform,
        status=args.status,
        since=args.since,
        until=args.until,
        limit=args.limit,
        offset=args.offset,
        sort_column=args.sort,
        sort_desc=not args.asc,
        filters=filters if filters else None
    )
    
    if "error" in result:
        print(f"Error: {result.get('error')}")
        if "message" in result:
            print(result.get('message'))
        sys.exit(1)
    
    placements = result.get("obj", [])
    print(f"Found {len(placements)} playlist placements:\n")
    
    for item in placements[:20]:
        pl = item.get("playlist", {})
        track = item.get("track", {})
        print(f"- {pl.get('name', 'Unknown')}")
        print(f"  Track: {track.get('name', 'Unknown')}")
        
        position = pl.get('position', 'N/A')
        peak = pl.get('peak_position', 'N/A')
        print(f"  Position: {position} (Peak: {peak})")
        
        followers = pl.get('followers')
        if followers:
            print(f"  Followers: {followers:,}")
        
        print(f"  Added: {pl.get('added_at', 'N/A')}")
        
        if args.status == 'past' and pl.get('removed_at'):
            print(f"  Removed: {pl.get('removed_at')}")
        
        curator = pl.get('curator_name', 'Unknown')
        print(f"  Owner: {curator}")
        print()
    
    if len(placements) > 20:
        print(f"... and {len(placements) - 20} more (use --limit to adjust)")


if __name__ == "__main__":
    main()
