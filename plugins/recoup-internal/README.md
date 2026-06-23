# Recoup Internal

Agent plugin for **Recoup's internal workflows** — engineering and operations.
Write and maintain high-signal GitHub tracking issues, deliver them docs-first
and test-driven from open to shipped, benchmark any plugin or skills folder
against the frontier of skill design, work the catalog-valuation sales funnel in
Attio, produce account-health snapshots for any Recoup account, and draft, ship,
and measure data-grounded social posts. Built by [Recoup](https://recoupable.com).

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
| [recoup-dev-issue-tracker](skills/recoup-dev-issue-tracker) | Write and maintain high-signal GitHub tracking issues that coordinate multi-PR, multi-repo work — structure, the Open→Done lifecycle, evidence/linking rules, and acceptance criteria |
| [recoup-dev-ship-issue](skills/recoup-dev-ship-issue) | Deliver a tracked issue end-to-end — documentation-driven (contract first), then test-driven (red→green) implementation, verified against the live preview and posted to the PR |
| [recoup-eval-skill-benchmark](skills/recoup-eval-skill-benchmark) | Benchmark any plugin, skill pack, or skills folder against the frontier (gstack, gbrain, compound-engineering, PM OS) — measure it, grade a 15-dimension scorecard, and produce a prioritized list of moves to steal |
| [recoup-funnel-valuation-pipeline](skills/recoup-funnel-valuation-pipeline) | Work the catalog-valuation sales funnel in Attio — qualify an inbound lead against revenue goals, enrich and advance the CRM record, and draft the first outreach email plus a one-page valuation PDF |
| [recoup-account-health-report](skills/recoup-account-health-report) | Produce an account-health snapshot for any Recoup account (artists, socials, chats, tasks, credits, subscription) as an ACCOUNT.md, a per-artist tree, and a polished status PDF — admin token inspects any account, owner token only its own |
| [recoup-social-ship-posts](skills/recoup-social-ship-posts) | Write, publish, and measure data-grounded LinkedIn and X posts — product announcements and artist highlights — with copy principles, CTA choice, connector publishing (incl. X native video), and a learn→draft→publish→re-measure loop |

## License

This project is licensed under the AGPL-3.0 for non-commercial use. See [LICENSE](LICENSE).

### Commercial Use

For commercial use or deployments requiring a setup, please contact us for a
commercial license at support@recoupable.com. By using this software, you agree
to the terms of the license.
