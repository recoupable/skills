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
| 3. Booked | The same day a time exists, a confirmation email in the invite's thread with the **timeline PDF** attached (see *Booked: the timeline PDF* below). It is the guest's written record of what happens next. | `Call Booked` |
| 4. Record | Written consent, sent with the interview outline 48 hours before, covers: recording, publication on the named platforms, use of clips and of the guest's name, photo and company name, and the right to withdraw before publication. No consent on file, no recording. Then 30 to 60 minutes remotely: their history in the industry, where AI does real work in the business today, the numbers behind it. Recorder notes go to the private guest folder. | `Call Booked` |
| 5. Publish | Within 48 h, once the consent is on file and the guest has approved their cover photo: YouTube (show playlist), Spotify, Apple, socials; the episode is added to the site's `content/podcast/episodes.json` in the same PR; the guest gets the full episode and clips. | unchanged |
| 6. Day 7 | One short email with three concrete things we could build for them, drawn from the call notes. One sentence each, no price. | `Scoping`, `project_type = Build` |
| 7. Reply | A proposal for a 2 to 4 week build, priced from the current private rate card with a deposit plus delivery split, in the order `gtm/playbooks/discovery-and-proposals.md` (marketing repo) sets. Terms are proposals until accepted. | `Proposal Sent` |
| 8. Deposit paid | The build runs. | `Won` |
| 9. Delivered | Testimonial request and a post-mortem in the private guest folder. After three paid, completed, reviewed builds, review the rate. | unchanged |
| No reply after 3 touches, or a decline | Close it honestly. | `Lost`, `lost_reason` set |

No new stages, no new list; a guest is an agency lead with a different first touch. This
file is public: no names, emails, deal terms, price figures or the exclusion list here.

### The invite

40 to 75 words: one real reason for writing, one sentence about the show, one specific
question. The hook is the only line that takes research; everything else is written fresh
for each guest. Operator rulings from the 2026-09-22 run (five rounds of review copies)
are marked; treat them as defects to check before every review copy, not style tips.

```
Subject: Interview request: {{topic, a few lowercase words}}

Hi {{first_name}},

{{HOOK: the specific thing they said or did about AI in their business. The phrase that
names the source ("your transparency report", "told Billboard") links to it.}} {{One
question about it that only they can answer.}}

I host the Recoup Podcast, 14k YouTube subscribers. {{A plain ask, worded differently
from every other email in the batch.}}
```

Checklist before any review copy leaves (each one was a real defect on 2026-09-22):

1. **Subject is `Interview request: <their topic>`**, e.g. `Interview request: the
   transparency report`. Not `Recoup Podcast: <Name>?` and not a headline.
2. **No sign-off in the body.** The house footer already carries the name; a name line
   above it is redundant.
3. **No stock close.** "Up for it?" and its cousins ("worth it?", "still open to it?") read
   as automation, worse when repeated across a batch. End on the specific question or a
   plain ask that no other email in the batch uses.
4. **Run the whole `unslop` skill, including its final self-audit ("what makes this
   obviously AI-generated?"), per draft and across the batch.** No sentence may appear in
   two emails of the same batch; the podcast sentence is the usual offender. Cut
   unverifiable claims ("nobody talks about this"), flattery ("so you'd know") and invented
   reactions ("the line I keep thinking about"). Never record "unslop: done" unless the
   self-audit happened.
5. **Link the source.** Any piece the body mentions (a post, report, column, interview)
   carries a hyperlink to it on the phrase that names it; the plain-text part prints the
   URL after the phrase. Open every URL before the review copy.

- **Hook:** one fact, one source, dated inside the last 12 months and read at the source.
  Research tools mis-attribute quotes between people and summarisers paraphrase; confirm
  the exact words on the page. No AI statement found means they are not a fit for this
  funnel; if the operator still wants the guest (a history episode), flag it in the lead
  file and let them decide.
- **Links:** "Recoup Podcast" links to
  `https://recoupable.dev/podcast?utm_source=email&utm_medium=invite&utm_campaign=<yyyy-mm>&utm_content=<lead-slug>`
  so a visit attributes to one guest; review copies use `utm_medium=review` so internal
  clicks never count. The source link is the only other link. No booking link in a first
  touch; scheduling comes after they say yes.
- **Before sending:** email verified; not a customer or a live agency lead (CRM and login
  records, read-only); not on the exclusion list; a review copy in the operator's inbox;
  the exact draft approved by the operator. Ten a day is a target, not an approval.
- **After sending:** sent copy, source links, provider id and approval evidence go in the
  private guest folder; the CRM note names the file; a dated follow-up task (+5 business
  days) written as a runbook.

### Nudges

Silence after 5 business days gets one nudge with a new angle (a second thing they said),
sent as a reply in the invite's thread (`In-Reply-To` and `References` set to the invite's
Message-ID, subject `Re: <invite subject>`). Same checklist: no sign-off, no stock close,
source linked, unslop across the batch. Second nudge at +10, `Lost` at three touches.
Nudges drafted and never sent are the common failure: check for them at the start of
every run.

