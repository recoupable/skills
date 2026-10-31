---
name: recoup-internal-consulting-feature-campaign
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal requests to turn verified app features and agent skills into a complete dated LinkedIn campaign: company posts, distinct founder repost takes, copywriting and independent copy editing, Higgsfield thumbnails and caption-independent carousels with exact Recoup typography and logo, and authorized daily scheduling through a requested end date."
---

# Feature-to-LinkedIn campaign

Turn documented product capabilities into a complete, reviewable publication schedule.
Use the selected private business workspace and its AGENTS.md, content policy and DESIGN.md.
Keep drafts, customer evidence and provider receipts there. This public skill contains no account
IDs, private paths, credentials, customer stories or assumed campaign dates.

This skill is self-contained. Writing standards, editorial procedure, graphics guidance and brand
assets ship locally. Other installed capabilities may help; their presence is not a prerequisite.
A skill invocation does not grant publishing or spending authority. Carry forward the user's actual
scope and authorization; an explicit request to write and schedule the campaign does not need a
second approval for each routine post.

## 1. Establish the complete campaign

Record the company and founder identities, intended reader, website CTA destination, start and
inclusive end date, IANA timezone, company posting time and desired founder action. Resolve missing
choices from the existing campaign before asking. Discover actual provider accounts and connection
state. Do not infer an identity from an account number in a historical file.

Expand every calendar day in the requested range before drafting. Daily includes weekends and
holidays unless specified otherwise. Compute each date in its timezone before converting to UTC;
a fixed UTC offset across daylight-saving changes is wrong. Preserve existing slots and provider IDs.
If the user asks to schedule all dates, finish the full range. A first-week sample or rolling queue
is not that result. Provider batch limits change execution size, not scope.

Keep one canonical ledger. Reconcile scheduled, draft, processing and published provider records
across all relevant pages before writes. Match known provider IDs, account, date, exact normalized
copy and media. Preserve unrelated posts. Unknown create outcomes require reconciliation before
retry; never create another item just because the first response timed out.

## 2. Build a source-backed topic plan

Read current public feature documentation, skill instructions and relevant implementation/release
evidence. Record the revision, source locator, actor, input, action, inspectable output and material
limits. Distinguish a documented method, implemented code, deployed capability and verified outcome.
A skill file does not prove every host has its tools or that a customer achieved a result.

Choose one useful job per post. Revisit a feature only through a distinct decision or use case.
Review adjacent topics and openings together. Don't fill dates with generic AI endorsements,
invented founder experience, unsupported savings or duplicate copy with a different noun.

Private evidence can inform a private brief; publish only authorized facts. Apply
`references/public-content-quality.md`, including source/competitor exclusions. Record missing
evidence and change the angle when needed instead of implying a capability exists.

## 3. Write company copy and a distinct founder take

Before drafting, read `references/voice-principles.md`, `references/anti-slop.md`,
`references/human-texture.md`, `references/ogilvy-rules.md` and the social section of
`references/formats.md`. Use `references/persuasion-playbook.md` for audience and positioning;
clarity and the user's conversational tone override pressure tactics.

For this campaign, the rules in this skill take precedence over optional advice in those references:
every company post and every founder take needs its own conversational website CTA. Advice that a
CTA is optional does not apply. Factual, plain language takes precedence over coined concepts,
metaphors or suggestions to add lived experience. Use a personal anecdote only when verified;
otherwise express an honest opinion or conditional decision. Do not invent a story to add texture.

Company pattern, applied flexibly:
- Open with the concrete reader task or decision.
- Name the supplied input, documented action and result someone can inspect.
- Explain one useful detail of the workflow. Preserve material conditions beside the claim.
- Include a practical starting prompt when it helps.
- End with one short, conversational website invitation.

Founder pattern: add an owner decision, review criterion or reason the work matters. Do not merely
repeat the company feature summary in first person. Use genuine opinion or a conditional choice;
never invent a customer conversation, personal result or past use to sound human.

