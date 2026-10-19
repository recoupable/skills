# Step 5 — The pre-publish gate, and verifying after

Two checklists and the platform traps behind them. Every item here exists because it went wrong on a
real run.

## Gate zero: let the API check the shape (2026-10-19)

Video posts go through `POST /api/posts` (`recoup-internal-social-ship-posts` step 4). It rejects an unknown
field, a missing per-platform field (YouTube `title`, a `description` everywhere else) and an over-limit body
(X weighted length included) with a 400 before anything posts, and reads the published text back
(`text_verified`). The old connector runner posted empty bodies silently (08-07, 08-12, 09-02); that class of
bug is why it was retired. A post is done only at `status: "posted"` with `text_verified: true`.

## Pre-publish gate

Run this against the final `post.config.mjs` **before** the publish command. It is fast and it has
already caught a live defect.

_The X character count is asserted by the API. What follows is the judgement it cannot make._

- [ ] **Dashes: rewrite the sentence, do not swap the character.** A comma dropped where the dash was
      leaves the same over-hedged rhythm that gave it away. Split in two, or use a colon when the
      second half explains the first. (Owner ruling 2026-08-04. On-screen text counts; internal docs
      do not. IG captions are editable in-app afterwards; X posts are not.)
- [ ] **A placeholder is never "fill it in later".** If the thing it points at does not exist yet,
      **cut the sentence.** A literal `<YT link>` reached a YouTube description on 2026-07-28.
- [ ] **Every link resolves.** A link to an asset that is not published yet is a placeholder wearing a
      URL.
- [ ] **CTA link is tagged** (`references/conversion.md`).
- [ ] **The destination was opened today, and it pays off this post's promise.** Not "does it return
      200" — *does the page continue the story the post told, and can it convert?* A homepage that
      loads fine is a dead end for a post about one artist's catalog. Precedent and the standing
      `/pricing` defect: `references/conversion.md`.
- [ ] **Attribution declared: visits readable by `utm_campaign`, the signup join unreadable (row 29).**
      Write it into `posts-log.md` now, at publish time. Deciding this at the re-pull is how two
      consecutive runs reported engagement in place of conversion.
- [ ] **Artist tagged with the correct per-platform handle** — they differ (`@gatsby.wtf` on IG vs
      `@gatsby_grace` on X). Confirm each rather than reusing one.
- [ ] **No leading @-tag on X.** A tweet that opens with a mention drops out of the main feed. Put the
      mention inline.
- [ ] **No AI disclosure** in any body copy (owner ruling 2026-07-28).
- [ ] **No third-party provider or model names on anything published (owner 09-04):** grep for fal,
      MiniMax, Seedance, ElevenLabs, Grok, OmniHuman, Muse.
- [ ] **The image depicts what the copy's opening line describes.** Caught on 2026-07-28: the LinkedIn
      body opened "Two pictures of the same bedroom on the same night" while the config still pointed
      at a timeline card, which shows neither picture. Copy and image are chosen together.
- [ ] **No link in a LinkedIn body** — LinkedIn throttles body links. It goes in the first comment.
- [ ] **Account routing is verified, not assumed** (see below).

## Account routing

Recoup official has no YouTube connector (its LinkedIn connection posts to the company page) and @recoupai replies 403 (unfixed since 2026-07-24,
so put the reply's content inline and set `reply: null`); verify the target account with
`GET /api/connectors` before every publish (ACCOUNT.md owns the table):

```bash
curl -sS "https://recoup-api.vercel.app/api/connectors?account_id=<ACCOUNT_ID>" \
  -H "x-api-key: $RECOUP_API_KEY"
```

## Post-publish verification

A returned id is not proof the post is correct. **Neither is a verification you skim.** Read the published
text back and compare programmatically; refuse an empty body (08-07 ig object, 08-12 wrong-account empty
tweet, 09-02 two empty tweets). X permits a media-only post, so it returns a real tweet id for an empty
body; the runner now throws on empty resolved text. When a fix does not work, the theory is wrong, not the
dose: the "over 280 chars" theory cost the second empty tweet (09-02).

Compare the published field to the config **programmatically** and print the result. On 2026-08-12
the verifier printed `text: https://t.co/wejzAvboDm`, which *was* the evidence the body was empty,
and the run read past it and reported the post fine. A strict equality check cannot be read past:

```bash
# example: IG caption must be byte-identical to what the config intended
node --input-type=module -e "
import cfg from './content/<slug>/post.config.mjs';
/* ...fetch published caption into `live`... */
console.log('matches config exactly:', live === cfg.copy.ig);"
```

**Prefer the public surface over the connector's read path.** The connector's own detail endpoints
401 on X and returned an empty envelope for YouTube on 2026-08-12. What is publicly visible is what
the audience sees, and it is what to verify against: X syndication, the YouTube watch page,
the IG media endpoint's `permalink` + `caption`.

| Platform | Verify | How |
|---|---|---|
| **X** | the **body text published** AND the **video attached** | public syndication endpoint, no auth: `GET https://cdn.syndication.twimg.com/tweet-result?id=<ID>&lang=en&token=a`. Check `text` is your copy, **not just** that `mediaDetails[].type` is `video`. On 2026-08-12 the media check passed on a tweet whose `text` was nothing but the `t.co` media link, and the run reported success. **A `text` field containing only a `t.co` URL means the body is empty.** |
| **YouTube** | `privacyStatus: public`, `uploadStatus: processed`, **and the description survived** | read them off the `YOUTUBE_UPDATE_VIDEO` response envelope (`result.data.status` / `result.data.snippet`) |
| **Instagram** | the reel URL resolves | `curl -o /dev/null -w "%{http_code}"` → 200 |
| **LinkedIn** | the post URL **and** that the first comment landed | `post_url` + `text_verified` from `GET /api/posts/{id}`; open the post to check the owner's first comment |

### YouTube traps

- **oEmbed gives false negatives** (curl without a User-Agent returned `Unauthorized` for a public video,
  2026-07-28): trust the API's `privacyStatus`, not oEmbed.
- **A partial-snippet update can wipe the description** because `videos.update` replaces the snippet part it
  is given; it survived on 2026-07-28 by luck. Always send the full snippet and re-read the description
  length afterwards.
- **`embeddable: false`** is a channel default the connector ignores; flip it by hand in YouTube Studio.

OpusClip import for scheduling a finished film: `POSTING-PLAYBOOK.md` (workspace) owns the recipe.

## Log it

One row per post in `posts-log.md`: platform, account, URL/URN, asset, arc + character, CTA and its
tag, sign-off used, and the verification result. Then the ~48h re-pull for engagement **and**
conversion (`references/conversion.md`).
