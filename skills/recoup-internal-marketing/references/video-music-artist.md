# Artist music video — the Brauxelion recipe (codified 2026-08-31)

Make a finished 9:16 music video from a real artist's own song. Pull the audio and lyrics, build a word-timed scene table, generate Nano Banana 2 stills from a face guide, animate the singing shots with OmniHuman and everything else with H3 Max, then cut it in HyperFrames to the actual track. Clone `content/letal-xlug/` and work from that. The 27 second Brauxelion cut we shipped on 2026-08-28 is the reference, Tomas Mika `Hx2b6Q0i6Z4` is the next run.

> **Status:** proposal, not yet a skill. Reference project: `content/letal-xlug/` (SCRIPT.md + video/). Cost on the reference: ~$9.50 generation (Nano Banana 2 + OmniHuman + H3 Max), 27.0s at -14.1 LUFS.

## When to use

- A real artist on our roster (or a prospect) has a **released song** and wants a finished vertical video cut to **their own audio** — not a /music generation, not a product tour.
- Consent and likeness gates apply exactly as in `NARRATIVE.md` / `cast/<character>/`.

## Not this

- Data-in-motion (Style A), 3D product reveal (Style B), recipe BTS (Style E) — no numbers or UI here.
- Style F animated music video (`content/rough-draft/`, `content/pennies/`) — those are *invented* characters for the /music launch, not a real face.
- Company-level internal film (Valuation Quest, Operator) — this film has no Recoup story; the story is the song.

## 0. Does the marketing skill have a subskill for this?

**No.** `recoup-internal-marketing` routes to styles (A–F) and to `recoup-internal-video-grok-1.5-imagine-facetime` / `recoup-content-make-video`, but none implements the real-artist 9:16 music video. The format routing table (`references/video-formats.md`) lists cinematic narrative (Style D) and animated music video (Style F) — both assume generated / invented visuals. The brauxelion build (above) is the first proven recipe for a real artist + real master, and is pending codification as **Style G: artist music video**. This doc is that proposal.

## 1. Pull the song + lyrics (Tomas Mika notes, 2026-08-31)

**Audio first, always.** You cannot write the scene table without the song map.

### 1a. Audio

- Prefer the **master WAV** from the artist. Ask in the approval DM. Until it arrives, a YouTube rip is the approval cut only: `yt-dlp -f 18 --extractor-args youtube:player_client=android -o audio/...mp4 https://www.youtube.com/watch?v=Hx2b6Q0i6Z4` → `ffmpeg -vn -c:a pcm_s16le -ar 16000 audio.wav`. Measure with `ffmpeg -filter loudnorm` or `bs1770` — the braux rip was **-5.9 LUFS / +1.9 dBTP** (brickwalled; mux with linear gain only, never `loudnorm`). For Tomas: `Hx2b6Q0i6Z4` 159s, 6.8MB mp4 → `tomas-mika-Hx2b6Q0i6Z4.wav` 9.7MB on `/tmp`.
- If the verse-only cut is needed (braux was 36.5→60.6s = 24.1s, cuts snapped to transcript gaps), slice after Scribe word times, crossfade 60ms at the downbeat. Keep the full wav too.

### 1b. Lyrics / transcript — use YouTube auto-captions, not Whisper

**New finding (2026-08-31, Tomas Mika):** the Recoup **YouTube connector** (`YOUTUBE_LIST_CAPTION_TRACK` / `YOUTUBE_LOAD_CAPTIONS`) returns text **only for videos you own** — `LOAD_CAPTIONS` 403s on non-owned auto-generated tracks. The Apify YouTube scraper (`subtitles` field on `POST /api/artist/socials/scrape`) only populates when scraping a **single video URL**, not a channel list (our `myco wtf` channel batch returned `subtitles: null` on all 5 samples).

**Working path for non-owned artist videos:**

```bash
yt-dlp --skip-download --write-auto-sub --sub-langs "es,es-419,en" \
  --sub-format vtt --extractor-args "youtube:player_client=android" \
  -o "/tmp/tomas-sub.%(ext)s" "https://www.youtube.com/watch?v=Hx2b6Q0i6Z4"
# → /tmp/tomas-sub.es.vtt 7.8KB + /tmp/tomas-sub.en.vtt 8.0KB
# Kind: captions, Language: es, webvtt with <c> word tags
```

Clean with: strip `<[^>]+>`, timestamp lines, `[Music]`/`[Música]`, dedupe consecutive duplicates (the VTT repeats each line 3× for karaoke). Tomas ES cleaned ≈ 180 words, 159s.

Fallback only: `npx hyperframes transcribe --model large-v3-turbo --language es audio.wav` or `scripts/audio.mjs` Scribe pass. On 2026-08-31 `whisper-cpp 0.15.3` with `ggml-large-v3-turbo.bin 270MB` failed `expected 587 tensors got 111` — mismatch. Use yt-dlp first; it is free, timestamped, and language-native.

