# Contributing

We welcome contributions — especially new skills for the music industry.

## Adding a Skill

1. Create a new directory under `skills/` with a `SKILL.md`:

```
skills/my-new-skill/
└── SKILL.md
```

2. Fill in the frontmatter:

```yaml
---
name: my-new-skill
description: What it does and when to use it. Include trigger phrases.
---
```

3. Write clear instructions in the body. Keep it under 5,000 words — move heavy reference material to a `references/` subdirectory.

4. Open a pull request.

## Skill Guidelines

- **One skill, one job.** Each skill does one thing well.
- **Self-contained.** No cross-dependencies between skills.
- **Description is the trigger.** The `description` field determines when an agent loads the skill. Be specific — include the phrases a user would actually say.
- **Real instructions, not theory.** Tell the agent exactly what to do, step by step.
- **No secrets.** Don't include API keys, tokens, or credentials. Reference environment variables instead.

## Skill Size

- `SKILL.md` body: under 5,000 words
- Put large reference material in `references/`
- Put executable code in `scripts/`
- Critical instructions go at the top

## Portability checklist (required — runs in CI)

Every skill must be cross-harness portable. Before opening a PR, confirm:

- [ ] **Self-contained** — references only files inside the skill's own directory (no `../`, no other skill's dir, no plugin-root paths).
- [ ] **No platform variables** — no `${CLAUDE_PLUGIN_ROOT}` / `$CLAUDE_*` in the body (they don't expand in markdown and don't exist off Claude Code).
- [ ] **Backtick paths, not markdown links** for `references/`/`scripts/` (`` `references/foo.md` ``, not `[foo](./references/foo.md)`).
- [ ] **Scripts co-located** in the skill's `scripts/`, invoked as `python3 scripts/foo.py`; sibling/helper imports also co-located.
- [ ] **Shared files duplicated + registered** in `scripts/vendored.json` (drift-checked byte-for-byte).

Run locally before pushing:

```bash
python3 scripts/portability_lint.py
python3 scripts/check_vendored.py
python3 scripts/validate_manifests.py
```

See the **Portable Skill Contract** in `AGENTS.md` for the full rules and rationale.

## Code of Conduct

Be kind, be helpful, build things that help artists.
