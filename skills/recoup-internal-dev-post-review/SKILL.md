---
name: recoup-internal-dev-post-review
description: >-
  Recoup staff only. With the explicit recoup-internal keyword, draft, post, or
  update a Recoup project delivery or review summary in Slack #code-review. Use
  for "post this to Slack code review", "summarize what shipped for the team",
  or "update the existing Slack review post". Use a different workflow for
  technical PR review, GitHub delivery, or the Vercel Board.
---

# Recoup code review posts

Write one Slack post per goal or meaningful milestone so a teammate can understand
what changed and what to review or try. Use GitHub for routine PR, CI, and work-in-progress history.

## Gather the facts

1. Read the work item, related PRs, and any existing summary in Recoup Slack `#code-review`.
2. Verify which PRs merged, what was deployed, and what was tested. Name the client or account role in a test when it matters. Keep any unverified rollout or acceptance visible.
3. Consolidate related work across repositories under the same goal. Post when the team has a useful result, an actionable review request, or a decision to make.

## Write the post

- **Goal:** Name the epic or the concrete capability this work implements. Link an existing epic or authoritative documentation when it helps explain the capability.
- **Previous:** Describe the setup or behavior this work changes. Use this baseline even when posting after delivery.
- **Expected:** Describe what someone should be able to do after the change. Where it helps, say what the user provides, what the system does, and what the user gets back. Keep the explanation in one short paragraph.

Use a bold label and its text on the same line. Leave a blank line between
Goal, Previous, and Expected. Use plain sentences and skip em dashes. Follow
with compact bullets for the material changes and verification. Link PR labels
as `repo#123` and strike through the linked label after verifying the PR merged.
Leave an open PR label unstruck. Describe deployment and firsthand verification
in the bullet text. Avoid counting a merge, a deploy, and a user test as the same event.

End with **Next for [person]:** when someone has a concrete review, decision,
or acceptance check. Say where to do it, what to try, and what success looks like.
See `references/example.md` for the Skills over MCP delivery post.

## Post or maintain the summary

Verify the destination is Recoup Slack `#code-review`. Draft when asked for a
draft. Send or edit only when the user authorizes that action. Prefer a narrow
edit to the existing summary when it was created by you or specifically designated
for editing. Preserve the author's wording and unrelated content. Start a top-level
post for a new outcome, and use a thread for substantive follow-up on an existing
outcome. Check for an existing post before sending or retrying.

Use Slack's supported link and strikethrough formatting. Include only facts and
artifacts appropriate for the channel. Verify the posted or edited text, links,
and spacing in Slack and return the message permalink. When Slack delivery is
unavailable, give the user the draft and identify the blocker.
