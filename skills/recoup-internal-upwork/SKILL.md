---
name: recoup-internal-upwork
description: >-
  INTERNAL — Recoup staff tooling, gated by the recoup-internal keyword. Invoke
  ONLY when the request explicitly includes "recoup-internal" (e.g.
  "recoup-internal apply to this Upwork job"). Never use for customer-facing or
  artist requests.
  Find and apply to Upwork contract work end to end: triage the client before
  writing anything, verify every claim against the actual repositories, draft
  the cover letter and screening answers, pick the right work-sample pack, set
  the rate, and log the outcome so the filter improves. Use when asked to
  "apply to this Upwork job", "write an Upwork proposal", "should I bid on
  this", "triage this client", "is this job worth connects", "find Upwork jobs
  worth applying to", or when an Upwork job posting is pasted in. Requires a
  local workspace directory and read access to the repositories behind any
  claim being made.
---

# Upwork: find work and win it

The repeatable motion for turning an Upwork posting into a submitted proposal.
Built from real proposals starting 2026-08-11; every rule below exists because
breaking it cost something.

**Connects are money and attention is scarce.** Most of the value in this skill
is in refusing jobs (Step 0) and in not writing a single false or unearned
sentence (Step 2). The drafting is the easy part.

## The workspace

This skill reads and writes a persistent workspace directory. Ask the owner for
its path on first run and reuse it after. Expected layout:

```
<workspace>/
  RUNBOOK.md     ordered procedure + current connect balance
  PROFILE.md     the facts bank: verified claims + how to re-verify each
  PORTFOLIO.md   exact copy of the live portfolio entries, reused verbatim
  ANSWERS.md     the recurring screening questions, marked portable vs job-specific
  TEMPLATE.md    letter shape + voice rules
  LOG.md         one row per proposal: date, job, client read, rate, connects, outcome
  assets/        screenshots and logos cleared for public use
  applications/
    YYYY-MM-DD-<slug>/
      JOB.md            the posting captured verbatim + client read + decisions
      COVER-LETTER.md   the submission
      QUESTIONS.md      screening answers (only if the posting asks any)
      work-sample.*     the attachment, html source plus rendered pdf
```

If the workspace does not exist yet, create it and populate `PROFILE.md` as you
verify claims. **`PROFILE.md` is the only source for reusable claims.** Nothing
enters a letter that is not in it or freshly verified in a repository.

## Step 0 — Triage gate

**Do this before writing a single word.** The most expensive available mistake is
a great proposal for a client who was never going to pay. Kill on any red.

| Check | Where | Kill criterion |
|---|---|---|
| Avg hourly paid vs posted band | client panel | Gap wider than ~3x. A client posting $100–500 who has paid $15.79 is not a $100–500 client |
| **Spend per hire** = total spent ÷ hires | client panel | Under ~$1,000 when the job claims months at 30+ hrs/week |
| Already interviewing | activity panel | 15+ means the shortlist probably exists |
| Recent job domains | client history | Nothing adjacent to the posting = brokering, not building |
| Connects vs balance | proposal page | Never spend more than ~1/3 of the balance on one uncertain job |
| Boost feasibility | proposal page | If 1st place needs several times your balance, boosting is off. Do not let it change the bid |
| Hard filters | posting | Location, timezone, mandatory certs. Never spend connects on a filter you fail |

**Amber, not red:** a genuinely new client with *no* postings and *no* hires.
That is unknown risk, which beats known-bad risk. Cheap bids there are fine.

**Not amber:** an account with a real history that happens to be bad. Thirty-nine
postings, twelve hires and $50 disbursed is not "no data," it is data. Distinguish
these two carefully; they look similar at a glance and mean opposite things.

Write the triage result into `JOB.md` before drafting. **If the recommendation is
skip and the owner applies anyway, log that too** — overrides are how the filter
gets tested. Say the recommendation once, plainly, then do the work asked for.

## Step 1 — Capture the job

Create `applications/YYYY-MM-DD-<slug>/JOB.md`. Paste the posting **and the client
history block**; Upwork discards it when the job closes and it is the highest
signal on the page. Add the triage table and a requirements-vs-our-position table
with an honest verdict per line.

