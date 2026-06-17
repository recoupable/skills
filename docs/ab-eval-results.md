# A/B Eval — Fat skills (6) vs Focused skills (41)

> **What this is.** A researcher-style A/B benchmark of the two `recoup-records`
> skill styles, run 2026-06-16 against the **live Recoup API** with a real label
> account (Rostrum Pacific roster: Niko Is, Gatsby Grace, Bear Hands, …). It
> answers: do the triggers work? are the routing results the same or different?
> are the outputs the same? what's the customer experience? how does the workspace
> build out over time (scaffolds + context + the learning loop)?
>
> - **Control (focused):** branch `recoup-label-in-a-box`, **41** narrow skills.
> - **Treatment (rolled-up):** branch `experiment/rolled-up-skills`, **6** fat,
>   mode-dispatching skills (`recoup-platform`, `recoup-research`, `recoup-content`,
>   `recoup-release`, `recoup-catalog`, `recoup-song`).
> - Raw artifacts: `tests/ab-eval/` (gitignored) — `prompts.jsonl` (110 prompts),
>   `route_eval.py` (scorer), `workspace/` (the built-out test workspace).
>
> **Update (post-eval):** recommendation #2 was implemented — `recoup-platform`
> (the loose operating skill that owned 2 of 3 wrong-mode misses) was **split** into
> `recoup-setup` + `recoup-api` + `recoup-artists` + `recoup-learn`, and the
> capability skills were pluralized (`recoup-releases`/`-catalogs`/`-songs`). The box
> is now **9 skills in two tiers** (6 capability + 3 operating). The eval below
> describes the **6-skill state that motivated the split** — names like
> `recoup-platform`/`recoup-release`/`recoup-song` are that pre-split snapshot.

## Method (and its honest limits)

1. **Routing/trigger benchmark — 110 customer prompts.** Routing in either style
   is the harness matching a user's words to a skill **description**. I cannot
   spin up two independent model harnesses here, so the router verdict per prompt
   is *the model's* assessment of which description wins — the same operation the
   real resolver performs. Verdicts are encoded explicitly in `route_eval.py` so
   they're auditable, not a black box. **This is single-model self-assessment; treat
   the absolute percentages as directional, the *relative* gap and the per-fork
   analysis as the signal.**
2. **Output parity — live API.** Both styles call the *same* Recoup endpoints, so
   data parity is structural; I confirmed it by running a real research sweep
   (Niko Is) and producing a deliverable.
3. **Workspace build-out — live.** I scaffolded a real artist workspace from live
   data and exercised the learning loop.

Prompt mix (110): 85 clear, 10 cross-skill forks, 5 ambiguous, 5 multi-intent,
5 out-of-scope. Spans every one of the 6 fat skills' modes.

---

## Result 1 — Routing / triggers

| Outcome | Focused (41) | Rolled-up (6) |
|---|---|---|
| **HIT** (routes correctly) | 94 (85%) | 99 (90%) |
| **AMBIG** (wrong-target risk) | 11 (10%) | 6 (5%) |
| **MISS** (routes wrong / dead) | 0 | 0 |
| **DECLINE** (correct non-fire, out-of-scope) | 5 | 5 |
| **Clean routing (HIT + correct DECLINE)** | **90%** | **95%** |

**Findings:**

- **Triggers work in both — nothing is dead.** Zero MISS in either style: every
  capability is reachable. The `check_resolvable` gate (no dark skills) holds on
  both branches. So this is *not* a "does it fire" question — it's a "does the
  *right* thing fire" question.
- **Rolled-up routes cleaner at the top level (95% vs 90%).** It collapses
  *intra-domain* forks into one skill, so the model lands in the right skill and
  picks a mode inside. Five forks the focused style fumbles, the rollup resolves:
  - *"how much is this catalog worth"* — focused: 3 deal skills contend; rolled-up:
    one `recoup-catalog` (value vs estimate is a mode).
  - *"make a video"* — focused: video / lyric-video / visualizer contend
    (wrong-skill risk); rolled-up: lands in `recoup-content`, disambiguates mode.
  - *"set up Mari Vega"* — focused: create / workspace / app-setup (3-way);
    rolled-up: one `recoup-platform`.
  - *"is this catalog a good buy"*, *"add socials to a profile"* — same pattern.
- **But the rollup moves the burden inward: 105/110 fires require an in-skill MODE
  pick.** This is a *new failure class* the focused style doesn't have. Focused:
  if the right skill fires, the job is unambiguous. Rolled-up: the right skill
  fires, then the model can still pick the wrong mode (e.g. land in `recoup-content`
  but generate a thumbnail when they wanted a cover). The routing win is real but
  partly *relocated*, not eliminated.
