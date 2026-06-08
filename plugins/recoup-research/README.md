# Recoup Research

Music industry research for AI agents. Artist analytics, audience insights, playlist intelligence, competitive analysis, trend detection, and outreach — powered by the [Recoup](https://recoupable.com) research API.

## Install

### Claude Code

```bash
claude plugin install https://github.com/recoupable/recoup-research
```

### Claude Cowork

1. Open the plugin marketplace (puzzle-piece icon in the sidebar).
2. Click **Add custom plugin** and paste:
   `https://github.com/recoupable/recoup-research`
3. Approve the requested tool permissions.
4. Restart the Cowork session so manifests load.

### Codex

```bash
codex plugin install https://github.com/recoupable/recoup-research
```

### Cursor

1. Cursor → Settings → Plugins → **Add custom plugin**.
2. Paste the GitHub URL above.
3. Restart Cursor so `.cursor-plugin/plugin.json` loads.

### Via Marketplace

If you've already added the [Recoup marketplace](https://github.com/recoupable/marketplace):

```bash
/plugin install recoup-research@recoup-marketplace
```

## Setup

Set your Recoup API key (already set automatically in Recoup sandboxes):

```bash
export RECOUP_API_KEY="recoup_sk_..."
```

Don't have a key? Get one instantly:

```bash
curl -s -X POST "https://api.recoupable.com/api/agents/signup" \
  -H "Content-Type: application/json" \
  -d '{"email": "agent+'"$(date +%s)-$RANDOM"'@recoupable.com"}' | jq -r .api_key
```

## Skills

| Skill | What it does |
|-------|-------------|
| [recoup-weekly-brief](skills/recoup-weekly-brief) | **Customer-facing.** Dated, delta-focused weekly artist brief. Fires 5 endpoints in parallel, diffs vs the prior brief, writes a markdown file the customer opens every Monday. |
| [recoup-new-release-monitor](skills/recoup-new-release-monitor) | Confirms a release went live and builds a launch-day alert — what dropped, where it's landing, first streaming signal. |
| [recoup-streaming-check](skills/recoup-streaming-check) | Streaming-health spot-check — diffs the current snapshot vs the last check, flags spikes/drops, names the likely driver. |
| [recoup-tiktok-per-song](skills/recoup-tiktok-per-song) | **Customer-facing.** Per-song TikTok signal view. The API has no per-song TikTok counts, so this builds signal from activity feeds + cited web research and refuses to fabricate numbers. Targets the #1 customer ask. |
| [recoup-release-pack](skills/recoup-release-pack) | **Customer-facing.** Structured pre-release marketing brief: 3 visualizer directions, 5 content angles, ranked playlist targets, platform hooks, narrative thread. Grounded input for downstream creative work, not finished assets. |
| [recoup-artist-research](skills/recoup-artist-research) | Full artist research sweep — profile, metrics, audience, playlists, competitive position. The default one-shot entry point. |
| [recoup-playlist-intelligence](skills/recoup-playlist-intelligence) | Playlist pitching targets, gap analysis, catalog optimization. Find which playlists peers are on that you aren't. |
| [recoup-audience-analysis](skills/recoup-audience-analysis) | Audience demographics, geographic strategy, TikTok-to-Spotify pipeline, tour routing, market expansion. |
| [recoup-competitive-analysis](skills/recoup-competitive-analysis) | Head-to-head comparison, roster benchmarking, collaboration targets, release timing strategy. |
| [recoup-trend-detection](skills/recoup-trend-detection) | A&R discovery (anchor + similar + web), viral song autopsy. Find emerging artists before they blow up. |
| [recoup-people-outreach](skills/recoup-people-outreach) | Industry people search, contact enrichment, outreach draft generation, CRM enrichment. |
| [recoup-web-intelligence](skills/recoup-web-intelligence) | Web search, deep research, URL extraction, entity enrichment. Also the graceful degradation fallback. |

## Commands

| Command | What it does |
|---------|-------------|
| `/recoup-research [artist]` | Full research sweep → executive brief |
| `/recoup-scout [genre]` | A&R discovery → ranked scouting report |
| `/recoup-pitch [artist]` | Playlist pitch targets → ranked pitch list |
| `/recoup-compare [A] vs [B]` | Head-to-head comparison → gap analysis |

## Agents

| Agent | Focus |
|-------|-------|
| research-analyst | Deep research synthesis — executive briefs with specific numbers |
| market-scout | Trend detection — find emerging artists and market opportunities |

## API Coverage

This plugin wraps the current Recoup research API surface (backed by Songstats;
entity IDs are short alphanumeric strings):

- **Artist data:** profile, metrics (16 platform sources), audience, similar, playlists, tracks, career, insights, milestones, URLs
- **ID-based detail:** albums, track detail, track playlists (provider IDs from search)
- **Discovery:** search (`type=artists|tracks|labels`) + similar artists (anchor-based; there's no standalone discover/charts/genres endpoint)
- **Web intelligence:** web search, deep research, people search, URL extraction, entity enrichment

Removed in the Songstats migration (don't call them): `cities`, `charts`,
`discover`, `genres`, `festivals`, `radio`, `venues`, `rank`, `instagram-posts`,
`playlist`/`curator` detail. Geography now comes from `audience`; discovery from
`similar` + `web`.

Full endpoint documentation: [developers.recoupable.com](https://developers.recoupable.com)

## Layout

```
skills/
├── recoup-artist-research/     # Full artist research sweep
├── recoup-playlist-intelligence/ # Playlist pitching & gaps
├── recoup-audience-analysis/   # Demographics & geography
├── recoup-competitive-analysis/ # Comparison & positioning
├── recoup-trend-detection/     # Discovery & viral autopsy
├── recoup-people-outreach/     # People search & outreach
├── recoup-weekly-brief/        # Recurring dated artist brief
├── recoup-new-release-monitor/ # Launch-day drop confirmation + alert
├── recoup-streaming-check/     # Streaming spike/drop spot-check
└── recoup-web-intelligence/    # Web research fallback
commands/
├── recoup-research.md          # /recoup-research
├── recoup-scout.md             # /recoup-scout
├── recoup-pitch.md             # /recoup-pitch
└── recoup-compare.md           # /recoup-compare
agents/
├── research-analyst.md         # Deep synthesis persona
└── market-scout.md             # Discovery persona
references/
├── endpoints.md                # Full curl examples per endpoint
├── response-shapes.md          # Actual JSON response structures
└── workflows.md                # 11 multi-step research workflows
evals/                          # Validation fixtures
```

## Examples

### Research an artist

```
/recoup-research "Joy Crookes"
```

Returns a synthesized brief: streaming snapshot, geographic hotspots, audience demographics, playlist position, competitive landscape, and recommendations.

### Find playlist pitch targets

```
/recoup-pitch "Joy Crookes"
```

Returns a ranked list of playlists that similar artists are on but Joy Crookes isn't — sorted by peer overlap and follower reach.

### Scout emerging artists

```
/recoup-scout R&B --country US --listeners 50000-200000
```

Returns emerging R&B artists in the US filtered to 50K-200K monthly listeners (client-side on the metrics snapshot), ranked with cross-platform validation.

### Compare two artists

```
/recoup-compare "Joy Crookes" vs "Jorja Smith"
```

Returns a side-by-side comparison across every dimension: streaming metrics, playlists, audience, and geography.

## Support

- Email: `support@recoupable.com`
- Website: [recoupable.com](https://recoupable.com)
- Docs: [developers.recoupable.com](https://developers.recoupable.com)

## License

[Apache-2.0](./LICENSE)
