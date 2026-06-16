# Experiment: rolled-up (fat) skills vs focused skills

> A/B test of skill granularity for `recoup-records`. Two branches hold two
> variants of the **same** capabilities so we can compare how the model routes
> and performs.

## The two variants

| | Focused (control) | Rolled-up (treatment) |
|---|---|---|
| **Branch** | `recoup-label-in-a-box` | `experiment/rolled-up-skills` |
| **Skill count** | 41 | **6** |
| **Shape** | many narrow skills; the resolver picks the skill | a handful of fat skills; the resolver picks the skill, then the **skill body picks the mode** |
| **Routing burden** | on the resolver (41-way) | split: resolver (6-way) + in-skill mode dispatch |

## What rolled up into what

Six fat, mode-dispatching skills absorb the entire plugin (songwriting was
removed):

- **`recoup-research`** ← artist-research, audience, competition, scout, playlists,
  outreach, tiktok, brief, web-intelligence (9) · modes: overview · audience ·
  competition · discover · playlists · contacts · tiktok · weekly-update · web
- **`recoup-content`** ← content (router), caption, image, video, lyric-video,
  visualizer, pack, reformat, trend (9) · modes: caption · image · video ·
  lyric-video · visualizer · reformat · pack · trend
- **`recoup-release`** ← release start, brief, campaign, doc, demo, monitor (6) ·
  modes: plan · brief · campaign · doc · monitor · demo
- **`recoup-catalog`** ← deal start, ingest, value, dashboard, report, demo,
  catalog-value (7) · modes: review · ingest · value · dashboard · report ·
  estimate · demo
- **`recoup-song`** ← song analyze, hook, pitch-kit (3) · modes: analyze · hook · pitch
- **`recoup-platform`** ← setup, setup-sandbox, api, artist-create, artist-workspace,
  learn (6) · modes: setup · sandbox · api · create-artist · workspace · learn

**`recoup-songwriting` was removed** (capability dropped, not folded). Nothing else
stayed standalone — the plugin is now 6 fat skills, end to end.

All references/scripts/templates each cluster needed were carried into the fat
skill (union, deduped), so capability is preserved — only the packaging changed.

## How to run the A/B

```bash
# control (focused)
git checkout recoup-label-in-a-box
#   install recoup-records, then run the test prompts

# treatment (rolled-up / fat)
git checkout experiment/rolled-up-skills
#   install recoup-records, then run the SAME test prompts
```

### What to measure (same prompts on both)

1. **Trigger accuracy** — does the right skill fire from a vague ask? On the fat
   branch the description is broader (many sub-intents in one), so watch for
   *over-firing* (fat skill grabs an unrelated ask) and *under-firing* (the broad
   description is too diffuse to match). `resolver-eval.jsonl` encodes the intents
   to try (43 positives spanning every sub-mode + 10 cross-skill negatives).
2. **Mode selection** — once a fat skill fires, does the model pick the correct
   *mode* from the body? (This burden doesn't exist on the focused branch.)
3. **Execution quality** — does the model follow the right procedure, or does the
   bigger body cause it to skip steps / blend modes?
4. **Context cost** — the fat skills load a larger body + more references on
   invocation; compare tokens/latency.
5. **Cross-skill forks** — the genuinely confusable boundaries (audio vs data,
   value-with-files vs public estimate, catalog playlist strategy vs single-song
   pitch, write-vs-analyze a song). Both branches must get these right.

### Test prompts

Use the `intent` strings in `plugins/recoup-records/resolver-eval.jsonl` (this
branch) — they cover every sub-mode and the cross-skill negatives. Same gates run
on both branches: `check_resolvable.py` (reachability), `run_resolver_eval.py`
(structural routing + coverage), `portability_lint.py`.

## Hypotheses

- **For:** fewer skills = less resolver ambiguity at the top level; related modes
  share context so the model reasons about a domain holistically; fewer
  "dark"/duplicate skills.
- **Against:** a broad description is a fuzzier trigger; a big body invites
  step-skipping / mode-blending; you pay the full body's context cost even when
  you only need one mode (vs the focused skill's tight body).

The point of the branch is to find out empirically, not to assume.
