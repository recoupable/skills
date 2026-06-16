# Skill naming & description convention

> Build-time reference for skill authors (including non-engineers building their
> own skills). This doc is **not shipped** with any install and a `SKILL.md` must
> **never** link to it — embody the guidance as behavior instead.

A skill's `name` and `description` do three jobs at once. Optimize for all three —
they don't compete:

1. **Browse-discovery (human).** A user scans the `/` list and thinks *"wait, I
   can do that?"* The name is a billboard for a capability.
2. **Tag-by-name (human).** Users invoke skills by naming them mid-prompt
   ("use the brand-kit skill and the caption skill to…"). Names must be
   memorable and sayable.
3. **Auto-trigger (agent).** The agent matches a vague request to a description
   and fires the skill without being named. Descriptions are the trigger.

Most users are not good prompters. Jobs 1–2 expand *what they know they can do*;
job 3 expands *how they prompt*. A good skill serves all three.

---

## Naming convention

**Pattern:** `recoup-{domain}-{action|thing}` — domain first, ≤ 3 tokens.

- **Domain first** so the alphabetical list self-groups by subject. Domains are a
  small, stable set: `setup · artist · song · content · deal · release`. New
  skills slot into an existing domain; we rarely add a domain.
- **Action or thing second**, whichever a human would say:
  - Action skills take a **verb**: `recoup-song-analyze`, `recoup-deal-value`.
  - Artifact skills take a **noun**: `recoup-deal-dashboard`, `recoup-release-doc`.
- **Never four tokens.** `recoup-content-cover-art`, not
  `recoup-content-create-coverart`. (The action lives in the description; the
  name stays scannable.)
- **Front doors keep `-start`:** `recoup-deal-start`, `recoup-release-start`.
- **The skim test:** from the name alone, would Molly (a non-technical music
  marketer) know roughly what it does? If not, rename.

This matches the scope-token + modality guidance in `capability-plugins.md`.

---

## Description template

```text
<Plain-English what + the win — one sentence a musician understands, no jargon>.
Use when <situations / trigger phrases the user would actually say>.
<Modes it covers, if merged>. <Needs X / outputs Y, if relevant>.
```

Rules:

- **Lead with the human benefit**, third person, zero jargon. The first sentence
  is the billboard *and* the agent's primary signal.
- **Then the triggers** — real phrases a user would type ("find the hook",
  "did my release drop"). This is what fires auto-trigger.
- **Persona via situation, never a gate.** Write "Use when reviewing, selling, or
  financing a catalog" (implies buyer/seller/lender) — not "For catalog buyers"
  (which makes the agent skip it for a seller and makes a human feel excluded).
- **Merged skills must advertise their modes** in the description so a browsing
  user still discovers them: "…covers lyrics, mix critique, metadata, and hook."
- **Mechanics go in the body, not the description.** No `POST /api/...`,
  `account_id`, "async run", or "8 sequential API calls" in the description —
  they waste the always-in-context budget and lose the human.
- Keep it to ~1–2 sentences + triggers. Trim run-ons.

---

## Granularity: when to merge skills into modes

The only real tension is overwhelm (fewer skills) vs discovery (visible
capabilities). Resolve it with one test:

> **Merge into a parent-with-modes only when (a) the parent name still evokes a
> clear capability, and (b) each mode is something a user would naturally say.
> Never hide a capability a user wouldn't otherwise know exists. When unsure,
> keep it visible.**

The model is the `rostrum-brand-kit` skill: one browseable name, invoked with
"use the *space heater* brand" — the mode is sayable, so the merge works.

Applying the test:

| Cluster | Decision | Why |
| --- | --- | --- |
| Song (7) | **Merge → 2** (`recoup-song-analyze`, `recoup-song-pitch`) | All operate on one audio file; modes (lyrics, mix, metadata / hook, playlist, sync) are sayable and advertised in the description. |
| Graphics (3) | **Merge → 1** (`recoup-content-graphic`) | Interchangeable still-image formats from similar inputs. |
| Setup (2) | **Merge → 1** (`recoup-setup`) | Sandbox scaffolding is a branch of first-run setup. |
| Onboarding (2) | **Merge → 1** (`recoup-artist-create`) | Folder conventions become a reference inside create. |
| Pre-release brief (2, duplicate) | **Merge → 1** (`recoup-release-brief`) | True duplicate across two plugins. |
| **Monitors (3)** | **Keep split** | "Did my release drop", "are streams spiking", "what's new this week" are three distinct high-intent things a user browses for. Burying them as modes of one "monitor" hides capability — fails the discovery test. |

---

## Overlap / disambiguation checklist

Because the agent auto-routes, two skills must never both look right for one
request. For every pair on the same topic:

- Each description names its lane ("use me for X, use `recoup-…` for Y").
- On-demand vs scheduled twins each state their mode in the first sentence
  ("Ask now…" vs "Runs weekly and saves…").
