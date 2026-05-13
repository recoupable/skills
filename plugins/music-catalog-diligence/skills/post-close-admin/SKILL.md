---
name: post-close-admin
description: Use after a music catalog acquisition closes, when transferring royalty administration, updating registrations, tracking ownership changes, monitoring first statements, or preventing post-close income leakage. Triggers include "post-close", "transfer administration", "registration updates", "catalog migration", "first post-close statements", "income leakage", or "ownership transfer plan".
---

# Post-Close Admin

Turn diligence data into an administration transition plan after close. The goal
is to prevent income leakage while ownership records, registrations, and
royalty systems move to the buyer.

## Workflow

1. Start from the final canonical catalog, rights map, and closing schedules.
2. Confirm acquired assets, excluded assets, territories, and effective date.
3. Generate transfer worklists for PROs, MLC, SoundExchange, distributors,
   publisher admins, neighboring rights societies, and internal royalty systems.
4. Track registration updates and payment direction changes.
5. Monitor first post-close statements against expected income.
6. Flag missing income, old payees, unmatched works, or statement gaps.
7. Write a post-close admin plan under `memos/`.

## Output

Return:

- Transfer checklist.
- Registration update list.
- Provider/account owner list.
- First-statement monitoring plan.
- Income leakage watchlist.
- Open issues and owners.

## Guardrails

- Do not assume closing schedules match diligence tables; compare them.
- Do not overwrite historical evidence.
- Do not mark transition complete until first statement checks are done or
  explicitly deferred.
