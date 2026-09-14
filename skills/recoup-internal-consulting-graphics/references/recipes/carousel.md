# Recipe: Carousel

A **swipe-through narrative** that earns saves and shares — LinkedIn document posts and Instagram
carousels. Unlike a single graphic, a carousel is a *sequence with an arc*: the cover wins the swipe,
the body delivers one idea per card, the last card pays off and asks.

**Compose it as:** this recipe × a style template (usually `framework-blocks` for teaching, `statement`
for a manifesto/POV) held **consistent across every slide** × a format. Tokens from the top-level `DESIGN.md`.

## Format
- **4:5 (1080×1350)** or **1:1 (1080×1080)** — the first slide sets the ratio for the whole set.
- **Count:** 5–10 slides on LinkedIn (5 for a tight narrative, 8–10 for a deep dive); 5–7 on Instagram.
- **LinkedIn:** export the slides to a single **PDF** (document post). IG: separate images.
- Specs + safe zones: `references/dimensions.md`.

## The arc (structure)
1. **Cover (slide 1) — the swipe-stopper.** A bold claim, number, or promise + a subtle `swipe →`
   affordance. This slide decides reach; spend disproportionate effort here. (It's a `statement`/`stat`
   composition even if the body is `framework-blocks`.)
2. **Body (slides 2…N−1) — one idea per card.** Same template, same palette, escalating. Never two ideas
   on a card. Carry a persistent element (slide number or progress dots, a consistent accent rule) so the
   set reads as one piece.
3. **Payoff (slide N).** The takeaway in one line + **one clear next step** (follow, comment a keyword,
   DM) + the footer signature (Recoup mark · {{AUTHOR_NAME}} · {{BRAND_WEBSITE}}).

## The craft bar
- **Momentum:** every slide should make the reader want the next. End body cards on a mini-cliffhanger or
  an open loop where it helps.
- **One idea per card** — if a slide has two points, split it.
- **The cover decides everything** — a brilliant body behind a weak cover is unseen.
- **Consistency over variety *within* a set** (the opposite of the across-series rule): vary the *content*,
  not the style. The cohesion is the point.
- **End with the ask** — never let the last slide just trail off.

## Render
Loop the viewport per slide, then assemble for LinkedIn:
```bash
HTML_DIR="/abs/path/slides"   # slide-1.html … slide-N.html
for f in "$HTML_DIR"/slide-*.html; do
  n=$(basename "$f" .html)
  npx playwright screenshot --viewport-size="1080,1350" "file://$f" "$HTML_DIR/$n.png"
done
# LinkedIn document post: combine the PNGs into one PDF (e.g. img2pdf / a quick script) for upload.
```

## Quality checklist
- [ ] Cover stops the swipe (bold claim/number + `swipe →`)
- [ ] One idea per body card; consistent template + palette across all slides
- [ ] Persistent cohesion element (slide number / accent rule)
- [ ] Final slide = takeaway + one clear next step + footer
- [ ] Reads at phone scale; each slide earns its place
- [ ] Exported to PDF for LinkedIn