Every company post and every founder take includes the verified website URL. For Recoup campaigns,
use https://recoupable.com unless the user chooses another destination. Invite the reader to get the
relevant free agent skill or book a call about AI transformation services. Choose the ask that fits
the post; no mandatory double CTA, urgency, “comment to unlock” or vague “learn more.” Free describes
the skill itself, not the paid app, AI client, API or third-party usage. Examples:

> You can get the free catalog audit agent skill at https://recoupable.com.

> If you want help figuring out where AI fits in your company, you can book a call with us at https://recoupable.com.

Keep short paragraphs and ordinary words. Rough targets are 100–180 words for company copy and
50–100 for the founder; exceptions can be longer when necessary. Never cut a meaningful condition
to force a word count. No Markdown headings/frontmatter in the actual provider payload.

## 4. Copy edit, then normalize the complete collection

Follow `references/editor-review.md`: dispatch one fresh-context read-only editor with the finished
batch, evidence and local house standards. The editor returns notes; the author implements accepted
changes and records why others were rejected. The reviewer cannot publish or silently change facts.
If independent review is unavailable, perform a separate cold-read pass and label it honestly.

Apply `references/text-normalization.md` after editing. Keep concrete openings and consistent terms
across comparable items without making every sentence identical. Review all company openings, then
all founder takes. Preserve IDs, dates, sources, uncertainty, conditions and distinct topics.

Normalize the exact publishing text: real newlines, stable Unicode, no literal backslash-n, no
accidental metadata, private paths or doubled CTAs. For visual formats, apply the headline-only and caption-hidden checks in
`references/visual-storytelling.md` before approving copy. Check provider length and links. Save the final
payload and hash. Run the bundled checker with actual public files:
`python3 scripts/check_public_copy.py <public-file> ...`.
Scripts ship alongside this skill; resolve paths from its installation. Mechanical checks do not
certify readability or truth. Record the reviewed revision; subsequent edits invalidate affected
reviews and hashes.

## 5. Create the final branded thumbnail

Read `brand/GUIDE.md`, `brand/finals.json`, `references/prompt-kit.md` and
`references/visual-storytelling.md`. Stage the brand with
`node brand/materialize.mjs <output-directory>` using the installed script path. Inspect an actual
approved reference; record whether it was inspected for direction or passed to the generator.

Use the established blog-thumbnail workflow:
1. Write a clear hook that states the feature's job and benefit without needing the caption.
   For an AI/agent feature, name AI or the agent in the headline so a reader understands who
   performs the work. Start around 3–6 words, but use more when clarity needs it; reflow rather
   than hiding the mechanism in small copy or shrinking the type.
2. Reuse suitable approved thumbnail artwork when it exists. When new art is needed, use
   Higgsfield for one text-free, logo-free illustration with room for editable headline and logo.
   Select a currently available image model and supported settings. Preview cost before paid
   submission, state the known estimate, and stay within authorized scope. No credit purchases,
   budget changes or unbounded regeneration loops. Save every returned job ID immediately.
3. Wait for the exact jobs, preserve successes and reconcile unknown outcomes before retries.
   Keep original provider files in ignored dated work storage. Record URL, prompt, model, parameters,
   original hash, selected-art hash and actual billed credits only when returned. Estimates are not
   billing receipts. Missing generation access is a blocker, not permission to call another provider
   “Higgsfield.”
4. Composite the illustration with editable DM Sans text and the exact official Recoup SVG lockup.
   Feature thumbnails include the logo by default; an explicit campaign override wins. Never ask
   the generator to draw the logo. Use the white or ink asset appropriate to the background, preserve
   proportions and clear space, and keep it separate from the headline. Do not repeat a slogan footer.
5. Use a supported feed image size; 1200×630 is the Recoup feature-campaign default. Inspect each
   final export at full size and about 160px wide: readable hook, recognizable illustration, loaded
   font, visible logo, no clipping, overlap or misleading UI imitation. Reflow text before shrinking it.
   A successful render call and a source-art preview do not prove the final cover passed.
