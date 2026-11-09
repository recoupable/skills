---
name: recoup-internal-consulting-weekly-project-review
description: "Prepare and update a visual weekly project review in a selected private workspace for recoup-internal consulting. Use for a Monday project agenda, weekly project progress, or refreshing a sponsor's project review. Group by project: progress this week, blockers or slowdowns, work for next week, and decisions to discuss."
---

# Weekly project review

Create a brief that people can read together on a call and send as a document. Use the
selected workspace's instructions and existing client records. Keep private client content
there; this skill's examples are fictional.

## Update the review

Start with the previous dated review, the user's latest corrections, recent account activity,
and the relevant owning project records. Keep the existing project order. Review every project,
including secondary work, then give the main projects the most space. Inventory the whole
reporting window before condensing it. If a local checkout stops before the current week,
review current owning-repository PR bodies and release records rather than relying on
old local summaries. Merged code is not proof of a live deployment.

Follow the user's current project relationships when grouping the review. A vendor,
collaborator or supporting experiment belongs under the project it advances, unless
the user treats it as a separate project. Attribute meetings and support to concrete
results or actionable issues; omit vague activity-only cards and invented status checks.

Present each project as a closed disclosure card with three closed sections:

- **Progress this week:** concrete changes in the reporting window, attributed correctly.
- **Blockers:** preserve the distinction between blockers that stop the named work and
  slowdowns that allow other progress. Name the dependency and what would help.
- **Focus:** proposed priorities, work that can continue now, and questions to discuss.
  Use names and dates inside the content when useful; avoid deadline-heavy section titles.

Use native accessible disclosures for both levels. Start all projects and sections closed,
keep each independently operable, and provide a simple way to collapse everything after a
call topic. Keep important Focus and continuing-work text at normal body contrast, not
muted gray. Smaller muted text is for metadata and evidence limits only. Printed exports
can expand all content; the interactive review keeps it progressively disclosed.
Do not infer a whole-project status from individual dependencies. Keep project headers
neutral; blocker/slowdown labels belong beside the specific issues inside Blockers.

Use one point per visible bullet. Do not combine a dependency, an unaffected activity and a
proposed task into one sentence. Keep work that can continue separate from the blocker or
slowdown. Use all substantive supported progress, with no one-sentence or one-item cap.
Do not inflate the amount of work by treating parts of one rollout as separate launches;
briefly identify the shared rollout when listing its useful components.

Use the user's everyday language. Avoid management-field labels such as owner, checkpoint,
next outcome, workstream, velocity and percent complete. A plain sentence such as
"Morgan will show the revised search on Friday" is enough.

Keep dated source pointers in the JSON's `evidence` fields or an internal source note. The
renderer excludes evidence from the audience-facing HTML/PDF. Evidence should distinguish code
released, live behavior checked, access granted, actual usage, and measured results. Missing
evidence stays missing. An old release is background, not new weekly progress. Never infer
completion from an issue title, a drafted message, or a future meeting invitation.

If the review is prepared before the reporting window ends, label it as a draft through the
last checked date. Compare last week's agreed work with what happened; explicitly carry forward
unfinished items. Do not silently replace the original commitment or pretend a date was agreed.

Use the workspace's existing review record when one exists. Otherwise keep one dated JSON review
and a short index in its client delivery folder. Update account activity with actual preparation,
decisions and unresolved facts. Link to implementation issues rather than creating a second backlog.

## Render a visual draft

The scripts ship alongside this skill. Use `fixtures/example.json` for the input shape and
`scripts/render_review.py` for a self-contained HTML review. It supports nested project/section disclosures; there is no backend or browser-side editing. It can be sent as an HTML file.

From the installed skill directory, with explicit input/output paths:

```sh
python3 scripts/render_review.py --input /absolute/private/review.json --output /absolute/private/review.html
```

Optional `--brand-css /absolute/inline-fonts.css` embeds a supplied brand stylesheet. Without it,
the page uses system fonts. Supplied theme CSS is applied after the base layout.
Use an explicitly requested client app design as the baseline and preserve its actual
font, tokens and reading width in the private workspace; do not copy client assets into this skill. No network fonts, analytics, hosted assets or external scripts are used.
The script also supports `--pdf /absolute/private/review.pdf` and `--font /absolute/body.ttf`.
PDF output requires reportlab. An optional `pdf_theme` object in the input can set
`background`, `card`, `text`, `muted`, `line`, `accent`, `warning` and `danger` to six-digit
hex colors. Primary and secondary projects use visible bullets; secondary text fields
accept lists or older single strings. PDF pages give each project its own wide page, keeping continuing work inside Focus. Keep generated assets in the private workspace.

Open the result and inspect a desktop-sized overview, a focused project, a narrow viewport, and
the PDF when generated. Verify readable text, unclipped content, working navigation, all projects
present, and correct draft dates. Present the visual draft to the user so their feedback can improve it.

Keep the first version simple. A shareable document is usually enough to learn whether the review
format works. Consider a shared app or board when people need live edits or task history, preserving
the client's access boundaries. Do not create a database, external account or hosted site just to
produce the weekly review. Sending, publishing and recurring scheduling retain their normal
authorization requirements; creating this skill does not authorize them.
