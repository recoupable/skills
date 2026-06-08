# Tickets — Deep E2E Review

Actionable tickets distilled from `e2e-review/FIXES.md` (deep pass, 2026-06-07,
7 record-label personas, live API). Related findings that share one fix are merged
into a single ticket; every FIXES ID is traced in **Source**.

**Priority mapping:** P0 = S1 blocker (silently wrong / can't complete) · P1 = S2
major · P2 = S3 minor · P3 = S4 polish.

**Fix locus** — *where the work has to happen*:
- 🏠 **In-repo** — fixable here with skill/doc/script edits (teach the agent the
  right call, shape, or guardrail). No other team needed.
- 🔀 **Both** — ship an in-repo mitigation **now** (graceful handling / correct
  call), but full resolution also needs an external change (the **API** repo, the
  **research provider** Songstats, or the **Flamingo** model/preset). Each 🔀 ticket
  splits acceptance criteria + tests into *In-repo now* vs *External (blocks full fix)*.

**Order:** in-repo tickets first (**RCP-001–016**), then the 6 external-dependency
tickets last (**RCP-017–022**). No ticket is purely external — every one has an
in-repo action. See [External dependencies](#external-dependencies).

**How to close a ticket:** check `- [ ] DONE` only when every acceptance-criteria
box **and** the **Test** box(es) below it pass.

> Many references are **vendored** (`content-api.md`, `flamingo-api.md`, research
> `endpoints.md`/`response-shapes.md`). Edit the **canonical** copy, then re-sync
> per `scripts/vendored.json` and run `python3 scripts/check_vendored.py`.

## Board

| ID | P | Locus | Title | Source | Done |
|---|---|---|---|---|---|
| RCP-001 | P0 | 🏠 In-repo | Switch activity feed `milestones` → `career`; collapse `career`/`insights` | A-1, D-2, A-2 | ☐ |
| RCP-002 | P0 | 🏠 In-repo | Deals: manifest provider label ≠ normalizer key → silent valuation loss | E-1, E-2, E-3 | ☐ |
| RCP-003 | P0 | 🏠 In-repo | Standalone `content-creation`/`short-video` carry pre-fix async image contract | G-2 | ☐ |
| RCP-004 | P0 | 🏠 In-repo | Flamingo invents structure past audio length → validate timestamps/lyrics vs duration | B-3, B-4 | ☐ |
| RCP-005 | P1 | 🏠 In-repo | Onboarding routes to standalone tier + smoke test returns nothing | F-2, F-1 | ☐ |
| RCP-006 | P1 | 🏠 In-repo | Two skill tiers collide on the same triggers with no deferral | G-1, G-3 | ☐ |
| RCP-007 | P1 | 🏠 In-repo | Static-graphic skills prescribe a video-only QA step (`analyze` 400s on images) | C-4 | ☐ |
| RCP-008 | P1 | 🏠 In-repo | Standardize a "resolve-or-disclose" step across research skills | A-4, A-8 | ☐ |
| RCP-009 | P2 | 🏠 In-repo | `tracks` instrumental/version dupes → false "new releases" | A-5 | ☐ |
| RCP-010 | P2 | 🏠 In-repo | Release skills declare `license: Proprietary` / `status: draft` vs plugin Apache-2.0 | D-3 | ☐ |
| RCP-011 | P2 | 🏠 In-repo | `name:` ≠ directory slug (`chartmetric`, `songwriting`) | G-4 | ☐ |
| RCP-012 | P2 | 🏠 In-repo | `recoup-create-artist` prereqs list only Bearer; setup issues an API key | F-3 | ☐ |
| RCP-013 | P2 | 🏠 In-repo | Document `web` POST `formatted` field | A-7 | ☐ |
| RCP-014 | P2 | 🏠 In-repo | Deal demo AHA depends on a manual `assumptions.yaml` overwrite | E-4 | ☐ |
| RCP-015 | P2 | 🏠 In-repo | Workspace artist name can collide with a real provider entity | A-9 | ☐ |
| RCP-016 | P2 | 🏠 In-repo | Reconcile cross-preset inconsistency in `recoup-song-analyzer` | B-5 | ☐ |
| RCP-017 | P0 | 🔀 Both | `music_theory` returns unparseable string; add defensive preset parser | B-1, B-2, B-6 | ☐ |
| RCP-018 | P0 | 🔀 Both | `/research/audience` always empty → detect + disclose, don't emit hollow demographics | A-3, C-3, D-1 | ☐ |
| RCP-019 | P1 | 🔀 Both | Content cost estimate: pack POSTs (405); `estimate` ignores `type=image` | C-2, C-1 | ☐ |
| RCP-020 | P2 | 🔀 Both | `/accounts/id` vs `/accounts/{id}` report different IDs | F-4 | ☐ |
| RCP-021 | P2 | 🔀 Both | `similar` ignores weighting params (provider can't weight) + caveat | A-6 | ☐ |
| RCP-022 | P2 | 🔀 Both | `caption` returns `font:null`; mark `content` a draft | C-5 | ☐ |

## External dependencies

The 6 tickets below (RCP-017–022) need a change outside this repo for a *complete*
fix. Each still has an in-repo mitigation that should ship regardless.

| Ticket | External owner | What they must change |
|---|---|---|
| RCP-017 | API / Flamingo model (`/api/songs/analyze`) | `music_theory` preset should emit valid JSON + a non-degenerate chord cycle |
| RCP-018 | API + provider (Songstats) / account plan | `/research/audience` returns empty for all artists — fix provider mapping or document the tier that unlocks it |
| RCP-019 | API (`/api/content/estimate`) | add real `type=image` pricing (currently ignores `type`, returns the video price) |
| RCP-020 | API (`/api/accounts/id` + `/accounts/{id}`) | align the two IDs (or document the active-account-id vs record-id distinction) |
| RCP-021 | API + provider (`/research/similar`) | support weighted matching (genre/audience/mood); passing weights currently errors |
| RCP-022 | API (`/api/content/caption`) | return a real `font` instead of `null` |

---

# In-repo tickets

## RCP-001 · P0 · Switch activity feed `milestones` → `career`
- [ ] **DONE** — all criteria + test below pass

**Source:** A-1, D-2, A-2 (was RCP-001) · **Area:** recoup-research, recoup-releases (Phase 6) ·
**Locus:** 🏠 In-repo (the data already exists at `/research/career` — just point the skills at it)

**Problem.** `/research/milestones` returns `[]` for *every* artist tested (Laufey,
Sabrina Carpenter — both actively charting), while `/research/career` and
`/research/insights` carry the real activity feed (20 items: track/album charts,
playlist adds, video). Skills that use `milestones` as the activity source produce
empty "what's new / did it drop / what drove the spike" sections — the whole reason
they exist. `career` and `insights` are also byte-identical, so any skill calling
both wastes a credit.

**Affected files.**
- `plugins/recoup-research/skills/{recoup-weekly-brief,recoup-new-release-monitor,recoup-streaming-check,recoup-artist-research,recoup-trend-detection,recoup-tiktok-per-song}/SKILL.md`
- their vendored `references/endpoints.md` + `references/response-shapes.md`
- `plugins/recoup-releases/skills/recoup-release-start/SKILL.md` (Phase 6 references the monitors)

**Fix / acceptance criteria.**
- [ ] All six research skills read activity from `/research/career` (fallback `insights`); `milestones` demoted to optional or removed.
- [ ] `endpoints.md` documents `career` == `insights` (pick `career` canonical) and notes `milestones` is currently empty.
- [ ] No skill fetches both `career` and `insights`.
- [ ] Vendored copies re-synced.

**Test.**
- [ ] Re-run `weekly-brief` + `new-release-monitor` on Laufey → activity section lists the 20 real `career` items (not "quiet week").
- [ ] `grep -rl "research/milestones" plugins/recoup-research` returns nothing (or only an "is empty" note); no skill greps both `career` and `insights`.
- [ ] `python3 scripts/check_vendored.py` exits 0.

**Evidence.** `e2e-review/deep/A-research/{milestones-laufey.json (==[]), career-laufey.json (20 items)}`.

---

## RCP-002 · P0 · Deals provider-vocabulary mismatch → silent valuation loss
- [ ] **DONE** — all criteria + test below pass

**Source:** E-1, E-2, E-3 (was RCP-002) · **Area:** recoup-deals (ingest) ·
**Locus:** 🏠 In-repo (both scripts + the SKILL live here)

**Problem.** `build-file-manifest.py` emits human labels (`ASCAP`, `The MLC`,
`SoundExchange`, `YouTube`, or `None`), but `normalize-royalty-statement.py
--provider` requires lowercase keys (`ascap`, `mlc`, `soundexchange`,
`youtube-content-id`). The deal-start SKILL says to pass the manifest's
`likely_provider` straight to `--provider` — which fails for **every** provider.
A dropped provider is silently excluded from the ledger → understated valuation.
In testing, losing YouTube moved top-1 concentration from the intended ~35% to
29.77%, suppressing the materiality finding. No coverage assertion catches it.

**Affected files.**
- `plugins/recoup-deals/skills/recoup-deal-ingest/scripts/build-file-manifest.py`
- `plugins/recoup-deals/skills/recoup-deal-ingest/scripts/normalize-royalty-statement.py`
- `plugins/recoup-deals/skills/recoup-deal-start/SKILL.md` (Phase 2 step 2a)
- vendored script copies in `recoup-deal-analysis` / `recoup-deal-dashboard` scripts/

**Fix / acceptance criteria.**
- [ ] Manifest emits a canonical `provider_key` field (exact `--provider` value) alongside the display label; `None`/unclassified files (e.g. distributor) get a header-sniff fallback or are queued, never silently skipped.
- [ ] deal-start Phase 2 passes `provider_key`, not the display label.
- [ ] Before concentration/valuation, assert `appended_provider_count == expected_provider_count`; on mismatch, fail loud and list dropped providers.
- [ ] Vendored copies re-synced.

**Test.**
- [ ] Run `recoup-deal-demo` end-to-end on the 5-provider demo catalog → all 5 normalize, the coverage assertion passes, top-1 concentration reproduces ~35%.
- [ ] Negative test: drop one provider file → the coverage assertion fails loud and names the dropped provider (does not silently understate).
- [ ] `python3 scripts/check_vendored.py` exits 0.

**Evidence.** `e2e-review/deep/E-deals/deals/demo-catalog/` + manifest label vs `--help` key table in FIXES E-1.

---

## RCP-003 · P0 · Standalone content skills carry the pre-fix async image contract
- [ ] **DONE** — all criteria + test below pass

**Source:** G-2 (was RCP-003) · **Area:** standalone skills (`content-creation`, `short-video`) ·
**Locus:** 🏠 In-repo (doc edits; the API already behaves correctly — the skill text is stale)

**Problem.** `skills/content-creation/SKILL.md:23` still says "Image and video
generation are async — they return a `runId`." Image generation is actually **sync**
(`{imageUrl, images}`, confirmed ~20s live). A user on the standalone skill polls
`/tasks/runs?runId=…` for an asset that already returned → hangs. The plugin's
`content-api.md` was corrected in the prior run; the standalone tier was not.

**Affected files.**
- `skills/content-creation/SKILL.md`
- `skills/short-video/SKILL.md`, `skills/short-video/references/short-video-manual.md`

**Fix / acceptance criteria.**
- [ ] Standalone content skills state image + caption + video `animate` are **sync**; only `create`/edit (`PATCH`) are async.
- [ ] Align the contract with the plugin's `content-api.md` (sync/async table, GET estimate, transcribe `audio_urls[]`).
- [ ] Decide: vendor the corrected contract into the standalone skills (+ register in `scripts/vendored.json`) **or** deprecate them in favor of the plugin (see RCP-006).

**Test.**
- [ ] `grep -nE "async|runId" skills/content-creation/SKILL.md skills/short-video/SKILL.md` shows image gen described as sync (no "poll runId" for images).
- [ ] Live image-gen smoke from the standalone skill returns `{imageUrl}` directly, with no polling step.
- [ ] If vendored: `python3 scripts/check_vendored.py` exits 0.

**Evidence.** `e2e-review/deep/C-content/image-run.json` (sync `{imageUrl,images}`).

---

## RCP-004 · P0 · Validate Flamingo timestamps/lyrics against real audio duration
- [ ] **DONE** — all criteria + test below pass

**Source:** B-3, B-4 (was RCP-005) · **Area:** recoup-song-analysis ·
**Locus:** 🏠 In-repo (guard against the model's hallucination client-side; no API change needed)

**Problem.** On a 30-second preview, `sync_brief_match` returned `best_sync_moments`
up to `2:20-2:50` — it invented a full ~3-minute structure. `recoup-song-hook` feeds
those windows to a video skill → out-of-range clips. `lyric_transcription` likewise
returns partial, mid-word lyrics on previews with no warning.

**Affected files.**
- `plugins/recoup-song-analysis/skills/{recoup-song-hook,recoup-song-sync-brief,recoup-song-lyrics,recoup-lyric-video}/SKILL.md`
- `plugins/recoup-song-analysis/references/flamingo-api.md`

**Fix / acceptance criteria.**
- [ ] Hook + sync-brief fetch/know the true duration and discard or clamp any window beyond it.
- [ ] All song skills detect preview audio (short duration or `p.scdn.co/mp3-preview` host) and warn "preview = partial; supply full audio."

**Test.**
- [ ] Run `recoup-song-hook` on a 30s preview → returns ≤1 valid window, every window `end ≤ duration`; 5-window over-range output no longer occurs.
- [ ] Run any song skill on a `p.scdn.co/mp3-preview` URL → the "preview = partial" warning is printed.

**Evidence.** `e2e-review/deep/B-song/{sync_brief_match.json,lyric_transcription.json}`.

---

## RCP-005 · P1 · Onboarding routes to the standalone tier and demos an empty call
- [ ] **DONE** — all criteria + test below pass

**Source:** F-2, F-1 (was RCP-008) · **Area:** recoup-essentials (`recoup-setup`) ·
**Locus:** 🏠 In-repo (routing/copy edits; the smoke-test swap depends on RCP-018 but the fix here is local)

**Problem.** `recoup-setup`'s seeded memory block + "Which skill to reach for" table
list only the standalone skills — never the richer plugins (`recoup-research` (12),
`recoup-content` (13), `recoup-releases` (5), `recoup-song-analysis` (7),
`recoup-deals` (6)). And the Step 8 smoke test tells a new user to "pull audience
demographics," which returns nothing (RCP-018). Worst first impression at the
moment of adoption.

**Affected files.** `plugins/recoup-essentials/skills/recoup-setup/SKILL.md` (Steps 7–8).

**Fix / acceptance criteria.**
- [ ] Memory block + routing table name the plugin routers (`recoup-research`, `recoup-content`, `recoup-song-analyzer`, `recoup-release-start`, `recoup-deal-start`) and explain the standalone↔plugin relationship (RCP-006).
- [ ] Smoke test uses a call that returns rich data today (e.g. monthly listeners or current playlist placements).

**Test.**
- [ ] `grep` the seeded memory block → all 5 plugin routers are named.
- [ ] Run the Step-8 smoke call as written → returns non-empty data (no empty-audience dead end).

**Evidence.** FIXES F-1/F-2.

---

## RCP-006 · P1 · Two skill tiers collide on the same triggers with no deferral
- [ ] **DONE** — all criteria + test below pass

**Source:** G-1, G-3 (was RCP-009) · **Area:** standalone skills vs plugins (cross-cutting) ·
**Locus:** 🏠 In-repo (description/policy edits; `chartmetric` needs its own token but that's a config note, not an API change)

**Problem.** None of the 8 standalone skills reference/defer to the plugins, so up
to 4 skills fire on one request ("make a TikTok for X" → `content-creation` +
`short-video` + `recoup-content` + `recoup-short-video`). Research collides across
**two providers** (`chartmetric` = Chartmetric, `music-industry-research` =
Songstats), and `chartmetric` needs `CHARTMETRIC_REFRESH_TOKEN` (not provisioned by
setup) so it triggers but fails for Recoup users.

**Affected files.** `skills/{content-creation,short-video,music-industry-research,chart-metric,release-management,streaming-growth,trend-to-song}/SKILL.md` (descriptions).

**Fix / acceptance criteria.**
- [ ] Decide the canonical tier policy (recommend: standalone = portable no-plugin fallback).
- [ ] Each standalone skill's description adds "if the `recoup-<x>` plugin is installed, prefer it."
- [ ] `chartmetric` description states it requires its own token and is opt-in; Recoup users are pointed at the research tier for provider-consistent numbers.

**Test.**
- [ ] `grep "if the recoup-" skills/*/SKILL.md` → every standalone skill with a plugin twin defers to it.
- [ ] `chart-metric/SKILL.md` description mentions `CHARTMETRIC_REFRESH_TOKEN` + opt-in.
- [ ] Dry-run trigger "make a TikTok for X" → review which descriptions match and confirm a single clear winner (no 4-way collision).

**Evidence.** FIXES G-1 collision table; grep showing zero plugin cross-refs.

---

## RCP-007 · P1 · Static-graphic skills prescribe an image-incompatible QA step
- [ ] **DONE** — all criteria + test below pass

**Source:** C-4 (was RCP-010) · **Area:** recoup-content ·
**Locus:** 🏠 In-repo (agent reads the PNG itself; no server-side image-analyze endpoint required)

**Problem.** The router's "verify before claiming done → analyze the result" points
at `/content/analyze`, which is video-only (400s on stills). That makes the QA step
impossible for `cover-art`, `thumbnail`, `quote-cards`, `promo-graphic`, `carousel`
(5 of 13 skills).

**Affected files.** `plugins/recoup-content/skills/recoup-content/SKILL.md` (step 5) + the 5 image skills.

**Fix / acceptance criteria.**
- [ ] Image skills get an image-aware QA path (agent visual read of the PNG, dimension/aspect check, unwanted-text check) instead of the video analyzer.
- [ ] Router step 5 distinguishes image vs video QA.

**Test.**
- [ ] Generate a `cover-art` PNG → run the new image QA path; it confirms dimensions/aspect and flags stray text, with **no** `/content/analyze` call on the image.
- [ ] `grep` the 5 image skills → none route stills through `/content/analyze`.

**Evidence.** FIXES C-4 (+ prior TEST-LOG ticket #2).

---

## RCP-008 · P1 · Standardize a "resolve-or-disclose" step across research skills
- [ ] **DONE** — all criteria + test below pass

**Source:** A-4, A-8 (was RCP-011) · **Area:** recoup-research ·
**Locus:** 🏠 In-repo (skill-logic guardrails on responses the API already returns)

**Problem.** Skills mostly describe the happy path. A nonexistent artist returns a
clean `{"status":"error"}` and a fresh key returns empty `organizations`, but most
skills don't branch — they'd fire 5 endpoints that all error, or imply an empty
roster is the answer.

**Affected files.** All `plugins/recoup-research/skills/*/SKILL.md`; cross-ref `recoup-essentials/skills/recoup-api` stop rule.

**Fix / acceptance criteria.**
- [ ] Every research skill has a first "resolve-or-stop" step: on `.status=="error"`/empty results, tell the user "couldn't resolve {artist}" with the search fallback.
- [ ] On empty `organizations`, state that an empty roster is expected for a new key and research works by name (mirror the `recoup-api` stop rule).

**Test.**
- [ ] Run a research skill on a nonsense artist (`"zzzznotanartist"`) → it stops with "couldn't resolve" + search fallback, not 5 cascading errors.
- [ ] Run a roster-browse skill with an empty-org key → it explains the empty roster is expected, doesn't present it as "no artists."

**Evidence.** FIXES A-4, A-8.

---

## RCP-009 · P2 · `tracks` instrumental/version dupes → false "new releases"
- [ ] **DONE** — all criteria + test below pass

**Source:** A-5 (was RCP-012) · **Locus:** 🏠 In-repo ·
**Files:** `plugins/recoup-research/skills/recoup-new-release-monitor/SKILL.md` (+ any `tracks` consumer).

**Fix / acceptance criteria.**
- [ ] Dedup by base title (strip ` - Instrumental` / ` - Sped Up` / ` - Live` / ` (feat. …)`) before reporting new releases.

**Test.**
- [ ] Feed `tracks-laufey.json` through the skill → instrumental/sped-up variants collapse into their parent; the "new releases" count matches distinct songs.

**Evidence.** `e2e-review/deep/A-research/tracks-laufey.json`.

---

## RCP-010 · P2 · Release skills' license/status frontmatter contradicts the plugin
- [ ] **DONE** — all criteria + test below pass

**Source:** D-3 (was RCP-013) · **Locus:** 🏠 In-repo ·
**Files:** `plugins/recoup-releases/skills/recoup-release-*/SKILL.md`.

**Fix / acceptance criteria.**
- [ ] Set `license: Apache-2.0` (or drop to inherit from the plugin) and flip `status` off `draft`.

**Test.**
- [ ] `grep -nE "^(license|status):" plugins/recoup-releases/skills/recoup-release-*/SKILL.md` shows no `Proprietary` / `draft`.
- [ ] `python3 scripts/validate_manifests.py` exits 0.

---

## RCP-011 · P2 · `name:` ≠ directory slug
- [ ] **DONE** — all criteria + test below pass

**Source:** G-4 (was RCP-014) · **Locus:** 🏠 In-repo ·
**Files:** `skills/chart-metric/SKILL.md` (`name: chartmetric`), `skills/song-writing/SKILL.md` (`name: songwriting`).

**Fix / acceptance criteria.**
- [ ] Align frontmatter `name` to the directory slug (or rename dirs with `git mv`); update any cross-refs + `scripts/vendored.json` if paths change.

**Test.**
- [ ] For both skills, frontmatter `name` == directory slug.
- [ ] `python3 scripts/portability_lint.py` and `python3 scripts/check_vendored.py` exit 0.

---

## RCP-012 · P2 · `recoup-create-artist` prereqs omit the API-key path
- [ ] **DONE** — all criteria + test below pass

**Source:** F-3 (was RCP-015) · **Locus:** 🏠 In-repo ·
**Files:** `plugins/recoup-essentials/skills/recoup-create-artist/SKILL.md`.

**Fix / acceptance criteria.**
- [ ] State "either `RECOUP_API_KEY` (x-api-key) or `RECOUP_ACCESS_TOKEN` (Bearer)" to match `recoup-api`.

**Test.**
- [ ] `grep -nE "RECOUP_API_KEY|x-api-key" plugins/recoup-essentials/skills/recoup-create-artist/SKILL.md` → both auth methods documented.

---

## RCP-013 · P2 · Document `web` POST `formatted` field
- [ ] **DONE** — all criteria + test below pass

**Source:** A-7 (was RCP-018) · **Locus:** 🏠 In-repo ·
**Files:** research `endpoints.md` / `response-shapes.md` (canonical + vendored).

**Fix / acceptance criteria.**
- [ ] Document the `{formatted, results, status}` shape; note skills may surface `formatted` directly.

**Test.**
- [ ] `grep -n "formatted" plugins/recoup-research/**/references/{endpoints,response-shapes}.md` → field documented.
- [ ] `python3 scripts/check_vendored.py` exits 0.

**Evidence.** `e2e-review/deep/A-research/web-laufey.json`.

---

## RCP-014 · P2 · Deal demo AHA depends on a manual `assumptions.yaml` overwrite
- [ ] **DONE** — all criteria + test below pass

**Source:** E-4 (was RCP-019) · **Locus:** 🏠 In-repo ·
**Files:** `plugins/recoup-deals/skills/recoup-deal-demo/` (fixtures + SKILL).

**Fix / acceptance criteria.**
- [ ] Ship a dedicated `fixtures/demo-data-room/assumptions.yaml` (threshold 25) and copy it verbatim instead of relying on the heredoc-overwrite step.

**Test.**
- [ ] Run `recoup-deal-demo` straight through (no manual overwrite) → threshold 25 is applied and the materiality/AHA finding appears.

---

## RCP-015 · P2 · Workspace artist name can collide with a real provider entity
- [ ] **DONE** — all criteria + test below pass

**Source:** A-9 (was RCP-020) · **Locus:** 🏠 In-repo ·
**Files:** `recoup-artist-workspace` / research resolution skills.

**Fix / acceptance criteria.**
- [ ] When a workspace artist resolves to a provider match, show the matched `name/site_url` and confirm identity before attaching metrics.

**Test.**
- [ ] Resolve workspace artist "Gatsby Grace" → skill surfaces the matched provider `name/site_url` and asks to confirm before attaching metrics (no silent attach to the wrong entity).

**Evidence.** `q=Gatsby Grace` resolved to a real Songstats artist.

---

## RCP-016 · P2 · Reconcile cross-preset inconsistency in the song analyzer
- [ ] **DONE** — all criteria + test below pass

**Source:** B-5 (was RCP-022) · **Locus:** 🏠 In-repo ·
**Files:** `plugins/recoup-song-analysis/skills/recoup-song-analyzer/SKILL.md`.

**Fix / acceptance criteria.**
- [ ] Pick a canonical source per field (tempo from `catalog_metadata`, comps from `similar_artists`) and note values are independent model estimates — don't present two BPMs/comp-lists silently.

**Test.**
- [ ] Run the analyzer on a track that previously showed BPM 88 vs 85 → output presents one canonical BPM + one comp list, with an "estimates may vary by preset" note.

**Evidence.** BPM 88 vs 85; differing comp lists across presets.

---

# External-dependency tickets (do in-repo mitigation now; full fix blocked upstream)

## RCP-017 · P0 · `music_theory` returns an unparseable string; add a defensive parser
- [ ] **DONE (in-repo)** — in-repo criteria + in-repo test pass
- [ ] **DONE (external)** — upstream fix shipped + external test passes

**Source:** B-1, B-2, B-6 (was RCP-004) · **Area:** recoup-song-analysis ·
**Locus:** 🔀 Both (in-repo parser makes it usable; the model/preset is the root cause)

**Problem.** `music_theory` is documented as JSON but `.response` came back as a
single-quoted Python dict string (`"{'key': 'Bb major', …}"`) that `jq` can't
parse; server "success" masks it. Skills keying off `.response.key`/
`.chord_progression` (`recoup-song-metadata`, `recoup-song-hook`) get nothing.
The chord progression also degenerates into a 3-chord loop to the token limit.

**Affected files.**
- `plugins/recoup-song-analysis/references/flamingo-api.md` (canonical) + vendored copies
- `plugins/recoup-song-analysis/skills/{recoup-song-metadata,recoup-song-hook,recoup-song-analyzer}/SKILL.md`

**Fix / acceptance criteria.**
*In-repo now —*
- [ ] Song skills parse defensively: try object → `json.loads` → single-quote→double-quote repair → fall back to text.
- [ ] `flamingo-api.md` documents that `music_theory` currently returns a string needing repair, and which presets are JSON vs text.
- [ ] Skills collapse repeated chords and mark harmonic data low-confidence.

*External (blocks full fix) — API / Flamingo model (`/api/songs/analyze`) —*
- [ ] `music_theory` preset emits valid JSON and a single, non-degenerate chord cycle so the in-repo repair becomes unnecessary.

**Test.**
- [ ] *In-repo:* feed the captured single-quoted `music_theory.json` string through the parser → `key` + `chord_progression` recovered, repeated chords collapsed.
- [ ] *External:* after the preset fix, the raw `.response` parses with `json.loads` directly (no repair) and the chord cycle is non-degenerate.

**Evidence.** `e2e-review/deep/B-song/music_theory.json`.

---

## RCP-018 · P0 · `/research/audience` always empty → detect + disclose
- [ ] **DONE (in-repo)** — in-repo criteria + in-repo test pass
- [ ] **DONE (external)** — upstream fix shipped + external test passes

**Source:** A-3, C-3, D-1 (was RCP-006) · **Area:** recoup-research, recoup-content, recoup-releases ·
**Locus:** 🔀 Both (in-repo graceful disclosure; external to actually return audience data)

**Problem.** `/research/audience` returned `[]` for every artist/platform tested
(Laufey, Addison Rae; instagram + tiktok). `recoup-audience-analysis` is built
entirely on it; `competitive-analysis`, `release-pack`, `artist-research`, the
release Phase-2 brief, and `content-pack`'s audience "moat" all degrade silently to
hollow demographics. May be plan/provider gating on a fresh key — but no skill
detects or explains it.

**Affected files.**
- `plugins/recoup-research/skills/{recoup-audience-analysis,recoup-competitive-analysis,recoup-release-pack,recoup-artist-research}/SKILL.md` + vendored `endpoints.md`
- `plugins/recoup-content/skills/recoup-content-pack/SKILL.md`
- `plugins/recoup-releases/skills/recoup-release-marketing-brief/SKILL.md`

**Fix / acceptance criteria.**
*In-repo now —*
- [ ] Every audience consumer checks for empty `audience[]` and either falls back to `web`/`deep` research or states "audience demographics unavailable for this artist/plan" — never prints an empty table as an answer.
- [ ] `endpoints.md` documents that `audience` is currently empty and how skills degrade.

*External (blocks full fix) — API + provider (Songstats) / account plan —*
- [ ] Determine whether `audience` is tier-gated or a provider-mapping bug; if gated, return a `checkoutUrl` skills can surface; if a bug, fix the provider mapping so real demographics return.

**Test.**
- [ ] *In-repo:* run `recoup-audience-analysis` on Laufey (empty `audience[]`) → it discloses "unavailable" or falls back to `web`/`deep`, never prints an empty table.
- [ ] *External:* after the upstream fix, `/research/audience?artist=Laufey` returns non-empty demographics and `recoup-audience-analysis` renders them.

**Evidence.** `e2e-review/deep/A-research/audience-tiktok-laufey.json` + Addison Rae probe.

---

## RCP-019 · P1 · Content cost-estimate is broken for batch + image paths
- [ ] **DONE (in-repo)** — in-repo criteria + in-repo test pass
- [ ] **DONE (external)** — upstream fix shipped + external test passes

**Source:** C-2, C-1 (was RCP-007) · **Area:** recoup-content ·
**Locus:** 🔀 Both (in-repo: fix the call to GET+batch; external: estimate has no image price)

**Problem.** `recoup-content-pack` gates spend with `POST /content/estimate` + a
body — but estimate is **GET** (`POST` → 405 verified) and ignores
`artist_account_id`/`count` (the param is `batch`). So the pack's headline safety
feature is broken. Separately, `estimate?type=image` returns the **video** price
($0.82) — `type` is a no-op, so the 5 image skills have no real estimate.

**Affected files.**
- `plugins/recoup-content/skills/recoup-content-pack/SKILL.md` (lines ~23–26)
- `plugins/recoup-content/references/content-api.md` (canonical) + vendored copies

**Fix / acceptance criteria.**
*In-repo now —*
- [ ] Pack uses `GET "$BASE/content/estimate?type=video&batch=$ASSET_COUNT"`; body dropped.
- [ ] `content-api.md` states `estimate` is video-priced and ignores `type`; image skills quote a flat image cost rather than calling estimate.
- [ ] Vendored copies re-synced.

*External (blocks full fix) — API (`/api/content/estimate`) —*
- [ ] Add real `type=image` pricing so image skills can call estimate instead of hardcoding a flat cost.

**Test.**
- [ ] *In-repo:* `GET /content/estimate?type=video&batch=5` returns a price; the pack no longer issues a `POST` (which 405s).
- [ ] *In-repo:* `python3 scripts/check_vendored.py` exits 0.
- [ ] *External:* `GET /content/estimate?type=image` returns an image-specific price (≠ the video $0.82).

**Evidence.** FIXES C-1/C-2 estimate probes; `POST` → 405 verified live.

---

## RCP-020 · P2 · `/accounts/id` vs `/accounts/{id}` ID mismatch
- [ ] **DONE (in-repo)** — in-repo criteria + in-repo test pass
- [ ] **DONE (external)** — upstream fix shipped + external test passes

**Source:** F-4 (was RCP-016) · **Locus:** 🔀 Both ·
**Files:** `plugins/recoup-essentials/skills/recoup-api/SKILL.md`.

**Fix / acceptance criteria.**
- [ ] *In-repo now:* document the active-account-id vs account-record-id distinction so the agent-account check is robust.
- [ ] *External (API):* align the two endpoints so they report the same ID and the doc workaround becomes unnecessary.

**Test.**
- [ ] *In-repo:* following the documented check, the agent correctly identifies its account despite the two IDs.
- [ ] *External:* `/accounts/id` and `/accounts/{id}` report the same identifier.

---

## RCP-021 · P2 · `similar` blends sonic + commercial adjacency; weighting params error
- [ ] **DONE (in-repo)** — in-repo criteria + in-repo test pass
- [ ] **DONE (external)** — upstream fix shipped + external test passes

**Source:** A-6 (was RCP-017) · **Locus:** 🔀 Both ·
**Files:** `recoup-trend-detection`, `recoup-competitive-analysis` SKILLs.

**Fix / acceptance criteria.**
- [ ] *In-repo now:* caveat that `similar` blends sonic + popularity adjacency (e.g. Laufey → SZA, Sabrina Carpenter), so don't treat it as a pure sound-alike list.
- [ ] *External (API + provider):* support weighted matching — passing `genre/audience/mood` weights currently returns `status:error` (Songstats doesn't weight).

**Test.**
- [ ] *In-repo:* skill output for Laufey includes the adjacency caveat and doesn't present `similar` as a pure sound-alike list.
- [ ] *External:* `GET /research/similar?artist=Laufey&genre=1&audience=0&mood=0` returns `status:ok` with a weighted set (today it returns `status:error`).

**Evidence.** `similar-laufey.json`; live `?genre=1&audience=0&mood=0` → `status:error`.

---

## RCP-022 · P2 · `caption` returns `font:null`; mark `content` a draft
- [ ] **DONE (in-repo)** — in-repo criteria + in-repo test pass
- [ ] **DONE (external)** — upstream fix shipped + external test passes

**Source:** C-5 (was RCP-021) · **Locus:** 🔀 Both ·
**Files:** `plugins/recoup-content/references/content-api.md`, `recoup-brand-voice-caption/SKILL.md`.

**Fix / acceptance criteria.**
- [ ] *In-repo now:* document `caption.content` as a draft and that `font` may be null, so a downstream overlay must default it.
- [ ] *External (API `/content/caption`):* return a real `font` instead of `null`.

**Test.**
- [ ] *In-repo:* `content-api.md` states caption is a draft + `font` may be null; the caption skill defaults the font before overlay.
- [ ] *External:* `/content/caption` response includes a non-null `font`.

**Evidence.** `caption.json`.

---

## Not ticketed (positives to preserve)
From FIXES G-5 + "what's strong": live data quality (`profile`, `metrics`,
`playlists`, `tracks`, `career`, `web`, `similar`); Flamingo `catalog_metadata` /
`sync_brief_match` / `content_advisory` / `audience_profile` / `mix_feedback`; sync
content image gen; the deterministic deal/release validators and the
"What I did NOT do" honesty recap (adopt repo-wide); the `recoup-api` "never invent
a roster" guardrail; `song-writing` as a clean standalone.