6. Keep editable HTML/SVG, selected compact artwork, final WebP, alt text, generation provenance and
   brand.lock.json in the dated bundle. Preserve existing delivery paths. PNG upload exports and
   dependency installs stay in ignored work storage. Some SVG renderers cannot decode embedded WebP;
   use an embedded PNG for composition and visually verify rather than shipping a blank background.

Do not replace distinct illustrations with a repeated card template to finish a large batch. For
precise charts use verified numbers and deterministic geometry, keeping the rest of the campaign's
visual language. Show composed final examples, not only raw generator results.

## 5a. Adapt features into visual stories when requested

Follow `references/visual-storytelling.md` for carousel and thumbnail adaptations. Write the title
sequence first: it must explain the agent, supplied inputs, action, inspectable output/evidence,
human decision and next step without captions or small text. Use the shortest complete story;
these are narrative requirements, not a mandatory six-slide template.

Reuse the existing thumbnail artwork for card 1, cropping and recomposing it on a seamless matching
background. Reuse artwork, not a flattened thumbnail with its old empty text area. Keep its headline
editable and improve it when necessary. For supporting cards, generate simple narrative-specific
Higgsfield scenes when the required art is missing; preserve already suitable scenes. Each card
shows one concept through an action or relationship. Inspect final exports at phone width and run
an independent headline-only/caption-hidden review. A three-second comprehension target is not a
measured result without a reader test.

Export the approved story as a LinkedIn PDF or ordered Instagram images when requested, plus
matching alt text and a transcript. Verify current platform/provider constraints before delivery.
A derivative draft does not authorize another platform, account or publication. Preserve good
scheduled originals and provider IDs; any authorized format replacement needs reconciliation,
exact-payload review and readback. Never create a second original merely to add a carousel.

## 6. Schedule every authorized company slot and verify it

After copy and visual review, reconcile again. Use current connector schemas. With Post Bridge,
discover accounts, upload the final media and create a post with the exact company account, caption,
media ID, non-draft state and explicit future timestamp. Omitting the timestamp can publish now.
Update existing campaign items in place rather than recreating them. A media upload may be reused
only within its actual provider lifetime; do not assume it persists after all using posts publish.

Work in bounded batches. Persist each upload ID, post ID, payload hash, media hash, intended time
and actual response immediately. Read each post back and compare account, full text, media, time
and non-draft scheduled status. An accepted call or draft is not a verified scheduled slot. Respect
rate limits; after an ambiguous mutation, search all relevant pages and match the exact item before
retrying. Never retry the whole batch on a partial failure.

Finish with a complete expected-versus-actual ledger: every requested company date has exactly one
verified scheduled or already-published campaign item. Report exact gaps, duplicates and provider
horizon/permission blockers if any. Do not silently move past dates or burst missed posts into today.
Scheduling is not publication. Keep provider receipts private and move bundles to published only
when their required channels are verified live.

## 7. Handle native founder reposts truthfully

A native “Repost with thoughts” needs the company's published LinkedIn post, the founder identity
and an actually supported repost action. A scheduled provider item ID is not a LinkedIn permalink.
A standalone personal post with similar text is not a repost.

If the provider cannot schedule dependent native reposts, complete the company schedule and save
all reviewed founder takes as pending. Use an existing authorized follow-up automation, or create
one only when requested, to verify each original is live and repost once under the founder identity.
Check native activity before retrying an uncertain action. Save both live URLs and the relationship.
Report this distinction; do not claim personal reposts are scheduled merely because copy is ready.

When a full company schedule exists, change any authorized replenishment automation to reconciliation
and publication/repost verification. It must not recreate already queued dates. Preserve its end date,
notification intent and unrelated engagement/commenting policy unless the user changes them.

## Delivery

Provide the skill or review PR, a complete campaign review artifact, exact date coverage and verified
scheduled count, graphic examples, and any remaining native-repost/provider limits. Preserve the
work in the owning repositories with their normal PR workflow. A public skill contains only reusable
procedures and synthetic examples; real campaign copy, account identifiers and receipts stay private.
