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
| 5. Publish | **Owned by the podcast skill:** post-production through scheduling follows the `recoup-internal-podcast` skill's `references/podcast-episode.md`; sales resumes at the live-links email. Within 48 h, once the consent is on file and the guest has approved their cover photo: YouTube (show playlist), Spotify, Apple, socials; the episode is added to the site's `content/podcast/episodes.json` in the same PR; the guest gets the full episode and clips. | unchanged |
| 5b. Wrap-up | The day the last short posts (about a week after the episode): one threaded email that closes the run and asks for guest recommendations (see *The wrap-up email*). Goes to the guest and anyone they looped in (comms, assistant). | unchanged |
| 6. Day 7 after release | One short email with three concrete things we could build for them, drawn from the call notes. One sentence each, no price. | `Scoping`, `project_type = Build` |
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

### Right after the recording (same day)

The recording is the discovery call; close it out before anyone opens the raw files. Learned on the
2026-10-13 run, where the release plan, two deliverables and their dates were agreed only on tape.

1. **File the recorder notes** in the private episode folder (`episodes/<date>-<slug>/recording/`):
   the summary and the transcript, verbatim as pasted, each with a header that says where the interview
   starts and ends and what is off air. Above the pasted summary, write what was agreed off air: release
   date, every deliverable promised with its date (clip folder, live links, analytics), tag handles, cuts
   or off-the-record requests, and any correction the guest made. Then two lists: the recorder's
   mishearings (names, companies, products), and **claims to check before any card**: every figure the
   guest gave, anything the guest corrected on tape, and dates that contradict the record. Check the
   plan's never-raise items were not raised.
2. **Write the episode README** status: recorded, consent, release and deliverables as agreed, next steps.
   Update the plan's status line and the guest's email index.
3. **CRM:** a note naming the files; complete the outline task; one dated runbook task per promise made
   on tape, plus release day and the day-7 email. **Day 7 counts from release, not from the recording.**
   The stage stays `Call Booked` until the episode is live.
4. **Collect build angles** for the day-7 email while the call is fresh: each workflow the guest described,
   with the numbers they gave. Not an offer until drafted and approved.
5. **Hand over to post-production** at the raw files (`recoup-internal-podcast` → `references/podcast-episode.md`).

### The wrap-up email

Sent the day the last short goes out, so the guest hears "it's done" from us instead of
noticing the posts stop. It has two jobs: close the run with a thank-you, and turn the guest
into the source of the next guest. First run 2026-10-11. Write it on that day; the day-7
build email is a separate decision (see below).

```
Subject: Re: <invite subject>        (threaded on the latest message in the guest thread)
To: the guest + everyone they looped in (comms team, assistant); CC the cofounder

Hi {{first_name}}{{ and comms contact first_name}},

The last of the {{n}} clips went out today, so the episode run is complete. Thank you {{both}}.
{{One line acknowledging something they actually did, e.g. listened, reshared, posted a clip;
leave it out if nothing happened.}}

Attached is every post on every platform, as a one-page PDF and a spreadsheet, so you can
reshare whichever channels suit you. The video files are still in the folder if you'd rather
post from your own accounts: {{clips folder link}}

One ask before we close the thread: who should we have on next? {{Their strongest point from
the episode, restated as they made it}} is the thread we want to keep pulling, so we're looking
for {{two or three kinds of people tied to that point, e.g. the other side of the deals they
described}}. If someone comes to mind, an intro or just a name helps.

Recoup Podcast: https://recoupable.dev/podcast?utm_source=email&utm_medium=reply&utm_campaign=<yyyy-mm>&utm_content=<guest-slug>
```

**The attachments: every post, every platform.** One row per post in a CSV
(`item,title,date,platform,account,url`; item is `Full episode` or `Clip <n>`), built from the
post ledger, every URL opened (200) before it goes in. The PDF is generated from the same CSV
so the two never disagree:

```
python3 scripts/podcast_posts_sheet.py <guest>-recoup-podcast-posts.csv --brand <recoup-sky brand kit> \
  --guest "<Name>" --role "<Title>, <Company>" --company "<Company>" --role-url <company site> \
  --slug <guest-slug> --campaign <yyyy-mm> --out posts-sheet.html --pdf recoup-podcast-posts-<guest-slug>.pdf
```

It uses the same brand kit and layout as the guest brief and the timeline PDF (lockup header,
sky labels, the meta strip, a pale card for the full episode, the forest note), so the guest's
three PDFs read as one set. The script fails on more than one page, an em or en dash, or a CSV
URL that did not become a link. Read the preview before attaching. Store the CSV, HTML and PDF
in the private episode folder (`episodes/<date>-<slug>/release/wrap-up/`).

Rules:

1. **Make the guest ask specific.** Name the kinds of people, tied to the guest's own point on
   the episode. "Any recommendations?" gets a polite "I'll think about it" and no names.
2. **Only real things.** A number (views across the clips, a tagged visit count) goes in only
   if it was measured that day; a reshare or post is acknowledged only if it happened.
   Otherwise leave both out rather than estimating.
3. **Address everyone who was looped in.** A guest's comms team often joins the thread after
   recording; they are the people most likely to repost later, so they get the folder link too.
4. **Same send path and checklist as every guest email:** threaded reply, no body sign-off,
   no stock close, unslop with the self-audit, review copy in the operator's inbox, exact
   draft approved, approval quote in the sent record.
5. **Close out:** log it in the guest's email record; every name they send becomes a lead with
   `lead_source = Podcast` and "referred by <guest>" in the first invite's hook research.

**Wrap-up vs. day-7.** The shorts run one a day for seven days, so the wrap-up and the day-7
build email can fall on the same day. Don't send two emails in one day. Send the wrap-up
first; send the day-7 build email only if the call surfaced a real build, and a few days later
in its own thread. A guest who is not a build lead (a consultant, a peer) gets the wrap-up only.

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


## Episode packaging and production

Episode copy, the cover spec, guest photo sourcing and Spotify for Creators edits live in the
`recoup-internal-podcast` skill (`references/podcast-packaging.md`), with post-production and shorts.
