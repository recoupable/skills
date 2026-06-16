---
name: recoup-content-caption
description: Write social captions that sound like a specific artist — not generic AI. Use when the user says "write a caption for [artist]", "caption this post in [artist]'s voice", "give me an IG caption for the new single", "what should [artist] post", "caption ideas for the launch", or any request for caption / post copy for an artist. Reads the artist's own voice from their workspace (`context/artist.md`, `context/audience.md`) — falling back to their real past captions via the API — then drafts on-brand caption options and writes them back into the workspace.
---

# Brand-Voice Caption

Anyone can ask a model for "a caption." The value here is **voice fidelity**: a
caption that sounds like *this* artist, drawn from how they actually talk and
what their fans respond to — not the beige "music marketing" register a bare
model defaults to. The job is a loop, not a one-shot: **diarize the voice →
draft in it → verify it actually sounds like them → hand back post-ready
options.** A draft that doesn't pass the voice check is not done.

This skill is artist-workspace-native. Read `references/workspace-context.md` for
the read-context-first / write-back rules, `references/account-resolver.md` for
auth and the `account_id`-vs-`id` distinction, and `references/research-context.md`
for the live signals that ground a caption in what's actually happening. (All
three ship alongside this skill.)

## Inputs

- **Artist** (required) — name or workspace slug.
- **Subject** (required) — what the caption is about: a single/release, a song, a
  photo dump, a tour date, an announcement. If the user didn't say, **ask** (see
  the decision brief in Phase 3) — a caption with no subject is filler.
- **Platform** (optional) — Instagram / TikTok / X / YouTube. Default Instagram;
  affects length, line breaks, and hashtag convention.
- **Count** (optional) — how many options. Default 3, each a *distinct angle*.

## The procedure

### Phase 0 — Resolve the artist and workspace

Find `artists/{slug}/`, read `RECOUP.md` for IDs. See
`references/account-resolver.md`. If the artist has no record at all, run
`recoup-artist-create` first. If there's a workspace but no voice context yet,
note it — Phase 1 will fall back to real posts.

### Phase 1 — Diarize the voice (the moat; do this before drafting)

Do **not** just "read artist.md." Build a **voice fingerprint**: a short,
explicit distillation of *how this artist writes*, the way an analyst writes a
one-page dossier rather than dumping raw files. This fingerprint is what every
draft is checked against in Phase 5, so make it concrete and falsifiable.

**Primary — workspace context (source of truth):**

```bash
cat "$ARTIST_DIR/context/artist.md"   2>/dev/null   # voice, tone, aesthetic, do/don'ts
cat "$ARTIST_DIR/context/audience.md" 2>/dev/null   # who fans are, how THEY talk
```

**Fallback — real past captions (when there's no `artist.md`):** learn the voice
from what the artist has actually posted. Use the row `id` (not `account_id`):

```bash
curl -sS "${AUTH[@]}" \
  "https://api.recoupable.com/api/artists/$ARTIST_ROW_ID/posts" \
  | jq -r '.posts[].caption // empty' | head -30
```

Treat 10–30 real captions as **few-shot voice anchors**. If neither workspace
context nor posts exist, **stop and ask** the user for voice guidance — do not
invent a persona.

**Write the fingerprint down** (in working notes, not a committed file) with
concrete, checkable signals:

```
VOICE FINGERPRINT — {artist}
- Length/shape: e.g. "1–2 short lines, hard line breaks, no paragraphs"
- Capitalization: e.g. "all-lowercase except brand/song titles"
- Emoji: e.g. "0–1 emoji, only 🖤 or 🌀; never strings of them"
- Punctuation tics: e.g. "no end punctuation; em-dashes for asides"
- Slang / lexicon: e.g. "says 'we' not 'I'; calls fans 'the swarm'"
- Recurring themes: e.g. "night driving, faith, the city"
- Do NOT: e.g. "no hashtags in-caption; no 'link in bio'; no exclamation hype"
```

If the artist file has an explicit "voice"/"tone" section, that overrides
inference.

### Phase 2 — Gather the subject + live signals

Pull the facts the caption should reference, from the workspace where possible:

```bash
cat "$ARTIST_DIR/releases/$RELEASE_SLUG/RELEASE.md" 2>/dev/null   # narrative, date, title
```

For a song's mood/lyric, the `recoup-song-analysis` skills can supply a hook or
lyric line — but **never paste third-party copyrighted lyrics wholesale**;
reference or paraphrase. For *what's true right now* (a milestone, a chart entry,
a playlist add worth nodding to), see `references/research-context.md` and layer
it in **only if it sharpens the caption** — don't shoehorn a stat into a vibe post.

### Phase 3 — Decision brief (only when a choice changes the output)

