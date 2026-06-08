# Pattern: the capability (department / team) plugin

> Build-time reference for plugin authors. This doc is **not shipped** with any
> install and a `SKILL.md` must **never** link to it — embody the guidance as
> behavior instead.

This is the **default** plugin shape, and the companion to the workflow-bundle
pattern (see `workflow-plugins.md`). A capability plugin is a cluster of
related skills owned by **one team or department**, each skill independently
useful, with **no mandatory order** and **no single shared artifact**.

Think "a toolbox a team reaches into" — not "a pipeline you run start-to-finish."
The user picks the one skill that answers their question right now.

---

## When to use this pattern (and when not to)

Use a capability plugin when **all** of these hold:

- The skills serve **one audience / team** (the install unit is "the marketing
  team," "the A&R team," "operations").
- Each skill is **independently valuable** — a user reaches for one without
  needing the others.
- There is **no required sequence** and **no shared workspace** the skills jointly
  build up.
- New skills get added over time as the team's needs grow.

Prefer a **workflow-bundle plugin** instead when the skills are stages of one
named, recurring process that accumulates into a single artifact (a release, a
deal, a tour). When in doubt: *"Would a user run these in a fixed order to produce
one deliverable?"* — yes → workflow bundle; no → capability plugin.

A repo will typically have **several** capability plugins (one per team) plus,
optionally, one or more workflow bundles alongside them.

---

## The organizing principle: audience, not topic or mechanism

Pick the plugin boundary by **who installs and owns it** — the team/department —
not by:

- **Topic** (don't make a "playlists" plugin — playlists show up in research,
  marketing, and ops).
- **Mechanism** (don't make an "automations" or "reports" plugin — "it runs on a
  schedule" is not a team).
- **Lifecycle stage** (that's the workflow-bundle's job).

> **Litmus test:** *"Whose toolbox is this?"* If the answer is a team
> ("the marketing team," "A&R"), it's a capability plugin and the team name is the
> plugin name. If the answer is "everyone," it's the general/essentials plugin. If
> the answer is "whoever's running process X," it's a workflow bundle.

The one allowed exception is a **general** plugin (e.g. `*-essentials`) for the
handful of skills *every* team needs (house voice, shared standards). Keep that
bar high — team-specific skills do not belong there.

---

## Anatomy

| Ingredient | Required? | Notes |
| --- | --- | --- |
| **A set of focused skills** | ✅ | One job per skill; each independently useful |
| **A router / entry-point skill** | ✅ (strongly) | One skill that resolves a fuzzy request and points to the right focused skill |
| **Clear, modality-aware names** | ✅ | The name says *what it does* and *how* (see "Naming" below) |
| **Cross-routes between overlapping skills** | ✅ | Every pair on the same topic must say "use me for X, use the other for Y" |
| **Per-skill references / scripts** | optional | Co-located and self-contained; shared files are vendored |
| **A plugin README** | ✅ | A skills table + "which one do I use?" guidance for the team |

Unlike a workflow bundle, a capability plugin has **no** shared workspace
contract, **no** mandatory orchestrator that runs everything end-to-end, and
**no** single "open this first" artifact. Each skill stands alone.

---

## The router skill (the one piece people skip and shouldn't)

A capability plugin can sprawl into a dozen skills a user can't tell apart. The
fix is a **router**: one entry-point skill whose job is to resolve "I want to do
something in this area" into the right focused skill.

A good router:

- Asks only the question(s) that change which skill applies.
- Names the focused skills and what each is for.
- Hands off — it routes, it doesn't try to do every job itself.
- Says so plainly when no skill fits yet (rather than faking one).

This is the capability-plugin equivalent of the workflow bundle's orchestrator —
but it **routes** to independent skills rather than **driving** a fixed pipeline.

---

## Disambiguation is the whole game (avoiding overlap confusion)

Because capability plugins group by team, the same **topic** often appears on
multiple skills, and the same topic can appear across **multiple plugins**. The
risk: a user asks "help with playlists" and three skills plausibly match. Two
tools prevent this:

### 1. Scope tokens — *what* the skill operates on
Mark the object in the name with the narrowest true scope:

- `*-artist-*` — one artist
- `*-song-*` — one song/track
- `*-catalog-*` — a catalog of releases
- `*-account-*` — an account/brand/label
- (no token) — capability-general

The same capability can exist at multiple scopes (artist vs. song vs. catalog
analysis) — the token is what tells them apart.

### 2. Modality — *how* the skill works
Three modalities recur, and the name should signal which:

| Modality | What it is | Tell-tale suffixes |
| --- | --- | --- |
| **Playbook** | A "how to plan/think" guide; no live data | `-planner`, `-campaign`, `-growth` |
| **Research (on-demand)** | Ask now, pull live data, answer | `-research`, `-analysis`, `-intelligence`, `-brief` |
| **Monitor (scheduled)** | Runs on a cadence, saves an artifact, alerts | `-monitor`, `-watch`, `-check`, `-tracker`, `-report`, `-dashboard`, `-digest` |

The same topic frequently has both an **on-demand** and a **scheduled** twin
(analyze-now vs. watch-weekly). When it does, the two **must cross-route** and each
must state its modality in the first sentence of its description ("Ask now…" vs.
"Runs weekly and emails…"). That pairing is the cleanest way to make a B/C
duplicate read as intentional rather than redundant.

> A capability plugin may legitimately hold both an on-demand analysis *and* its
> scheduled-monitor twin. Just make it intentional and documented — not accidental.

---

## Naming rules (recap)

- kebab-case, lowercase, prefixed with the brand.
- Name for the **capability**, not the team and not a helper verb. (The plugin
  carries the team name; the skill carries the capability.)
- The **skim test**: from the name alone, would a user know what it does?
- Scope token + modality suffix together make the name self-explaining
  (`{brand}-artist-competitor-watch` = a scheduled monitor of one artist's
  competitors).

---

## Build blueprint

1. **Name the team** — that's the plugin (`{brand}-{team}`).
2. **Inventory the skills** that team owns. For each, confirm it's independently
   useful (if it's meaningless outside a single process, it belongs in a workflow
   bundle instead).
3. **Add a router skill** as the entry point.
4. **Name each skill** with a scope token + modality suffix; run the skim test.
5. **Cross-route** every same-topic pair (and any topic that also lives in another
   plugin).
6. **Write the README** with a skills table and a short "which one do I use?" map.
7. Keep each skill **self-contained**; vendor any shared reference/script.

---

## Quality bar

- A user can scan the skills table and know which one to pick without reading
  bodies.
- No two skills are ambiguous for the same request; where topics overlap, the
  descriptions cross-route.
- The router resolves "I want to do something in this area" to a single skill.
- Nothing team-specific has leaked into the general/essentials plugin.
- Every skill earns its place by doing real work, not restating another skill.

If skills in the plugin can only be used in a fixed order to build one deliverable,
you don't have a capability plugin — you have a workflow bundle. Use that pattern
instead (`workflow-bundle-plugins.md`).
