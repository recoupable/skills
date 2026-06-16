# RESOLVER — recoup-records skill dispatcher (ROLLED-UP / fat-skill experiment)

> **Experiment branch.** This is the *maximal* rolled-up variant: 41 focused
> skills folded into **6 fat, mode-dispatching skills** — the entire plugin. The
> A/B question vs the focused branch: does the model route + perform better with a
> handful of fat skills (where the *mode* is picked inside the skill body) or many
> narrow ones?
>
> **Routing implication:** you almost never disambiguate within a domain — you
> route to the **one** fat skill and it picks the mode from the ask. The resolver's
> real job is now just the boundaries *between* the six skills.
>
> **Read the matched skill's `SKILL.md` before acting.** Verified by
> `scripts/check_resolvable.py` (every skill reachable) and
> `resolver-eval.jsonl` (intents route to the right fat skill).

## The six fat skills (each picks its own mode)

| Intent (any of these) | Fat skill | Modes inside |
|---|---|---|
| set up / connect Recoup · scaffold my sandbox · call the API or a connector (Google Docs/Drive/Gmail/TikTok) · create/onboard an artist · "what artists do I have" / organize an artist's files · "remember this" / capture a learning | `recoup-platform` | setup · sandbox · api · create-artist · workspace · learn |
| research an artist · audience/demographics/markets · compare artists/positioning · find emerging talent · which playlists · find managers/A&R/press · which songs on TikTok · weekly brief · are streams spiking · search the web / deep research / enrich any company/label/venue/person | `recoup-research` | overview · audience · competition · discover · playlists · contacts · tiktok · weekly-update · web |
| caption · cover art/thumbnail/carousel/promo/quote card · short video · lyric video · visualizer/Canvas · reformat for platforms · content pack · react to a milestone/trend | `recoup-content` | caption · image · video · lyric-video · visualizer · reformat · pack · trend |
| plan a release · creative brief · rollout schedule · RELEASE.md / DSP pitch / one-sheet · did the release drop / launch alert · release demo | `recoup-release` | plan · brief · campaign · doc · monitor · demo |
| review/underwrite a catalog deal · clean a data room · catalog valuation (with files) · build the dashboard · IC memo/financing pack PDF · value from public data (no files) · deal demo | `recoup-catalog` | review · ingest · value · dashboard · report · estimate · demo |
| analyze a song from audio (BPM/key/genre/mood/lyrics/mix) · find the hook · playlist pitch / sync brief | `recoup-song` | analyze · hook · pitch |

---

## Cross-skill disambiguation (the forks between the six skills)

These are the boundaries *between* fat skills — the resolver's real job now:

- **Audio vs data.** Anything from a song's **audio file** (hook, mix, BPM, lyric
  transcription, sync brief) → `recoup-song`. Anything from **research data / the
  web** (catalog playlist strategy, audience, metrics) → `recoup-research`.
- **Valuation fork.** Value **with seller files / a data room**, or value from
  **public data only** — both are `recoup-catalog` (value vs estimate modes).
- **Playlists.** Catalog-wide playlist *strategy* (no audio) → `recoup-research`
  (playlists). A single song's playlist *pitch* from its audio → `recoup-song`
  (pitch).
- **Briefs.** A recurring artist performance brief → `recoup-research`
  (weekly-update). A pre-release creative brief → `recoup-release` (brief).
- **"Make something for a milestone."** The reactive post → `recoup-content`
  (trend). The underlying milestone *data* → `recoup-research`.
- **Artist setup vs research.** Create/onboard or organize an artist's files →
  `recoup-platform` (create-artist / workspace). Research an existing artist →
  `recoup-research`.
- **API vs domain skill.** A raw REST/connector call or first-run setup →
  `recoup-platform` (api / setup). A domain task (research/content/release/deal/
  song) → that domain's fat skill, which makes its own calls.