If the subject, angle, or platform is genuinely ambiguous **and** the choice
changes the caption materially, ask **one** decision-brief question (not a vague
"what do you want?"). Otherwise pick the reasonable default and note it. Format:

```
D1 — <one-line question>
Context: <artist + what we're captioning, 1 sentence>
ELI10: <plain-English stakes a non-marketer follows, 2–3 sentences>
Recommendation: <option> because <one-line reason>
A) <option> (recommended)
   ✅ <concrete pro>
   ❌ <honest con>
B) <option>
   ✅ <pro>
   ❌ <con>
Net: <the actual tradeoff in one line>
```

Use this for real forks only (e.g. "drop the release date in the caption, or
keep it mysterious?"). Don't interrogate the user about things you can default.

### Phase 4 — Draft in-voice

Write `Count` options, each a **distinct angle** (e.g. direct/hype,
intimate/personal, witty/dry, fan-to-fan). Every option must be generated
*through* the Phase 1 fingerprint — use the real captions as few-shot anchors so
the register matches. Platform shaping: respect the fingerprint's length/line-break
habits and the platform norm (IG: caption + grouped hashtags or none per the
artist; X: tighter, no hashtag walls; TikTok: hook-first).

**Optional API assist (on-screen / burned-in video text only):** when the caption
is overlay text for a video rather than a post caption, generate via the endpoint
and reuse its styling hints:

```bash
TOPIC="In ${ARTIST_NAME}'s voice (${VOICE_SUMMARY}). Post is about: ${SUBJECT}."
curl -sS -X POST "https://api.recoupable.com/api/content/caption" \
  "${AUTH[@]}" -H "Content-Type: application/json" \
  -d "$(jq -n --arg topic "$TOPIC" --arg len "short" '{topic:$topic, length:$len}')"
# -> { content, font, color, borderColor, maxFontSize }
```

`length` is `short` (default) | `medium` | `long` | `none`. The styling fields
matter only for burned-in video text; for a plain post caption use `content` as
one more candidate (still run it through Phase 5).

### Phase 5 — Verify against the fingerprint (the loop; do not skip)

A bare model drifts to generic on the first try. Before presenting, **score every
draft against the voice fingerprint and the anti-slop checklist**. This is the
text analog of the content analyze-gate: you cannot trust a draft you haven't
checked.

For each draft, check:

- [ ] **Matches the fingerprint** — length/shape, capitalization, emoji habit,
      punctuation tics, lexicon. Quote the signal it hits.
- [ ] **Avoids every "Do NOT"** in the fingerprint.
- [ ] **Not AI-slop** — no "Get ready to…", "Mark your calendars", "We can't wait
      for you to hear…", "🔥 OUT NOW 🔥", em-dash-stuffed hype, or empty
      superlatives the artist would never say.
- [ ] **Says something** — references the real subject/signal, not a generic vibe
      that fits any artist on any day.
- [ ] **Benchmarked** (when posts were available) — would it sit naturally next to
      the artist's real top captions? If it stands out as "an AI wrote this," cut it.

Any draft that fails → **redraft or drop it**, don't present it. Voice over
volume: three captions that nail the voice beat ten that miss.

### Phase 6 — Present, then persist

Show the surviving options to the user, **labeled by angle**, with the platform
noted and a one-line note on which fingerprint signals each leans on. On approval,
write them back into the workspace and commit:

```bash
mkdir -p "$ARTIST_DIR/content/captions"
# write the chosen/option set to a dated markdown file, then:
git add "$ARTIST_DIR/content/captions" && \
  git commit -m "content: brand-voice captions for ${SUBJECT}"
```

If there's no workspace, return the options in the conversation.

## Guardrails

- **Never fabricate the voice.** No `artist.md` and no posts → ask, don't invent.
- **Verification is mandatory.** Presenting an unchecked draft is the failure mode
  this skill exists to prevent — run Phase 5 every time.
- **Don't overwrite static context.** `context/artist.md` is the maintained source
  of truth; this skill *reads* it and writes captions to `content/captions/`.
- **Lyrics.** Reference or paraphrase the artist's own lyrics; never reproduce
  third-party copyrighted lyrics wholesale.
- **Stop at the asset.** This skill writes captions; it does not post or schedule.

## Anti-slop quick reference (the Phase 5 rubric, inline)

Reject on sight: "Get ready", "Mark your calendars", "You won't want to miss",
"link in bio" (unless the artist actually says it), exclamation-hype stacks,
emoji strings, and any line that would fit any artist. Keep: their real tics,
their lexicon, their restraint.

## References

- `references/workspace-context.md` — read-context-first, the context files, write-back.
- `references/account-resolver.md` — auth modes + `account_id` vs row `id`.
- `references/research-context.md` — live signals to ground the caption in what's true now.
