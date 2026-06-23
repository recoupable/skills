# Skill Rename Proposal — v3 (uniform `recoup-[domain]-[verb]-[noun]`)

> **Supersedes v2 (`skill-rename-proposal.md`).** v2 explored *deliverable-led,
> freeform* names (`recoup-graphic-designer`, `recoup-pitch-this-song`,
> `recoup-research-an-artist`) with no fixed prefix. v3 commits to the opposite:
> **one uniform convention** — every skill is `recoup-[domain]-[verb]-[noun]`,
> exactly four words, domain-first.
>
> **Target shape:** the current fat skills unfold into a domain-grouped middle tier
> — the empirically-recommended hybrid between the fat-skill and focused extremes
> (see `ab-eval-results.md` and `experiment-rolled-up-skills.md`). Fat
> skills won top-level routing; focused skills won discoverability. This splits the
> *capability* domains (where discovery matters) while keeping the *workflow*
> domains (release, catalog) mostly folded behind one orchestrator.

## The convention

- **`recoup-[domain]-[verb]-[noun]` — exactly 4 words.** The verb+noun tail makes
  every name self-describing. The test: would a non-technical music marketer know
  what it does from the name alone?
- **Domain-first** so the `/` menu auto-clusters by domain when sorted.
- **Domains are job-named, not source-named.** It's `research`, not `web` — the
  data source (open web vs Songstats API) is an implementation detail the user
  shouldn't have to think about. Only fall back to a mechanism word when there is
  no honest job word (the sole case: `platform-api-access`).
- **No singletons in the capability tier.** No capability domain is left as a
  singleton; weak/singleton domains (`setup`, `api`, `learn`, `scout`, `playlist`,
  `outreach`, `web`) were absorbed into broader job-named domains.

## Two tiers

- **Platform** — operate the Recoup system itself (auth, access, memory).
- **Capability** — the label work: `roster · research · song · content · release · catalog`.

---

## The skills

### platform — operate the system

| Skill | Fires on |
|---|---|
| `recoup-platform-connect-account` | first-run: verify email, get API key |
| `recoup-platform-build-workspace` | scaffold the org/artist folder tree |
| `recoup-platform-api-access` | raw API resources + run a connector (Docs/Gmail/TikTok) |
| `recoup-platform-capture-lesson` | "remember this so we don't redo it" |

### roster — your artists

| Skill | Fires on |
|---|---|
| `recoup-roster-add-artist` | onboard / add a new artist |
| `recoup-roster-list-artists` | "what artists do I have", list my roster |
| `recoup-roster-manage-artist` | work inside one artist's files/context, update their brand |

### research — intelligence

| Skill | Fires on |
|---|---|
| `recoup-research-artist-overview` | full research sweep on one of your artists (audience/competition/tiktok = modes) |
| `recoup-research-find-talent` | find emerging/unsigned artists (A&R scouting) |
| `recoup-research-playlist-targets` | which playlists to target + placement gaps |
| `recoup-research-find-contacts` | find managers/A&R/press + draft outreach |
| `recoup-research-weekly-brief` | recurring "what changed" + streaming-spike check |
| `recoup-research-the-web` | open-web / deep research + enrich any entity (label, venue, person) |

### song — single-song audio

| Skill | Fires on |
|---|---|
| `recoup-song-analyze-audio` | BPM/key/genre/mood, lyrics, mix critique |
| `recoup-song-find-hook` | best 5–15s of a song to clip |
| `recoup-song-placement-pitch` | playlist pitch + sync brief (from the audio) |

### content — assets

| Skill | Fires on |
|---|---|
| `recoup-content-write-caption` | caption in the artist's voice |
| `recoup-content-make-graphics` | cover art / thumbnail / carousel / promo / quote card |
| `recoup-content-make-video` | short video, lyric video, visualizer, per-platform reformat |
| `recoup-content-asset-pack` | batch of 15–30 assets for one song |
| `recoup-content-reactive-post` | react to a real milestone/trend ("they just hit 1M") |

### release — release workflow

| Skill | Fires on |
|---|---|
| `recoup-release-plan-rollout` | full end-to-end workflow (brief / campaign / RELEASE.md = phases) |
| `recoup-release-track-drop` | did the single drop + launch-day alert |

### catalog — catalog deals

| Skill | Fires on |
|---|---|
| `recoup-catalog-review-deal` | full diligence (ingest / value / dashboard / IC memo = phases) |
| `recoup-catalog-estimate-value` | quick value from public streaming data, no seller files |

---

## How the fat skills unfold

| Current fat skill | Modes | Unfolds into |
|---|---|---|
| `recoup-setup` | connect, scaffold | `recoup-platform-connect-account`, `recoup-platform-build-workspace` |
| `recoup-api` | (raw access) | `recoup-platform-api-access` |
| `recoup-learn` | (capture) | `recoup-platform-capture-lesson` |
| `recoup-artists` | create, workspace | `recoup-roster-add-artist`, `recoup-roster-list-artists`, `recoup-roster-manage-artist` |
| `recoup-research` | overview, audience, competition, discover, playlists, contacts, tiktok, weekly-update, web | `recoup-research-artist-overview` (overview+audience+competition+tiktok), `recoup-research-find-talent`, `recoup-research-playlist-targets`, `recoup-research-find-contacts`, `recoup-research-weekly-brief`, `recoup-research-the-web` |
| `recoup-songs` | analyze, hook, pitch | `recoup-song-analyze-audio`, `recoup-song-find-hook`, `recoup-song-placement-pitch` |
| `recoup-content` | caption, image, video, lyric-video, visualizer, reformat, pack, trend | `recoup-content-write-caption`, `recoup-content-make-graphics`, `recoup-content-make-video` (video+lyric-video+visualizer+reformat), `recoup-content-asset-pack`, `recoup-content-reactive-post` |
| `recoup-releases` | plan, brief, campaign, doc, monitor, demo | `recoup-release-plan-rollout` (plan+brief+campaign+doc+demo), `recoup-release-track-drop` |
| `recoup-catalogs` | review, ingest, value, dashboard, report, estimate, demo | `recoup-catalog-review-deal` (review+ingest+value+dashboard+report+demo), `recoup-catalog-estimate-value` |

**Net:** capability domains split toward their browseable deliverables;
workflow domains (release, catalog) keep one fat orchestrator + one standalone
entry (`track-drop`, `estimate-value`) that users genuinely browse for separately.

## Naming alternates considered (kept on record)

- `recoup-content-asset-pack` ↔ `recoup-content-bulk-assets` (volume-led)
- `recoup-content-reactive-post` ↔ `recoup-content-moment-post` (less jargon)
- `recoup-song-placement-pitch` — "placement" is the umbrella for playlist + sync

## Next steps (not yet done)

1. `git mv` each current skill dir → new name; update `name:` frontmatter +
   cross-references + `scripts/vendored.json` paths.
2. Where a fat skill splits into several (setup, artists, research, content),
   carve the mode bodies/references into the new skill dirs.
3. Rewrite the `RESOLVER.md` routing table for the domain-grouped layout.
4. Rewrite `resolver-eval.jsonl` fixtures — one positive per skill + the
   cross-skill `not` constraints (audio-vs-data, song-pitch-vs-playlist-targets,
   reactive-post-vs-research, weekly-brief-vs-release).
5. Run the gates: `check_resolvable.py`, `run_resolver_eval.py`,
   `portability_lint.py`, `check_vendored.py`, `validate_manifests.py`.
