---
name: recoup-internal-consulting-linkedin-publisher
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Prepare, publish, or schedule a LinkedIn post using the selected workspace publishing account and verified provider state. Use for LinkedIn publishing and scheduling requests."
---

# Consulting LinkedIn Publisher

## Required public-content gate

Read `references/public-content-quality.md` before drafting, reviewing, illustrating or publishing.
It governs competitor/source restrictions, plain-language explanations, cover comprehension and
revision evidence. Apply it to every public format; older style examples do not override this gate.

## Visual handoff

When this workflow creates or requests a rendered artifact, use `recoup-internal-consulting-tasteful-design` and
the selected workspace DESIGN.md. House identity is Recoup Sky; explicit client/artist branding wins.
Pass brand/version, expression, format, reference IDs and output folder to the media skill. Its bundled
package supplies exact fonts/logos. Keep new derivatives in the current identity while preserving
historical evidence. Save editable source and brand.lock.json with the deliverable. Ordinary text
outputs stay text; a script is not a rendered video. Existing data dashboards retain their canonical
Recoup CSS during data updates. Do not publish private client work to the public Brand Studio.


**Workspace:** use the selected project and its `AGENTS.md`; keep existing entity folders and
Reality headings. Business paths below are relative to that project. Bundled resources are relative
to this installed skill; sibling capabilities resolve by their installed names. Never search another
private checkout for missing inputs. Use workspace identity, audience, pricing, and `DESIGN.md` fonts.
Local `_work` adapters and `evals` are optional workspace tools, not bundled dependencies. Check
presence and current help first; otherwise use an available connector for the same scoped operation.
If neither exists, report that step incomplete. For missing scorers, perform the stated checks and
label the result manual/unscored; never invent a numeric score or successful provider action.

Publish or schedule authorized content using the selected workspace's publishing account.

1. Read the source draft or signal and the workspace's voice/positioning rules. Shape the caption
   for LinkedIn; preserve the author's meaning and verify claims.
2. Discover the connected accounts through the available publishing connector or the workspace's
   reviewed provider configuration. Match the requested personal or company profile by its displayed
   identity and provider ID. Never use a plugin-embedded account ID or default to its author's account.
   If the intended profile remains ambiguous, resolve it before creating an external post.
3. Default to a local draft. If a publishing connector is available, use its supported draft,
   schedule, or publish action within the user's authorization. An authorized publish request does
   not need a second approval invented by this skill.
4. A workspace may supply `integrations/linkedin/_work/publish.py`. It is an optional local adapter,
   not part of this plugin. Inspect its current help and account mapping before use; do not assume
   arbitrary account IDs are accepted by its `--account` option. If no connector or compatible
   adapter exists, leave the caption/media ready and identify the missing publishing connection.
5. Attach media in a format the selected provider supports. Convert animation to MP4 when necessary;
   use an available media tool or the workspace's reviewed loop helper. Check document/carousel support
   against the provider's current capabilities. Keep original source assets.
6. Record the provider receipt, account, timestamp, URL, and actual state. Scheduled is not published;
   draft is not scheduled. Move a source to `content/04-published/` only after publication is verified.
7. Save the verified post URL for `recoup-internal-consulting-linkedin-audience` to inspect engagement later.

Credentials belong in the user's connector or selected workspace environment, never in this skill
or a chat message. Do not publish, send, or schedule without authorization for that action.

## Mechanical public-copy preflight

The checker ships alongside this skill. Run `python3 scripts/check_public_copy.py <public-file> ...`
on each public format and cover source, using actual workspace paths. Optionally pass
`--policy <workspace-policy.json>` with an `excluded_public_names` list. Fix blocking references
and private source paths before delivery. Missing input files fail the run. This checker cannot
verify factual accuracy, attribution, reader comprehension or raster text; perform the manual gate
and inspect exported images separately. Do not pass internal briefs or manifests as public copy.
