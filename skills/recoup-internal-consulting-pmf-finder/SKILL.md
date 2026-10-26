---
name: recoup-internal-consulting-pmf-finder
description: "Find and test product-market fit through buyer pull, paid demand, retention, and repeatable outcomes. Use for recoup-internal requests to run pmf-finder, test a pull hypothesis, diagnose weak demand, or choose the next PMF experiment."
---

# PMF Finder

Turn an idea or customer evidence into the next demand test using Rob Snyder's PULL framework: discover whom to serve and what unblocks them.

## Contract

- Produce an evidence-backed pull hypothesis, the weakest assumption, and one next experiment with a decision rule.
- Distinguish buyer pull, completed sales, delivered value, retention, and repeatability. None substitutes for the others.
- Preserve unknowns and disconfirming evidence; never certify PMF from a score, a small call batch, or enthusiasm alone.

Use the selected authorized business workspace and its instructions. Read relevant calls, opportunity, purchase, delivery, and retention records there. Keep evidence and memos there, not in this public skill. Without a selected workspace, use supplied inputs and return the memo in chat. Bundled paths are relative to this skill's directory.

This is a PMF loop, not generic call summarization, proposal writing, or marketing case studies. Start at the user's actual evidence stage. The source is primarily B2B; for consumer products, specify the payer/user and appropriate transaction and retention behavior.

## Phases

### 1. Establish the current bet

Identify the product/service, buyer/person, outcome, stage, and decision needed. Separate buyer, user, champion, and approver when they differ. Read evidence before asking for context that changes the decision. With sparse inputs, make a provisional hypothesis and name the field evidence needed; never invent interviews.

**Complete when:** one buyer/project is scoped; inputs distinguish records, user reports, and assumptions. Label unknown observation dates rather than inventing them.

### 2. Fill PULL before describing the solution

For that person, fill these four fields:

| Field | Question | Evidence to seek |
|---|---|---|
| **P — Project** | What outcome are they already trying to accomplish? | Their current work or intended outcome, not a software category or a feature request. |
| **U — Unavoidable** | Why must they act now rather than defer? | A real deadline, consequence, recurring obligation, or current attempt to change. |
| **L — List of options** | What could they use instead? | Actual considered/used tools, staff, agencies, manual work, internal builds, or doing nothing. |
| **L — Limitations** | Why are those options insufficient for this project? | Specific buyer-confirmed blockers, not our competitive claims. |

Mark fields **observed**, **inferred**, **unknown**, or **contradicted**, with evidence locators and counterevidence. Qualify observed claims as user-reported or directly verified. All four concern the same person/project, not a composite of interviews. Recurring work can be a project without a written to-do; tie time savings to that work.

Write: “We believe [person in situation] must [project] now because [trigger/consequence], but [options] fail because [limitations].” Keep proposed help separate. If an existing option works well enough, report the missing pull instead of adding persuasive messaging.

**Complete when:** each PULL field has a status and the hypothesis could be disproved. Read `references/field-guide.md` for discovery and signal distinctions when needed.

### 3. Design the smallest buying-behavior test

Choose the nearest untested assumption. If the blocker is unknown or contradicted, observe/discover it first; leave the offer pending. With a plausible buyer/project, prepare two text slides: (1) reflect PULL for correction; (2) propose narrow help, commercial basis, and next step. State what exists, is manual, or remains unbuilt. Do not build a platform to avoid customer contact.

Prepare discovery: why they accepted, agreed agenda, permission for questions, missing PULL fields, then the narrow offer. Ask for a purchase step, not whether they like the idea. Without pull, use the Hail Mary in `references/field-guide.md` to discover work they would pay to complete now.

For a new hypothesis, propose a small batch of comparable buyers; roughly five conversations is a useful review checkpoint, not a statistical threshold. Record buyer-selection criteria, the test, expected observable behavior, falsifying evidence, review date, owner, and what decision each outcome would change. When access is the bottleneck, propose direct observation or a short truthful outreach draft instead of more desk research.

**Complete when:** the user has a runnable test and pass/revise/stop criteria. Drafts do not authorize sending outreach, scheduling calls, offering binding terms, spending money, or publishing customer evidence; execute those only within the user's existing authorization.

