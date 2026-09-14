---
name: recoup-internal-consulting-article-illustrator
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Create Recoup editorial article heroes and editable concept diagrams: flow, comparison, cycle, stack, hub and framework. Uses approved brand references, exact DM Sans labels and supplied logos; generated environments are composed separately from text."
---

# Consulting Article Illustrator

Illustrate articles with Recoup editorial heroes and concept diagrams. Use the selected workspace
and its existing content bundle. Load DESIGN.md and brand/GUIDE.md (`brand/GUIDE.md`); an explicit
client/artist identity wins. Stage the self-contained brand package with
`node <installed-skill>/brand/materialize.mjs <output-directory>`.

## Workflow

1. Read the article. Plan one hero above the first line plus roughly one useful figure per major
   section (usually at most 4–6). One idea per figure; omit redundant pictures.
2. Choose a concept and archetype from references/prompt-kit.md. Prefer Paper trail, Margin notes,
   Catalog index or Blueprint among brand/finals.json references. Diagrams use paper/white/pale-blue
   surfaces, ink structure, sky connections and restrained lime emphasis. DM Sans is the exact label
   font, mono only for short indices. A restrained drawn line is optional; grey whiteboard and
   hand lettering are no longer the house default.
3. For exact diagrams, author editable SVG/HTML and render locally; use recoup-internal-consulting-graphics for
   rendering and format safe zones. For an expressive hero/environment use an available image tool
   or recoup-internal-consulting-higgsfield, then composite editable labels and supplied logo with HTML. Generate
   no text, logos or fake documents. Read the actual approved reference before prompting.
4. Review the render: accurate relationship, correct spelling, contrast, readable at article width,
   no overflow, exact loaded font/mark, one focal idea. Do not enforce legacy sample styling.
5. Save hero as images/image1.png above the first line, then image2.png onward in reading order.
   Use descriptive alt text explaining each figure. Keep editable sources and brand.lock.json with
   expression/reference IDs alongside the bundle. Scratch goes in content/_work/article-images/.

## Scheduled runs

recoup-internal-consulting-nightly-content passes the selected brand and reference IDs. Use local HTML/SVG rendering
for diagrams. If generative imagery is needed, use its configured available provider/model and
report unavailable access; never claim a generation succeeded or invent a score. Stage drafts for
review, never auto-publish. No additional provider call is needed to typeset an exact diagram.

## Historical samples

samples/flow.png, compare.png and cycle.png preserve the previous whiteboard identity as historical
references. They are not current Recoup exemplars. Use brand/finals.json and the new prompt kit.
