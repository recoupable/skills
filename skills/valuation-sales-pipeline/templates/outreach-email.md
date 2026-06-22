# First outreach email - template

First touch is **scannable in 3-5 seconds** - a busy inbox gives you a glance, not a read. Keep it
to **2 sentences + 3 bullets + 1 CTA**. From the **rep personally**; reference the **specific artist
+ their number**; **deliver the valuation PDF** as the long-form next step (give before you ask);
plain hyphens only (no em/en dashes, which read as AI-generated). Put the depth in the PDF, not the
email - the PDF is there for anyone who wants the data before taking the CTA.

## Reusable template

> **Subject:** {Artist} - your catalog valuation ({hook})
>
> Hi {first_name}, your {Artist} valuation {one-line context}. I finished the run - full breakdown
> attached, and the headline is a lot bigger: [attach: {Artist}-valuation.pdf]
>
> - {bullet 1 - the corrected headline: full lifetime streams vs. what the tool measured}
> - {bullet 2 - corrected value vs. the figure the tool showed}
> - {bullet 3 - one free insight: concentration, uncollected royalty source, master-vs-publishing}
>
> Worth 15 minutes this week to walk through it? [calendar link]
>
> - {rep_name}

Three short bullets, max one line each. If a point needs a sentence of caveat, it belongs in the
PDF, not here. Don't pitch the engagement in the cold email - that's the call (see Lever below).

## Variables

| Variable | Source |
| --- | --- |
| `{Artist}` | person record `looked_up_artist` |
| `{first_name}` | person record `name` (or "there") |
| `{hook}` | the one-glance reason to open - e.g. "your valuation was cut short (real number is ~10x higher)" |
| `{one-line context}` | the setup the bullets pay off - e.g. "stopped partway and priced it at {tool_value} off ~9% of the catalog" |
| `{bullet 1-3}` | from the lead JSON / PDF: corrected streams, corrected value vs. tool, one insight |
| `{rep_name}` | the Attio `owner` working the lead |
| `[calendar link]` | the rep's booking link |

## Lever (for the follow-up call, not the cold email)

Keep the cold email about *their* number + the CTA. Save the engagement framing for the call, and
tailor it to the relationship:

- **Owner/Operator** -> catalog growth + recovery on their own catalog. Strongest pilot fit.
- **Label / Manager / distributor** -> buyer-ready baseline + measurement/recovery across the whole roster.
- **Collaborator** -> artist-to-artist; deliver the baseline, confirm their role, widen later.
