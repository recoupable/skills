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

**Pattern:** `recoup-[domain]-[verb]-[noun]` — domain first, exactly four words.

- **Domain first** so the alphabetical `/` list self-groups by subject. Domains
  are a small, stable set: `platform · roster · research · song · content ·
  release · catalog`. New skills slot into an existing domain; we rarely add one.
- **Verb + noun tail** makes every name self-describing — it says what the skill
  does and to what: `recoup-research-find-talent`, `recoup-content-write-caption`,
  `recoup-catalog-estimate-value`, `recoup-roster-add-artist`.
- **The skim test:** from the name alone, would Molly (a non-technical music
  marketer) know what it does? If not, rename — the verb+noun tail exists to pass
  this test.
- **Routing lives in `RESOLVER.md`,** the plugin's dispatch table; every skill is
  flat and reachable from it (no separate "router" entry-point skill). Add a
  `RESOLVER.md` row whenever you add a skill — `scripts/check_resolvable.py`
  fails on any skill the resolver can't reach.

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
| Brand kit | **Merge → modes** (`rostrum-brand-kit`) | One browseable name; each brand is a sayable mode ("use the *space heater* brand"). |
| Song work | **Keep split** (`recoup-song-analyze-audio`, `recoup-song-find-hook`, `recoup-song-placement-pitch`) | "Analyze my audio", "find the hook", "pitch this song" are distinct high-intent things a user browses for — folding them would hide capability. |
| Content formats | **Keep split** (`recoup-content-write-caption`, `recoup-content-make-graphics`, `recoup-content-make-video`, …) | Each output is something a user names directly; one "content" skill would bury what's possible. |

---

## Overlap / disambiguation checklist

Because the agent auto-routes, two skills must never both look right for one
request. For every pair on the same topic:

- Each description names its lane ("use me for X, use `recoup-…` for Y").
- On-demand vs scheduled twins each state their mode in the first sentence
  ("Ask now…" vs "Runs weekly and saves…").
- No two skills share the same trigger phrases.
