# Outreach quality and draft approval

This gate applies to every email initiated by the sales workflow: warm or cold,
first contact or reply, follow-up, report delivery, test, apology, or correction.
It applies to Resend, Gmail, the Recoup API, scripts, subagents, and jobs that would
send an email indirectly. Existing customer schedules are not permission to add
sales messages or trigger extra sends.

## Prepare something worth reviewing

Before presenting the draft, answer these questions in the private review packet:

- **Why this person, now?** Name their current objective or request and the source.
  Billing status or an upcoming renewal alone is not a useful reason to email.
  Distinguish an active subscription from an active conversation or product use.
- **What is the current conversation?** Read the latest human correspondence and
  open promises, including who owns the relationship. Do not restart a stale idea,
  ask a question already answered, or use a product delivery receipt as a substitute
  for the thread. If you cannot retrieve the thread, tell the user what is missing
  before asking them to approve a draft that depends on it.
- **What does the recipient get?** Deliver a useful finding, completed work, or a
  direct answer to a current question. Explain its relevance. "I reviewed your
  account" followed by "which artist should we focus on?" asks the customer to do
  our planning. "Your reports arrived; want another post?" adds a new offer without
  establishing that it serves the current conversation. Rewrite or defer these.
- **What are we committing to?** List any new work, deadline, price, or account
  change implied by the draft. Finish owed work where authorized and feasible
  before making another offer. Do not invent a commitment just to fill a quota.
- **Is the ask earned?** Give one clear next step grounded in the evidence. A
  generic product link or polished prose cannot replace relevance. Check claims,
  recipient access to linked resources, and the actual attachments. Complete the
  house-style/unslop pass before the user reviews the final version.

If those answers are weak, improve the draft or explain why the contact is deferred.
A quota is a planning target, not a reason to lower the quality or approval bar.

## Present the exact email

Save a versioned draft in the private lead workspace and show the user:

1. Draft identifier/version and the complete To, CC, and BCC lists, including empty
   lists; sender and Reply-To addresses.
2. Exact subject and body, including links, signature/footer, and any tracking or
   unsubscribe elements the sender adds. Include a rendered HTML preview when
   sending HTML, alongside its plain-text version.
3. Every attachment, with a link to inspect the actual file and its final filename.
4. The reason for this contact, new commitments, and unresolved context from the
   quality review above, kept separate from the customer-facing copy.

Ask for approval to send that version only after the packet is complete. A batch
is reviewable only when every email is present with its own identifier and version.
Do not substitute a list of recipients/subjects or a summary for the actual drafts.

## Approval states

`DRAFT → AWAITING_APPROVAL → APPROVED → SENT`

- **Only the user's explicit approval to send the shown version** advances it to
  APPROVED. Record their exact approval text, message reference or timestamp, and
  the draft version it covers beside the draft. A self-written `approved: true`,
  CRM note, task, or subagent report is not evidence of user approval.
- "Be my CSO," "contact five customers," "send ten emails today," and "run the
  workflow" do not approve drafts that have not been shown. Neither do silence,
  elapsed time, an automatic goal continuation, available credentials, or an
  approval for a different contact or earlier campaign.
- "Send draft A v2" approves A v2 only. "Send all eight drafts shown above" can
  approve those eight unchanged versions. If the scope is ambiguous, clarify it
  while continuing safe preparation; do not send a guessed subset or replacement.
- Feedback such as "shorten it and send" produces a new draft for review. Any
  change to recipients, sender, Reply-To, subject, body, links, footer, or attachment
  contents, filename, or other reviewed properties invalidates the previous approval.
  Re-present the final version.
- While awaiting approval, do research and prepare deliverables/drafts. Do not
  enqueue, schedule, or call a send-capable workflow that could email anyone later.
  Do not mark a lead contacted, complete a delivery task, or claim the quota met.
  State the exact blocker: the user has not approved the remaining drafts.

## Immediately before sending

Read the user's approval evidence and compare the complete outgoing payload with
the reviewed version. Do not rely on a status flag alone. Verify every recipient
explicitly; never let a tool default a missing recipient or silently add CC/BCC.
An approved batch may contain no unapproved drafts. If the draft, approval evidence,
or match is missing, **stop before the send call** and return to review.

Use one stable idempotency key for the approved send. If the provider times out,
inspect the provider status before retrying; an unknown result is not a failed send
and does not authorize a fresh send with a new key. Once sent, retrieve the actual
message, verify it against the approved version, and record the provider ID and
delivery status separately. Record approval evidence in the Attio sent note too.
Approval of one message never approves a subsequent nudge or reply.

If an unapproved message was sent, stop further sends, tell the user exactly what
went out and to whom, and preserve the sent copy. Prepare any proposed correction
for review. Do not compound the incident with an unapproved apology email.

This is an instruction and audit boundary. It is not a claim that Markdown can
technically restrict every email API. Send helpers must check this evidence, and
must never create their own approval or bypass the gate with another tool.