### 4. Review actual behavior and revise the bet

Log each interaction separately: PULL evidence, exact buying action or absence, objections, next step/owner/date, purchase state, and new learning. Use `templates/pmf-loop.md` to maintain the hypothesis and evidence ledger; omit later-stage sections that have no evidence yet.

Distinguish compliments and hypothetical future use from buyer-driven attempts to start. A requested contract, payment, or an owned procurement step is more informative than excitement; still label which happened, not all as closed revenue. Enterprise procurement can delay a sale despite real pull: identify the buyer's required outcome date and work backward through approvals. Do not confuse an active buying process with an unowned “maybe next quarter.”

At the checkpoint, compare like-for-like buyers. If a minority pulls, retest that subgroup. If none pulls, revise the person, urgency, or limitation from the evidence. Without learning, return to firsthand observation. Record the old hypothesis, evidence, change, and next test. Extend a batch only when further evidence could change the decision.

**Complete when:** continue, narrow, revise, or pause follows from observed behavior, with one next action. Evidence missing is “not yet tested,” not “no demand.”

### 5. Test delivery and retention after a sale

When buyers commit, define the promised outcome and a candidate **X**: the concrete value event after which continued use or renewal should make sense. Deliver firsthand to learn X; distinguish this hypothesis from a demonstrated retention predictor. Design onboarding backward from X, with a measurable event, target time, owner, and customer confirmation. Logins, NPS, and generic activity alone do not establish delivered value.

Track who reached X, time to value, subsequent use/renewal/churn, and reasons over a stated observation window. Compare retained and churned cohorts before broadening the offer. One retained segment in a churning horizontal product is a new hypothesis to test, not automatic permission to declare victory or pivot the whole business. Service-shaped delivery is legitimate if sold honestly; track custom labor and what must become repeatable rather than calling bespoke consulting software PMF.

**Complete when:** delivery and retention have separate evidence or are explicitly pending, and the next test addresses the actual gap.

### 6. Repeat one successful customer pattern

Define an internal case-study pattern: same buyer situation → unavoidable project → failed alternatives → offer → achieved outcome → continued value. Seek matching customers, not unrelated wins. A sale alone is not a repeatable case study; learning records need not become public testimonials.

Inspect counts, time windows, and drop-offs across **pipeline** (right-buyer conversations), **sales** (purchase progress), and **delivery** (value and retention). Choose the evidenced bottleneck or, with sparse data, what to measure next. Test that constraint before adding features, segments, or volume.

**Complete when:** the repeatable unit, current constraint, and next learning checkpoint are explicit. A promising pattern is stronger evidence, not a guarantee of market size or enduring PMF.

## Output Format

Return a concise decision memo using the relevant sections of `templates/pmf-loop.md`:

1. Current bet and evidence stage.
2. PULL hypothesis with evidence, unknowns, and contradictions.
3. Buying behavior observed, separately from sales, delivery, and retention.
4. Biggest uncertainty or evidenced bottleneck.
5. One next experiment: buyer, action, expected behavior, disconfirmation, owner, review point.
6. Continue/narrow/revise/pause recommendation and what would change it.

Save to the selected workspace's existing opportunity/learning record when authorized, and report its path. Never manufacture a PMF percentage or guarantee from these inputs.

## Anti-Patterns

- Substituting TAM, personas, competitor lists, or feature roadmaps for buyer evidence.
- Treating stated pain, free design-partner feedback, usage, or one sale as PMF.
- Offering free pilots to evade a buying decision. A buyer-required pilot can be valid; define commercial terms, success criteria, decision owner, and conversion step.
- Inventing customers, prices, ROI, urgency, or competitive limitations to fill the framework.
- Scaling acquisition before learning why customers fail to buy, get value, or stay.

## Source

Adapted from Rob Snyder on Lenny's Podcast, *An 86-minute guide to finding PMF*: https://www.youtube.com/watch?v=19qrLchbQEc. See `references/field-guide.md` for timestamps, tactics, and source/adaptation distinctions. No transcript fetch or API credential required.
