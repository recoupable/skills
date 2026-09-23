# Character-swap edit (the "Hotel Lobby" trend format)

Take a real performance clip and replace the people in it while keeping every gesture, cut, camera
move and the original audio. Source recipe: Nick Khami's write-up
([x.com/skeptrune/status/2102417868134797634](https://x.com/skeptrune/status/2102417868134797634),
2026-09-22). First run on our account: 2026-09-23, Héctor Lavoe + Willie Colón over the COLORS
"Hotel Lobby" performance. Script: `scripts/reapi-edit.sh`.

**Use it when** a trend's value is the familiar performance with a surprising cast, and the cast is
people the audience recognises. **The video side is solved by the source clip; the only real work is
the references.** Every rejected or weak take on the first run traced to references, never to the clip.

## Why this is not fal

fal's Seedance rejects every photoreal face, including a face in a **video** input (see
`seedance.md`). This format needs `doubao-seedance-2.5-face` on **reAPI** (reapi.ai), a reseller
whose channel accepts real faces. Same weights, different ByteDance entitlement. Treat reAPI as
grey-market: it can disappear or flag the account without notice. Key in the project `.env`
(`REAPI_API_KEY`, gitignored). No upload endpoint, no balance endpoint.

**Wan 2.2 Animate Replace on fal was tried and is not a substitute** (2026-09-23): one image per
pass, no prompt, reframes the input, weak likeness on both people. Do not route here to save money.

## Casting: who the filter will take

- **Sitting and recent heads of state are refused upstream**, alone or together, on the moderated
  AND the `content_filter:false` route (Trump, Xi, 2026-09-23; error 80006). `content_filter:false`
  only removes reAPI's own layer. **Do not retry by stripping names or disguising the prompt.** That is
  defeating a safety check, and the photos trip it anyway. Recast.
- Tech founders (Nick's runs) and deceased musicians (ours) pass.
- A **living private person** (a collaborator, a friend) needs their yes before anything posts, and
  they supply the photos. That consent request is also the collaborator co-post, our largest reach lever.
- A **deceased artist** makes the piece a tribute: say so in the copy, never put a product claim in
  their mouth.

## The references (this is the job)

**Three photos per person, each with ONE named job.** Show them to the owner as a numbered contact
sheet, in request order, and get approval before spending a credit.

| # per person | Job | Must show |
|---|---|---|
| 1 | **Primary outfit** | The exact outfit wanted, head to toe if possible, **shoes visible** |
| 2 | **Build + footwear** | Full body. A different outfit is fine; the prompt says to ignore it |
| 3 | **Face** | Clear, frontal, in the **era/look** the audience knows (glasses, hair, beard) |

What the first run taught:

- **Era beats resolution.** Public-domain 1969 press photos were accurate and still read as the
  wrong people; the audience knows Lavoe in tinted aviators, not at 22. Pick the look the audience
  remembers, then match both leads to the same age.
- **Commons is rarely enough for musicians.** The winning set was album covers and press photos the
  owner found. They are generation references only, never published. Crop text and logos off covers.
- **Reject any reference with violence in it.** An album cover with a wrapped body at the artist's
  feet failed the whole task as "violence".
- **Backgrounds bleed.** A red studio backdrop in one build photo turned the whole orange set red
  (v2). Crop build/outfit photos to the person on a neutral ground, or name the source background
  colour in the prompt.
- **Two people in one photo:** name which one (position + a feature), and remember the position in
  the photo and the position in the output are separate instructions.
- **Dimensions 300–6000 px.** Upscale a small photo (a 237px one was rejected until 2x lanczos).
- **Contrasting outfits** (white vs dark pinstripe) read apart on a busy set; matching ones blur.

## The source clip

`yt-dlp` on this machine runs on Python 3.9 and only sees 360p. Use the standalone binary:
`curl -sL https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos -o ytdlp`.
Trim and crop to 4:3 with the performers and mic placed (Nick's COLORS values scale by 0.5 for the
1080p source: `crop=1440:1080:303:0`, `-ss 14.60575 -t 29.094603`, `fps=24`, `trim=end_frame=698`).
Keep the audio in the trimmed file. Edit mode takes 2–30s of source.

## Hosting inputs

URLs must be public bytes. **fal's CDN (`v3b.fal.media`) is unreachable from ByteDance's fetcher**
(80007 "resource inaccessible"). `litterbox.catbox.moe` (24h) works, but a fresh large upload can
time out reAPI's duration probe (30002); resubmit, or reuse an earlier link that already worked.

## The prompt (template)

```
Edit the entire source video @Video1.

Replace the viewer's LEFT performer with <NAME>.
Use @Image1 as his primary outfit reference: <every garment, colour, shoes>.
Use @Image2 for build and footwear only; ignore its <clothes, props, tint>.
Use @Image3 for his face: <hair, facial hair, glasses and lens colour>. Keep <signature item> on throughout.

Replace the viewer's RIGHT performer with <NAME>.
(same three lines, @Image4–6)

The photos provide identity and wardrobe only. Ignore the background colours of every photo.
The video provides motion, expressions, gestures, timing,
interactions, camera cuts, framing, lighting and background.
Preserve the original performance as faithfully as possible.
Do not swap positions or invent new movement or scene elements.
Keep the <set colour> studio and hanging microphone exactly as in @Video1.
Remove all rings, watches, bracelets, necklaces and earrings.
```

Request: `model doubao-seedance-2.5-face`, `omni_reference_task_type "edit"` (declared, so bad
params 400 at submit), `duration -1`, `size "adaptive"`, `resolution "1080p"`,
`generate_audio false`, default moderation.

## Cost and timing (2026-09-23)

Auto-duration reserves 30s of output plus the source; a 5s 720p test reserved 8,005 credits
($8.01). A 29s 1080p take runs ~$12–15, about 5 minutes. Rejected tasks are refunded. Keep $40+ on
the account so the reserve clears.

## QC, then export

Compare source and output at the same timestamps (1, 6, 12, 18, 24, 28s): positions, cuts,
set colour, then faces and wardrobe through the turns. Known misses on every run so far: jewelry
survives "remove all rings", lens tint drifts lighter. Restore the audio and export 1440×1080 for X
(the script does both, then decodes the file to catch errors metadata misses).

## Publishing

X first (the trend lives there); the source master may be muted or claimed on YouTube/Instagram.
Platform AI-content toggle on at upload (no AI disclosure in body copy, per the skill). Not in a
17:00 UTC slot another slate holds. Owner go-ahead before anything posts.
