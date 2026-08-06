# Meeting prep — the qualified-customer call

The send loop ends when a lead books a call. This is what happens next, and it is a
different motion: no longer "who do we contact", but "what do we put in front of someone
who has already agreed to spend thirty minutes with us."

Produces exactly three artifacts: **a pitch, a meeting plan, and the PDFs to deliver.**
Proven on Secondhand Talent (2026-08-04) and Duetti (2026-08-06).

## 1. Mine what they already told us

**Read the chat message BODIES, not the titles.** Titles are auto-generated and routinely
describe the wrong thing. On Duetti, every session was titled "Create New Artist"; the
bodies showed the buyer was building *artist marketing strategy decks*:

> *"what marketing channels can be good for them? between sirius XM, spotify, outdoor advertising, press, tiktok?"*
> *"i need to map out slides for a presentation"*
> *"can you share with me a north star goal for and 2 key supporting objectives for his integrated marketing strategy deck?"*

The entire pitch came from that gap. The titles alone would have produced the wrong call.

```
chat_messages.parts is a JSON object wrapping a nested list:
  {"id":…, "role":"user", "parts":[{"type":"text","text":"…"}]}
Extract with parts["parts"][*]["text"] — a naive parts[*] read returns nothing.
Path: sessions.account_id → chats.session_id → chat_messages.chat_id, role='user'.
```

Then read the full email thread and the Attio interaction fields (see *The contact dossier*
in SKILL.md). What the customer typed in their own words beats anything inferred.

## 2. Find the gap between public promise and published process

Read the customer's own website — homepage, about, and whatever page is aimed at the people
they serve. Write down the promises verbatim and the published process steps.
**The pitch is the gap between the two.**

Duetti's site promised "active catalog management" and "artist awareness with streaming
growth" to 1,100+ partners, but its published process was three steps ending at "Get paid" —
nothing after the transaction. That gap, plus a buyer who had been filling it by hand for
four weeks before giving up, *is* the pitch.

## 3. The pitch

Say what promise **they** made that they cannot keep at their scale, and position Recoup as
the layer that keeps it.

Never pitch the feature ("we send reports") — a feature gets priced per seat against a
dashboard. An operating-layer pitch is what supports an enterprise number.

Land it on something they already did: *"your own team was building this by hand last
October; this is the same work, running on its own."* Evidence from their own history beats
any claim about their goals.

## 4. The meeting plan

A table of time block → what you do → the win condition for that block.

- **Open on work already done**, not on introducing Recoup.
- **Put the discovery question early and stop talking after it.** The best question is one
  you genuinely cannot answer yourself.
- **Ask the scale question as a question** so they do the arithmetic out loud, rather than
  pitching the answer.
- **Close on the smallest real commitment** — usually a cadence, not a price. Get the
  cadence and the tier follows; lead with price and neither lands.
- **Respect the booked length.** A 30-minute slot is a 30-minute plan.

## 5. The PDFs — four shapes

Two is usually right for a first call.

| Shape | Job | Survives the call? |
| --- | --- | --- |
| **The data foundation** | Measured facts about *their* business | ✅ always |
| **A concrete deliverable built from their data** | Something usable tomorrow; proves the product by using it | ✅ always |
| **The argued case** | One recommendation, argued from their numbers | ⚠️ often needs re-aiming |
| **The options analysis** | Ranked paths, with one explicitly ruled out | ⚠️ most likely to be wrong |

**Invest in the first two; keep the last two short and hedged.** Secondhand Talent's four
were all written pre-call from an email thread. On the call the customer revealed the podcast
existed to feed a **production house**, not to be a media property — and the two argued
documents had been reasoning toward the wrong objective. The data report was untouched,
because measured facts do not care what the goal turns out to be.

Corollary: argue from **something the customer already did**, never from an assumed goal.

### House format

- Title, then `prepared by Recoup · <ISO date>`.
- A **`THE SHORT VERSION`** paragraph before any data — the whole argument in three sentences.
- Big stat blocks: `EPISODES 116` · `TOTAL RUNTIME 97 hrs` · `AUDIENCE, OWNED 0`.
- Every claim carries a measured number, its source, and the date it was pulled.
- **Say what not to do.** Secondhand Talent's monetization doc opens by killing CPM
  advertising: *"a single episode holds roughly two dollars of conventional ad inventory. No
  ad network will take that on, and the effort to pursue one returns nothing."* That
  paragraph is why the document is trusted.
- One document, one decision. Do not merge them.

### Name a recurring deliverable with its period, not its contents

"Artist Partner Review — August 2026" implies a September edition. "Roster Report" is a
one-off. Add a `Next review: <month>` footer. When the goal is a standing cadence, hand them
a document that has already assumed one.

## Guardrails

- **Never bring an account-health / account-status PDF to a prospect.** That format
  (`recoup-internal-account-health-report`) is internal tooling — account ids, credits,
  sandboxes, chat titles, a "Verdict" banner. Run it on a quiet account and you hand someone
  an audit of their colleague's inactivity.
- **Every number carries its limits on the same page** — Spotify-only, asset value not a bid,
  model weakest past ~3 years. Raise the weakness before a buyer who prices these
  professionally finds it; that is what buys credibility.
- **Don't answer in a document a question you should ask in the room.** "Which of these
  artists are actually yours" is discovery, not a deliverable.
- **Make everything forwardable.** The person on the call is often not the economic buyer.
  They will have to sell it internally without you.
- **Don't quote off a stale billing record.** Check whether collection is paused or the
  subscription is real before naming any number; defer with "let me confirm and come back."

## Worked examples

- Secondhand Talent, 2026-08-04 — four PDFs (catalog report, guest recommendations, the
  newsletter case, monetization options), all written pre-call from an email thread.
- Duetti, 2026-08-06 — pitch + meeting plan + two PDFs, built from 31 chat-message bodies,
  the email thread, and the customer's own website.
