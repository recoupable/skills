# PDF house style: one-page customer documents

The look of every PDF we hand a customer: numbers one-pagers, target lists, meeting
packs. First used on a podcast customer's monthly numbers and guest-target packs
(2026-09-22), which the team adopted as the standard. Start from the template instead of
rebuilding it.

- Template: `templates/pdf-house-style/page.html` (every component, with synthetic example content)
- Build + checks: `python3 scripts/build_pdf.py page.html Out.pdf --font <GeistPixel-Square.ttf> --preview out.png`
  (scripts ship alongside the skill)

## Workflow

1. Copy `templates/pdf-house-style/page.html` into the task's working folder (not the
   customer's record folder; only the PDF goes there).
2. Delete the components you don't need. One page, one decision.
3. Fill in real content. Every number needs a source and a pull date in the footer.
4. Build. The display font is Geist Pixel Square: pass its `.ttf` with `--font` (the Recoup
   marketing repo keeps it under `design/fonts/GeistPixel/ttf/`). Without it the title falls
   back to Geist Mono, which is acceptable for drafts only.
5. Read the preview PNG. The script checks page count, dashes and links; it cannot see a
   clipped label, a wrapped title or an empty half-page. Shorten labels rather than
   letting them ellipsize.
6. Put the PDF in the customer's deliver folder with a README listing what it is, the checks
   it passed, and where the source HTML lives.

## Tokens

| Token | Value | Job |
|---|---|---|
| `--ink` | `#0a0a0a` | text, never pure black |
| `--ink2` / `--muted` | `#52524e` / `#8a8a85` | secondary text, labels, footer |
| `--line` | `#e6e6e3` | card outlines, drawn as `box-shadow: 0 0 0 1px`, never `border` |
| `--surface` | `#fafaf9` | the short-version box |
| `--accent` | `#2a78d6` | **the one thing that carries the point** |
| `--accent-tint` | `#e8f1fc` | background of a highlighted tile or card |
| `--ctx` | `#c9c9c4` | context: the comparison bar, the quiet status |

Type: Geist Pixel Square for the title and big numbers; Plus Jakarta Sans for labels,
headings and values; Geist for body. Radius 12px on cards, 4px on bar ends.

## Color rule: one accent, one job

Blue marks the part of the page the reader should act on; gray is everything it is
compared against. Use it for the same meaning everywhere on the page (the 70% share, the
clips that win, the zero that needs fixing, the targets that are active). Never a second
hue, never a rainbow of categories. Color is never the only signal: every bar has its value
printed, every dot has a text label ("Posted Jan 12", "Quiet since Dec 1").

## Components (all in the template, in this order)

| # | Component | Use it for |
|---|---|---|
| 1 | Header + pixel title | `prepared by Recoup · <ISO date>`, and `Next review: <month>` for anything recurring. Title line 2 in muted gray names the period or the promise |
| 2 | The short version | The whole argument in three sentences, before any data |
| 3a | Hero number + split bar | One share of a whole (older vs new, ours vs theirs). The big number in accent |
| 3b | Ranked bars | Magnitude comparisons. Width = value / max × 80%. Highlighted group in accent, comparison in gray, legend below |
| 4 | Stat tiles | Where things stand. Three or four per row; highlight at most one or two |
| 5 | Entity grid | Shows, artists, venues, targets: artwork, tag, one line on the fit, status dot + label, contact link. Highlight the first pick |
| 6 | Next moves | Three bold verb phrases with one sentence each. Say what not to do when it builds trust |
| 7 | Message card | A ready-to-send email or pitch: send details on the left, body on the right (CSS `.msg`; add when needed) |
| 8 | Sources footer | Every system and pull timestamp, footnotes for anything with a different date, and what the data cannot see |

Message card markup, when a page carries a draft for the customer to send:

```html
<div class="msg"><div class="side"><div class="label">The first pitch</div><b>Recipient</b>
To and from, subject, and "sent by you, only after your sign-off".</div>
<div class="body"><p>Hi Name,</p><p>Body.</p></div></div>
```

## Rules the checks enforce, and the ones they don't

Enforced by `scripts/build_pdf.py` (exit 1 on failure):
- Page count within `--max-pages` (default 1). The page has a fixed height, so overflow
  spills onto page 2 and fails; cut content, don't shrink type below ~7pt.
- Zero em or en dashes in the text.
- Every `<a href>` became a PDF link annotation.
- All `embed:` images are inlined as base64, so the file survives forwarding offline.

Your job, by eye:
- Every platform claim links to the exact profile measured.
- When two documents go out together, their shared numbers match (same count, same date).
  If sources disagree, pick one, use it in both, and footnote its date.
- Artwork for every entity row; faces for artists (see `references/meeting-prep.md`).
- The document argues only from what the customer already did.
