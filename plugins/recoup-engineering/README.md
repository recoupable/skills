# Recoup Engineering

Agent plugin for **engineering workflows**. Write and maintain high-signal
GitHub tracking issues, deliver them docs-first and test-driven from open to
shipped, and benchmark any plugin or skills folder against the frontier of skill
design. Built by [Recoup](https://recoupable.com).

These are the dev-tooling skills behind the rest of the Recoup skills repo —
useful in any codebase, not just music. Three skills cover it:
`issue-management` to write the tracking issue, `issue-implementation` to deliver
it, and `skill-pack-benchmark` to grade a plugin or skills folder.

## Install

### Claude Code (CLI)

```bash
claude plugin install https://github.com/recoupable/recoup-engineering
```

### Claude Cowork

1. Open the plugin marketplace (puzzle-piece icon in the sidebar).
2. Click **Add custom plugin** and paste:
   `https://github.com/recoupable/recoup-engineering`
3. Approve the requested tool permissions (`Read`, `Write`).
4. Confirm install: type `/plugin` and check that `recoup-engineering` is listed.

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

## How it works

`issue-management` and `issue-implementation` are a pair: one writes the
tracking issue, the other implements it docs→tests→code with preview
verification. `skill-pack-benchmark` is self-contained — it ships a
deterministic measurement script (`scripts/measure.py`, stdlib-only, no network)
plus reference docs holding the frontier standard, and grades any target you
point it at.

## License

Apache-2.0. See [LICENSE](LICENSE).
