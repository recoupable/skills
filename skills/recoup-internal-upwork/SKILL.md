---
name: recoup-internal-upwork
description: >-
  INTERNAL — Recoup staff tooling, gated by the recoup-internal keyword. Invoke
  ONLY when the request explicitly includes "recoup-internal" (e.g.
  "recoup-internal apply to this Upwork job"). Never use for customer-facing or
  artist requests.
  Find, win and close Upwork contract work end to end: run the daily pipeline,
  triage a client before writing anything, verify every claim against the actual
  repositories, draft the cover letter and screening answers, pick the right
  work-sample pack, set the rate, then follow up, handle the reply, run the call
  and convert a trial into ongoing work. Use when asked to "apply to this Upwork
  job", "write an Upwork proposal", "should I bid on this", "triage this client",
  "is this job worth connects", "find Upwork jobs worth applying to", "run the
  Upwork pipeline", "a client replied", "prep for the client call", "follow up on
  my proposals", "why is nothing converting", or when an Upwork job posting is
  pasted in. Requires a local workspace directory and read access to the
  repositories behind any claim being made.
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

## The daily run

**Order matters, and it is not the order of the steps below.** The steps are the
procedure for one proposal. A day optimized for *closing* starts with the pipeline
that already exists, because a live thread converts far better than a new bid and
costs no connects.

1. **Read `LOG.md` and the connect balance.** Everything else is scoped by these.
2. **Answer any client reply first, before anything else.** Reply speed is one of
   the strongest conversion variables on the platform. An hour matters; a day
   costs you the job. See `references/closing.md`.
3. **Update the status of every open row.** Viewed, Declined, Job closed. This is
   the funnel data and it is worthless if backfilled later from memory.
4. **Follow up anything viewed but quiet past a week**, per the rules in
   `references/closing.md`.
5. **Only now** scan, triage and apply, and only if the connect floor allows.
6. **Log it.**

If the reply rate is zero after five or more proposals, insert a profile audit
before step 5 and stop applying until it is done. See "Diagnosing a funnel that is
not converting."

### Connect budget

A proposal costs 15 to 27 connects. **Never let the balance fall below ~27**, one
job's worth, or a reply-worthy find arrives and you cannot act on it. On
2026-08-12 the balance hit 1 with five proposals live.

Spending the last of a balance is defensible only when the day's scanning and
triage produced exactly one job worth bidding on and holding out is a bet on a
better one appearing. Say that reasoning out loud in `JOB.md` when you do it.

## Step 0 — Triage gate

**Do this before writing a single word.** The most expensive available mistake is
a great proposal for a client who was never going to pay. Kill on any red.

**These thresholds are provisional.** They were set from a handful of postings and
have produced zero outcomes so far. Treat them as strong priors rather than laws,
log every override, and retune them once `LOG.md` holds ten rows with outcomes.

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

The shape. **The open and the close are fixed sentences (owner ruling 2026-08-18,
set immediately after submitting proposal 16); the middle is built per job:**

1. **Greeting:** "Good morning," or "Good afternoon," plus the client's name when
   the posting or client panel supplies one. Pick morning vs afternoon by the
   **client's** local clock, which the client panel displays, not by yours.
2. **The fixed identity sentence, verbatim:** "I am Patrick Sweetman. A Sr
   Software Engineer from the USA with 12+ years of experience." One permitted
   slot: the role word may match the posting's own title (Fullstack, Frontend,
   Backend). Nothing else in the sentence changes.
3. **Credibility that answers their stated requirement**, in numbers they can
   check. Their exact version number, their hardest project, the thing you have
   already shipped that matches.
4. **A concrete next step that starts the project.** A named first deliverable,
   what they get to inspect at the end of it, and the order the rest would follow.
5. **Coverage sweep** of their remaining requirements, in their words.
6. **Rate, hours, timezone.** Plain.
7. **The fixed availability close, verbatim:** "I am available any time for an
   interview call to discuss the next steps."
8. **Sign off:** name and GitHub. No LinkedIn, it is off-platform.

Concise over complete: every sentence is either a checkable claim or a next step,
or it goes. **The letter carries no shortcomings.** Strengths only. A verified gap
is addressed only where the posting explicitly asks about it, and it is addressed
in that screening answer in one clause with a number, never in the letter. See
`references/cover-letter.md`. 250 to 400 words; over 500 does not get read.