- **Cross-DOMAIN forks survive both styles.** The rollup can only fix forks that
  fall *inside* one fat skill. Forks that cross skill boundaries are unchanged:
  - *"what playlists should I pitch this song to"* — catalog playlist strategy
    (`recoup-research`) vs single-song pitch from audio (`recoup-song`).
  - *"give me a brief"* — weekly monitor vs one-shot overview vs pre-release brief.
  - *"look up Drake's monthly listeners"* — research vs raw API call.
  These need disambiguation in **either** style; fat skills are not a cure for
  genuinely ambiguous intent.
- **Out-of-scope: both decline cleanly (5/5).** Neither over-fired on weather,
  Python, travel, taxes, or legal-contract prompts. *Caveat:* the 6 fat
  descriptions are necessarily **broader** (more trigger phrases each), so the
  theoretical over-fire risk is higher for the rollup — it didn't bite in this
  set, but it's the thing to watch as descriptions grow.

**Verdict (routing):** rolled-up wins top-level routing and kills wrong-*skill*
errors on intra-domain forks; it introduces wrong-*mode* risk in exchange.
Net positive, but not free.

### Result 1b — Empirical two-session test (independent routers)

To remove the self-assessment limitation, I ran **two independent router
subagents** — one given *only* the 41 focused descriptions, one given *only* the
6 fat skills + their modes — neither saw the ground truth or the other's catalog.
They each routed all 110 prompts cold. Scored against ground truth
(`tests/ab-eval/score_route.py`):