### 1c. Song map

Scribe or VTT word times → section table `Intro / Verse / Hook / Break` with lyric anchors (`content/letal-xlug/SCRIPT.md:53` Song map). Budget beats ≤6.5s (`HOOKS.md`).

## 2. Creative — lock the plan doc before any paid pixels

Write `SCRIPT.md` as the braux doc does (`CONTENT/letal-xlug/SCRIPT.md:1`): **Why his, Why ours** (single sentences + risk, per `references/topic-selection.md` — theirs first), **Arc/character/kind** (launch, no Recoup story), **Consent + rights** (likeness / recording / featured voice — three gates, `SCRIPT.md:25`), **Brand-safety lock** (braux: drill lyrics → clean visuals, no weapons/substances), **Numbers** (none on screen → nothing to audit), **Song map**, **Art direction** (continuity with EP artwork), **Hook** (first frame is the premise, no logo), **Scene table**, **Cost**, **Build order**, **Approval message**.

Get owner sign-off on the plan before generating.

## 3. Art direction + face guide

- Continuity with the artist's own world (braux: Metal Slug 3D game → racing level of same city). Pull the official thumbnail / cover as style ref.
- Face guide: `cast/<artist>/faceguide.png` white-bg expression sheet (Nano Banana 2, not Grok; seed from real room). Braux guide `cast/brauxelion/braux-faceguide.png` + `frontal-04.jpg` + official thumb + masked persona (`braux-masked-persona.jpg`) seeded every Nano Banana 2 call.

## 4. Stills → Motion → Composite (the cost ledger)

| Stage | Tool | When | Braux spend |
|---|---|---|---|
| Stills 19 + ~6 re-rolls | `fal-ai/nano-banana-2/edit` (Nano Banana 2) | All beats, reviewed on CONTACT-SHEET before any motion | ~$2.00 |
| Rap shots (lip-synced) | `fal-ai/omnihuman-1.5` image+audio, 1080p, $0.16/s | Any shot with mouth shapes, fed exact slice of wav | ~$2.70 for 4 shots |
| All non-lip motion (silent face, push-ins, plates, car, city) | `minimax/h3-max/image-to-video` 768P $0.04/s (promo to Sep 1) — **exclusively H3 Max** | Every shot without a mouth, including silent face / push-ins (ex-Wan 3.0) — see note below |  |
| Reject table | Kling Avatar v2 Pro burns subtitles; Sync Lipsync viable fallback $5/min; LTX drifts; InfiniteTalk drops | — | — |

**Gotchas codified from braux bake-offs (3 rounds, `SCRIPT.md:148-182`, now H3 Max-only):**
- Re-roll grins on stress beats, fix physics at the still (window half-up → hand through glass), never animate text with CSS `filter:invert` (headless ignores it — type it), never let Nano Banana 2 "two-shot" become a split grid (prompt: ONE continuous frame).
- H3 Max hallucinated signage / anime woman on wide street plates in the braux run — was moved to Wan 3.0 then; now H3 Max is the sole vendor, so add negative prompts (`no text, no signage, no letters, no people in background`) and re-roll until clean; the CONTACT-SHEET gate catches it.
- Cut headroom: never cut within ~0.15s of clip end (black frame at 4.6s, fixed to 0.18s headroom, verified by brightness).

## 5. HyperFrames composite

Clone `content/letal-xlug/video/` (or `content/pennies/video/` for a music-video harness), place clips on the song map by word times (Scribe), clips muted except lip-sync sources, burned hook line only if his official video has none, title card HTML typed. Snapshot at 6 points `npx hyperframes@0.7.5 snapshot --at <times>`, render `npm run render`, mux `drift.wav` at linear gain, frames out of render. Measure LUFS/TP, do not loudnorm.

## 6. Approval → publish

- Nothing posts before artist written yes. DM draft template in `SCRIPT.md:132` (Spanish, no em dashes, asks for master WAV + label clearance, states IG Collab plan and "VIDEO BY Recoup" credit).
- On yes: artist posts first, IG Collab to @recoupableai/sweetman, then 4-platform cut via `recoup-internal-social-ship-posts` (`utm_campaign=artist-slug`, yt description link, LI image not video, X no link in body).

## References

- Reference project: `content/letal-xlug/` (SCRIPT.md 193 lines, 19→7→4→v2 renders, Build log 08-28)
- Style F spec: `VIDEO-STYLES.md:210`
- YT transcript note: `yt-dlp --write-auto-sub` 7.8KB es.vtt 2026-08-31; connector 403 on non-owned; Apify `subtitles` null on channel list
- Voice model check: `references/voice.md` — baked on braux via Scribe word times at hook

