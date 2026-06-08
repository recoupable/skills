---
name: recoup-content-pack
description: Batch-generate a whole pack of content for one song — 15–30 assets as a "clip family" for a release push. Use when the user says "content pack", "batch of clips", "a week of content", "30 posts for the launch", "clip family", "fill my content calendar for [song]", or "lots of content for [release]". Fans out across formats (multiple short-video looks, quote cards, a carousel, a Canvas) and, with audience data, themes them to where the song's fans actually are. Estimates cost and confirms before spending.
---

# Content Pack

Modern release pushes need **volume** — the consensus is 15–30 assets per song, posted as
a cohesive "clip family." This skill orchestrates the other content skills to produce that
batch in one run, and (the moat) uses audience data to theme the pack toward where the
song's listeners actually are.

Read `references/content-api.md` (endpoints, async, `estimate`),
`references/account-resolver.md` (auth + IDs), `references/workspace-context.md`
(context + write-back), and `references/analyze-gate.md` (verify each asset). All ship
alongside this skill.

## This skill spends real credits — gate it

A 30-asset fan-out costs meaningfully more than one clip. **Always estimate and confirm
before generating:**

```bash
curl -sS -X POST "$BASE/content/estimate" "${AUTH[@]}" -H "Content-Type: application/json" \
  -d "$(jq -n --arg a "$ARTIST_ACCOUNT_ID" --argjson n "$ASSET_COUNT" '{artist_account_id:$a, count:$n}')"
```

Show the estimate and the planned asset list; only fan out after the user approves. On
`insufficient_credits`, surface the `checkoutUrl`.

## Steps

1. **Resolve artist + context** (`references/account-resolver.md`,
   `references/workspace-context.md`).
2. **Plan the pack.** A balanced default for one song (~20 assets):
   - 6–10 **short-video** clips across looks (bedroom / stage / outside / album-record-store)
     and hooks — lead each with a `recoup-song-hook` moment (from `recoup-song-analysis`).
   - 4–6 **quote cards** from the strongest lines.
   - 1 **carousel** (photo dump / lyric breakdown).
   - 1 **Canvas/visualizer** loop.
   - captions per asset in the artist's voice (`recoup-brand-voice-caption`).
3. **Theme to the audience (the moat).** With audience demographics / top cities (the
   `recoup-research` skills), bias looks and copy toward where the fans are — e.g. an R&B
   ballad → intimate/aesthetic edits, not high-energy meme cuts. State the targeting
   rationale in the manifest.
4. **Estimate + confirm** (above).
5. **Generate** by delegating to the per-format skills; **analyze-gate every asset**
   (`references/analyze-gate.md`) and drop/regenerate failures.
6. **Assemble a manifest** — list each asset, its format, hook/line, target platform, and
   suggested caption.

## Persist

Workspace → `artists/{slug}/releases/{release-slug}/content-pack/` with the assets +
`pack-manifest.md`, commit `{what}: {why}` (`references/workspace-context.md`). Otherwise
return the asset list + manifest.

## The boundary (read this)

This skill makes **legitimate creative volume + audience targeting** to power the real
pages an artist or marketer runs. It does **not** create or operate networks of fake/burner
accounts, proxy/anti-detect ban-evasion, or automated mass-posting. We supply the content
and the targeting, not an account farm. If the user asks for the farm, decline that part
and deliver the creative pack.

## Guardrails

- **Estimate + confirm before spending.** No silent 30-asset fan-outs.
- **Cohesion** — the pack is a clip *family*, consistent look + voice, not 20 unrelated files.
- **Never cross-post identical files** — see `recoup-content-reformat` for per-platform cuts.