### Running the day

- **Start with status, not research.** Provider `last_event` for every sent invite (only
  `bounced` means anything within minutes of sending; `opened`/`clicked` in the first
  seconds are mail scanners), per-lead page views by `utmContent`, due follow-up tasks and
  any unsent nudge drafts.
- **Check the research budget first.** A lead-research agent that runs out of credits
  mid-run leaves the day short; confirm the balance, run the named-person enrichment
  early (it is the cheapest source of verified addresses), and say plainly when the list
  is short and why instead of padding it.
- **Verification ladder:** an address published by the person (best), an SMTP `RCPT TO`
  probe with a random-address control (works only on Google-hosted mail; Outlook,
  Proofpoint, Rackspace and small hosts reject or drop the probe), then an enrichment
  address on a catch-all domain, where a bounce on send is the only signal. Never guess a
  pattern.
- **Login-record lookups:** some identity APIs sit behind a bot filter that rejects
  default HTTP-library user agents with 403; a 403 there is not a permission answer. Use
  curl or set a user agent before concluding access is broken.
- **Show the whole draft, send review copies of every round.** The operator reviews in
  their inbox; each fix round is a fresh review copy, and the approval quote goes in the
  sent record.

### Booked: the timeline PDF

Every booking gets the same follow-up, sent the day the time is confirmed (by the guest
picking a slot, by their booking page, or by the operator booking on the guest's own
scheduler). Nothing about the recording is left to the calendar invite alone.

1. **Fix the calendar invite first.** Title `Recoup Podcast recording: <Guest Name>`, the
   recording-studio link as the location, and the scheduler's auto-generated video link
   and reschedule text removed. A booking made on the guest's own scheduler carries *their*
   video link; the guest must get ours from us.
2. **Build the timeline PDF.** One Letter page, house style (`references/pdf-house-style.md`),
   titled *Your episode, step by step*, with the guest's name, title and company. Three
   numbered steps, each with a real date:
   1. *Your interview outline arrives*: the date, 48 hours before the recording.
   2. *We record*: date and time in the guest's timezone, the studio named, "join from the
      link in your calendar invite", scheduled length and expected recording length.
   3. *It goes live, and we tag you*: where it goes out (show platforms and socials) and
      **who we tag**: every account for the guest and their companies, each one checked on
      the platform before it goes in.
   Close with "Anything off?": reply to change the tag list before anything goes out.
   Store the HTML beside the PDF in the private episode folder (`episodes/<date>-<slug>/`).
3. **Send it as a threaded reply.** `Re: <invite subject>`, `In-Reply-To`/`References` on the
   invite's Message-ID, BCC the cofounder, PDF attached. Body is two sentences: they are
   confirmed for the Recoup Podcast (linked, `utm_medium=reply`) at the date and time, and the
   attached one-pager covers next steps (outline date, the studio, the tag list). The
   send-path gotcha: a payload with a PDF attachment overflows a command-line argument, so
   pipe it to the HTTP client from stdin.
4. **Approval as usual:** the exact draft and the PDF shown to the operator; a review copy
   when they ask for one. The approval quote goes in the sent record.
5. **Close out:** stage `Call Booked`, the sent file names the PDF, and two dated runbook
   tasks: the outline plus written consent 48 hours before, and a studio test the day
   before. The consent gate in step 4 of the loop still applies: no consent on file, no
   recording.

A confirmation without the PDF is incomplete: the timeline is what makes a cold guest show
up prepared and makes the tag list theirs to correct before publication.

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
| Colour | Reference uses dark ink on a flat accent; ours is white type on the Recoup Podcast blue sweep (the show's blue-sweep background and white lockup PNGs, in the operator's workspace) |

Square derivation: same margins and logo; title column 47% W and the title auto-steps
down (8.9 → 5.2% H) until the block clears the lockup row; the cutout is 62% H tall,
centred at 74% W, anchored to the bottom edge. The table is the spec; the operator's private
workspace carries a Pillow script and the two brand assets that implement it, and they are
not shipped with this skill.

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
