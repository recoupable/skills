# Example pipeline brief (spoofed)

> A sanitized example of the qualification output this skill produces from a real funnel
> run. **All names, emails, artists, and IDs below are fictional** - illustration only.

## Top leads, by catalog value (valued in the last ~24h)

| Email (spoofed) | Holder | Artist valued | Followers | Lifetime streams | Est. value | Relationship | Route |
|---|---|---|---|---|---|---|---|
| neontidemusic@example.com | Alex Rivera | Neon Tide | 47.8k | 41.2M | $312,500 | Owner/Operator | **Pursue** |
| lunalabel@example.com | Luna Collective (label) | Sora Vale | 51.0k | 33.9M | $268,400 | Label | **Pursue** |
| dj-paperclip@example.com | (collaborator) | Paperclip | 38.1k | 49.5M | $284,900 | Collaborator | **Pursue** |
| midtempo@example.com | - | Mild Current | 7.1k | 4.4M | $16,200 | Unknown | Backlog (small) |
| fan-typed-this@example.com | - | The Bedroom Demos | 0.2k | 5.5k | $220 | Fan/Other | Lost (junk) |
| pr-test@example.com | - | (seed row) | - | - | - | Unknown | Lost (test row) |

## Why the top three qualify

- **Real, mid-size catalogs** - tens of millions of lifetime streams, six-figure estimated
  value: actual recurring earnings to grow and recover against.
- **Official enough to say yes** - owner, label, and an insider collaborator.
- **Recent + intent** - all valued within a day; high engagement.

## Next actions (per pursued lead)

1. Enrich the Attio entry: set `catalog_value`, `relationship`, `owner`; keep stage at `New`.
2. Render the valuation PDF (`scripts/render_valuation_pdf.py`).
3. Draft the welcome email (`templates/outreach-email.md`) with one free insight.
4. Send, then advance to **Report Delivered** and log a note.

## Example filled outreach (spoofed)

> **Subject:** Neon Tide - your catalog valuation (+ one thing I'd fix first)
>
> Hi Alex, I'm Sam from Recoup - I saw you just ran a valuation on **Neon Tide**. Here's the
> full breakdown: **$312,500**, off 41.2M lifetime streams. [attach: Neon-Tide-valuation.pdf]
>
> One thing jumped out: several high-traffic playlists your closest peers sit on don't yet
> include Neon Tide, and 41M streams almost always have uncollected neighboring-rights and
> Content-ID income. I can quantify both for free.
>
> I help catalogs like Neon Tide's actually *grow* that number - recover what you're owed and
> lift monthly streams, tracked against this baseline. 15 minutes this week?
>
> - Sam
