# RESOLVER — Recoup Skills dispatcher (domain-grouped)

> The plugin's routing table for every skill in `skills/`. Capability and platform
> skills are named `recoup-[domain]-[verb]-[noun]`; internal staff skills are named
> `recoup-internal-[domain]-[verb]-[noun]` and are gated behind the `recoup-internal`
> keyword (Tier 3). The domain prefix tells you the room, the verb+noun tail tells
> you the job.
>
> **Read the matched skill's `SKILL.md` before acting.** Verified by
> `scripts/check_resolvable.py` (every skill has a route; every route resolves) and
> `scripts/run_resolver_eval.py` (routing fixtures + full coverage).

## Tier 1 — Capabilities (the label work)

### roster — your artists
| Intent | Skill |
|---|---|
| onboard / add / create a new artist, "set up [artist]", new signing | `recoup-roster-add-artist` |
| "what artists do I have", list my roster, what's in this sandbox | `recoup-roster-list-artists` |
| organize / update one artist's files, brand, or context | `recoup-roster-manage-artist` |

### research — intelligence
| Intent | Skill |
|---|---|
| research [artist], overview, audience/markets, compare artists, collaborators, which songs on TikTok | `recoup-research-artist-overview` |
| find emerging/unsigned artists, A&R scouting, why a song went viral | `recoup-research-find-talent` |
| which playlists to target, placement gaps, editorial vs algorithmic | `recoup-research-playlist-targets` |
| find managers/A&R/press + draft outreach | `recoup-research-find-contacts` |
| weekly brief, what changed this week, are streams spiking | `recoup-research-weekly-brief` |
| search the web, deep research, enrich any company/label/venue/person | `recoup-research-the-web` |

### song — single-song audio
| Intent | Skill |
|---|---|
| analyze a song's audio: BPM/key/genre/mood, lyrics, mix critique | `recoup-song-analyze-audio` |
| find the hook, best 5–15s to clip | `recoup-song-find-hook` |
| playlist pitch + sync brief from the audio | `recoup-song-placement-pitch` |

### content — assets
| Intent | Skill |
|---|---|
| write a caption in the artist's voice | `recoup-content-write-caption` |
| cover art / thumbnail / carousel / promo / quote card | `recoup-content-make-graphics` |
| short video / lyric video / visualizer / reformat for platforms | `recoup-content-make-video` |
| a whole content pack (15–30 assets) for one song | `recoup-content-asset-pack` |
| react to a milestone/trend, make something timely | `recoup-content-reactive-post` |

### release — release workflow
| Intent | Skill |
|---|---|
| plan/run a release, creative brief, rollout schedule, RELEASE.md/DSP pitch/one-sheet | `recoup-release-plan-rollout` |
| did the single drop, launch-day alert | `recoup-release-track-drop` |

### catalog — catalog deals
| Intent | Skill |
|---|---|
| review/underwrite a catalog deal, clean a data room, value with files, dashboard, IC memo | `recoup-catalog-review-deal` |
| value a catalog from public data only (no seller files) | `recoup-catalog-estimate-value` |

## Tier 2 — Platform (operate the system; not a label deliverable)
| Intent | Skill |
|---|---|
| first-run "set up / connect Recoup", verify email, get an API key | `recoup-platform-connect-account` |
| scaffold my sandbox / build my workspace folders | `recoup-platform-build-workspace` |
| call the Recoup API directly, fetch a resource, run a connector (Docs/Gmail/TikTok) | `recoup-platform-api-access` |
| "remember this" / capture a reusable lesson | `recoup-platform-capture-lesson` |

## Tier 3 — Internal (Recoup staff only · gated by the `recoup-internal` keyword)

> OFF by default. Route here **only** when the request explicitly contains the
> literal keyword `recoup-internal`. Never use these for customer-facing or artist
> work — they operate Recoup's own engineering and go-to-market systems.

| Intent | Skill |
|---|---|
| "recoup-internal" + write/maintain a GitHub tracking issue | `recoup-internal-dev-issue-tracker` |
| "recoup-internal" + implement/ship a tracked issue end-to-end (docs-first, TDD) | `recoup-internal-dev-ship-issue` |
| "recoup-internal" + benchmark/audit/grade a skill pack or plugin | `recoup-internal-eval-skill-benchmark` |
| "recoup-internal" + work the Attio catalog-valuation sales funnel | `recoup-internal-funnel-valuation-pipeline` |
| "recoup-internal" + account-health / account-status snapshot for a Recoup account | `recoup-internal-account-health-report` |
| "recoup-internal" + draft/ship/measure LinkedIn or X posts | `recoup-internal-social-ship-posts` |

---

## Cross-skill disambiguation (the boundaries that matter)

- **Audio vs data.** From a song's **audio file** (hook, mix, BPM, lyrics, sync
  brief) → the `recoup-song-*` skills. From **research data / the web** (catalog
  playlist strategy, audience, metrics) → the `recoup-research-*` skills.
- **Playlists.** Catalog-wide playlist *strategy* (no audio) →
  `recoup-research-playlist-targets`. A single song's playlist *pitch* from its audio
  → `recoup-song-placement-pitch`.
- **Valuation fork.** With seller files → `recoup-catalog-review-deal`. From public
  data only → `recoup-catalog-estimate-value`.
- **Briefs.** A recurring artist performance brief → `recoup-research-weekly-brief`.
  A pre-release creative brief → `recoup-release-plan-rollout` (brief mode).
- **"Make something for a milestone."** The reactive post →
  `recoup-content-reactive-post`. The underlying milestone *data* →
  `recoup-research-artist-overview`.
- **Roster vs platform.** Add/list/manage artists → the `recoup-roster-*` skills.
  First-run connect/scaffold → `recoup-platform-connect-account` /
  `recoup-platform-build-workspace`. A raw REST/connector call →
  `recoup-platform-api-access`.
