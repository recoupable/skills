---
name: recoup-internal-consulting-client-reconstruct
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Rebuild a client/deal folder from scratch using historical data. Use when a Won client or active deal has no folder (or a stale one), on \"reconstruct <client>\", \"we have history with X but no folder\", or after Attio shows a deal the filesystem is missing. Grounds the dashboard in Granola + Attio."
---

# Consulting Client Reconstruct

**Workspace:** use the selected project and its `AGENTS.md`; keep existing entity folders and
Reality headings. Business paths below are relative to that project. Bundled resources are relative
to this installed skill; sibling capabilities resolve by their installed names. Never search another
private checkout for missing inputs. Use workspace identity, audience, pricing, and `DESIGN.md` fonts.

When the CRM/Granola know about a relationship the repo doesn't (e.g. a Won deal with no
`clients/` folder), rebuild the folder from real history — without inventing facts.

## Steps
1. **Confirm the truth in Attio (live).** Stage, value, owner, linked company + parent/subsidiaries.
   This is authoritative for stage and $.
2. **Mine the Granola history.** Read `integrations/granola/<workspace>/clients/<name>/` (and
   `prospects/` if it pre-dates the win): champion, stakeholders, workstreams, cadence, key dates.
   Granola bodies are AI summaries — treat them as leads to verify, not gospel.
3. **Scaffold the folder.** Copy `clients/_TEMPLATE/` structure (00-context … 06-expansion + meetings)
   into `clients/<name>/` (or the right `pipeline/<stage>/` folder if not yet Won).
4. **Write the `AGENTS.md` dashboard** — status (from Attio), value, account structure, champion +
   stakeholders, workstreams, lead source, stakes, next action. **Reference** the Granola history
   (don't duplicate it). Put anything you couldn't verify under an explicit
   **"Open items to confirm"** section — never assert unverified client facts.
5. **Reconcile the board.** Update `pipeline/_board.md` and run `recoup-internal-consulting-integrations-sync` if
   other deals also drifted.
6. **Report** what you reconstructed and exactly which facts still need the user's confirmation.

Output: a grounded client/deal folder + an honest list of unknowns.

Resolve `<workspace>` from `integrations/granola/AGENTS.md`; preserve the existing mirror directory name.
