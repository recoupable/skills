# RESOLVER — recoup-records skill dispatcher (ROLLED-UP / fat-skill experiment)

> **Experiment branch.** This is the *rolled-up* variant: 41 focused skills folded
> into **12** — five fat, mode-dispatching skills (`recoup-research`,
> `recoup-content`, `recoup-release`, `recoup-catalog`, `recoup-song`) plus seven
> standalone foundation/utility skills. The A/B question vs the focused branch:
> does the model route + perform better with a few fat skills (where the *mode* is
> picked inside the skill body) or many narrow ones?
>
> **Routing implication:** within a domain you no longer pick a sub-skill — you
> route to the **one** fat skill and it picks the mode from the ask. So this table
> is short, and intra-domain disambiguation is the skill's job, not the resolver's.
>
> **Read the matched skill's `SKILL.md` before acting.** Verified by
> `scripts/check_resolvable.py` (every skill reachable) and
> `resolver-eval.jsonl` (intents route to the right fat skill).

## Foundation / setup

| Intent | Skill |
|---|---|
| First-run connect — verify email/PIN, issue + persist an API key | `recoup-setup` |
| Scaffold the whole account's folders on a fresh sandbox | `recoup-setup-sandbox` |
| Call the Recoup API / connectors directly (raw access) | `recoup-api` |
| Create / onboard / enrich a new artist (and set up their folder) | `recoup-artist-create` |
| Operate inside an existing artist's directory (enumerate/edit) | `recoup-artist-workspace` |

## The five fat skills (each picks its own mode)

| Intent (any of these) | Fat skill | Modes inside |
|---|---|---|
| research an artist · audience/demographics/markets · compare artists/positioning · find emerging talent · which playlists · find managers/A&R/press · which songs on TikTok · weekly brief · are streams spiking · search the web / deep research / enrich any company/label/venue/person | `recoup-research` | overview · audience · competition · discover · playlists · contacts · tiktok · weekly-update · web |
| caption · cover art/thumbnail/carousel/promo/quote card · short video · lyric video · visualizer/Canvas · reformat for platforms · content pack · react to a milestone/trend | `recoup-content` | caption · image · video · lyric-video · visualizer · reformat · pack · trend |
| plan a release · creative brief · rollout schedule · RELEASE.md / DSP pitch / one-sheet · did the release drop / launch alert · release demo | `recoup-release` | plan · brief · campaign · doc · monitor · demo |
| review/underwrite a catalog deal · clean a data room · catalog valuation (with files) · build the dashboard · IC memo/financing pack PDF · value from public data (no files) · deal demo | `recoup-catalog` | review · ingest · value · dashboard · report · estimate · demo |
| analyze a song from audio (BPM/key/genre/mood/lyrics/mix) · find the hook · playlist pitch / sync brief | `recoup-song` | analyze · hook · pitch |

## Standalone utility

| Intent | Skill |
|---|---|
| Write/evaluate lyrics & song concepts (no audio) | `recoup-songwriting` |
| Capture a solved problem / "remember this" into the learnings store | `recoup-learn` |

---

## Cross-skill disambiguation (the forks that still matter at the skill level)

These are the boundaries *between* fat skills — the resolver's real job now:

- **Audio vs data.** Anything from a song's **audio file** (hook, mix, BPM, lyric
  transcription, sync brief) → `recoup-song`. Anything from **research data / the
  web** (catalog playlist strategy, audience, metrics) → `recoup-research`.
- **Valuation fork.** Value **with seller files / a data room** → `recoup-catalog`
  (value mode). Value from **public data only, no files** → `recoup-catalog`
  (estimate mode). Both live in `recoup-catalog`.
- **Playlists.** Catalog-wide playlist *strategy* (no audio) → `recoup-research`
  (playlists). A single song's playlist *pitch* from its audio → `recoup-song`
  (pitch).
- **Briefs.** A recurring artist performance brief → `recoup-research`
  (weekly-update). A pre-release creative brief → `recoup-release` (brief).
- **Write vs analyze a song.** Write lyrics from scratch (no audio) →
  `recoup-songwriting`. Analyze an existing recording → `recoup-song`.
- **"Make something for a milestone."** The reactive post → `recoup-content`
  (trend). The underlying milestone *data* → `recoup-research`.
- **Create vs operate.** Bring a new artist into existence → `recoup-artist-create`.
  Work inside an artist's existing folder → `recoup-artist-workspace`.