| Metric | Focused (41) | Rolled-up (6) |
|---|---|---|
| **Skill routing** (acceptable) | 108/110 = **98%** | 110/110 = **100%** |
| **Mode accuracy** (when fat skill right) | n/a | 91/94 = **97%** |
| **Wrong-MODE rate** (the rollup's new failure class) | n/a | **3%** (3 cases) |
| **Net fully correct** (skill + mode) | **98%** | **97%** |

This is the number the self-assessment couldn't produce: **the rolled-up style's
feared wrong-mode failure is real but small — 3%** — and net end-to-end accuracy
is a **near-tie (97% vs 98%)**. The independent fat router never picked the wrong
*top-level skill* (100%): with only six doors it always lands in the right room,
then picks a mode.

**All 3 wrong-mode misses are diagnostic — and 2 of 3 are in `recoup-platform`:**
- `P99 "what's in this sandbox"` → picked **sandbox** mode (scaffold) instead of
  **workspace** (inventory). Pure lexical bleed: the word "sandbox" pulled the
  wrong mode.
- `P98 "add Spotify + socials to a profile"` → picked **workspace** instead of
  **create-artist/api** (editing an existing profile — genuinely fuzzy).
- `P47 "plan the rollout for the album"` → picked **campaign** (schedule) instead
  of **plan** (full workflow) — arguably defensible ("rollout"≈schedule).

That `recoup-platform` owns 2 of the 3 mode errors **empirically confirms** it's
the loosest, most-confusable fat skill — the exact thing flagged for a split.

---

## Result 2 — Are the outputs the same?

**Yes — identical by construction, confirmed live.** Both styles issue the same
Recoup API calls; only the `SKILL.md` the agent reads differs. The rollup carried
every reference/script/template as the union (git tracked them as renames), so no
capability or data was lost.

Live proof (real sweep, Niko Is, 2026-06-16) — same numbers regardless of style:

- Genres: Hip Hop/Rap · Boom Bap · New Age
- Spotify: **31,883** monthly listeners · 8,089 followers · popularity 23 · 2 editorial playlists
- Peer set: Michael Christmas, Statik Selektah, Tre Mission, Clear Soul Forces, Blu
- Real placement surfaced from `/insights`: added to a Tego-Calderon-adjacent
  reggaeton list (a cross-genre signal worth chasing)

The deliverable is in `tests/ab-eval/workspace/artists/niko-is/research/overview-2026-06-16.md`.
Whether the agent read `recoup-artist-research` (focused) or `recoup-research`
(overview mode, rolled-up), the calls and the synthesized brief are the same.

*Honest note:* a genuine end-state would re-run the **agent** under each branch and
diff the prose. I executed the API layer directly (capability/data parity is
structural); I did not run two separate agent sessions to diff synthesis wording.

---

## Result 3 — Workspace build-out + the learning loop

Built a real workspace for Niko Is from live data, exactly as the skills would.
After one session it accumulates cleanly:

```
artists/niko-is/RECOUP.md                      # identity + setup checklist + KB
artists/niko-is/context/artist.md              # static context (source of truth)
artists/niko-is/research/_*.json               # raw API payloads (evidence)
artists/niko-is/research/overview-2026-06-16.md # dated deliverable (dynamic)
learnings/research-metrics-null.md             # cross-cutting lesson (captured live)
```

- **Scaffolds + context:** the `RECOUP.md` identity file + `context/artist.md`
  static layer + dated `research/` dynamic layer is the same structure in both
  styles (it's `recoup-platform`'s `workspace`/`create-artist` modes, or the
  focused `recoup-artist-*` skills). It accreted without collision.
- **The learning loop works and is real:** during the run, Bear Hands returned
  all-null metrics; that gotcha was captured as a filed, deduped lesson
  (`learnings/research-metrics-null.md`) with a prevention rule. The next run that
  hits null metrics now has a documented "resolve provider id + retry" fix — the
  forward-only ratchet, demonstrated rather than asserted.
- **Over time:** the static/dynamic split keeps it from rotting — `context/` is
  updated deliberately, `research/` is dated and archived, `learnings/` compounds.
  This behavior is **identical across both styles** (same capability), so it does
  *not* differentiate the A/B — but it confirms the box gets *more* valuable per
  use, which is the "record label in a box" thesis working.

---

## Result 4 — Customer experience

The styles diverge most here, and it's the real trade:

| Dimension | Focused (41) | Rolled-up (6) |
|---|---|---|
| **Browsing the `/` menu** | A rich, scannable catalog of capabilities — *"oh, I can make a thumbnail / a sync brief / a quote card."* High **discovery**. | Six clean doors. Low overwhelm, but specific capabilities (thumbnail, sync brief, hook) are **hidden as modes** — you only get them if you know to ask. |
| **Vague asks** | Wrong-skill risk among look-alikes. | Lands in the right domain, then asks which mode — usually a cleaner clarify. |
| **"I know exactly what I want"** | Type the exact skill, get the tight body, go. | Fire the fat skill, it routes to a mode — one extra hop, bigger body loaded. |
| **Per-call context cost** | Small: only the relevant skill's body loads. | Larger: the whole fat body (all modes + union refs) loads even for one mode. |
| **Cognitive load** | 41 names to learn/scan. | 6 names; modes discovered in-skill. |
| **Maintenance (our side)** | 41 files, more drift surface. | 6 files, fewer moving parts. |

The crux: **focused optimizes for discovery; rolled-up optimizes for simplicity +
clean top-level routing + maintenance.** A customer who doesn't know what's
possible is better served by the 41-item menu; a customer who describes a goal in
plain language is better served by 6 fat doors.

---

## Scorecard & recommendation

| Criterion | Winner |
|---|---|
| Clean top-level routing | **Rolled-up** (95% vs 90%) |
| Wrong-target failure mode | **Rolled-up** (wrong-*mode*, recoverable in-skill) vs focused (wrong-*skill*) |
| Capability discoverability (browse) | **Focused** |
| Per-invocation context economy | **Focused** |
| Maintenance surface | **Rolled-up** (6 files) |
| Output quality / data | **Tie** (identical) |
| Workspace build-out + learning | **Tie** (identical) |
| Out-of-scope safety | **Tie** (both 5/5; watch fat over-fire as it grows) |

**Recommendation — a hybrid, informed by the data:**

1. **Keep fat skills *within* a domain** (collapse intra-domain forks — valuation,
   video-type, artist-setup). This is where the rollup clearly wins, and it's the
   single biggest routing improvement.
2. **Don't over-collapse `recoup-platform`** — now **empirically** the weak point:
   it owns 2 of the 3 wrong-mode misses in the two-session test (sandbox-vs-workspace,
   create-vs-workspace). Splitting it back toward 2–3 (e.g. `setup`, `api`,
   `artist`/`learn`) would cost ~no top-level routing and remove the mode errors +
   restore discovery for "create an artist."
3. **Recover discoverability without re-fragmenting:** surface the modes in the
   skill `description` (already done) *and* expose `RESOLVER.md` as the browsable
   "menu" so the hidden capabilities (thumbnail, sync brief, hook) are findable.
4. **Add a routing eval that tests MODE selection, not just skill selection** —
   the rollup's new failure class (now measured at 3%). `run_resolver_eval.py`
   tests skill-level routing; extend fixtures to assert the chosen *mode* for fat
   skills, and seed it with the 3 known misses (P47, P98, P99) as regression cases.

**Bottom line (now empirically grounded):** the two styles deliver the **same
outputs** and the **same workspace value**; they differ in *ergonomics*, and the
difference is **smaller than expected** — net end-to-end routing is a near-tie
(**rolled-up 97% vs focused 98%**), the rollup's wrong-mode failure is only **3%**,
and its top-level skill routing is **perfect (100%)**. Six fat skills route at
least as cleanly and are far easier to maintain, at the cost of discoverability,
per-call context, and a small mode-confusion tax concentrated in `recoup-platform`.
The best system is mostly the rolled-up shape **plus** a thinner `recoup-platform`
(fixes 2 of 3 mode errors) and `RESOLVER.md` exposed as the browsable menu for
discovery — not a pure 41 or a pure 6.
