---
name: recoup-internal-consulting-product-engine
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Turn verified user-facing releases and merged PRs into cited product-update signals and draft article, LinkedIn, and email bundles. Use for announcing shipped product work; never infer deployment or adoption from a merge alone."
---

# Consulting Product Engine

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

Turn verified product changes into cited draft content. Calls feed the insight side of the
flywheel; this skill feeds it from product releases. Keep the existing signal and idea-bundle layout.

## Inputs and source setup

Read the selected workspace's `integrations/github/AGENTS.md` or the user's explicit repository list.
Use its GitHub connector or CLI to read those repositories. Public repositories may allow anonymous
reads; private ones require the connected account's access. Never default to the plugin author's org.
A local `integrations/github/_work/pull_prs.py` is optional: inspect its configuration and `--help`
before using it. Missing access means an incomplete source, not an empty release history.

Use the workspace's `LAST_SYNCED` checkpoint only after the corresponding records are processed.
A merged PR is evidence of a code change. Verify deployment or release availability separately
before claiming users can use it, and obtain usage evidence before claiming adoption.

## Extract

1. Read merged PRs and release notes since the last successful checkpoint, scoped to configured repos.
2. Prefer explicit user-facing release labels. Otherwise inspect the change: a `feat:` title is a
   candidate, not proof; a `fix:` can matter to users. Exclude changes that have no user-visible effect.
3. Cluster related PRs into one feature. Record PR URLs and commit IDs with the claimed behavior.
4. Write one `product-update` signal per feature into `signals/`, with source, status, and verified
   availability. Avoid duplicating a signal already recorded for those source IDs.

## Draft

Read a fresh, verified signal and the workspace's audience/offer inputs. Stage a bundle at
`content/03-drafts/<date>-<feature-slug>/` containing:

- `meta.yml`: source references, date, engine: B, formats, draft states, and review results.
- `article.md`: the concrete problem, what changed, evidence, and a useful lesson.
- `linkedin.md`: one clear product outcome with a supported demo or example.
- `email.md`: an outcome-led subject, the new capability, a short verified demonstration, and one
  relevant product link. Use the actual sender's sign-off.
- `images/`: optional article/feature visuals via the installed graphics or illustration skills.
- `video/`: optional walkthrough via the installed video skill or an existing screen capture.

The workspace may provide an email template. If it does not, use the shape above rather than
searching another private repository for past sends. This skill owns the feature announcement;
`recoup-internal-consulting-email-atomizer` can reuse its source for other formats when requested.

Run `recoup-internal-consulting-copy-reviewer` then `recoup-internal-consulting-copy-editor` on each audience-facing format. Record
what actually ran. Keep customer email and broader social audiences distinct. Staging a bundle is
not sending it; dispatch uses the workspace's recipient policy and requires user authorization.

**Fictional example:** Cedar Lantern Studio releases a way to attach a reference file to an intake
request. A demonstration shows the attachment arriving with the request. That supports announcing
the capability; it does not support claiming revenue growth or hours saved.

## Workflow integration

`recoup-internal-consulting-nightly-ingestion` may run the extract phase when configured for the product repositories.
`recoup-internal-consulting-nightly-content` may draft those signals. These are capabilities, not a claim that a
scheduler is deployed. `products/05-shipped/` may supply additional source evidence; engagement
from an actual announcement can feed the existing product-demand record.
