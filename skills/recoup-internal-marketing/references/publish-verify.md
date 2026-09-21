# Step 5 — The pre-publish gate, and verifying after

Two checklists and the platform traps behind them. Every item here exists because it went wrong on a
real run.

## Gate zero: does the runner actually read your copy? (2026-08-12)

**Every other item on the checklist below validates the copy you can see in the config. None of them
validates that the runner will ever read it.** That gap shipped a post with an empty body.

`post.mjs` dereferences a specific shape. Get it wrong and the field is `undefined`, the connector
posts whatever it was handed, and **nothing warns you**:

| Platform | What `post.mjs` reads | Wrong shape gives you |
|---|---|---|
| X | `cfg.copy.x.text`, `cfg.copy.x.reply` | a flat string on `x` posts the **video with no text** |
| Instagram | `cfg.copy.ig` (a bare string) | an object throws `caption must be a valid string` |
| YouTube | `cfg.copy.yt.title`, `cfg.copy.yt.description` | an untitled upload |
| LinkedIn | `cfg.copy.li.body`, `cfg.copy.li.firstComment` | an empty share |
| all | `cfg.accounts[platform]` | **silently defaults to sweetman** |

X and Instagram want *opposite* shapes, and both directions have shipped.

### Run this, and do not publish if it exits non-zero

```bash
node --input-type=module -e "
import cfg from './content/<slug>/post.config.mjs';
import { ACCOUNTS } from './lib/post/connectors.mjs';
import fs from 'fs';
let fail = 0;
const chk = (l, ok, d='') => { console.log((ok?'  PASS  ':'  FAIL  ')+l+(d?'  '+d:'')); if(!ok) fail++; };
const c = cfg;
for (const p of Object.keys(c.copy)) {
  if (p === 'x')  { const t = c.copy.x.text;
                    // X weights every URL at 23 chars regardless of literal length
                    const w = typeof t==='string' ? [...t.replace(/https?:\/\/\S+/g,'x'.repeat(23))].length : 999;
                    chk('copy.x.text', typeof t==='string' && t.length>0, '('+w+' weighted)');
                    chk('copy.x.text <= 280 weighted', w<=280); }
  if (p === 'ig') chk('copy.ig is a bare string', typeof c.copy.ig==='string' && c.copy.ig.length>0);
  if (p === 'yt') chk('copy.yt.title/.description', !!c.copy.yt?.title && !!c.copy.yt?.description);
  if (p === 'li') chk('copy.li.body/.firstComment', !!c.copy.li?.body && !!c.copy.li?.firstComment);
}
for (const [p, name] of Object.entries(c.accounts || {}))
  chk('accounts.'+p+' resolves', !!ACCOUNTS[name], '-> @'+(ACCOUNTS[name]?.xHandle || name));
chk('accounts set for every platform being posted', Object.keys(c.accounts||{}).length > 0);
for (const f of [c.video, c.cover, c.liImage].filter(Boolean))
  chk('asset exists: '+f, fs.existsSync('content/<slug>/'+f));
const all = JSON.stringify(c.copy);
chk('no em/en dash', !/[—–]/.test(all));
chk('no placeholders', !/<[A-Z ]+>|TBD/.test(all));
console.log(fail ? '\n  '+fail+' FAILURE(S) - DO NOT PUBLISH' : '\n  pre-flight clean');
process.exit(fail ? 1 : 0);
"
```

It must be executable rather than a checklist item because a missing `accounts` key and a wrong copy shape
are invisible to reading; `process.exit(1)` is not. Weighted length: URLs count as 23 characters regardless
of real length, emoji and CJK count as 2.

## Pre-publish gate

Run this against the final `post.config.mjs` **before** the publish command. It is fast and it has
already caught a live defect.

_Dashes, placeholders and the X character count are asserted by the gate-zero script above. What
follows is the judgement the script cannot make._

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

Recoup official has no YouTube or LinkedIn connector and @recoupai replies 403 (unfixed since 2026-07-24,
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
| **LinkedIn** | the post URN **and** that the first comment landed | the runner returns `commentId`; a share URN with no `commentId` means the comment failed |

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
