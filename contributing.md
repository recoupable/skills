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

## Code of Conduct

Be kind, be helpful, build things that help artists.