## Step 2 — Verify against repositories, not memory

**The rule that has mattered most, and it runs in both directions.**

Count by **email**, never display name. `git shortlog` split one person across
three names and undercounted by 41 commits.

```bash
git -C <repo> log --all --author=<email> --format='%H' -- <path> | sort -u | wc -l
git -C <repo> log --all --format='%ae' -- <path> | sort | uniq -c | sort -rn | head
```

The second command ranks the owner against everyone else on that surface, which
is what turns "has some commits" into "the largest share of any author."

**Direction one, do not overclaim.** A framework never shipped does not go in the
letter. Clients who have made ten hires catch it and discount everything else.

**Direction two, do not underclaim, and never volunteer an unverified gap.**
A claim absent from `PROFILE.md` means *go look*, never *concede*. Two real cases:

- Owner recalled his Rails work as "very minimal." The repo held Rails 6.1.4, 284
  commits, ~1,600 lines of Ruby, 60% of it RSpec, plus Devise and Sidekiq. The
  draft was apologizing for a gap that barely existed.
- A draft opened "I do not have a design credential" because the facts bank
  listed none. The repos showed the owner was top committer on the public
  marketing site and held 985 commits on the product's component library.

A volunteered weakness is a claim like any other and needs the same evidence. It
costs more than an overclaim, because it spends the highest-leverage sentence in
the letter talking your own candidate down.

Add everything newly verified back to `PROFILE.md`, with the command that proves
it. Beware `--all`: it counts every branch and inflates repo-wide totals. Prefer a
path-scoped count or a main-branch count, and say which one you are quoting.

## Step 3 — Draft the cover letter

**Read the last two submitted letters in `applications/` end to end first.** Not
their checklists, the letters. Skipping this produced two discarded drafts in one
session. The house voice lives in those files.

The shape:

1. **State plainly that you want the work.** One sentence.
2. **Credibility that answers their stated requirement**, in numbers they can
   check. Their exact version number, their hardest project, the thing you have
   already shipped that matches.
3. **A concrete next step that starts the project.** A named first deliverable,
   what they get to inspect at the end of it, and the order the rest would follow.
4. **Coverage sweep** of their remaining requirements, in their words.
5. **Rate, hours, timezone.** Plain.
6. **Sign off:** name and GitHub. No LinkedIn, it is off-platform.

300 to 400 words. Under 250 reads thin for senior work; over 500 does not get read.

**You are applying, not reviewing.** Never grade, rank or diagnose the client's
posting or their project list. A draft that opened by sorting the client's three
projects into "wrapper" and "not a wrapper" read as a critique of the buyer, and
the reader could not tell whether the writer was applying or auditing them.
Reference their requirements only as the thing your experience answers.

Full voice rules, the gap-handling pattern, and the anti-patterns produced by
Upwork's own AI draft generator are in `references/cover-letter.md`.

## Step 4 — Screening questions

Many postings reuse the same three: recent experience, frameworks, testing and QA.
`ANSWERS.md` holds the current best versions with job-specific paragraphs marked.
Re-scope those, keep the rest. They are often read *before* the letter, so each
must stand alone; repeat a key concession even if the letter carries it.

Check whether the posting actually asks any. Several do not.

## Step 5 — Rate

**Set the rate after the evidence is in, not while drafting.** One bid moved
$60 → $70 once a repo proved the experience was stronger than remembered.

- **Check the pre-filled rate every time.** Upwork prefills something that is not
  always the profile rate. It has arrived $40 over a client's ceiling.
- Anchor on the client's own average paid, not the posted band.
- With no payment history to anchor on, bid where the work is worth taking. No
  rate wins a client who cannot pay, so discounting toward one who might not is
  a loss either way.
- Bidding under the band only makes sense paired with an explicit trial offer.

## Step 6 — Attachments and highlights

**Pick the sample pack that matches the shape of the job.** A tailored letter
arriving with an off-target attachment reads as a mail merge. Maintain two:

- **A bug-fix pack** for maintenance, stabilization and bug-fix jobs. Merged PRs
  written as symptom → root cause → fix → test evidence → what was verified.
  Proves rigor on someone else's code.