- No two skills share the same trigger phrases.

---

## Migration map (current → proposed)

**As built: 43 skills.** From the 6 plugins: 48 → 41 (song −4 (7→3), graphics −2 (3→1),
release-pack duplicate −1). Plus 2 curated standalone skills pulled into the bundle by the
generator's `EXTRA_SKILLS` map: `recoup-songwriting` (from `skills/song-writing`) and
`recoup-catalog-value` (from `skills/catalog-value-estimator`, input-gated vs
`recoup-deal-value`). `chart-metric`, `issue-implementation`, `issue-management`, and the 4
plugin-duplicated standalones (music-industry-research, content-creation, short-video,
release-management) were deliberately left out.

The `setup-sandbox`, `artist-workspace`, and 3-monitor merges in the table below were
**not** applied — per the granularity rule *"when unsure, keep it visible"*, each is a
distinct browse intent (same call as keeping the monitors split). They were renamed for
consistency but kept as separate skills. Optional future add: `recoup-account-profile` (→ 42).

### setup (→ 2)
| Current | Becomes |
| --- | --- |
| recoup-setup, recoup-setup-sandbox | `recoup-setup` (sandbox mode) |
| recoup-api | `recoup-api` |

### artist (→ 11)
| Current | Becomes |
| --- | --- |
| recoup-create-artist, recoup-artist-workspace | `recoup-artist-create` |
| recoup-artist-research | `recoup-artist-research` (router) |
| recoup-audience-analysis | `recoup-artist-audience` |
| recoup-competitive-analysis | `recoup-artist-competition` |
| recoup-playlist-intelligence | `recoup-artist-playlists` |
| recoup-people-outreach | `recoup-artist-outreach` |
| recoup-trend-detection | `recoup-artist-scout` |
| recoup-tiktok-per-song | `recoup-artist-tiktok` |
| recoup-weekly-brief | `recoup-artist-brief` |
| recoup-streaming-check | `recoup-artist-streaming` |
| recoup-web-intelligence | `recoup-web-research` (utility) |

### song (→ 2)
| Current | Becomes |
| --- | --- |
| recoup-song-analyzer, recoup-song-metadata, recoup-song-lyrics, recoup-song-mix-feedback | `recoup-song-analyze` (modes: report / metadata / lyrics / mix) |
| recoup-song-hook, recoup-song-playlist-pitch, recoup-song-sync-brief | `recoup-song-pitch` (modes: hook / playlist / sync) |

### content (→ 11)
| Current | Becomes |
| --- | --- |
| recoup-content | `recoup-content` (router) |
| recoup-short-video | `recoup-content-video` |
| recoup-brand-voice-caption | `recoup-content-caption` |
| recoup-content-pack | `recoup-content-pack` |
| recoup-content-reformat | `recoup-content-reformat` |
| recoup-carousel, recoup-promo-graphic, recoup-quote-cards | `recoup-content-graphic` (modes: carousel / promo / quote) |
| recoup-cover-art | `recoup-content-cover-art` |
| recoup-thumbnail | `recoup-content-thumbnail` |
| recoup-lyric-video | `recoup-content-lyric-video` |
| recoup-visualizer | `recoup-content-visualizer` |
| recoup-trend-jack | `recoup-content-trend` |

### deal (→ 6)
| Current | Becomes |
| --- | --- |
| recoup-deal-start | `recoup-deal-start` (orchestrator) |
| recoup-deal-ingest | `recoup-deal-ingest` |
| recoup-deal-analysis | `recoup-deal-value` |
| recoup-deal-dashboard | `recoup-deal-dashboard` |
| recoup-deal-report | `recoup-deal-report` |
| recoup-deal-demo | `recoup-deal-demo` |

### release (→ 6)
| Current | Becomes |
| --- | --- |
| recoup-release-start | `recoup-release-start` (orchestrator) |
| recoup-release-campaign | `recoup-release-campaign` |
| recoup-release-doc | `recoup-release-doc` |
| recoup-release-marketing-brief, recoup-release-pack | `recoup-release-brief` |
| recoup-release-demo | `recoup-release-demo` |
| recoup-new-release-monitor | `recoup-release-monitor` |

### optional
| New | Purpose |
| --- | --- |
| `recoup-account-profile` | Capture who the user is (artist / manager / label / investor) + goals, so every skill tailors output and routing. |

---

## Execution order

1. Rename in place with `git mv` (preserves history); update `name:` frontmatter,
   cross-references, READMEs, and `scripts/vendored.json` paths.
2. Merge clusters: compose the parent skill, move each former skill's body into a
   mode/reference, advertise modes in the description, delete the old dirs.
3. Rewrite descriptions to the template.
4. Re-sync vendored copies; regenerate the bundle
   (`python3 scripts/build_records_plugin.py`); run all four gates.
