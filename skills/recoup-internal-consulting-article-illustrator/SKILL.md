---
name: recoup-internal-consulting-article-illustrator
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Create bold article thumbnails with contrasting text and illustration, plus simple white-background inline figures. Uses Higgsfield artwork with editable DM Sans text and approved Recoup colors."
---

# Consulting Article Illustrator

Use the selected workspace and its existing content bundle. Load DESIGN.md and `brand/GUIDE.md`;
an explicit client/artist identity wins. Stage the self-contained brand package with
`node <installed-skill>/brand/materialize.mjs <output-directory>`.

## Approved article image system

- **Thumbnail, images/image1.png:** one bold focal illustration and a large, short text hook,
  usually 3–6 words. Choose any approved Recoup background color to suit the concept; blue is not
  required. Text and illustration must both contrast clearly against the background and read at
  160px wide. Use color, scale and composition to earn attention. No body copy or repeated footer.
- **Inline figures, images/image2.png onward:** simple illustrations on pure white #FFFFFF
  backgrounds. Keep object fills white by default, forest/ink outlines, blue connections and small
  lime accents. No pale-blue panels, tinted backgrounds or elaborate scenes. One useful concept
  per figure, with only the short labels needed to understand it.
- **Headlines:** required on the thumbnail; optional on inline figures. Do not repeat the surrounding
  article heading inside every illustration. When multiple titles work together, reading only those
  titles in order must tell the complete story. This never requires a headline on every asset.
- **Wordmark:** omit repeated Recoup wordmarks from individual illustrations. Use the exact supplied
  mark only where collection-level identification is useful. Never generate a logo.

## Workflow

1. Read the edited article. Plan a thumbnail above its first line and roughly one useful inline figure
   per major section (usually at most 4–6 figures). Omit redundant pictures. Draft the thumbnail hook
   and any optional figure titles together before designing. Keep claims faithful to the article.
2. Read `references/prompt-kit.md` and inspect the actual approved reference from `brand/finals.json`.
   Borrow relevant illustration language; keep the inline background white even when a reference
   uses another surface. Use the thumbnail's selected Recoup field and contrast deliberately.
3. Use recoup-internal-consulting-higgsfield for the thumbnail artwork and simple inline illustrations.
   Check the live model, preview cost before each paid generation, and retain exact prompts and job
   IDs. Generate artwork without text or logos, leaving room for the intended editable text. If an
   exact chart or data diagram requires deterministic geometry, author that diagram in HTML/SVG.
   Report unavailable provider access; do not silently substitute a different generator.
4. Use recoup-internal-consulting-graphics to add editable text and export each composition. Follow its
   thumbnail recipe for image1. Use exact DM Sans for the hook and labels; mono only for short indices.
   The generation preview is source artwork, not the finished thumbnail: the final export must include
   the text hook. Present the composed final PNG for approval.
5. Review the thumbnail at full size and 160px wide: readable hook, clear focal illustration, strong
   foreground/background contrast, safe crop and no clutter. Review inline figures at article width:
   white background, useful relationship, minimal labels, correct spelling, no unnecessary headline
   or wordmark. Check loaded fonts, clipping and overflow. If multiple titles work together, read
   them alone in sequence to verify the narrative.
6. Save images/image1.png above the first line, then image2.png onward in reading order, with descriptive
   alt text. Keep editable sources, selected generated artwork, generation records and brand.lock.json
   with the bundle. Temporary generation files belong in the workspace's dated
   `work/YYYY-MM-DD-<task-name>/` folder; reuse it when continuing the task.

## Scheduled runs

recoup-internal-consulting-nightly-content passes the selected brand, reference IDs, output folder and
these separate thumbnail/inline requirements. Use its configured Higgsfield access; report unavailable
access or rendering and stage the article without claiming missing images exist. Never auto-publish.

## Historical samples

samples/flow.png, compare.png and cycle.png preserve the previous whiteboard identity. They can help
explain simple figure structure; they are not current palette, typography or branding authorities.
Use the current brand package and the approved article image system above.
