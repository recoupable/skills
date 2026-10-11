# Recoup Research response shapes

Inspect returned JSON before using it. These are illustrative subsets of the
public contract, not guaranteed artist coverage or an exhaustive field list.
Recoup manages data connections; additional metadata can vary. Preserve
provenance and dates without assuming a particular vendor or ID format.

## Search and exact IDs

`GET /research?q=Drake&type=artists` returns `results`. Artist and track results
expose a generic `id` when an identifier is available. Select the intended match:

```json
{"status":"success","results":[{"id":"artist_example","name":"Drake"}]}
```

Use that research ID for artist `id`, album `artist_id`, or track `id` inputs as
appropriate. It is separate from Recoup account IDs and Spotify/Apple IDs.
For `/research/track/stats`, prefer ISRC or the supported Spotify/Apple selectors,
plus the required platform `source`.

## Lookup, profile and track

Lookup accepts a Spotify artist ID or URL. Profile and lookup expose available
`artist_info`; track detail exposes available `track_info` and metadata.
The coordinated adapter correction also exposes a root `id` for nested identity
payloads. Until that API release is deployed, use Search to resolve a generic ID.
Do not extract vendor-specific fields or invent an ID when it is absent.

```json
{"status":"success","id":"artist_example","artist_info":{"id":"artist_example","name":"Drake"}}
```

Track audio analysis, when present, is a list of `{key,value}` entries. Inspect
what was returned; do not assume tempo, demographics or per-song TikTok counts
are available. Use sourced web research when structured data is missing.

## Metrics and stored measurements

Artist and current track statistics use `stats`, with per-platform `source` and
metric fields inside `data`. Keep a returned `data_source` label and capture
timestamp for traceability. Missing provenance stays unknown. Metrics are
synchronous snapshots; these routes do not return a `202 refresh_pending` job.
A platform-displayed play count is not a verified royalty-bearing stream count.

## Collections

- Albums: `albums`; catalog entries can be track-shaped rather than distinct albums.
- Tracks: `tracks`; catalog completeness and fields vary.
- Related artists: `artists`; no weighted similarity score is calculated.
- Artist playlists: `placements`; past scope is all-time and can include current placements.
- Track playlists: `placements`; filtering support and fields vary by data connection.
- Audience: `audience`; geography, age and gender coverage are not guaranteed.
- Platform links: `urls`, containing `{domain,url}` pairs.

## Activities

Career, insights and milestones return available activity arrays under their
respective keys. The coordinated milestones fix preserves an activity array
that earlier code can discard; verify the API release before interpreting an
empty milestone list. None of these feeds guarantees a complete career history.
Inspect dates and activity fields before using an event in public content.

## Errors and recovery

An error response uses `status: "error"` and an `error` field. Check the HTTP
status before parsing success fields. For `402 insufficient_credits`, show
`billingUrl` and stop. Empty successful data means no matching data was returned;
it is not a warm-up signal. A `501` means the operation is unsupported by the
configured research connection. Surface that gap and use an available workflow.
For transient failures, retry only a bounded number of times.
