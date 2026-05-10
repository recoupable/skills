# Contributing

We welcome contributions — new music-industry skills and new vertical plugins.

## Decide where your work belongs

| Type of contribution | Where it goes |
| -------------------- | ------------- |
| A generic music skill (anyone in the music business might use it) | `skills/{skill-name}/` — listed in the `recoupable-skills` plugin |
| A vertical workflow with 3+ related skills, commands, agents, or scripts | A new plugin folder under `plugins/{plugin-name}/` |
| A new skill that belongs to an existing vertical plugin | Inside that plugin: `plugins/{plugin}/skills/{skill-name}/` |

When in doubt, start as a skill under `skills/`. Promote to a plugin when the workflow grows past three related skills AND needs scripts, agents, or commands.

## Add a new skill (broad)

1. Create a new directory under `skills/` with a `SKILL.md`:

   ```text
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

3. Write clear instructions in the body. Keep `SKILL.md` under 5,000 words — move heavy reference material to `references/`.

4. Add the skill path to `marketplace.source.json` under the `recoupable-skills` plugin's `skills` array:

   ```jsonc
   "skills": [
     "./skills/artist-workspace",
     "./skills/my-new-skill",   // ← here
     ...
   ]
   ```

5. Regenerate the platform marketplace files:

   ```bash
   python3 scripts/generate-marketplaces.py
   ```

6. Validate:

   ```bash
   python3 scripts/validate-manifests.py
   ```

7. Open a pull request.

## Add a new vertical plugin

1. Scaffold the plugin directory:

   ```text
   plugins/my-plugin/
   ├── .claude-plugin/plugin.json
   ├── .codex-plugin/plugin.json
   ├── .cursor-plugin/plugin.json
   ├── skills/
   ├── agents/         (optional)
   ├── commands/       (optional)
   ├── scripts/        (optional)
   ├── templates/      (optional)
   ├── evals/          (optional)
   ├── fixtures/       (optional)
   ├── references/     (optional)
   ├── README.md
   └── LICENSE
   ```

2. Author each plugin manifest. The minimum required fields:

   ```jsonc
   // .claude-plugin/plugin.json
   {
     "name": "my-plugin",
     "version": "0.1.0",
     "description": "What this plugin does.",
     "author": { "name": "Recoupable", "email": "agent@recoupable.com" },
     "license": "Apache-2.0"
   }
   ```

   ```jsonc
   // .codex-plugin/plugin.json
   {
     "name": "my-plugin",
     "version": "0.1.0",
     "description": "What this plugin does.",
     "skills": "./skills/",
     "interface": { "displayName": "My Plugin", "category": "Music" }
   }
   ```

   ```jsonc
   // .cursor-plugin/plugin.json
   {
     "name": "my-plugin",
     "version": "0.1.0",
     "description": "What this plugin does.",
     "skills": "./skills/",
     "agents": "./agents/",
     "commands": "./commands/"
   }
   ```

3. Add the plugin to `marketplace.source.json`:

   ```jsonc
   {
     "name": "my-plugin",
     "version": "0.1.0",
     "description": "What this plugin does.",
     "category": "Music",
     "type": "self-contained",
     "source": "./plugins/my-plugin",
     "keywords": [...],
     "interface": {
       "displayName": "My Plugin",
       "shortDescription": "...",
       "longDescription": "...",
       "brandColor": "#345A5D",
       "capabilities": ["Read", "Write"]
     }
   }
   ```

4. Regenerate marketplace files and validate:

   ```bash
   python3 scripts/generate-marketplaces.py
   python3 scripts/validate-manifests.py
   ```

5. Open a pull request.

## Guidelines for skills

- **One skill, one job.** Each skill does one thing well.
- **Self-contained.** No cross-dependencies between skills.
- **Description is the trigger.** Vague descriptions don't activate. Include trigger phrases users say.
- **Real instructions, not theory.** Tell the agent exactly what to do, step by step.
- **No secrets.** Reference environment variables — never hardcode credentials.
- **Cross-platform.** Scripts should work on macOS and Linux when possible.

## Skill size

- `SKILL.md` body: under 5,000 words.
- Heavy reference material → `references/`.
- Executable code → `scripts/`.
- Critical instructions stay at the top of `SKILL.md`.

## Release checklist

Before merging any change:

- [ ] `python3 scripts/generate-marketplaces.py` produced no diff (or diff is committed)
- [ ] `python3 scripts/validate-manifests.py` exits 0
- [ ] New or changed plugin has a bumped `version` in its `plugin.json` and in `marketplace.source.json`
- [ ] `CHANGELOG.md` updated when releasing a new plugin or breaking change
- [ ] No secrets or credentials added
- [ ] Plugin-specific tests pass (if the plugin has its own test suite)

## Code of Conduct

Be kind, be helpful, build things that help artists.
