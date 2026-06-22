# Recoup Internal

Agent plugin for **Recoup's internal workflows** — engineering and operations.
Write and maintain high-signal GitHub tracking issues, deliver them docs-first
and test-driven from open to shipped, benchmark any plugin or skills folder
against the frontier of skill design, work the catalog-valuation sales funnel in
Attio, and produce account-health snapshots for any Recoup account. Built by
[Recoup](https://recoupable.com).

These are the internal-facing skills behind the rest of the Recoup skills repo —
the dev-tooling and ops skills the team runs, as opposed to the artist/label
product (see `recoup-records`).

## Install

### Claude Code (CLI)

```bash
claude plugin install https://github.com/recoupable/recoup-internal
```

### Claude Cowork

1. Open the plugin marketplace (puzzle-piece icon in the sidebar).
2. Click **Add custom plugin** and paste:
   `https://github.com/recoupable/recoup-internal`
3. Approve the requested tool permissions (`Read`, `Write`).
4. Confirm install: type `/plugin` and check that `recoup-internal` is listed.

### Cursor

1. Cursor → Settings → Plugins → **Add custom plugin**.
2. Paste the GitHub URL above.
3. Restart Cursor so `.cursor-plugin/plugin.json` loads the skills.

## Skills

| Skill | What it does |
|-------|-------------|
| [issue-management](skills/issue-management) | Write and maintain high-signal GitHub tracking issues that coordinate multi-PR, multi-repo work — structure, the Open→Done lifecycle, evidence/linking rules, and acceptance criteria |
| [issue-implementation](skills/issue-implementation) | Deliver a tracked issue end-to-end — documentation-driven (contract first), then test-driven (red→green) implementation, verified against the live preview and posted to the PR |
| [skill-pack-benchmark](skills/skill-pack-benchmark) | Benchmark any plugin, skill pack, or skills folder against the frontier (gstack, gbrain, compound-engineering, PM OS) — measure it, grade a 15-dimension scorecard, and produce a prioritized list of moves to steal |
| [valuation-sales-pipeline](skills/valuation-sales-pipeline) | Work the catalog-valuation sales funnel in Attio — qualify an inbound lead against revenue goals, enrich and advance the CRM record, and draft the first outreach email plus a one-page valuation PDF |
| [recoup-account-status](skills/recoup-account-status) | Produce an account-health snapshot for any Recoup account (artists, socials, chats, tasks, credits, subscription) as an ACCOUNT.md, a per-artist tree, and a polished status PDF — admin token inspects any account, owner token only its own |

## License

Apache-2.0. See [LICENSE](LICENSE).