- **A product case-study pack** for build, product, AI-agent and 0-to-1 jobs.
  The product with public screenshots and interface numbers, then one subsystem
  written as "we added X because users hit Y." Proves you ship products.

Before attaching, map the pack against the client's stated evaluation criteria
and count the hits. A bug-fix pack was once queued for a greenfield build job
where it hit 1.5 of 8 criteria; the purpose-built pack hit 7.

Rules for any pack: cite PRs as `repo #number` rather than links, since Upwork
warns on contact details and external links can be flagged. Never include
customer data or identifiable third parties who did not consent to appear in a
job application. Screen for what a fix reveals about your own product: a PR
proving you repaired something can simultaneously advertise that it was broken.

Portfolio highlights are picked **per job**, maximum four, from `PORTFOLIO.md`.

Regenerate a pack by editing its `.html` and rendering headless:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --no-pdf-header-footer --print-to-pdf=work-sample.pdf work-sample.html
```

Inline images as base64 data URIs so the PDF is self-contained. Verify the page
count and eyeball page one before sending; full-width 1440x900 screenshots
overflow a letter page, so place two side by side at 50% rather than stacking.

## Step 7 — Pre-submit verification

**Copy every field from the file, not from chat.** In one session five of eight
pastes silently dropped characters mid-word. Several breaks still parsed as
English, so a skim missed them, and one deleted the two most valuable verified
claims in an answer. Keep paragraphs unwrapped to single lines in the file so the
web textarea does not inherit hard line breaks.

- [ ] No em dashes anywhere customer-facing. They are the loudest AI tell
- [ ] American spellings if the client is US
- [ ] Rate in the letter matches the rate in the bid field
- [ ] Every claim traceable to `PROFILE.md` or a repository
- [ ] Commit counts scoped correctly, and the scope stated
- [ ] No location or availability claim that contradicts a linked public profile
- [ ] Read every field end to end in the rendered form, aloud if possible

## Step 8 — Log it

Update `LOG.md`: status to Submitted, plus a running note on what was decided and
why. Update the outcome when it lands.

`Draft` → `Submitted` → `Viewed` / `Interviewing` / `Hired` / `Declined` / `Job closed`

The open question the log exists to answer: **does client payment history predict
outcome better than skill fit does?** Record both for every proposal so the answer
arrives on its own. Until roughly ten rows exist it is noise; after that the
pattern is readable and the triage thresholds above should be retuned against it.

**Follow-up cadence:** one week. Then a short message referencing something
specific about their product. Do not follow up sooner on a job with 50+
proposals; they have not started reading.

## Finding jobs worth applying to

Scrape wide, then score locally on **what the client actually pays**. The full
recipe, including the scoring script and the input schema, is in
`references/job-search.md`.

**The one rule that governs this whole step: filter on behavior, not on the
posting.** A job board's rate filter matches the *posted band*, which the client
writes and nothing enforces. In a real scan of seven AI-agent postings, every one
advertised a respectable band and the clients paid between $5.70 and $47.49 an
hour. The rate filter excluded zero bad payers, because bad payers post good
bands. Pull the band filter out of the query and apply it to the client's own
average paid after the results land.

Rank by, in order:

1. **Average hourly actually paid**, at or above the target rate. This is the
   whole ballgame and every other signal is secondary to it.
2. **Ratio of posted-band ceiling to average paid.** Wider than ~3x is a kill.
3. **Proposal count** under ~50. Over 100 is a lottery ticket bought with
   connects you do not have.
4. **Skill fit** against `PROFILE.md`, favoring postings whose hardest
   requirement is something already shipped and public.
5. **Total client spend, only in combination with a healthy average paid.**

**Total spend on its own is a trap.** The two largest spenders in that same scan,
at $2.8M and $98K, paid $10.40 and $19.04 an hour. Any ranking that leads with
total spend surfaces precisely the clients to avoid.

Prefer few, well-matched, fully verified proposals over volume. Four proposals at
16 to 27 connects each will exhaust a standard balance in one session. Write each
scan to `scans/YYYY-MM-DD-<slug>.md` next to its raw JSON, including the scans
that surface nothing: a category that reliably returns saturated, low-paying
postings is worth knowing about before you query it again.