**You are applying, not reviewing.** Never grade, rank or diagnose the client's
posting or their project list. A draft that opened by sorting the client's three
projects into "wrapper" and "not a wrapper" read as a critique of the buyer, and
the reader could not tell whether the writer was applying or auditing them.
Reference their requirements only as the thing your experience answers.

**Do not warn them about their own project, and do not explain the craft to them.**
No lists of pitfalls, traps, risks or "things people usually get wrong here." No
tutorial on how the thing they already built works. A client who has shipped a
product has already met the complexities, and a proposal that recites them reads
as either a pitch for a rescue they did not ask for or a lecture from someone who
assumes they are naive. One buyer put it directly in their posting:

> "Please don't approach your proposal by telling us about all of the pitfalls and
> traps waiting for us. We've had great developers and product managers working
> extremely hard to build a great product, and we haven't overlooked the
> complexities and nuances. We need someone to take a really well-built product and
> build on top of it, not tell us how they're going to save it from assured
> collapse... Better to focus on why your experience is a good fit, rather than
> explaining coding to us."

**Treat that as the house rule on every proposal, whether or not the posting says
it.** Most buyers who feel this way never write it down; this one did, which is the
only reason we know how it lands. The permitted version is a single clause showing
you have met the same difficulty in your own work — *"ICS feeds disagree about
timezones, which I have dealt with"* — never a paragraph about what might go wrong
in theirs. Difficulty is evidence when it is in your history and an insult when it
is in their future.

This has one deliberate exception: **a stated gap of your own is not a warning about
their project.** "I have not used Firebase in production" is a fact about you, and it
belongs in the screening answer that asked about Firebase (never the letter, per Step
3). Rewriting it as "Firestore's data modeling traps are where projects like yours
fail" is the banned move wearing a disguise.

### You are writing to win the contract, not to document your limits

**A verified gap gets one clause. Never a paragraph, never a second mention.** The
rule against overclaiming is about truth and it does not move. This rule is about
*proportion*, and it has been violated far more often than the truth rule ever was.

Measure it before submitting. On a five-question proposal in 2026, **three answers
opened with the word "No"** and a fourth spent its closing paragraph explaining
what a better-suited candidate would find easier. Every individual sentence was
true. The proposal still read like a list of reasons to hire someone else.

**Banned, because each one doubles the space the negative occupies:**

- **Meta-commentary about your own honesty.** "I want to be straight about that."
  "I will not stretch to claim one." "Rather than have you find it in week two."
  You are not paid for announcing that you are honest. You are paid for the fact,
  which is shorter.
- **Arguing the other candidate's case.** "Where a fan would be faster than me is
  knowing without looking which venue a team plays at." That is writing a
  competitor's proposal inside your own.
- **Explaining why the gap matters to them.** They wrote the requirement. They know.
  Restating it adds weight to the one thing you want to weigh least.
- **Repeating a gap already conceded elsewhere** in the letter or another answer.
  Once. That is the whole budget.

**Where the negative sits depends on the question:**

| Question type | Handling |
|---|---|
| **Binary and personal** ("are you a sports fan", "are you US-based") | Answer with the bare word and stop. Burying it reads evasive. Then pivot immediately to what they said actually matters |
| **Capability** ("do you have experience with X") | **Lead with the adjacent thing you have shipped**, and locate the boundary in a clause near the end. "I run my development through Claude as a production platform, [evidence]. Lovable itself I have not used" beats "No, I have not used Lovable." Identical honesty, inverted emphasis |

**When a gap must be named, the frame is the ramp, and the ramp needs evidence.**
"I learn quickly" is an adjective and the voice rules already ban those. The
evidenced forms:

- **A named zero-to-shipped instance.** Solidity from nothing to 19 public repos.
- **A costed estimate you would be held to.** "Helix is documented REST with
  app-token auth, so a day of ramp rather than a week." A number a client can hold
  you to beats any adjective, and it converts the gap into a commitment.

**The pre-submit check, worth thirty seconds:** read only the *first sentence* of
every answer, in order, and nothing else. If that sequence would not make someone
want to hire you, restructure before you send. Then count how many answers open on
a negative word. More than one in four means the proposal is documenting instead of
selling.

