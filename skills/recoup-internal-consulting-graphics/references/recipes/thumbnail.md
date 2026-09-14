# Recipe: Thumbnail

The output whose only job is to **earn the click at tiny scale** — a YouTube thumbnail, a blog/article
hero, a LinkedIn/Open-Graph link-preview card. It is read at ~160px wide in a noisy feed, so it is the
*most* contrast- and hierarchy-disciplined thing the kit makes.

**Compose it as:** this recipe × a style template (usually `statement` for a hook, `stat` for a number)
× a format. Pull tokens from the project's top-level `DESIGN.md`.

## Format
- **YouTube / video:** 1280×720 (16:9).
- **Link / OG preview** (LinkedIn, X, blog share): 1200×630 (1.91:1).
- **In-feed thumbnail:** 1080×1350 (4:5) or 1080×1080.
- Exact specs + safe zones: `references/dimensions.md`.

> **Animated hero?** This PNG stays the **poster + OG image** (link-preview cards never animate). To add
> motion *on the owned blog*, mount a muted `<video>` loop behind it — drop-in template
> `library/web/blog-hero.html`, render the loop with `recoup-internal-consulting-hyperframes-video`. Playbook:
> `knowledge/sops/animated-media-for-posts-and-article-headers.md`.

## The craft bar (what makes it good)
1. **One 3–6 word hook, enormous.** The words *are* the design — they should fill roughly a third to a
   half of the frame. If it needs a sentence, it's a `statement` post, not a thumbnail.
2. **One high-contrast focal element.** A face mid-emotion, a single number, or one object/diagram — never
   a scene. The eye must land in <1 second.
3. **Maximum contrast.** Commit to a dark field (`--ink`/`--navy`) with one `--signal` pop, or a crisp
   light field with a near-black hook. No pale gradients, no mid-tones fighting the text.
4. **No body copy.** No paragraphs, no captions, no multi-line subheads. Supporting text (if any) is one
   short kicker.
5. **Footer is optional.** Thumbnails often drop the footer to maximize focal size — keep just the Recoup
   mark in a corner if it fits without crowding; otherwise omit.

## Composition pattern
Asymmetric: hook anchored to one side (or top/bottom third), focal element balancing the opposite weight.
Generous margins. The single `--signal` accent points the eye to the word/number that matters.

## The 160px test (non-negotiable)
Shrink the render to ~160px wide (or squint). If the hook isn't instantly legible and the focal element
isn't obvious, it fails — increase type size and contrast, cut elements, try again.

## Avoid (the tells)
Multiple ideas · paragraphs of text · low contrast · tiny type · a busy scene · 4+ colors · generic stock.

## Render
Single PNG at the target size:
```bash
npx playwright screenshot --viewport-size="1280,720" "file:///abs/path/thumb.html" "/abs/path/thumb.png"
```

## Quality checklist
- [ ] Hook ≤6 words and is by far the biggest element
- [ ] One clear focal element; eye lands in <1s
- [ ] Committed field + one `--signal` pop; AA contrast on the hook
- [ ] No body copy; ≤1 short kicker
- [ ] Passes the 160px / squint test
- [ ] On-brand type + palette from `DESIGN.md`
