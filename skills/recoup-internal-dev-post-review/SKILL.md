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

## Draft and revise before showing the post

Run these passes yourself, then return or post the polished version. Use the
conversation as a starting point and check delivery claims against the work item
and PRs. Keep draft iterations private unless the user asks to see them.

1. **Draft from the facts.** Write a plain account of the change, the old setup,
   what shipped, what was verified, and who needs to act. Preserve details that
   determine whether the rollout is ready.
2. **Find the product capability.** Move the goal one level above the patch,
   connector, or client used in the conversation. Ask what common capability was
   added and whether the goal still makes sense in another supported client.
   Keep the specific system or feature that makes the goal recognizable. If the
   goal could describe many unrelated projects, bring it back down a level. Keep
   client-specific evidence in the delivery bullets.
3. **Rewrite the change from the user's side.** Make Previous the actual setup,
   including any extra step the change removes. Make Expected describe the user
   action, the system behavior that matters, and the result. Preserve real access
   boundaries. Put implementation details and verification in the bullets so the
   opening can stay short. Give a teammate enough detail to check the result.
4. **Make the handoff runnable.** Read the next step as the recipient. Remove
   assumptions about their client, setup, or habits. Name a particular client
   only when the check requires it. Include the setup, the action, the observable
   success condition and any follow-on step that depends on success.
5. **Capture one useful screenshot.** Show the actual result when possible. For
   a UI change, capture the changed screen. For code or infrastructure, capture
   the relevant diff, verified output, or the official docs section that explains
   the capability. Choose a screenshot that helps the reader understand or check
   the post. See the screenshot guidance below.
6. **Polish and read back.** Link unfamiliar capabilities to official docs or
   the owning work item. Verify links and PR states. Check the Slack spacing and
   remove repetition. Read the post once as a teammate who has not seen the chat.
   Revise any line that makes them guess what changed, what is proven, or what to
   do. Ask the user only for a missing fact or decision that changes the outcome,
   audience, or authorized action.

## Use the Slack format

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
See `references/example.md` for the revision history and final Skills over MCP post.

## Include the screenshot

Capture the real screen with an available screenshot tool and inspect the image.
Crop to the relevant area and check that the text is readable. Omit credentials,
customer data, and material the channel cannot access. Use a short caption that
identifies what readers are seeing and, for a product result, its environment
when relevant. A screenshot of docs explains the capability. Use a delivery
bullet for any separate verification claim.

Include the image with the draft when possible. For an authorized post, attach
it to the same Slack message using the available upload surface. Verify the
attachment after sending. If capture or upload is unavailable, use the relevant
source link and keep the written update. If text is already posted, preserve the
existing message and report any attachment failure without posting it again.

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
