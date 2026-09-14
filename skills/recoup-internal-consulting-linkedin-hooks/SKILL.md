---
name: recoup-internal-consulting-linkedin-hooks
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Write or critique the first line of a LinkedIn post (the hook) using patterns reverse-engineered from real top-performing posts. Use on \"write hooks for this\", \"give me 10 hooks\", \"fix this hook\", \"why won't this hook land\", \"what's a scroll-stopping opener\", or whenever drafting/critiquing a post's line 1. This is the dedicated hook engine; recoup-internal-consulting-linkedin-post-architect handles whole-post structure and defers here for the hook; recoup-internal-consulting-copy-writer governs voice/anti-slop."
---

# Consulting LinkedIn Hooks

**Workspace:** use the selected project and its `AGENTS.md`; keep existing entity folders and
Reality headings. Business paths below are relative to that project. Bundled resources are relative
to this installed skill; sibling capabilities resolve by their installed names. Never search another
private checkout for missing inputs. Use workspace identity, audience, pricing, and `DESIGN.md` fonts.
Local `_work` adapters and `evals` are optional workspace tools, not bundled dependencies. Check
presence and current help first; otherwise use an available connector for the same scoped operation.
If neither exists, report that step incomplete. For missing scorers, perform the stated checks and
label the result manual/unscored; never invent a numeric score or successful provider action.

Line 1 is ~80% of a LinkedIn post's performance — it decides whether anyone reads line 2. This skill
generates and critiques hooks from **patterns measured against real engagement**, not generic advice.
Patterns + cited examples + the empirical rules live in **references/hook-patterns.md (`references/hook-patterns.md`)** — read it before writing or grading a hook.

## The one rule
Steal **structure**, not persona or slop. The patterns come from creators (Justin Welsh, Jasmin Alić,
Ruben Hassid, …) whose voice the owner doesn't share. Map the shape onto the owner's substance (AI/agents for
music & media; B2B AI adoption) and run the result through `recoup-internal-consulting-copy-writer` (no banned words,
no em-dash). Ruben Hassid's AI hooks are the closest direct transfer — start there for AI content.

## To WRITE hooks
1. **Name the post's job and the engagement goal.** Comments, or saves/shares? That picks the pattern
   family: belief/identity → comments; utility/interrupt → saves/shares (see the engagement-signature
   note per pattern in the reference).
2. **Generate 8–12 options across at least 4 different patterns** (don't give 10 variants of one). Pull
   from the 8 patterns in `references/hook-patterns.md`. Keep each **≤60 characters, one idea, no
   question, no listicle count** (a vivid specific number is fine; a count is not).
3. **Write the one-two punch:** for the top 3, draft line 2 as well (a ≤8-word amplifier/twist) — the
   hook is really the first two lines before the fold.
4. **Run voice + anti-slop:** pass the finalists through `recoup-internal-consulting-copy-writer`. Cut any banned word,
   em-dash, or borrowed-persona edge.
5. **Hand off:** for a full post around the hook, continue in `recoup-internal-consulting-linkedin-post-architect`.

## To CRITIQUE a hook
Grade it against the reference's cross-cutting rules and name the failing one specifically:
- Over 60 chars / two ideas / buried lede → too long; cut to the claim.
- A question, or a listicle count ("5 ways…") → swap for a declarative pattern.
- Vague/clever instead of concrete → rewrite with a specific.
- Doesn't match the engagement goal → switch pattern family.
Then rewrite it 2–3 ways across different patterns and say which you'd ship and why.

## Keep it current
Hooks decay; "best practice" is just "what got engagement last month." Re-run the scrape +
`swipe/_work/analyze_hooks.py` monthly (or via `recoup-internal-consulting-integrations-sync`) and refresh
`references/hook-patterns.md` from the new top set. Origin evidence + method:
`swipe/2026-06-25-hook-analysis.md`.
