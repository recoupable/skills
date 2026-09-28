# Building a recurring character (earned on Jenny, 2026-09-21)

The kit for an invented, recurring on-camera character: one identity, one sheet, one voice, reusable in
every still and video prompt. Reference kit: the account workspace's `cast/jenny/`. Six body passes were
spent learning the rules below; a new character should take two.

## 1. Identity bake-off, four models, one prompt

Write the brief as one paragraph (face, age, skin, hair, build, wardrobe, register) and generate two
images per model with the same prompt, 3:4, model defaults. Contact sheet, owner picks one image.

| Model | Endpoint | Billed / image | Notes |
|---|---|---|---|
| Muse Image | `meta/muse-image/text-to-image` | $0.01 | house still model; most "real person", least glamour |
| Qwen Image 3 | `alibaba/qwen-image-3/text-to-image` | $0.01 | fal has no "Qwen 2.1"; 3 is the current one. Polished, stock-photo read |
| GPT Image 2.5 Sunburst | `openai/gpt-image-2.5/sunburst/text-to-image` | ~$0.04 at `quality: high` | refuses body-shape wording; softens the figure |
| Grok Imagine 2.0 | `xai/grok-imagine-image/v2.0/text-to-image` | $0.06 | closest to a body brief as written; 90–100s per image |

Delete the losing candidates once the owner picks; keep the winner and the log.

## 2. The sheet: generate panels, assemble deterministically

Ask `fal-ai/nano-banana-2/edit` (2K, 16:9, the chosen still as the only reference) for the panels: full-body
front, side, back, plus faces (happy, sad, talking, curious, confident), each with a small label. **It adds
a duplicate face panel in every pass**, so do not fight it: detect the panels by white-gap projection,
drop the duplicate, and assemble the sheet in code (`assemble-sheet.py` in the reference kit). The canon
sheet is one row.

**Two copies, always.** Video endpoints (`minimax/h3-max/reference-to-video` and kin) refuse images over
5760px on a side or with aspect outside 0.4–2.5; a one-row sheet fails both. Keep `<name>-sheet-video.png`
as the same panels in two rows (assembled by `assemble-video-sheet.py`) for every video prompt.

## 3. Body changes: face-only reference, then measure

- **A full-body reference anchors the old figure** harder than any prompt (the plate-versus-character
  rule). To change the build, reference **only the face panel** and describe the body in words.
- **Nano Banana will not change proportions** in any wording (four passes, all regressed to moderate);
  **Muse and GPT refuse** body-shape prompts. **Grok 2.0 edit and Qwen 3 edit follow them**; Grok stays
  plausible, Qwen overshoots. Grok's "change one thing" edits are conservative and saturate after one pass.
- **A numeric note ("25% slimmer hips") is a measured warp, not a re-roll:** `slim-hips.py` rescales the
  hip band per row about the body's own centre (cosine ramps waist → hip → knee) and fills the vacated
  silhouette from background sampled **outside the body's bounding columns**. Sampling near a soft edge
  paints the fill skin-tone; sampling at the bounding column paints it with the body.
- Stills made from the sheet drift the body (a studio still pushed the hips past the sheet); film stills
  say "body exactly as the FRONT panel".

## 4. Voice: bake-off on the hook line, owner listens, record the winner

Four to six voices, same line, eleven_v3, normalised to the same loudness, one review file with 0.7s gaps,
revealed in Finder. The narrator default (Jessa) is not a candidate for a character. Record voice id, model,
settings and date in the guide. The character's own lines then follow `voice.md` (spoken-text style,
per line, measured gain + limiter).

## 5. The guide

`cast/<name>/<name>-face-guide.md`: role, name and the ruling date, the anchor files, hard identifiers,
build canon ("the sheet is the measure; do not push past it"), wardrobe, register, voice, use notes, and
provenance of every generation (model, seed, prompt file). Register the character in `cast/README.md`.

## Cost anchor

Jenny, identity to approved sheet with three body revisions: $3.76 billed on fal, plus the lip-sync gate
tests $1.52. A second character on these rules: about $1.
