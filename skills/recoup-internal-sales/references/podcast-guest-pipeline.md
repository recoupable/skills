# Podcast guest pipeline

The podcast is the top of the Agency Leads funnel, not a media project. A cold lead is
invited onto a 30 to 60 minute episode about their history in music and how they use AI;
the conversation tells us what to build for them. Started 2026-09-14. The operator's
working folder is `workspace/sales/podcast/` (pipeline README, invite templates, guest
folders, episode copy, cover generator); this file carries only what a cold reader needs
to run it the same way.

## The loop and the Attio mapping

| Step | What happens | Agency Leads |
|---|---|---|
| 1. Invite | Ten invites a day to qualified leads: people who own or run a music business and have said something public about AI or automation in it within the last 12 months. The invite sells the episode, not Recoup. | `New`, `lead_source = Podcast`; `project_type` stays unset until discovery confirms a build |
| 2. Reply | Any reply. Flag after 3 days with no time on the calendar, ahead of anything further down the board. | `In Conversation` |
| 3. Record | The booking confirmation carries the written consent: recording, publication on the named platforms, use of clips and of the guest's name, photo and company name, and the right to withdraw before publication. No consent on file, no recording. Then 30 to 60 minutes remotely: their history in the industry, where AI does real work in the business today, the numbers behind it. Recorder notes go to the private guest folder. | `Call Booked` |
| 4. Publish | Within 48 h, once the consent is on file and the guest has approved their cover photo: YouTube (show playlist), Spotify, Apple, socials; the episode is added to the site's `content/podcast/episodes.json` in the same PR; the guest gets the full episode and clips. | unchanged |
| 5. Day 7 | One short email with three concrete things we could build for them, drawn from the call notes. One sentence each, no price. | `Scoping`, `project_type = Build` |
| 6. Reply | A proposal for a 2 to 4 week build, priced from the current private rate card with a deposit plus delivery split, in the order `discovery-and-proposals.md` sets. Terms are proposals until accepted. | `Proposal Sent` |
| 7. Deposit paid | The build runs. | `Won` |
| 8. Delivered | Testimonial request and a post-mortem in the private guest folder. After three paid, completed, reviewed builds, review the rate. | unchanged |
| No reply after 3 touches, or a decline | Close it honestly. | `Lost`, `lost_reason` set |

No new stages, no new list; a guest is an agency lead with a different first touch. This
file is public: no names, emails, deal terms, price figures or the exclusion list here.

### The invite

Three sentences, one question, two links, no second offer, no em dashes. The hook is the
only line that takes research; name, topic and company are fills from the lead file, so
ten a day is a copy job.

```
Subject: Recoup Podcast invite: {{first_name}} on {{topic_short}}

{{HOOK: one sentence citing the specific thing they said or did about AI in their business, with where and when it was said.}}

I host the Recoup Podcast and I'd like to record a 30 to 60 minute conversation with you on how you got into music and how {{company}} is using AI in the business today; the episode goes out on YouTube, Spotify, Apple Podcasts and Recoup's socials, and you get the full episode and clips to post yourself.

Would you be up for recording in the next two weeks? Pick any slot that suits you here: {{booking_link}}
```

- **Hook:** one fact, one source, dated inside the last 12 months. A quote is best, a public
  action is fine, a guess is not allowed. No AI statement found means they are not a fit for
  this funnel; use the standard outreach instead.
- **Links:** "Recoup Podcast" links to
  `https://recoupable.dev/podcast?utm_source=email&utm_medium=invite&utm_campaign=<yyyy-mm>`
  (send month), so a guest request shows its batch in the CRM note. The booking link is
  printed as is. No third link.
- **Before sending:** email verified; not a customer or a live agency lead (CRM and login
  records, read-only); not on the exclusion list; the exact draft approved by the operator.
  Ten a day is a target, not an approval.
- **After sending:** sent copy, provider id and approval evidence go in the private guest
  folder; the CRM note names the file.

### The day-7 follow-up

Subject `Three things we could build for {{company}}`. One line from the recording, then
three numbered sentences, each naming a workflow they described, what we would build, and
the result they would see. Close with one question: which of the three is worth a 20 minute
call. No price, no deck, no link but the episode.

### Measure

Vercel Web Analytics on `/podcast`: `podcast_platform_clicked`, `podcast_episode_clicked`,
`subscribe_submitted` (source `/podcast`), `podcast_guest_requested`. In the CRM: guests by
`lead_source = Podcast` at each stage, and the count that reached `Won`. The number that
matters is paid builds per ten invites; report it monthly against the invite batches by
`utm_campaign`.

## Episode copy that supports a premium price

Guests and prospects read the episode page before they read anything else we send. Every
title and description is sales copy for a firm that charges six figures for a build:

- **Title shape:** `<the specific claim> w/ <Guest Name>`. Panels end in `(panel)`.
- **Description:** one specific claim in the first sentence, hard nouns over adjectives,
  no hype words, no emoji, no em dashes, guest links kept, then one fixed closing line:
  *"Recoup designs and builds the systems behind conversations like this one: catalog data,
  royalty operations, and AI agents for labels, publishers, funds and management companies.
  recoupable.dev"*
- **Cold open:** a 6 to 14 second clip of the guest's strongest line sits between the intro
  sting and the episode, on every platform.
- **Back catalog:** a Web3-era episode is reframed to the business lesson in the title and
  first sentence, not rewritten into something it was not. Six were retitled 2026-09-14;
  the copy is in `workspace/sales/podcast/episodes/retitle-2026-09-14.md`.

## Cover spec (measured from the reference show's thumbnails, 2026-09-14)

The reference thumbnails are 2000×1125 (some 4000×2250). Fractions are of the short side
(H) unless marked W, so the same numbers drive the square Spotify art.

| Element | Spec |
|---|---|
| Canvas | 16:9 for YouTube and site cards; 1:1 for Spotify episode art (min 1400², we ship 2000²) |
| Margin | 10% H on every side (112 px at 1125). Logo, title and guest line all start on the left margin |
| Logo | Show lockup, height 12.5% H (140 px), top-left corner on the margin |
| Title | Left column, max width 47.5% W; font 8.9% H (100 px), medium weight, line pitch 1.27×; 2 to 3 lines; the block sits in the lower half, ending ~28% H above the bottom |
| Guest line | Under the title: name at 4.1% H semibold, org/role at 3.7% H regular, bottom of block 18% H above the bottom edge |
| PFP placement | Right side, from 40% W to the right edge, face centred at ~71% W; head top on the top margin (10% H); shoulders bleed off the bottom edge |
| PFP style | Background-removed cutout of a real photo, full colour, no circle, no frame, no tint, no drop shadow; the sweep shows around the silhouette |
| Colour | Reference uses dark ink on a flat accent; ours is white type on the Recoup Podcast blue sweep (`assets/recoup-podcast-blue-sweep-background.png`, lockup `recoup-podcast-white-transparent.png`) |

Square derivation: same margins and logo; title column 47% W and the title auto-steps
down (8.9 → 5.2% H) until the block clears the lockup row; the cutout is 62% H tall,
centred at 74% W, anchored to the bottom edge. `workspace/sales/podcast/scripts/make-covers.py`
implements both.

## Guest photo sourcing

Use the guest's own published artist image, never a fan photo or a screenshot.

- **Spotify artist image (best, no auth):** `https://open.spotify.com/oembed?url=https://open.spotify.com/artist/<id>`
  returns `thumbnail_url` at 320 px. Swap the image-id prefix `ab67616100005174` for
  `ab6761610000e5eb` to get the 640 px original from the same CDN.
- **Cutout:** `rembg` (bria-rmbg model, ~1 GB first download). It does not install on
  Python 3.13 (numba/llvmlite); use a 3.12 venv, `pip install --no-deps rembg` plus
  `onnxruntime numpy pillow opencv-python-headless scipy pooch jsonschema tqdm scikit-image`,
  and stub the three `pymatting` imports in `rembg/bg.py` (only alpha-matting needs them).
  Check the mask on a flat colour before using it.
- Store `guests/<slug>/headshot-source-<origin>.jpg` and `headshot-cutout.png` in the
  workspace; the cover script picks the cutout up by slug.

## Editing episodes on Spotify for Creators

The dashboard is the only write path (the RSS is read-only and cached for up to an hour, so
verify in the dashboard, not the feed). Learned on the 2026-09-14 run:

- **Login needs the human.** Automated logins hit "We need to make sure that you're a human";
  open a headed `agent-browser` window, let the operator log in and solve it, then drive.
  **Save the auth state immediately** (`agent-browser state save <file>`): a browser relaunch
  drops the session and every edit after that silently lands on the login page.
- Two shows can share one account. Pick the show by its id in the URL
  (`/pod/show/<showId>/episodes`), not by name; an empty duplicate "Recoup Podcast" show
  exists on the same login.
- Episode details page: tick the **HTML** switch (click the checkbox via the DOM, the
  label click does not register), then `fill` the title input and the HTML textarea.
  Paragraphs as `<p>`, links as `<a href>`; the editor strips nothing else we used.
- **Cover upload:** the page has two image `input[type=file]`; the first (`#show-art-upload`)
  is the SHOW cover, the second is the episode cover. Uploading to the first overwrites the
  show art. Give the second an id, upload to it, then click the crop dialog's own Save (the
  last `Save` button in the snapshot), wait ~10 s, then the page-level Save.
- Search on the episodes list is a plain substring; "w/ Kantor" with a trailing space in the
  stored title did not match, "Kantor" did.
