---
name: recoup-internal-consulting-ai-roi-framework
description: Plan, track, and measure a client's AI initiative portfolio using the 1-3-1 funding and realized-value framework. Use for explicit recoup-internal requests to create or refresh an AI roadmap, prioritize AI investments, set pilot gates, reconcile AI ROI, or run quarterly AI portfolio reviews across clients. Produces a funded roadmap, initiative register, benefit ledger, and scale/revise/stop decisions in the selected private workspace.
---

# AI ROI framework

Turn client AI ambitions into an evidence-backed investment portfolio, then maintain it through decisions and captured outcomes. Adapted from Alex Lieberman / Tenex's 1-3-1 framework; read `references/framework.md` before planning or reviewing. Read `references/measurement.md` when defining KPIs or reconciling returns. Use `templates/portfolio.md`, `templates/initiative.md`, and `templates/review.md` for outputs. These resources ship inside this skill; resolve them relative to its directory.

## Establish scope and evidence

1. Identify the selected client, authorized private workspace, sponsor, decision maker, currency, fiscal period, and planning horizon. Read its governing instructions and existing canonical roadmap, agreements, financial records and delivery evidence before changing anything. Reuse established project names and records.
2. Determine mode: create a portfolio, update existing initiatives, evaluate funding, or review outcomes. For a multi-client request, work in each client's authorized records separately and create only a permitted summary linking them. Do not copy confidential evidence between clients or into this public skill.
3. Inventory current initiatives, pilots, tools, contracts and shared infrastructure, including ongoing commitments. Distinguish proposals, authorized funding, actual spend, source merge, deployment, user adoption and measured business outcomes. A shipped tool alone proves no return.
4. Use accessible authorized sources first. Record source/date/owner for every consequential claim. Label missing inputs `[MISSING]`, unverified claims `[UNVERIFIED]`, and assumptions explicitly. Ask only for inputs needed for a decision; continue preparing independent work. Unknown revenue permits an absolute budget scenario, not invented revenue or approval.

## Plan the investment portfolio

1. Record the client's business goals and existing departmental KPIs before choosing AI projects. Map each opportunity to a specific workflow, affected population, baseline pain and measurable outcome. Assess potential value and execution feasibility with explicit reasons; this lightweight opportunity screen is our implementation extension, not a reproduction of Tenex's separate AI Triage Matrix.
2. Give each funding tranche exactly one primary category: foundation, experimentation, efficiency or innovation. Link secondary benefits without creating duplicate return claims. Preserve a pilot's history when it graduates to an efficiency or innovation tranche; never relabel sunk pilot spending away.
3. Propose a company-wide spending ceiling and protected commitments. Show the revenue/absolute amount, denominator, category amounts, already committed spend, remaining headroom and proposed next release. Apply the source's ranges only as adjustable starting scenarios. Funding is a decision, not an automatic percentage entitlement.
4. Build foundation alongside the first two or three useful use cases. Prioritize shared data definitions, access, security, integrations, governance, documented processes and role-based training that unblock those cases. Name the use cases served; avoid a foundation-only roadmap without shipping or reuse evidence.
5. For each pilot, write a hypothesis, representative sample and relevant subgroups, quality and service guardrails, total time including review/rework, maximum spend, end date, and precommitted scale/revise/stop thresholds. A revision must name a specific change, a fresh cap and another decision date. Separate passing segments from failing ones.
6. For a major efficiency rollout, name how recovered capacity becomes economic value and who captures it. For innovation, define attribution and margin economics. Scale the proof required to the size, reversibility, risk and cost of waiting. A strong pilot may earn bounded expansion before financial benefits materialize; do not describe that as realized ROI.
7. Among initiatives meeting their own function's evidence bar, prioritize potential value, confidence in evidence, dependencies, delivery capacity and timing. Explain tradeoffs in plain language. Keep residual funding uncommitted when no candidate qualifies; avoid a universal score that lets high potential cancel a failed quality gate.
8. Produce a sequenced roadmap: now / next / later with dates or explicit conditions, owners, dependencies, tranche amounts, acceptance evidence, next decision and review date. Later items remain conditional. Operationalize the next bounded action with owner and due date.

## Track without losing the baseline

Maintain stable client-scoped initiative, tranche, cost and benefit IDs. Use `templates/portfolio.md` and one `templates/initiative.md` per material initiative, or map the same fields into the client's existing tracker. Link implementation issues rather than making a second backlog.

Keep lifecycle stage (discovery, pilot, rollout, operating, paused, stopped) separate from benefit status (projected, provisional, realized, withdrawn). Keep original targets and approved budgets versioned; record dated revisions beside them rather than rewriting history. Track evidence freshness, blockers, spend to date, remaining commitments, full ongoing costs, adoption, quality and the next funding decision.

Maintain a benefit ledger with a unique economic event/population/time window for each claim. Mark overlapping claims and resolve them before totals. Capacity consumed by avoided hires cannot also be valued as redeployed hours. Shared foundation may enable a return but cannot claim the same downstream dollars again. Shared costs appear once at program level; reconcile any project allocations to the same cost IDs.

## Measure and decide

1. Separate projected potential, observed operational improvement, verified period benefit and annualized run rate. Record the measurement interval and population for all four. Do not turn reported time savings into realized dollars by multiplying wages.
2. Verify capture through avoided approved hires, displaced paid work, measurable redeployment or reduced expense. Preserve quality/service levels and a credible counterfactual. For innovation use a matched holdout or staggered rollout where feasible; otherwise disclose attribution weakness and keep unproven financial benefit provisional.
3. Reconcile gross benefit, full period costs, net benefit and ROI ratio separately. Include software/API, implementation/integration, training/change management, operations, human review, error correction and attributable delivery labor. Distinguish project rollout economics from program economics including experiments and foundation. Never sum revenue and the profit derived from that revenue.
4. Review efficiency's provisional gains after one to two quarters; withdraw unsupported claims. Innovation may need two to four quarters for outcomes, but review leading indicators within a quarter. These are adjustable source defaults, not excuses to skip explicit checkpoints.
5. Every quarter compare each initiative with targets recorded at funding. Assess captured value, experiments ending in decisions, and comparable foundation-enabled deployments becoming faster, cheaper, safer and more reliable. Examine actual adoption/reuse; normalize comparisons for scope differences.
6. End with concrete decisions: release a bounded tranche/scale, revise and retest a named hypothesis, hold pending named evidence, or stop. Record decision maker, rationale, amount, conditions, owner and next review. Recommend rather than execute spending, staffing, permissions or external communications unless separately authorized.

## Completion contract

Deliver an updated canonical portfolio and roadmap, initiative cards, budget reconciliation, benefit ledger, and a dated decision/review log using the templates or existing equivalents. State evidence as-of date, missing inputs, assumptions, approvals pending and next owner/action. For a small update, edit the affected fields and log the decision instead of regenerating every artifact. Multi-client summaries must preserve currencies, measurement windows and confidentiality; do not pool incomparable results into one ROI figure.

Before handoff, check budget arithmetic and denominator choices, no duplicate benefits/costs, net versus gross, actuals versus annualized forecasts, original-target preservation, subgroup guardrails, and an owner/date for every open decision. Use `evals/evals.json` as synthetic practice cases; it contains no client facts.
