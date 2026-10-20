# One Recoup customer release

Author customer skills once in `skills/`; `package_files(..., 'customer')` is the
only inventory boundary. It includes every tracked non-internal skill and its
support files and rejects dependencies on excluded internal skills. Stage new
files before local builds. No package maintains a separate allowlist.

Build all artifacts with one version and source commit:

```sh
python3 scripts/build_plugin_packages.py --version 2026.1020.1 --out /tmp/recoup-release --chatgpt-app-id asdk_app_REGISTERED_ID --workspace-name recoup-skills
python3 scripts/validate_release_parity.py --out /tmp/recoup-release
```

The output directory must have no existing `claude/` tree. Builds are deterministic
for the same tracked bytes, source commit, version, app ID and workspace alias.

| Artifact | Shape and intended installation |
| --- | --- |
| `recoup-customer-VERSION.zip` | Public OpenAI submission adapter; Codex manifest and direct remote MCP |
| `recoup-workspace-VERSION.zip` | ChatGPT workspace adapter; Codex manifest plus `.app.json` referencing the existing registered app, with no direct MCP config |
| `recoup-local-VERSION.zip` | One customer plugin root with Claude, Codex and Cursor manifests; direct remote MCP |
| `recoup-buyer-VERSION.zip` | `START HERE.html` plus `recoup-plugin/`, whose contents are exactly the local adapter; no nested install ZIP |
| `recoup-claude-VERSION.zip` and `claude/` | Identical Claude-only customer tree for directory submission and generated `claude-directory` branch |
| `recoup-full-VERSION.zip` | Separate full staff source package; never distribute to customers |

The product identifier is `recoup-plugin`, display name Recoup. The workspace
adapter alone may retain the existing registered package alias (`recoup-skills`)
through `CHATGPT_WORKSPACE_PACKAGE_NAME`. This is intentional host identity
compatibility, not a separate customer skill inventory. Never replace a registered
ChatGPT app ID merely to make names look alike.

Claude/Codex use `.mcp.json` with remote HTTP type. Cursor uses `mcp.json` without
the type key. All point only to `https://api.recoupable.dev/mcp`; tokens are managed
by the host's OAuth flow. Claude directory artwork lives in `branding/` instead of
`assets/`. These adapter differences do not change skill or support-file bytes.
The local adapter includes all three manifests but only one copy of the skills.

## Release manifest consumed by buyer distribution

`release-manifest.json` retains `version`, `commit`, and `packages.customer`
compatibility. It adds:

- `customer_content`: sorted `skills` inventory, `files` mapping each `skills/**`
  path to its SHA-256, and `sha256` of canonical sorted compact JSON of that map.
- `customer_content_sha256`: the same shared digest at the release root.
- `packages.{customer,workspace,local,buyer,claude}`: each has `file`, exact archive
  `sha256`, identical customer `skills` and `customer_content_sha256`.
- `packages.workspace.chatgpt_app_id` and `package_name`: deliberate app linkage
  and optional registered alias.
- `packages.claude.tree`: the generated relative tree (`claude`).

Each customer artifact also contains `RELEASE.json` with `version`, `commit`, and
`customer_content_sha256`. The buyer copy is inside `recoup-plugin/`. LICENSE is
included. Distribution should consume `packages.buyer.file` and `.sha256` directly;
do not overlay Marketing-owned manifests or wrap another version's skill ZIP.

The validator checks archive checksums, exact customer bytes/inventory, all host
manifest versions/identifiers, direct MCP or registered app mapping, wrapper
shape, and Claude tree/archive equality. Publication runs only after verification.

Source/release parity is not store publication parity. GitHub builds and the
`claude-directory` branch do not prove that a provider approved or published that
version. Record the exact uploaded archive checksum and provider review result
separately. Never describe a submitted or approved version without that evidence.
