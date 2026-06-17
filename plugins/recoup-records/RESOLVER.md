# RESOLVER — recoup-records skill dispatcher (ROLLED-UP / fat-skill experiment)

> **Experiment branch.** 41 focused skills folded into **9 fat, mode-dispatching
> skills**, organized in **two tiers**: six **capability** skills (the label work)
> and three **operating** skills (how you run/configure the box). The A/B question
> vs the focused branch: does the model route + perform better with a handful of
> fat skills (mode picked inside the skill) or many narrow ones?
>
> **Routing implication:** you rarely disambiguate within a domain — route to the
> one skill and it picks its mode. The resolver's real job is the boundaries
> *between* the nine skills + which tier a request belongs to.
>
> **Read the matched skill's `SKILL.md` before acting.** Verified by
> `scripts/check_resolvable.py` (every skill reachable) and `resolver-eval.jsonl`.

## Tier 1 — Capabilities (the label work; each produces a deliverable)

| Intent (any of these) | Skill | Modes inside |
|---|---|---|
| create/onboard an artist · "what artists do I have" / list my roster · organize or update an artist's files/context | `recoup-artists` | create · workspace |
| research an artist · audience/demographics/markets · compare artists/positioning · find emerging talent · which playlists · find managers/A&R/press · which songs on TikTok · weekly brief · are streams spiking · search the web / deep research / enrich any company/label/venue/person | `recoup-research` | overview · audience · competition · discover · playlists · contacts · tiktok · weekly-update · web |
| caption · cover art/thumbnail/carousel/promo/quote card · short video · lyric video · visualizer/Canvas · reformat for platforms · content pack · react to a milestone/trend | `recoup-content` | caption · image · video · lyric-video · visualizer · reformat · pack · trend |
| plan a release · creative brief · rollout schedule · RELEASE.md / DSP pitch / one-sheet · did the release drop / launch alert · release demo | `recoup-releases` | plan · brief · campaign · doc · monitor · demo |
| review/underwrite a catalog deal · clean a data room · catalog valuation (with files) · build the dashboard · IC memo/financing pack PDF · value from public data (no files) · deal demo | `recoup-catalogs` | review · ingest · value · dashboard · report · estimate · demo |
| analyze a song from audio (BPM/key/genre/mood/lyrics/mix) · find the hook · playlist pitch / sync brief | `recoup-songs` | analyze · hook · pitch |

## Tier 2 — Operating the box (config / plumbing; not a label deliverable)

| Intent (any of these) | Skill | Modes inside |
|---|---|---|
| first-run "set up / connect Recoup" · scaffold my sandbox / build my workspace folders | `recoup-setup` | connect · scaffold |
| call the Recoup API directly · fetch any platform resource · run a connector (Google Docs/Drive/Gmail/TikTok) · edit a pasted Doc/Sheet URL | `recoup-api` | (raw access) |
| "remember this" / "that worked" / capture a reusable lesson into the learnings store | `recoup-learn` | (capture) |

---

## Cross-skill disambiguation (the boundaries that matter)

- **Audio vs data.** From a song's **audio file** (hook, mix, BPM, lyric
  transcription, sync brief) → `recoup-songs`. From **research data / the web**
  (catalog playlist strategy, audience, metrics) → `recoup-research`.
- **Valuation fork.** With seller files **or** from public data only — both are
  `recoup-catalogs` (value vs estimate modes).
- **Playlists.** Catalog-wide playlist *strategy* (no audio) → `recoup-research`
  (playlists). A single song's playlist *pitch* from its audio → `recoup-songs`.
- **Briefs.** A recurring artist performance brief → `recoup-research`
  (weekly-update). A pre-release creative brief → `recoup-releases` (brief).
- **"Make something for a milestone."** The reactive post → `recoup-content`
  (trend). The underlying milestone *data* → `recoup-research`.
- **Tier boundary — work vs operating the box:**
  - Onboard/organize an artist (roster work) → `recoup-artists`. Research an
    existing artist → `recoup-research`. First-run connect/scaffold → `recoup-setup`.
  - "What artists do I have" (inventory) → `recoup-artists` (workspace). "Scaffold
    my sandbox" (build the tree) → `recoup-setup` (scaffold). Different jobs.
  - A raw REST/connector call → `recoup-api`. A domain task → that capability
    skill, which makes its own calls via the same API.