**This rule never licenses a false claim.** A gap asked about directly is still
answered truthfully in the same breath. What changes is the word count and the
running order, not the facts.

Full voice rules, the gap-handling pattern, and the anti-patterns produced by
Upwork's own AI draft generator are in `references/cover-letter.md`.

### The unslop pass

If the `unslop` skill is installed (https://www.skills.sh/cursor/plugins/unslop,
via `npx skills add`; it removes AI tells from prose), run it over the finished
letter and every screening answer as the last drafting step, before Step 7. It generalizes the em-dash rule to the whole
catalog of tells: AI vocabulary, "not just X, but Y", rule-of-three padding,
filler phrases, hedging.

Two of its instructions are subordinate to this skill and do not apply:

- **The fixed frame outranks it.** The greeting, the identity sentence, and the
  availability close are verbatim by owner ruling. Unslop edits the middle only.
- **"Add soul" never adds claims.** Unslop asks for opinions and mess; a cover
  letter's voice comes from specific verified numbers, not from invented
  personality. If an unslop rewrite introduces a sentence that is not a checkable
  claim or a next step, revert it. Cutting tells: yes. Adding color: no.

## Step 4 — Screening questions

Many postings reuse the same three: recent experience, frameworks, testing and QA.
`ANSWERS.md` holds the current best versions with job-specific paragraphs marked.
Re-scope those, keep the rest. They are often read *before* the letter, so each
must stand alone. Since the letter carries no gaps (Step 3), the screening answer
that asks about a gap is that gap's only home; make it complete there.

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
- [ ] The unslop pass ran over every customer-facing field (Step 3, "The unslop
      pass") and the fixed-frame sentences survived it verbatim
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

**Record `Viewed` as its own status, every day.** Without it there is no funnel and
no way to tell whether a losing streak is caused by targeting, by the profile, or
by the letters. It is the cheapest diagnostic available and it is the one most
easily skipped.

The open question the log exists to answer: **does client payment history predict
outcome better than skill fit does?** Record both for every proposal so the answer
arrives on its own. Until roughly ten rows exist it is noise; after that the
pattern is readable and the triage thresholds above should be retuned against it.

## Step 9 — Follow up, reply, and close

The work is not over at Submitted, and this is where a proposal becomes a
contract. The full playbook is in `references/closing.md`: reply speed, what the
first response has to do, running the call as discovery rather than demo, holding
the rate by moving the scope, the paid trial, converting a trial into ongoing
work, follow-up craft, and the platform rules that void payment protection.

The three that matter most:

- **Answer within the hour.** Everything else in the playbook is worth less than
  this one habit.
- **Hold the rate, move the scope.** When a client pushes on price, reduce what
  they get, never what an hour costs. A discount is permanent and invisible; a
  smaller first slice is neither.
- **Never move off-platform before a contract exists.** It violates the terms and
  it voids payment protection, which is the only thing standing between you and
  an unpaid invoice with a stranger.

## Diagnosing a funnel that is not converting

Read the failure at the point it breaks, and fix only that.

| Symptom | Most likely cause | What to do |
|---|---|---|
| Not even viewed | Timing, crowding, or a profile filtered out before it is read | Apply to fresher postings with fewer proposals; audit the profile |
| Viewed, no reply | The letter, the rate, or the profile behind the link | Re-read the last two letters against `TEMPLATE.md`; audit the profile |
| Replies, no contract | The call, the scope, or the rate | `references/closing.md` |
| Contracts, no repeat work | Delivery, not sales | Out of scope for this skill |

**The profile audit, when replies are zero after five or more proposals.** Stop
applying and look at the thing every client looks at and this skill never checks:
Job Success Score, review count, completed contracts, the headline, the first two
lines of the overview, the rate against the category, and whether the portfolio
entries match the work being bid on.

**The cold-start problem, and why it is the owner's call.** A profile with no
completed contracts and no reviews competes badly against bidders carrying a 100%
JSS and fifty reviews, regardless of how good the proposal is. The standard remedy
is to deliberately win one small, cheap, fast job to earn a first five-star
review, then price back up. **That directly contradicts the rate discipline in
Step 5**, so the skill does not get to choose. Put the trade to the owner
explicitly, with the current JSS and review count in hand, and let them decide.
Do not quietly start bidding low and call it strategy.

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
