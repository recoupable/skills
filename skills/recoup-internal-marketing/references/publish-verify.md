# Step 5 — The pre-publish gate, and verifying after

Two checklists and the platform traps behind them. Every item here exists because it went wrong on a
real run.

## Pre-publish gate

Run this against the final `post.config.mjs` **before** the publish command. It is fast and it has
already caught a live defect.

- [ ] **No em dashes or en dashes in any published copy.** Owner ruling, 2026-08-04: `—` and `–`
      are the clearest tell that a post was written by an AI, and one in a caption undoes the
      credibility the numbers were there to earn. This covers every field that reaches an audience:
      captions, tweets, YouTube titles and descriptions, LinkedIn bodies and first comments,
      on-screen text. Internal docs and code comments are exempt; anything a reader sees is not.

      **Rewrite the sentence, do not swap the character.** A comma dropped in where the dash was
      usually leaves the same over-hedged rhythm that gave it away. Split into two sentences, or use
      a colon when the second half explains the first.

      ```bash
      node -e 'const c=(await import("./content/<slug>/post.config.mjs")).default;
      const bad=/[—–]/; for (const [k,v] of Object.entries(c.copy))
        console.log(k, bad.test(JSON.stringify(v)) ? "*** DASH PRESENT ***" : "clean");' --input-type=module
      ```

      Caught late on the LATASHÁ ten-year slate: the Instagram caption shipped with two em dashes
      before the rule existed. IG captions are editable in-app; X posts are not.
- [ ] **No placeholders anywhere.** Grep the whole config for `<`…`>` — `<YT link>`, `<COST>`, `TBD`.
      On 2026-07-28 a literal `<YT link>` was in the YouTube description and the X reply and would
      have shipped as visible text. **A placeholder must never ship.** If the thing it points at does
      not exist yet, cut the sentence.
- [ ] **Every link resolves.** A link to an asset that is not published yet is a placeholder wearing a
      URL.
- [ ] **CTA link is tagged** (`references/conversion.md`).
- [ ] **The destination was opened today, and it pays off this post's promise.** Not "does it return
      200" — *does the page a convinced viewer lands on continue the story the post told, and can it
      actually convert?* A homepage that loads fine is still a dead end for a post about one artist's
      catalog. On 2026-07-30 a four-platform slate shipped with every CTA resolving correctly to a
      page that had produced **zero trials since 2026-06-06**.
- [ ] **Attribution declared: readable or not.** If nothing records `utm_campaign` yet, write
      "conversion unreadable for this slate" into `posts-log.md` now, at publish time. Deciding this
      at the re-pull is how two consecutive runs reported engagement in place of conversion.
- [ ] **X body is under 280 weighted**, computed with URLs counted as 23 characters each regardless of
      literal length. Compute it; do not eyeball it.
- [ ] **Artist tagged with the correct per-platform handle** — they differ (`@gatsby.wtf` on IG vs
      `@gatsby_grace` on X). Confirm each rather than reusing one.
- [ ] **No leading @-tag on X.** A tweet that opens with a mention drops out of the main feed. Put the
      mention inline.
- [ ] **No AI disclosure** in any body copy (owner ruling 2026-07-28).
- [ ] **The image depicts what the copy's opening line describes.** Caught on 2026-07-28: the LinkedIn
      body opened "Two pictures of the same bedroom on the same night" while the config still pointed
      at a timeline card, which shows neither picture. Copy and image are chosen together.
- [ ] **No link in a LinkedIn body** — LinkedIn throttles body links. It goes in the first comment.
- [ ] **Account routing is verified, not assumed** (see below).

## Account routing

Connections are per artist account, and they are **not symmetrical**. Verify, do not assume:

```bash
curl -sS "https://recoup-api.vercel.app/api/connectors?account_id=<ACCOUNT_ID>" \
  -H "x-api-key: $RECOUP_API_KEY"
```

Verified 2026-07-28:

| Account | X | Instagram | YouTube | LinkedIn |
|---|---|---|---|---|
| **Recoup official** | ✅ | ✅ | ❌ | ❌ |
| **sweetman** | ✅ | ✅ | ✅ | ✅ |

So a company announcement can post IG + X as Recoup official, but **YouTube and LinkedIn must be
sweetman** — there is no Recoup connection for them. Route per platform with `accounts:` in
`post.config.mjs`.

**Known issue:** replies from **@recoupai** return 403 "not permitted" while the main post succeeds
(unfixed since 2026-07-24). So when posting X as Recoup official, put everything the reply would have
carried **inline in the main tweet** and set `reply: null` — an errored reply adds nothing.

## Auth: prefer the API key

Use **`RECOUP_API_KEY`** (`x-api-key`) over `RECOUP_ACCESS_TOKEN` (`Authorization: Bearer`). The access
token lives ~1 hour, and the documented failure is a human review pause — the YouTube
unlisted → eyeball → public flip — outlasting it and 401ing the final call. The API key does not
expire. The shared runner's `authHeaders()` prefers the key and falls back to the token.

## Post-publish verification

A returned id is not proof the post is correct.

| Platform | Verify | How |
|---|---|---|
| **X** | the **video actually attached** | public syndication endpoint, no auth: `GET https://cdn.syndication.twimg.com/tweet-result?id=<ID>&lang=en&token=a` → `mediaDetails[].type` should be `video`. The connector's read endpoints 401 on our connection. |
| **YouTube** | `privacyStatus: public`, `uploadStatus: processed`, **and the description survived** | read them off the `YOUTUBE_UPDATE_VIDEO` response envelope (`result.data.status` / `result.data.snippet`) |
| **Instagram** | the reel URL resolves | `curl -o /dev/null -w "%{http_code}"` → 200 |
| **LinkedIn** | the post URN **and** that the first comment landed | the runner returns `commentId`; a share URN with no `commentId` means the comment failed |

### Two YouTube traps

**oEmbed gives false negatives.** `youtube.com/oembed?url=…` returned `Unauthorized` for a video that
was correctly public — curl without a User-Agent. On 2026-07-28 this nearly triggered a "fix" to a
working post. Trust the API's `privacyStatus`, not oEmbed.

**A partial-snippet update can wipe the description.** `YOUTUBE_UPDATE_VIDEO` with `title` but no
`description` risks clearing it, because YouTube's `videos.update` replaces the snippet part it is
given. On 2026-07-28 the description survived (the connector merges) — that was luck, not design.
**Always send the full snippet, and re-read the description length afterwards.**

**`embeddable: false`** is a channel default the connector ignores; a Short we want to embed on the
site has to be flipped by hand in YouTube Studio.

## Log it

One row per post in `posts-log.md`: platform, account, URL/URN, asset, arc + character, CTA and its
tag, sign-off used, and the verification result. Then the ~48h re-pull for engagement **and**
conversion (`references/conversion.md`).
