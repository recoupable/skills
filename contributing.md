# Contributing

We welcome new music skills and new vertical plugins.

## Where things go

| Type | Location |
|------|----------|
| Generic music skill | `skills/{name}/` — listed in the `recoup-skills` plugin |
| Vertical workflow (3+ skills + scripts/agents/commands) | `plugins/{name}/` — self-contained plugin |
| New skill inside an existing plugin | `plugins/{plugin}/skills/{name}/` |

When in doubt, start as a skill under `skills/`. Promote to a plugin once it grows past three related skills AND needs scripts, agents, or commands.

## How to add anything

1. Read [`AGENTS.md`](./AGENTS.md) — it documents the skill format, plugin layout, and validation rules.
2. Edit `marketplace.source.json` to register what you added.
3. Run:
   ```bash
   python3 scripts/generate-marketplaces.py
   python3 scripts/validate-manifests.py
   ```
4. Open a pull request.

CI runs the validator on every PR.

## Code of Conduct

Be kind, be helpful, build things that help artists.
