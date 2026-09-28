# Step 4 — Format routing

The account workspace's `VIDEO-STYLES.md` is the source of truth for what each style is and which
project to clone. This page is the **routing table** from a brief to a format. Gates, build order
and handoffs are owned by `SKILL.md`.

## Route by the JOB, not by what looks impressive

| The job | Format | Skill / source |
|---|---|---|
| A single number or a weekly result is the hero | **Data-in-motion** (stat cards, count-ups) | Clone the style's reference project |
| Announce a **shipped feature** where seeing the real UI is the point | **3D product reveal** | Clone the reference project. Validated winner for feature announcements |
| Brand film, manifesto, hype piece where the *feeling* is the point | **Kinetic keynote** | Clone the reference project. **Not** for feature explainers |
| Entertainment: emotional live-action carrying a **value**, not a feature | **Cinematic narrative** (face guide → stills → i2v → composite) | Clone the reference project; character kit from `cast/` |
| A two-person conversation / talking-head ad with real dialogue | **FaceTime call** | `recoup-internal-video-grok-1.5-imagine-facetime` |
| A character SPEAKS the VO to camera (spoken-word ad, testimonial) | **Lip-synced still** (Muse/NB2 still → MiniMax H3 Max lip-sync or reference-to-video with the approved VO line, ≤15s audio per clip) | `references/video-pipeline.md` → *Lip-synced VO over a still* |
| Explain a **method** — how something was made, how a number was derived | **Recipe / BTS artifact walk** | Clone the reference project |
| Captions or graphic overlays onto existing footage | hyperframes caption / overlay workflows | `embedded-captions`, `talking-head-recut` |
| A **scene we could never shoot** carries the beat: a character in a place, a physical action, a location | **Generated plate** (Seedance 2.5), our typography composited over it | `references/seedance.md`. Invented characters are fine; **no photoreal face of any origin** can be a reference through fal (real photo, Muse sheet, or Seedance's own frame); stylized faces can |
| **Recreate a trend**: a known performance clip with a new cast (the "Hotel Lobby" swap) | **Character-swap edit** (source clip + 3 references per person → reAPI Seedance 2.5 `edit` → original audio restored) | `references/character-swap-edit.md`, `scripts/reapi-edit.sh`. Real faces allowed on reAPI, not fal; heads of state refused. Owner approves the reference sheet before any credit |
| A song is the whole story, cut to 9:16, **photoreal cast** | **Music video** (song → cast → Muse stills → H3 Max i2v per clip → composite) | **`recoup-music-video`**; reference project SMALL ROOM |
| A song is the whole story, cut to 9:16, **stylized / animated cast** | **Music video, Seedance slate** (song → cast photoreal from references → re-render in one style → sheets as references → one Seedance take per song section → Topaz → composite) | `references/seedance.md` → *The decision gate*; reference project `content/off-the-stage/seedance/slate.mjs`. A photoreal face never gets into Seedance through fal; a stylized one does |

**Concrete beats stylish for a feature or product announcement:** show the real interface and the
real change; the ruling and the head-to-head are in the account's `VIDEO-STYLES.md`.

**LinkedIn is an image post, not video:** see `SKILL.md` → Step 5 (owner ruling 2026-07-28). Size it
1080x1350 (4:5), link in the first comment.

A format with no skill yet is built from its reference project: clone it, never rebuild from scratch.

## The third act of a shipped-feature film (2026-08-11)

A cut worked for 24 seconds, then cut to `38 QUERIED · 38 RETURNED · 0 FAILURES · 111 SHOWS`. Every
figure was true. It failed because 38 was a population the single-artist story had never introduced.

> **Every number in the final act must attach to a noun the film has already put on screen.**
> A true number about a new subject is a subject change, and a subject change 24 seconds into a
> 40-second film reads as a different video.

For a shipped API or feature the third act is **the contract, not the benchmark**, in three beats:

1. **The request.** The literal call with the real field names: `POST /api/research/events` over
   `{ "artist_id": "…" }`, captioned "one required field."
2. **The constraint that makes it safe.** Show the field that does *not* exist: `artist_id REQUIRED`,
   `date OPTIONAL`, `name` struck as `NOT A FIELD`.
3. **Every answer it can give**, including the empty list and the error. The error card is the most
   persuasive frame, because it is the one a competitor would hide.

**Then end on something the viewer can run**, not "learn more": `docs.recoupable.dev/llms.txt` and
`chat.recoupable.dev/keys` under "give your agent the docs and a key."

**curl every CTA before scripting it.** "Tell Claude to use it through our MCP" would have been a
checkable lie: the MCP carries `prompt_sandbox` and `run_sandbox_command` and nothing else. `llms.txt`
200, `llms-full.txt` 200 and containing the endpoint, the keys page 200; the MCP line was cut.

**Route around a tag-eating page and log which defect.** `/pricing` hardcodes `utm_campaign=free` on
its own free CTA and overwrites the campaign tag on the converting click (five consecutive slates
unattributable). Pointing at `chat.recoupable.dev/keys` sidesteps it; say in `posts-log.md` which
defect you routed around.
