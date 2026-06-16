---
name: recoup-content-caption
description: Write social captions that sound like a specific artist — not generic AI. Use when the user says "write a caption for [artist]", "caption this post in [artist]'s voice", "give me an IG caption for the new single", "what should [artist] post", "caption ideas for the launch", or any request for caption / post copy for an artist. Reads the artist's own voice from their workspace (`context/artist.md`, `context/audience.md`) — falling back to their real past captions via the API — then drafts on-brand caption options and writes them back into the workspace.
---

# Brand-Voice Caption

Anyone can ask a model for "a caption." The value here is **voice fidelity**: a caption
that sounds like *this* artist, drawn from how they actually talk and what their fans
respond to. The whole job is (1) gather the real voice, (2) draft in it, (3) hand back
post-ready options.

This skill is artist-workspace-native. Read `references/workspace-context.md` for the
read-context-first / write-back rules and `references/account-resolver.md` for auth and
the `account_id`-vs-`id` distinction. (Both files ship alongside this skill.)

## Inputs

- **Artist** (required) — name or workspace slug.
- **Subject** (required) — what the caption is about: a single/release, a song, a photo
  dump, a tour date, an announcement. If the user didn't say, ask — a caption with no
  subject is just filler.
- **Platform** (optional) — Instagram / TikTok / X / YouTube. Defaults to Instagram;
  affects length and hashtag conventions.
- **Count** (optional) — how many options. Default 3.

## Steps

### 1. Resolve the artist and workspace

Find `artists/{slug}/`, read `RECOUP.md` for IDs. See `references/account-resolver.md`.
If the artist has no record at all, run `recoup-artist-create` (Recoupable skills library)
first.

### 2. Gather the voice (the moat — do this before drafting)

**Primary — workspace context (source of truth):**

```bash
cat "$ARTIST_DIR/context/artist.md"   2>/dev/null   # voice, tone, aesthetic, do/don'ts
cat "$ARTIST_DIR/context/audience.md" 2>/dev/null   # who fans are, how THEY talk
```

Pull out concrete voice signals: sentence length, capitalization habits, emoji/no-emoji,
slang, recurring themes, punctuation tics, and anything in an explicit "voice" or "tone"
section.

**Fallback — real past captions (when there's no `artist.md`):** learn the voice from what
the artist has actually posted. Use the row `id` here (not `account_id`):

```bash
curl -sS "${AUTH[@]}" \
  "https://api.recoupable.com/api/artists/$ARTIST_ROW_ID/posts" \
  | jq -r '.posts[].caption // empty' | head -30
```

Treat 10–30 real captions as **few-shot examples** of the voice. If neither workspace
context nor posts exist, stop and ask the user for voice guidance — do **not** invent a
persona.

### 3. Gather the subject context

Pull the facts the caption should reference, from the workspace where possible:

```bash
cat "$ARTIST_DIR/releases/$RELEASE_SLUG/RELEASE.md" 2>/dev/null   # release narrative, date, title
```

For a song's mood/lyrics, the `recoup-song-analysis` skills (Recoupable skills library)
can supply a hook or lyric line — but never paste third-party copyrighted lyrics wholesale;
reference or paraphrase.

### 4. Draft in-voice

Write `Count` distinct caption options, each grounded in the voice signals from step 2 and
the subject from step 3. The model doing the drafting is *you* — use the real captions as
few-shot anchors so the output matches their register, not a generic "music marketing"
tone. For each option vary the angle (e.g. direct/hype, intimate/personal, witty), and
include platform-appropriate hashtags/CTA from `context/audience.md`.

**Optional API assist (on-screen / video overlay text):** when the caption is burned-in
text for a video rather than a post caption, generate it via the endpoint and reuse its
styling hints. Encode the voice + subject into `topic`:

```bash
TOPIC="In ${ARTIST_NAME}'s voice (${VOICE_SUMMARY}). Post is about: ${SUBJECT}."
curl -sS -X POST "https://api.recoupable.com/api/content/caption" \
  "${AUTH[@]}" -H "Content-Type: application/json" \
  -d "$(jq -n --arg topic "$TOPIC" --arg len "short" '{topic:$topic, length:$len}')"
# -> { content, font, color, borderColor, maxFontSize }
```

`length` is `short` (default) | `medium` | `long` | `none`. The styling fields matter only
for burned-in video text (hand them to the video/edit step); for a plain post caption,
just use `content` as one more option.

### 5. Present, then persist

Show the options to the user, labeled by angle, with the platform noted. On approval, write
them back into the workspace and commit:

```bash
mkdir -p "$ARTIST_DIR/content/captions"
# write the chosen/option set to a dated markdown file, then:
git add "$ARTIST_DIR/content/captions" && \
  git commit -m "content: brand-voice captions for ${SUBJECT}"
```

If there's no workspace, just return the options in the conversation.

## Guardrails

- **Never fabricate the voice.** No `artist.md` and no posts → ask, don't invent.
- **Don't overwrite static context.** `context/artist.md` is the maintained source of
  truth; this skill *reads* it and writes captions elsewhere (`content/captions/`).
- **Lyrics.** Reference or paraphrase the artist's own lyrics; never reproduce third-party
  copyrighted lyrics wholesale.
- **Voice over volume.** Three captions that nail the voice beat ten generic ones.

## Reference

- `references/workspace-context.md` — read-context-first, the context files, write-back.
- `references/account-resolver.md` — auth modes + `account_id` vs row `id`.
