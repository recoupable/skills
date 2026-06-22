# First outreach email — template

Principles: from the **rep personally**; reference the **specific artist + their number**;
**deliver the valuation PDF** (give before you ask); include **one free, specific insight**;
end with a **tiny CTA**. Founder/operator-to-operator, not salesy. Tailor the lever to the
relationship (owner vs. label vs. collaborator).

## Reusable template

> **Subject:** {Artist} — your catalog valuation (+ one thing I'd fix first)
>
> Hi {first_name}, I'm {rep_name} from Recoup — I saw you just ran a valuation on
> **{Artist}**. Here's the full breakdown: **{est_value}**, off {streams_millions}M
> lifetime streams. [attach: {Artist}-valuation.pdf]
>
> One thing jumped out: {one specific, free insight — a playlist gap, a likely-uncollected
> royalty source like neighboring rights / Content ID, or a concentration note}. That alone
> is usually worth more than the tool fee.
>
> I help catalogs like {Artist}'s actually *grow* that number — recover royalties you're
> already owed and lift monthly streams, measured against today's baseline. Worth a 15-min
> call this week? Happy to send a short growth plan first either way.
>
> — {rep_name}

## Variables

| Variable | Source |
| --- | --- |
| `{Artist}` | person record `looked_up_artist` |
| `{first_name}` | person record `name` (or "there") |
| `{est_value}` | `est_catalog_value` |
| `{streams_millions}` | `lifetime_streams` / 1e6, rounded |
| `{rep_name}` | the Attio `owner` working the lead |
| `{one specific insight}` | from research — playlist gap, uncollected royalty source, concentration |

## Lever by relationship

- **Owner/Operator** → catalog growth + recovery on their own catalog. Strongest pilot fit.
- **Label / Manager** → buyer-ready baseline + measurement/recovery across the whole roster.
- **Collaborator** → artist-to-artist; deliver the baseline, confirm their role, widen later.
