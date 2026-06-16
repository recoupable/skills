# Scaffold spec — build a cross-platform Agent Skills repo (public OR private)

You are an agent. Your job: scaffold a complete, governed **agent-skills monorepo** for a company, given that company's name, departments/teams, **distribution track**, and a few identity details. This single spec replaces two earlier specs and the Codex `plugin-creator` skill — it can scaffold **either** of two tracks from the same conventions:

- **Public track** — skills/plugins that **anyone** can install (`npx skills add`, public marketplace add).
- **Private track** — plugins that a **team admin** installs and pushes to the org (enterprise Cowork / Codex personal-or-team marketplace, auto-install).

Pick the track first (§1). Everything after that is shared, with the few track-specific knobs called out inline and summarized in one table (§19). Follow it end to end. **Do not skip files.**

---

## 0. What you are building (mental model)

A **monorepo** that packages reusable AI **skills** (instructions following the [Agent Skills open standard](https://agentskills.io/specification)) so the same skill bodies run unchanged across **Claude Code, Cowork, Codex, and Cursor** — only the thin install/discovery *wrapper* differs per platform.

The repo ships skills through **two distribution layers**:

1. **Standalone skills** — a top-level `skills/` directory of portable, self-contained skills that drop into *any* agent. These install via `npx skills add <org>/<repo>` **and** as a single "library" plugin (the repo root is itself registered as a plugin whose `skills` path is `./skills/`).
2. **Plugins** — rich bundles in `plugins/<name>/` that ship skills **plus** agents, hooks, shared references, evals, and fixtures, installed through each runtime's plugin system. A skill is a subset of a plugin. (No `commands/` — this repo is skills-only; see AGENTS.md "No slash-commands".)

Both layers are authored once and install across every harness. Every plugin carries parallel per-harness manifests, and the repo carries parallel marketplace catalogs.

```text
repo root
├── README.md, AGENTS.md, CLAUDE.md, contributing.md           # docs + governance
│   (private add-ons: RUNBOOKS.md)
├── LICENSE
├── .gitignore
├── .claude-plugin/
│   ├── marketplace.json          # Claude / Cowork catalog (lists EVERY plugin)
│   └── plugin.json               # repo-as-plugin manifest (ships top-level skills/)
├── .codex-plugin/plugin.json     # repo-as-plugin manifest for Codex (has `skills` + `interface`)
├── .agents/plugins/marketplace.json   # Cursor + Codex/agents catalog (parity with .claude-plugin)
├── .claude/settings.json         # PRIVATE ONLY: auto-add marketplace + auto-install essentials
├── .github/workflows/validate.yml     # CI: runs the Python validation gates
│   (private add-ons: CODEOWNERS, pull_request_template.md)
├── scripts/                      # validation gates + vendored.json (shared-file registry)
│   ├── portability_lint.py
│   ├── check_vendored.py
│   ├── validate_manifests.py
│   └── vendored.json
├── skills/                       # STANDALONE portable skills (unprefixed, npx-installable)
│   └── <capability>/SKILL.md     # one folder per skill; optional references/ scripts/ templates/ fixtures/
├── docs/                         # OPTIONAL build-time skill-craft reference (NOT shipped to users)
└── plugins/<prefix>-<group>/
    ├── .claude-plugin/plugin.json     # Claude / Cowork manifest
    ├── .codex-plugin/plugin.json      # Codex manifest (has `skills` + `interface` block)
    ├── .cursor-plugin/plugin.json     # Cursor manifest (has `skills` + `repository`; NO `interface` block)
    ├── README.md, LICENSE, .gitignore
    ├── skills/<prefix>-<capability>/SKILL.md   # one folder per skill (prefixed)
    ├── references/               # optional: shared docs, VENDORED byte-identical into each skill that uses them
    ├── agents/                   # optional: subagents
    ├── hooks/                    # optional: hooks.json + scripts
    ├── evals/                    # optional: eval scenarios
    └── fixtures/                 # optional: golden / demo data
```

**The three-layer update reality (explain this to the maintainer):** pushing to `main` does **not** auto-update installed users. A merge reaches plugin users only after they run the marketplace-update + plugin-update commands, **and only if the plugin `version` was bumped** — the version string is the update cache key, so shipping content without a bump is a silent no-op. (Standalone-skill users re-run `npx skills add` to pull the latest. Local-dev iteration uses the cachebuster flow in §18.)

---

## 1. Pick the track first (this changes several knobs)

| | **Public track** (default) | **Private track** |
|---|---|---|
| **Installed by** | anyone | a **team admin**, pushed to the org |
| **Use when** | skills are shareable; you want `npx skills add` distribution | skills are company-confidential; distribution is enterprise/admin-managed |
| **`LICENSE`** | open (`Apache-2.0` / `MIT`) | `Proprietary` |
| **Top-level `skills/` layer** | **yes** (npx-installable, unprefixed) | optional — often dropped (plugins only) |
| **`npx skills add`** | yes | n/a |
| **Repo-as-plugin (`{{PREFIX}}-skills`)** | yes | only if shipping the skills layer |
| **`{{PREFIX}}-essentials` auto-install plugin** | no | **yes** |
| **`.claude/settings.json` (auto-add + auto-install)** | no | **yes** |
| **Codex personal/team marketplace `policy`** | `AVAILABLE` (opt-in) | essentials `INSTALLED_BY_DEFAULT`; rest `AVAILABLE` |
| **`.github/CODEOWNERS` + PR template** | optional | **recommended** |
| **README install** | public + npx + marketplace add | enterprise admin + private-repo token note |

Confirm the track with the maintainer **before writing files**. Everything below applies to both tracks unless tagged **[PUBLIC]** or **[PRIVATE]**.

---

## 2. Inputs — collect these before scaffolding

Accept reasonable defaults; confirm the derived names once before writing files.

| Input | Example | Used for |
|---|---|---|
| **Track** | `public` / `private` | Picks the knob set in §1 + §19 |
| **Company legal/parent name** | `Recoupable` | `author.name`, attribution, owner object — stays the real company name |
| **Brand name** (may equal company) | `Recoup` | User-facing display labels (`Recoup — Research`) |
| **Brand prefix** (kebab, lowercase) | `recoup` | Plugin + plugin-skill identifiers |
| **GitHub org** | `recoupable` | Plugin source URLs, repo links (lowercase) |
| **GitHub repo name** | `skills` | `https://github.com/<org>/<repo>.git` |
| **License** | `Apache-2.0` (public) / `Proprietary` (private) | `LICENSE`, every manifest `license` field |
| **Maintainer name / email / GitHub handle** | `Sidney Swift` / `agent@company.com` / `sidneyswift` | Owner objects, CODEOWNERS, READMEs |
| **Support email** | `agent@recoupable.com` | `owner.email`, `author.email`, attribution — **must match across every layer** |
| **Departments / teams** | Research, Deals, Content, Songs | Become plugins (one per audience cluster) |
| **Known plugin skills per dept** (optional) | "artist research", "royalty normalization" | Become prefixed `skills/` folders inside a plugin |
| **Known standalone skills** (optional, public) | "songwriting", "getting started" | Become unprefixed top-level `skills/` folders |

### Derived names (compute these, then confirm)

- **Marketplace name** = the short brand handle (recoup uses `recoup`). This is the `@`-suffix in plugin installs (`<plugin>@<marketplace>`).
- **Repo-as-plugin name** = `<prefix>-skills` (e.g. `recoup-skills`) — the library plugin whose `skills` path is the top-level `./skills/`.
- **Plugin identifier** = `<prefix>-<group>` (kebab, lowercase). `group` = the install **audience**, not a fancy label.
- **Plugin display label** = `<Brand> — <Group>` (e.g. `Recoup — Research`).
- **Plugin skill identifier** = `<prefix>-<capability>` (kebab, lowercase) — named for **what it does**, never the owning team.
- **Standalone skill identifier** = `<capability>` (kebab, lowercase, **no prefix** — portable + brand-neutral).
- **[PRIVATE]** always include a `<prefix>-essentials` plugin — the universal/auto-install bucket.

> **Name normalization (apply to every identifier):** `My Plugin` → `my-plugin`; `My--Plugin` → `my-plugin`; underscores, spaces, punctuation → `-`; lower-case, consecutive hyphens collapsed; max 64 chars. The outer folder name and the manifest `"name"` are **always identical**.

> **Placeholder convention:** `{{COMPANY_LEGAL_NAME}}`, `{{BRAND_NAME}}`, `{{PREFIX}}`, `{{MARKETPLACE}}`, `{{GH_ORG}}`, `{{GH_REPO}}`, `{{OWNER_NAME}}`, `{{OWNER_EMAIL}}`, `{{OWNER_GH}}`, `{{LICENSE}}`, `{{VERSION}}` (start `0.1.0`; the library plugin may start `1.0.0`). Per-plugin: `{{GROUP}}`, `{{PLUGIN}}` (=`{{PREFIX}}-{{GROUP}}`), `{{GROUP_TITLE}}`, `{{CATEGORY}}` (e.g. `Music` / `Productivity` / `Creative` / `Technology`), `{{PLUGIN_DESC}}`. Replace **every** occurrence.

---

## 3. Naming conventions (the load-bearing rules)

1. **Everything is kebab-case, lowercase** — marketplace, plugins, skills, folders, files. No underscores, no spaces.
2. **Prefix *plugins* and *plugin skills* with `{{PREFIX}}-`.** A bare plugin name collides with built-ins and loses the brand.
3. **[PUBLIC] Standalone (top-level `skills/`) skills are UNPREFIXED, plain-English.** A generic agent installing them via `npx skills add` should see a name that describes the capability, not your company.
   - ✅ standalone: `songwriting`, `getting-started`, `release-management`, `chart-metric`
   - ✅ plugin skill: `{{PREFIX}}-artist-research`, `{{PREFIX}}-song-analyzer`, `{{PREFIX}}-deal-ingest`
   - ❌ `{{PREFIX}}-songwriting` as a *standalone* (over-branded); ❌ `artist-research` as a *plugin skill* (missing prefix)
4. **Name a skill for the capability, not the department or a helper verb.** Keep a verb only when the verb *is* the capability (`{{PREFIX}}-create-wiki`).
   - ❌ `{{PREFIX}}-watch` (watch what?), `generate-vendor-list` (leading verb), `operations-vendor-tool` (department prefix)
5. **The skim test** — assume the user sees a flat list where the **name is the only visible thing**. From the name alone, will they know what it does? If not, it's too vague.
6. **The `description` is the load-bearing field** — the router reads it, not the name. Lead with concrete trigger phrases the user would actually type, then a bidirectional `Do NOT use for X — use Y instead` cross-route clause.
7. **The frontmatter `name` MUST match the skill folder name exactly** (CI enforces this).
8. **Router skill pattern** — give each plugin one **entry-point skill** (`{{PREFIX}}-<group>-analyzer` or similar) that resolves inputs and routes to focused sub-skills (e.g. `recoup-song-analyzer`).
9. **What stays the real company name (not branded):** `author.name`, `interface.developerName`, the GitHub org/repo, owner objects, support email, and prose attribution. Only *identifiers* and *display labels* take the brand prefix.

### Mapping departments → plugins; standalone vs plugin

- **Standalone (top-level `skills/`)** = generally useful, single-job, fully self-contained, no enterprise dependency. **[PUBLIC]** repos lean on this layer heavily.
- **Plugin (`plugins/<prefix>-<group>/`)** = a cluster of related skills for one audience, or anything needing agents/hooks/evals/shared references. Each department/audience cluster → one `{{PREFIX}}-<group>` plugin. Pick `group` by **install audience**, not org-chart title.
- A skill lives in exactly one place. For multi-team usefulness, leave it with the primary owner and let other teams cross-install — **never duplicate a whole skill across plugins.** (Shared *reference/script files* are vendored — see §8.)
- **Promote standalone skills into a plugin when they share a canonical reference** (cross-dependency breaks self-containment — move them under a plugin and vendor the shared doc into each, §8).
- If a skill fits no plugin and isn't a clean standalone, **stop and ask** before inventing a new plugin (new plugins are high-bar: owner, three manifests, catalog registration in both catalogs).
- **[PRIVATE]** keep the `essentials` bar high: only things *every* employee plausibly needs.

---

## 4. Versioning

> Two valid models exist. Use **Model A (per-plugin, version in the catalog)** by default — it is what the validation gate in §9 enforces. Use **Model B (synchronized)** only if the maintainer explicitly asks for it (older all-plugin private repos).

### Model A — per-plugin semver, version lives IN the catalog entries (default)

- **Each plugin owns an independent `version`** (strict `MAJOR.MINOR.PATCH`). Bump only what changed (`feat`→minor, `fix`→patch, breaking→major).
- **The `version` appears in FOUR places per plugin and must be identical across all four:**
  1. `plugins/{{PLUGIN}}/.claude-plugin/plugin.json`
  2. `plugins/{{PLUGIN}}/.codex-plugin/plugin.json`
  3. `plugins/{{PLUGIN}}/.cursor-plugin/plugin.json`
  4. that plugin's **entry in both marketplace catalogs**
- The repo-as-plugin (`{{PREFIX}}-skills`) also carries a version everywhere (start `1.0.0`).

### Model B — synchronized semver, NO version in catalog entries (alternative)

- **All plugins share ONE version string**, identical across all three manifests of all plugins; bumped once at release in lockstep. **`version` does NOT go in catalog entries** (manifest wins silently otherwise). Contributors leave the version alone; the maintainer bumps at release.

Both models share the why: **the version is the update cache key; content pushed without a bump never reaches installed users.** Verify before shipping:

```bash
# Model A: all four copies print the same string
grep -rn '"version"' plugins/{{PLUGIN}}/.claude-plugin/plugin.json \
  plugins/{{PLUGIN}}/.codex-plugin/plugin.json \
  plugins/{{PLUGIN}}/.cursor-plugin/plugin.json
python3 scripts/validate_manifests.py
```

---

## 5. Build order

1. Create the directory tree.
2. Write `scripts/` validation gates + an initial `scripts/vendored.json` (§8–9).
3. Write the marketplace catalogs (§6) + the repo-as-plugin root manifests (§7).
4. Write root docs: `AGENTS.md`, `CLAUDE.md`, `README.md`, `contributing.md` (§16). **[PRIVATE]** add `.claude/settings.json`, `RUNBOOKS.md`.
5. Write `LICENSE` + `.gitignore` (§10).
6. Write `.github/workflows/validate.yml` (§11). **[PRIVATE]** add CODEOWNERS + PR template.
7. **[PUBLIC]** Write the standalone skills under `skills/` (§13).
8. For each plugin: three manifests + `README.md` + `LICENSE` + `.gitignore` + ≥1 starter `SKILL.md` (§12, §14); vendor any shared references and register them in `vendored.json`.
9. *(optional)* Write the `docs/` skill-craft reference (§15).
10. Run all three validation gates + the pre-flight checklist (§17), then the Codex/dev install handoff (§18).

---

## 6. Marketplace catalogs (both must list every plugin, in parity)

Use **two** catalogs: `.claude-plugin/marketplace.json` (Claude / Cowork) and `.agents/plugins/marketplace.json` (Cursor + Codex/agents). `validate_manifests.py` enforces **dual-manifest parity**: both list the same plugins with the same `name`, `source`, and `version`.

**Source format:** each entry's `source` is a **relative path string** from the repo root — `"."` for the repo-as-plugin, `"./plugins/<plugin>"` for a plugin. The gate checks the directory exists.

> **Enterprise-Cowork variant [PRIVATE]:** if your Cowork validator rejects relative-string sources, switch the `.claude-plugin/marketplace.json` entries to a `git-subdir` source object with a full `https://` URL + explicit `ref` + `path`. Keep the `.agents` catalog on relative strings and note this divergence in `AGENTS.md`.

### `.claude-plugin/marketplace.json` (Claude / Cowork)

```json
{
  "name": "{{MARKETPLACE}}",
  "owner": { "name": "{{BRAND_NAME}}", "email": "{{OWNER_EMAIL}}", "url": "https://{{company-domain}}" },
  "plugins": [
    {
      "name": "{{PREFIX}}-skills",
      "source": ".",
      "description": "The skills library — portable skills you can drop into any agent. Also installable via `npx skills add {{GH_ORG}}/{{GH_REPO}}`.",
      "version": "1.0.0",
      "author": { "name": "{{COMPANY_LEGAL_NAME}}", "email": "{{OWNER_EMAIL}}", "url": "https://{{company-domain}}" },
      "homepage": "https://{{company-domain}}",
      "repository": "https://github.com/{{GH_ORG}}/{{GH_REPO}}",
      "license": "{{LICENSE}}",
      "keywords": ["agent-skills"],
      "category": "{{CATEGORY}}"
    },
    {
      "name": "{{PLUGIN}}",
      "source": "./plugins/{{PLUGIN}}",
      "description": "{{PLUGIN_DESC}}",
      "version": "{{VERSION}}",
      "author": { "name": "{{COMPANY_LEGAL_NAME}}", "email": "{{OWNER_EMAIL}}", "url": "https://{{company-domain}}" },
      "homepage": "https://{{company-domain}}",
      "repository": "https://github.com/{{GH_ORG}}/{{GH_REPO}}",
      "license": "{{LICENSE}}",
      "keywords": ["{{PREFIX}}", "{{GROUP}}", "agent-skills"],
      "category": "{{CATEGORY}}"
    }
    // …one entry per plugin. EVERY entry carries an explicit "version" (Model A).
  ]
}
```

### `.agents/plugins/marketplace.json` (Cursor + Codex/agents)

Identical plugin list (parity on `name` + `source` + `version`). Each entry **may add** an `interface{}` block (Cursor display metadata — parity ignores it) **and** a `policy{}` block (Codex install governance — see §6a). The parity check ignores both.

```json
{
  "name": "{{MARKETPLACE}}",
  "interface": { "displayName": "{{BRAND_NAME}} — Skills" },
  "owner": { "name": "{{BRAND_NAME}}", "email": "{{OWNER_EMAIL}}", "url": "https://{{company-domain}}" },
  "plugins": [
    {
      "name": "{{PLUGIN}}",
      "source": "./plugins/{{PLUGIN}}",
      "version": "{{VERSION}}",
      "description": "{{PLUGIN_DESC}}",
      "author": { "name": "{{COMPANY_LEGAL_NAME}}", "email": "{{OWNER_EMAIL}}", "url": "https://{{company-domain}}" },
      "homepage": "https://{{company-domain}}",
      "repository": "https://github.com/{{GH_ORG}}/{{GH_REPO}}",
      "license": "{{LICENSE}}",
      "keywords": ["{{PREFIX}}", "{{GROUP}}", "agent-skills"],
      "policy": { "installation": "AVAILABLE", "authentication": "ON_INSTALL" },
      "category": "{{CATEGORY}}",
      "interface": {
        "displayName": "{{BRAND_NAME}} — {{GROUP_TITLE}}",
        "shortDescription": "One-line audience-facing summary.",
        "longDescription": "Fuller description of what the plugin's skills do and who installs it.",
        "developerName": "{{COMPANY_LEGAL_NAME}}",
        "category": "{{CATEGORY}}",
        "capabilities": ["Read", "Write"],
        "websiteURL": "https://{{company-domain}}",
        "brandColor": "#345A5D"
      }
    }
    // …plus the {{PREFIX}}-skills repo-as-plugin entry, same as the Claude catalog.
  ]
}
```

> **Author-email parity:** every plugin's `author.email` in both catalogs **and** in that plugin's own three manifests must equal `{{OWNER_EMAIL}}`.
> **Render order:** plugin order in `plugins[]` is render order in Codex. **Append** new entries unless asked to reorder.
> **`displayName`** belongs inside the marketplace `interface` object (and inside each entry's `interface`), never as a bare `plugins[]` field.

### 6a. Codex `policy` block (governs how a team admin's marketplace installs)

Every `.agents` entry that targets Codex should carry a `policy` plus `category`:

```json
"policy": { "installation": "AVAILABLE", "authentication": "ON_INSTALL" }
```

- **`policy.installation`** ∈ `NOT_AVAILABLE` | `AVAILABLE` | `INSTALLED_BY_DEFAULT`. (Codex rejects any other value at load time and refuses the whole marketplace.)
  - **[PUBLIC]** default every plugin to `AVAILABLE` (opt-in).
  - **[PRIVATE]** `{{PREFIX}}-essentials` → `INSTALLED_BY_DEFAULT` (auto-installed for everyone); the rest → `AVAILABLE`. To auto-install *every* plugin, set them all to `INSTALLED_BY_DEFAULT`.
- **`policy.authentication`** ∈ `ON_INSTALL` | `ON_USE`. Default `ON_INSTALL`. Override only when the user specifies.
- **`policy.products`** is an override — omit it unless the user explicitly requests product gating.
- Always write `policy.installation`, `policy.authentication`, and `category` even when they are defaults.

### 6b. Codex personal vs team marketplace destination

- The **personal** Codex marketplace file is `~/.agents/plugins/marketplace.json` (discovered implicitly — do **not** tell the user to run `codex plugin marketplace add` for it).
- A **repo/team** marketplace is the `.agents/plugins/marketplace.json` *inside this repo*. A team admin installs it explicitly: `codex plugin marketplace add <path-to-repo>` (or the repo URL). Only give reinstall instructions for a non-default marketplace **after** confirming it is actually installed.
- For a brand-new personal marketplace file, seed the root with top-level `"name"`, an `"interface"` object containing `"displayName"`, and a `plugins` array before adding the first entry.

---

## 7. Repo-as-plugin (root manifests that ship the standalone `skills/` layer)

The repo root is itself a plugin so the top-level `skills/` install through the plugin systems too (not only `npx`). Create two root manifests pointing at `./skills/`. **[PRIVATE]** create these only if you ship the skills layer.

### `.claude-plugin/plugin.json` (root)
```json
{
  "name": "{{PREFIX}}-skills",
  "version": "1.0.0",
  "description": "AI agent skills for {{domain}} — <one line>.",
  "author": { "name": "{{COMPANY_LEGAL_NAME}}", "email": "{{OWNER_EMAIL}}", "url": "https://{{company-domain}}" },
  "homepage": "https://{{company-domain}}",
  "repository": "https://github.com/{{GH_ORG}}/{{GH_REPO}}",
  "license": "{{LICENSE}}",
  "keywords": ["agent-skills"]
}
```

### `.codex-plugin/plugin.json` (root)
Same as above **plus** `"skills": "./skills/"` and an `interface` block (so Codex/Cursor discover the top-level skills and render display metadata):
```json
{
  "name": "{{PREFIX}}-skills",
  "version": "1.0.0",
  "description": "AI agent skills for {{domain}} — <one line>.",
  "author": { "name": "{{COMPANY_LEGAL_NAME}}", "email": "{{OWNER_EMAIL}}", "url": "https://{{company-domain}}" },
  "homepage": "https://{{company-domain}}",
  "repository": "https://github.com/{{GH_ORG}}/{{GH_REPO}}",
  "license": "{{LICENSE}}",
  "keywords": ["agent-skills"],
  "skills": "./skills/",
  "interface": {
    "displayName": "{{BRAND_NAME}} Skills",
    "shortDescription": "<short>",
    "longDescription": "<long>",
    "developerName": "{{COMPANY_LEGAL_NAME}}",
    "category": "{{CATEGORY}}",
    "capabilities": ["Read", "Write"],
    "websiteURL": "https://{{company-domain}}",
    "brandColor": "#345A5D"
  }
}
```

> Cursor auto-discovers the top-level skills through the `.agents/plugins/marketplace.json` repo-as-plugin entry (`source: "."`); no separate root `.cursor-plugin/plugin.json` is needed.
> Keep `apps`/`mcpServers` **out** of any `plugin.json` unless their companion files (`.app.json`, `.mcp.json`) actually exist. Omit fields the validator rejects (e.g. `hooks` inside `plugin.json`).

---

## 8. The Portable Skill Contract (the load-bearing portability discipline)

Every skill — standalone **and** plugin — must run on **any** harness (Claude Code, Codex, Cursor, bare `npx skills`). Five rules, enforced by `scripts/portability_lint.py`:

1. **Self-contained.** A skill reads/executes **only files inside its own directory** (`references/`, `scripts/`, `templates/`, `fixtures/`, `assets/`). Never reference `../`, `../../references/`, another skill's directory, or a plugin-root `scripts/`/`references/`.
2. **No platform variables in the body.** Do **not** write `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_SKILL_DIR}`, or any `$CLAUDE_*` path in a SKILL.md body. They only expand in JSON configs (hooks/`.mcp.json`) on Claude Code and ship as literal, broken strings elsewhere. Use plain relative paths. *(Exception: `hooks/hooks.json` and `.mcp.json` MAY use `${CLAUDE_PLUGIN_ROOT}` — it expands in JSON on Claude Code.)*
3. **Reference docs with backtick paths, never markdown links.** Write `` `references/foo.md` `` (a backtick path the agent can locate), not `[foo](./references/foo.md)`. Agents interpret markdown links as CWD-relative `Read` calls, and the CWD is never the skill dir.
4. **Co-locate scripts; invoke relatively.** Ship scripts in the skill's own `scripts/` and call them as `python3 scripts/foo.py`. Add a one-line note that scripts ship alongside the skill. A script's imported siblings must live in the same `scripts/`.
5. **Duplicate shared material; drift-check it.** If two skills need the same reference/script, **copy it into each**; register every copy in `scripts/vendored.json` so `scripts/check_vendored.py` keeps them byte-identical (§8a). Vendoring is allowed; silent divergence is not.

> **Why:** `${CLAUDE_PLUGIN_ROOT}` is Claude-Code-only and doesn't expand in markdown; runtime CWD is the user's project, not the skill dir. Self-containment with relative/backtick paths is the only pattern that travels across harnesses.

### 8a. Vendoring shared files (`scripts/vendored.json` + drift check)

The canonical copy lives at the plugin root (e.g. `plugins/{{PLUGIN}}/references/foo.md`); each skill that uses it gets a vendored copy under the skill's own `references/`. Two group shapes — single files and whole directories:

```json
{
  "_comment": "Maps each canonical shared file/dir to its vendored copies, kept byte-identical by scripts/check_vendored.py.",
  "groups": [
    {
      "canonical": "plugins/{{PLUGIN}}/references/foo.md",
      "copies": [
        "plugins/{{PLUGIN}}/skills/{{PREFIX}}-a/references/foo.md",
        "plugins/{{PLUGIN}}/skills/{{PREFIX}}-b/references/foo.md"
      ]
    },
    {
      "canonical_dir": "plugins/{{PLUGIN}}/templates/workspace",
      "copies_dirs": ["plugins/{{PLUGIN}}/skills/{{PREFIX}}-a/templates/workspace"]
    }
  ]
}
```

Start it with `{"groups": []}` if nothing is shared yet. **Editing a vendored file (no `--sync` flag):** change the **canonical** copy only, then re-sync every copy, then re-check. **Never hand-edit a vendored copy.**

```bash
python3 - <<'PY'
import json, shutil
for g in json.load(open("scripts/vendored.json"))["groups"]:
    if "canonical" in g:
        for c in g["copies"]:
            shutil.copyfile(g["canonical"], c)
    else:
        for d in g["copies_dirs"]:
            shutil.copytree(g["canonical_dir"], d, dirs_exist_ok=True)
PY
python3 scripts/check_vendored.py
```

---

## 9. Validation gates (three Python scripts — all must exit 0)

Write these three scripts (stdlib only, no dependencies). They are the repo's quality gate and run in CI. Track the **exit code**, not the counts.

```bash
python3 scripts/portability_lint.py    # every skill is cross-harness portable (§8)
python3 scripts/check_vendored.py      # vendored copies are byte-identical to canonical (§8a)
python3 scripts/validate_manifests.py  # manifests valid JSON + semver + source exists + dual-catalog parity (§4, §6)
```

- **`portability_lint.py`** — walks every `SKILL.md`. Flags: any `${CLAUDE_*}`/`$CLAUDE_*` variable in a body; any `../…/references|scripts|templates|fixtures|assets/` escape; any `skills/<other>/…` cross-skill reference; any markdown link to a local resource (must be a backtick path); any backticked/fenced resource token that leaves the skill dir or points at a missing file. Exit 1 on any violation, printing `file:line`.
- **`check_vendored.py`** — reads `scripts/vendored.json`. For each file group asserts every copy is byte-identical (`filecmp.cmp(..., shallow=False)`); for each dir group asserts the trees match. Exit 1 on drift/missing; no-op (exit 0) if `vendored.json` is absent.
- **`validate_manifests.py`** — every `marketplace.json`/`plugin.json`/`.mcp.json` is valid JSON; each catalog plugin entry has `name`+`source`+`version`; `version` matches `^\d+\.\d+\.\d+([-+].+)?$`; `source` resolves to a real directory; names unique; **dual-manifest parity** on `(name, source, version)` (the `.agents` copy may add `interface`/`policy`, ignored). Exit 1 on any problem.

> These three scripts are domain-agnostic — reproduce them as-is. Only `vendored.json` is repo-specific.

---

## 10. `LICENSE` and `.gitignore`

### `LICENSE`
- **[PUBLIC]** the chosen open license verbatim (e.g. `Apache-2.0`, `MIT`). Each plugin also ships its own `LICENSE` (same license). A manifest claiming `MIT` with no matching `LICENSE` is a contradiction reviewers will trip over.
- **[PRIVATE]** a short `Proprietary` notice.

### `.gitignore`
```gitignore
# macOS
.DS_Store
.AppleDouble
.LSOverride

# OneDrive / SharePoint sync metadata
~$*
.~lock.*
desktop.ini
Thumbs.db

# Editor/IDE
.idea/
.vscode/
*.swp
*~
.obsidian/

# Node / Python tooling
node_modules/
__pycache__/
*.pyc
.venv/

# Local secrets
.env
.env.local
*.key
*.pem

# Per-machine settings (a committed .claude/settings.json is fine, private track)
.claude/settings.local.json
```

---

## 11. `.github/` files

### `.github/workflows/validate.yml` (required — runs the Python gates)
```yaml
name: validate

on:
  pull_request:
  push:
    branches: [main]

jobs:
  portability:
    name: Portability + drift + manifests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Portable Skill Contract lint
        run: python3 scripts/portability_lint.py
      - name: Vendored-file drift check
        run: python3 scripts/check_vendored.py
      - name: Manifest + parity validation
        run: python3 scripts/validate_manifests.py
```

### `.github/CODEOWNERS` *(optional [PUBLIC]; recommended [PRIVATE])*
```text
# Auto-routes PR review by file path. Add domain leads per-plugin as they onboard:
#   /plugins/{{PLUGIN}}/  @{{OWNER_GH}} @their-handle
*  @{{OWNER_GH}}
```

### `.github/pull_request_template.md` *(optional [PUBLIC]; recommended [PRIVATE])*
A skill-PR checklist: what's in the PR + which plugin or the standalone layer; valid frontmatter; `name` matches folder; description packed with real trigger phrases; portability checklist (self-contained, no `$CLAUDE_*`, backtick paths, scripts co-located, shared files vendored + registered); no secrets inline; how it was tested; version bumped if a plugin changed.

---

## 12. Plugin manifests (three per plugin)

For **every** plugin create all three. They share `name`, `version`, `description`, `author`, `license`, `keywords`. Differences: Codex and Cursor both add `"skills": "./skills/"`; Codex adds an `interface` block; Cursor adds a per-plugin `repository` and **no `interface` block** (its schema is `additionalProperties: false`).

### `plugins/{{PLUGIN}}/.claude-plugin/plugin.json`
```json
{
  "name": "{{PLUGIN}}",
  "version": "{{VERSION}}",
  "description": "{{PLUGIN_DESC}}",
  "author": { "name": "{{COMPANY_LEGAL_NAME}}", "email": "{{OWNER_EMAIL}}", "url": "https://{{company-domain}}" },
  "homepage": "https://{{company-domain}}",
  "repository": "https://github.com/{{GH_ORG}}/{{GH_REPO}}",
  "license": "{{LICENSE}}",
  "keywords": ["{{PREFIX}}", "{{GROUP}}", "agent-skills"]
}
```

### `plugins/{{PLUGIN}}/.codex-plugin/plugin.json`
```json
{
  "name": "{{PLUGIN}}",
  "version": "{{VERSION}}",
  "description": "{{PLUGIN_DESC}}",
  "author": { "name": "{{COMPANY_LEGAL_NAME}}", "email": "{{OWNER_EMAIL}}", "url": "https://{{company-domain}}" },
  "homepage": "https://{{company-domain}}",
  "repository": "https://github.com/{{GH_ORG}}/{{GH_REPO}}",
  "license": "{{LICENSE}}",
  "keywords": ["{{PREFIX}}", "{{GROUP}}", "agent-skills"],
  "skills": "./skills/",
  "interface": {
    "displayName": "{{BRAND_NAME}} — {{GROUP_TITLE}}",
    "shortDescription": "One-line audience-facing summary.",
    "longDescription": "Fuller description of what the plugin's skills do and who installs it.",
    "developerName": "{{COMPANY_LEGAL_NAME}}",
    "category": "{{CATEGORY}}",
    "capabilities": ["Read", "Write"],
    "websiteURL": "https://{{company-domain}}",
    "brandColor": "#345A5D"
  }
}
```

### `plugins/{{PLUGIN}}/.cursor-plugin/plugin.json`
```json
{
  "name": "{{PLUGIN}}",
  "version": "{{VERSION}}",
  "description": "{{PLUGIN_DESC}}",
  "author": { "name": "{{COMPANY_LEGAL_NAME}}", "email": "{{OWNER_EMAIL}}" },
  "homepage": "https://{{company-domain}}",
  "repository": "https://github.com/{{GH_ORG}}/{{PLUGIN}}",
  "license": "{{LICENSE}}",
  "keywords": ["{{PREFIX}}", "{{GROUP}}", "agent-skills"],
  "skills": "./skills/"
}
```

### `plugins/{{PLUGIN}}/README.md`, `LICENSE`, `.gitignore`
- `README.md`: what the plugin is, primary audience, per-harness install (Claude Code CLI, Cowork, Cursor), a Skills table (Skill | What it does) starting with the router skill, a "how it works" note (incl. that shared references are **vendored byte-identical** into each skill), requirements, and the license line. Note Cursor auto-discovers skills from `skills/`.
- `LICENSE`: same license as the repo.
- `.gitignore`: the macOS/editor/secret lines from §10 (so the plugin stays clean if split into its own repo).

---

## 13. Standalone skills (top-level `skills/`) — [PUBLIC]

Public, unprefixed, fully self-contained skills (npx-installable). Each obeys the Portable Skill Contract (§8).

```text
skills/<capability>/
├── SKILL.md            # required — name MUST be the unprefixed folder name
├── README.md           # optional
├── references/         # optional: docs the body points to with backtick paths
├── scripts/            # optional: co-located executables, invoked `python3 scripts/foo.py`
├── templates/          # optional: scaffold files copied into a user workspace
└── fixtures/           # optional: sample / golden data
```

```yaml
---
name: <capability>                  # MUST match the folder name; NO prefix
description: >
  Lead with WHEN it fires — concrete phrases the user would actually type
  ("write a song", "evaluate these lyrics"), product names, file types.
  Then WHAT it does and produces. End with a bidirectional cross-route:
  "Do NOT use for X — use <other-skill> instead."
---

# Skill title

Body: what it does, the step-by-step workflow, required inputs, edge cases, a
quality bar (the #1 failure mode to avoid), and when to escalate. Embody
principles as behavior — do NOT link to docs/ or any repo-relative path.
```

> Standalone skills omit `metadata.owner`/`status` and the brand prefix on purpose — they're brand-neutral portables.

---

## 14. Plugin skills (prefixed) + rich plugin internals

Every plugin must ship **at least one** `SKILL.md` (an empty `skills/` dir adds no value and can warn on validate). Plugin skills are prefixed and may carry `metadata`.

```text
plugins/{{PLUGIN}}/skills/{{PREFIX}}-<capability>/
├── SKILL.md            # required — name MUST match the folder
├── references/         # optional (vendored copies of plugin-root references live here)
├── scripts/            # optional: co-located executables (+ vendored shared scripts)
├── templates/          # optional
├── fixtures/           # optional
└── evals/              # optional: evals.json + cases
```

```yaml
---
name: {{PREFIX}}-<capability>       # MUST match the folder name exactly
description: >
  WHEN it fires (concrete trigger phrases) → WHAT it does/produces →
  bidirectional cross-route "Do NOT use for X — use {{PREFIX}}-<other> instead."
license: {{LICENSE}}                # optional
metadata:
  owner: {{OWNER_EMAIL}}
  status: draft                     # draft | stable | deprecated
  user-invocable: true              # optional — lets the user invoke directly (e.g. a /slash command)
---
```

### Skill body rules (both layers)
- **Real skills do agent work** (API calls, file generation, lookups, multi-step coordination). A runbook the agent just reads back to a human stays an SOP doc, not a skill.
- **Self-contained** (§8): copy the SKILL.md folder into a fresh location — it must still work. No links to `docs/`, plugin-root files, or repo-relative paths; vendor what you need.
- **General-user path is the default;** any enterprise dependency (an MCP, SharePoint/M365, an org directory) is the optional, flagged branch.
- **Secrets:** never inline keys/tokens/PII; reference a secrets manager / env var by name; document the env var a script reads. Provide `scripts/.env.example` if a script needs config.
- **`status` starts `draft`,** promote to `stable` after one successful end-to-end run.
- **Markdown hygiene:** language-tag every code fence (use ```text for plain command/spec blocks); spaced table pipes (`| --- |`) so files pass markdownlint.

### Optional plugin assets
- `agents/<name>.md` — subagents (focused reviewers/analysts the skills can dispatch).
- `hooks/hooks.json` (+ scripts) — event automation. Hooks JSON **may** use `${CLAUDE_PLUGIN_ROOT}` (it expands in JSON on Claude Code) — a SKILL.md body never may (§8 rule 2).
- `evals/` — scenarios that assert the skill fires and produces correctly.
- `fixtures/` — golden inputs/outputs and demo data (vendor demo dirs via `vendored.json`).
- `requirements.txt` — if scripts need third-party Python.

---

## 15. `docs/` — optional build-time skill-craft reference (NOT shipped to users)

*(Recoup folds this "why/craft" guidance into `AGENTS.md`/`CLAUDE.md` instead of a separate `docs/` tree. Include `docs/` only if the maintainer wants a dedicated craft layer.)*

If you create it, it never ships with an install, so **never link a SKILL.md back to it** — embody the content as runtime behavior. Pages: `docs/README.md` (index + "a skill ships, these docs don't"), `docs/principles.md` (name for what it does; assess through doing; ship real work; audit before suggesting; wall avoidance/reroute; optimize useful-context-per-token; embody don't reference), `docs/anti-patterns.md` (twenty-question intake quiz; connector dead end; enterprise assumptions in general-user skills; behavioral triggers as descriptions), `docs/patterns.md` (thin harness → fat skills → fat data; single entry question; raw → synthesized; skillify loop; status skill; personal-OS folder), `docs/writing-skills.md` (the skim test; load-bearing description; single vs multi-skill; quality bar; routing health; secrets discipline). Replace example skill names with `{{PREFIX}}-…` / unprefixed forms.

---

## 16. Root docs

### `AGENTS.md` — the authoritative ops/rules layer (most important governance file)
Persistent instructions any agent loads when working on the repo. Must contain, in full:
- **[PRIVATE: put FIRST] Shipping changes safely:** `main` is production. Two hard rules — (1) never push to `main`; every change lands via a reviewed PR; (2) always start from latest production (`git checkout main && git pull origin main`) before branching. Then the copy-pasteable non-engineer workflow: branch → change → `git add -A && git commit` → `git push -u origin <branch>` → **open the PR yourself** with `gh pr create` (don't just hand a link; don't merge). Include the pre-start safety check and "when in doubt, stop and ask." Releasing (version bump + merge) is a maintainer task.
- **Repository purpose + structure:** the dual-distribution model (standalone `skills/` + `plugins/`), the repo-as-plugin, both ASCII trees.
- **Glossary:** skill, plugin, harness, marketplace registry, canonical/vendored, router skill.
- **How skills load:** progressive disclosure (frontmatter always in context → SKILL.md body when relevant → linked files on-demand); the description is the trigger.
- **Rules:** read before you act; respect boundaries (self-contained); design for composability; keep it simple; one skill one job; no secrets.
- **Skill format + frontmatter** for both layers (unprefixed standalone vs prefixed plugin); how to write the description.
- **Plugins guidance:** author a plugin by copying an existing one; ship all three manifests; promote standalone skills into a plugin when they share a canonical reference.
- **The marketplace registry:** the two catalogs that must stay in **content parity** (edit one, edit the other); author-email parity across layers; the Codex `policy` enums (§6a).
- **Naming & branding:** reproduce §3 in full; preserve history on renames with `git mv` then update frontmatter/cross-refs/README tables/`vendored.json`.
- **The Portable Skill Contract:** reproduce §8 in full (the five rules + the "why").
- **Versioning:** reproduce §4 (default Model A; note Model B for synchronized private repos).
- **Validation gates:** the three Python scripts + "all must exit 0"; the vendored-file edit recipe (§8a).
- **Plugins table + "where does this skill go?" table:** keep updated whenever a plugin/skill is added.
- **When to ask before acting:** *act without asking* (add/edit a skill, fix typos, update a catalog table, open a draft PR); *ask first* (create/rename/delete a plugin, modify CODEOWNERS or a marketplace.json structurally, push to `main`, touch CI); *never without direction* (repo visibility/settings, branch protection, push secrets, mirrors/forks).
- **Three-layer update model + anti-patterns** (team-specific skills in essentials; renaming when relabeling would do; updating one manifest/catalog and forgetting the other; vague descriptions; hand-editing a vendored copy; `git rm`-ing a plugin to clean up — deprecate instead; pushing to `main` without a PR).
- **References + "when unsure, ask"** closing note.

### `CLAUDE.md`
Identical content to `AGENTS.md` (recoup ships them identical), or a one-line `@AGENTS.md` import / a `ln -s AGENTS.md CLAUDE.md` symlink if the platform supports it. **Avoid a plain copy that silently drifts.**

### `README.md` — human-facing intro + install
- One-paragraph description (same content across Claude Code, Cowork, Codex, Cursor; link the spec).
- **[PUBLIC] Standalone Skills table:** Skill | What it does (linking each `skills/<name>`).
- **Plugins table:** Plugin | What it does (linking each `plugins/<name>`).
- **[PUBLIC] Install — standalone:** `npx skills add {{GH_ORG}}/{{GH_REPO}}` (note this also installs third-party skills into the same `.agents/skills/` location).
- **Install — Claude Code:** `/plugin marketplace add {{GH_ORG}}/{{GH_REPO}}` then `/plugin install {{PLUGIN}}@{{MARKETPLACE}}`. Lowercase-org caveat (macOS case-collision rename bug with mixed-case org names).
- **Install — Cursor / Cowork:** marketplace add / enterprise admin push.
- **[PRIVATE]** the auto-prompt flow driven by `.claude/settings.json`; private-repo token note (`export GITHUB_TOKEN=…` repo scope; `gh auth login` for manual installs); enterprise admin connects Cowork to `marketplace.json` and pushes to groups.
- **Creating a skill** TL;DR + a pointer to `contributing.md`.
- **[PUBLIC] About** section (website, app, support email).

### `contributing.md`
- How to add a skill (mkdir under `skills/` or a plugin, frontmatter, body under ~5,000 words, open a PR).
- Skill guidelines (one job; self-contained; description is the trigger; real instructions; no secrets).
- **Portability checklist (required — runs in CI):** the five Portable Skill Contract checks + "run the three gates locally before pushing."
- Pointer to the Portable Skill Contract in `AGENTS.md`.
- **[PRIVATE]** add the three contribution paths by technical level (Cowork Skills UI → maintainer migrates; github.com pencil-edit → Propose changes; clone + branch + PR) and the CODEOWNERS review flow.

### `RUNBOOKS.md` *(optional [PUBLIC]; recommended [PRIVATE])*
Step-by-step: add a skill (standalone or to a plugin); create a new plugin (three manifests + both catalogs + README/LICENSE + CODEOWNERS line + tables); rename a plugin (`git mv`, update manifests + both catalogs + docs + cross-refs + `vendored.json` + user uninstall/reinstall note — no auto-migration); migrate a skill between layers/plugins (`git mv`, update tables + `vendored.json`); deprecate a skill (`metadata.status: deprecated` + dated note, keep one release cycle); edit a vendored file (the re-sync recipe); cut a release (bump the changed plugin's version everywhere, merge, notify with update commands); roll back (revert + bump forward); useful commands.

### `.claude/settings.json` *(PRIVATE only)*
```json
{
  "extraKnownMarketplaces": {
    "{{MARKETPLACE}}": { "source": { "source": "github", "repo": "{{GH_ORG}}/{{GH_REPO}}" } }
  },
  "enabledPlugins": { "{{PREFIX}}-essentials@{{MARKETPLACE}}": true }
}
```
(Per-machine overrides live in `.claude/settings.local.json`, gitignored.)

---

## 17. Pre-flight checklist (run before declaring done)

- [ ] **All three validation gates exit 0:** `python3 scripts/portability_lint.py && python3 scripts/check_vendored.py && python3 scripts/validate_manifests.py`.
- [ ] Both catalogs exist and list **every** plugin (incl. the `{{PREFIX}}-skills` repo-as-plugin if shipped), with an explicit `version` per entry (Model A).
- [ ] Dual-manifest parity on `(name, source, version)` for every plugin.
- [ ] Every plugin has all three manifests; `version` identical across the three manifests **and** both catalog entries.
- [ ] Cursor manifest has **no** `interface` block; Codex manifest + repo-root Codex manifest carry `"skills": "./skills/"`.
- [ ] Every `.agents` Codex entry has `policy.installation` (valid enum), `policy.authentication`, and `category`. **[PRIVATE]** essentials = `INSTALLED_BY_DEFAULT`.
- [ ] **[PUBLIC]** root `.claude-plugin/plugin.json` + `.codex-plugin/plugin.json` exist and ship the top-level `skills/`; standalone skills are **unprefixed**.
- [ ] Plugin skills are **prefixed**; every `SKILL.md` `name` matches its folder exactly.
- [ ] Every `SKILL.md` description leads with trigger phrases and has a bidirectional cross-route clause.
- [ ] **Portable Skill Contract holds:** no `$CLAUDE_*` in any SKILL.md body; no `../`/cross-skill refs; backtick paths not markdown links; scripts co-located; shared files vendored + registered.
- [ ] No SKILL.md links to `docs/` or any repo-relative path.
- [ ] `AGENTS.md`/`CLAUDE.md` + `README.md` tables list all plugins (and standalone skills).
- [ ] `LICENSE` matches the track; `.github/workflows/validate.yml` exists. **[PRIVATE]** `.claude/settings.json`, CODEOWNERS, PR template.
- [ ] No secrets anywhere: `grep -rniE 'api_key|bearer|secret|password|token' plugins/ skills/ scripts/ .github/`.
- [ ] No tracked `.DS_Store`; all JSON parses.
- [ ] Author email matches `{{OWNER_EMAIL}}` across every manifest, both catalogs, and `metadata.owner`.
- [ ] No `[TODO: …]` placeholders left in any manifest.
- [ ] Final confirmation with the maintainer on derived names (marketplace, plugin identifiers, display labels) before any push.

---

## 18. Local-dev updates + Codex install/share handoff

### Iterating on a local plugin (cachebuster + reinstall)
While developing an installed local plugin, content changes won't reach a running session until the plugin's update cache key changes. Don't hand-edit `marketplace.json` for this — bump the cachebuster, then reinstall:

```bash
# Bumps the plugin's cachebuster so the next install pulls fresh content.
python3 scripts/update_plugin_cachebuster.py <plugin-path>
```

Then have the user reinstall the plugin (and, for a non-default marketplace, `codex plugin marketplace add <repo-or-path>` first). New threads pick up the change after reinstall. For the standalone layer, users re-run `npx skills add {{GH_ORG}}/{{GH_REPO}}`.

### Codex app handoff (when a marketplace-backed plugin was created/updated)
End the final user-facing response with a short handoff. Say `To view this in the Codex app:` then write **Markdown links** (not raw URLs or code spans):
- `View <normalized plugin name>` → `codex://plugins/<normalized plugin name>?marketplacePath=<absolute marketplace.json path>`
- `Share <normalized plugin name>` → same URL with `&mode=share`

URL-encode the path segment/query value. Do **not** add `pluginName` or `hostId` params (Codex derives them). Omit these links entirely when no marketplace entry was created or updated.

---

## 19. Public vs private knobs (one-glance summary)

| Knob | Public / open (default) | Private / team-admin |
|---|---|---|
| `LICENSE` | open (`Apache-2.0` / `MIT`) | `Proprietary` |
| Top-level `skills/` layer | **yes** (npx-installable, unprefixed) | optional / often dropped (plugins only) |
| `npx skills add` distribution | yes | n/a |
| Repo-as-plugin (`{{PREFIX}}-skills`, `source: "."`) | yes | only if shipping the skills layer |
| `{{PREFIX}}-essentials` auto-install plugin | no | **yes** |
| Codex `policy.installation` default | `AVAILABLE` | essentials `INSTALLED_BY_DEFAULT`, rest `AVAILABLE` |
| `.claude/settings.json` (auto-add + auto-install) | no | **yes** |
| `.github/CODEOWNERS` + PR template | optional | **recommended** |
| README install | public + npx + marketplace add | enterprise admin + token note |
| `AGENTS.md` "Shipping changes safely" first | optional | **yes, first section** |
| `docs/` craft layer | fold into AGENTS.md (optional) | optional |
| Catalog `source` | relative string (`"."`, `"./plugins/x"`) | relative string, or `git-subdir` HTTPS if Cowork-strict |

Everything else — naming, the Portable Skill Contract, vendoring, per-plugin versioning, the two-catalog parity, the three Python gates, the Codex `policy`/deeplink/cachebuster mechanics — is **identical** in both tracks.

---

## 20. When unsure, ask

If a request is ambiguous, clarify before acting: *"You're asking me to X. I'd interpret that as Y, which would create/change Z. Proceed, or did you mean something different?"* Scaffolding files in a fresh repo is safe to do autonomously; creating a NEW plugin beyond the departments given, renaming identifiers, editing a vendored copy by hand, writing a marketplace file Codex needs approval for, or pushing to `main` are not — confirm first.
