# Template: A practical framework

Working-document structure with numbered steps. Reference: carousel-catalog-index, carousel-blueprint or carousel-blue-notes.
These are new Recoup layout shells, not exact replicas of Studio Finals. For an exact approved
carousel template use its hashed kit in brand/finals.json. Preserve its own related palette.

Run `node <installed-skill>/brand/materialize.mjs <output-directory>` and save the HTML there.
Fill the content/attribution slots (omit attribution if unnecessary). Example copy is illustrative.
Default canvas 1080×1350; recompose for another aspect ratio using dimensions.md and the output recipe.

```html
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><link rel="stylesheet" href="recoup-brand/brand.css"><style>*{box-sizing:border-box;margin:0}body{width:1080px;height:1350px;padding:80px;position:relative;overflow:hidden;font-family:var(--brand-body-font),sans-serif;color:var(--ink);background:var(--paper)}
.kicker{font:400 20px var(--brand-label-font),monospace;letter-spacing:.12em;text-transform:uppercase}
h1{font-family:var(--brand-display-font),sans-serif;font-size:88px;font-weight:500;line-height:1.06;letter-spacing:-.045em;margin:64px 0 32px;max-width:900px}p{font-size:30px;line-height:1.45;font-weight:400}em{font-style:normal;background:var(--signal);color:var(--ink);padding:0 .08em}
footer{position:absolute;bottom:64px;left:80px;right:80px;display:flex;justify-content:space-between;align-items:center;font-size:22px}footer img{width:190px;height:auto}.notes{display:grid;gap:22px;margin-top:48px}.note{background:var(--tint);border:1px solid var(--recoup-border);border-radius:18px;padding:28px 32px;font-size:32px}.note b{font-weight:500}.note span{font:400 20px var(--brand-label-font);margin-right:24px;color:var(--recoup-link)}</style></head><body><div class="kicker">RECOUP / A PRACTICAL FRAMEWORK</div><h1>From a question<br>to a <em>next step.</em></h1><div class="notes"><div class="note"><span>01</span><b>Gather</b><p>Bring the relevant sources together.</p></div><div class="note"><span>02</span><b>Understand</b><p>Find what changes the decision.</p></div><div class="note"><span>03</span><b>Act</b><p>Name the owner and the next step.</p></div></div><footer><img src="recoup-brand/logos/lockup-ink.svg" alt="Recoup"><span>{{ATTRIBUTION_OR_CONTEXT}}</span></footer></body></html>
```

Check font loading, exact mark, contrast, safe margins, text overflow and phone-size readability.
Keep one main idea. Use actual evidence for a stat; never infer a number from example copy.
