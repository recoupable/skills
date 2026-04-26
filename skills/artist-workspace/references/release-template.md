# RELEASE.md Template

Create at `releases/{release-slug}/RELEASE.md`. Fill from the Spotify album response (`GET /api/spotify/album?id=$ALBUM_ID`). Leave optional fields out rather than guessing.

```markdown
---
title: {Album Name}
slug: {release-slug}
type: album|single|ep|compilation
spotifyAlbumId: {Spotify album ID}
spotifyUrl: {external_urls.spotify}
releaseDate: {YYYY-MM-DD}
totalTracks: {n}
coverArtUrl: {images[0].url — typically 640px wide}
---

# {Album Name}

{Optional one-line description — only if you have real editorial context. Skip otherwise.}

## Tracklist

1. {Track name} — {mm:ss}
2. {Track name} — {mm:ss}

## Notes

{Anything release-specific that doesn't belong in the tracklist — chart performance, critical reception, related research, campaign notes. Append over time.}
```

## Field notes

- **`slug`** mirrors the directory name. Kebab-case the title; suffix `-single` or `-ep` if needed to disambiguate from an album of the same name.
- **`type`** — use Spotify's `album_type` directly (`album`, `single`, `compilation`). For EPs, Spotify often returns `album` or `single` depending on duration; override to `ep` if the artist treats it as one.
- **`releaseDate`** — ISO 8601. Spotify returns `YYYY-MM-DD` for full albums, but `YYYY` or `YYYY-MM` for older releases — keep whatever precision Spotify returns.
- **`coverArtUrl`** — prefer `images[0].url` (640px). Don't download the image into the folder unless a downstream task needs the bytes; the URL is enough for most agents.

## Tracklist format

Pull from `tracks.items[]` in the Spotify album response. For each item:

- `name` → track name
- `duration_ms` → format as `mm:ss` (`(duration_ms / 1000 / 60) | floor` for minutes, `(duration_ms / 1000) % 60` for seconds, padded)
- `track_number` → use as the list index (1, 2, 3, ...)

Don't link out to individual track Spotify URLs in the tracklist — clutters the file. The album-level `spotifyUrl` is enough.
