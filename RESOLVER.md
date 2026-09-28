# RESOLVER — Recoup Skills dispatcher (domain-grouped)

> The plugin's routing table for every skill in `skills/`. Capability and platform
> skills are named `recoup-[domain]-[verb]-[noun]`; internal staff skills are named
> `recoup-internal-[domain]-[verb]-[noun]` and are gated behind the `recoup-internal`
> keyword (Tier 3). The domain prefix tells you the room, the verb+noun tail tells
> you the job.
>
> **Read the matched skill's `SKILL.md` before acting.** Verified by
> `scripts/check_resolvable.py` (every skill has a route; every route resolves) and
> `scripts/run_resolver_eval.py` (routing fixtures + full coverage).

## Tier 1 — Capabilities (the label work)

### roster — your artists
| Intent | Skill |
|---|---|
| onboard / add / create **one** new artist, "set up [artist]", new signing | `recoup-roster-add-artist` |
| bootstrap an **empty** org's whole roster (no artists yet) — bulk-onboard a list via parallel subagents | `recoup-roster-onboard` |
| "what artists do I have", list my roster, what's in this sandbox | `recoup-roster-list-artists` |
| organize / update one artist's files, brand, or context | `recoup-roster-manage-artist` |

### research — intelligence
| Intent | Skill |
|---|---|
| research [artist], overview, audience/markets, compare artists, collaborators, which songs on TikTok | `recoup-research-artist-overview` |
| find emerging/unsigned artists, A&R scouting, why a song went viral | `recoup-research-find-talent` |
| which playlists to target, placement gaps, editorial vs algorithmic | `recoup-research-playlist-targets` |
| find managers/A&R/press + draft outreach | `recoup-research-find-contacts` |
| weekly brief, what changed this week, are streams spiking | `recoup-research-weekly-brief` |
| search the web, deep research, enrich any company/label/venue/person | `recoup-research-the-web` |

### song — single-song audio
| Intent | Skill |
|---|---|
| create an original song / track through Recoup; approve idea, genre, lyrics/prompt and generation | `recoup-song` |
| MiniMax Music 3 model-specific caption, lyric timing, genre coverage or past-generation guidance | `recoup-minimax-music-3` |
| analyze a song's audio: BPM/key/genre/mood, lyrics, mix critique | `recoup-song-analyze-audio` |
| find the hook, best 5–15s to clip | `recoup-song-find-hook` |
| playlist pitch + sync brief from the audio | `recoup-song-placement-pitch` |

### content — assets
| Intent | Skill |
|---|---|
| write a caption in the artist's voice | `recoup-content-write-caption` |
| cover art / thumbnail / carousel / promo / quote card | `recoup-content-make-graphics` |
| narrative music video from an approved song, or create the song first (Small Room workflow) | `recoup-music-video` |
| short video / lyric video / visualizer / reformat for platforms | `recoup-content-make-video` |
| a whole content pack (15–30 assets) for one song | `recoup-content-asset-pack` |
| react to a milestone/trend, make something timely | `recoup-content-reactive-post` |

### release — release workflow
| Intent | Skill |
|---|---|
| plan/run a release, creative brief, rollout schedule, RELEASE.md/DSP pitch/one-sheet | `recoup-release-plan-rollout` |
| did the single drop, launch-day alert | `recoup-release-track-drop` |

### catalog — catalog deals
| Intent | Skill |
|---|---|
| review/underwrite a catalog deal, clean a data room, value with files, dashboard, IC memo | `recoup-catalog-review-deal` |
| value a catalog from public data only (no seller files) | `recoup-catalog-estimate-value` |
| measure an artist's NFT/onchain earnings, value an artist who sold music NFTs | `recoup-nft-valuation` |

## Tier 2 — Platform (operate the system; not a label deliverable)
| Intent | Skill |
|---|---|
| first-run "set up / connect Recoup", verify email, get an API key | `recoup-platform-connect-account` |
| "where am I in my Recoup setup" / onboarding status / what should I do next / activation checklist | `recoup-platform-track-onboarding` |
| scaffold my workspace folders / mirror my roster, or build the org's full self-managing "music-company OS" (structure + brain + janitor + plugin, seeded with `artists/` and wired to the API) | `recoup-platform-build-os` |
| call the Recoup API directly, fetch a resource, run a connector (Docs/Gmail/TikTok) | `recoup-platform-api-access` |
| email a report / summary / notification to the account owner or a recipient (send email from a task) | `recoup-platform-email-helper` |
| "remember this" / capture a reusable lesson | `recoup-platform-capture-lesson` |

## Tier 3 — Internal (Recoup staff only · gated by the `recoup-internal` keyword)

> OFF by default. Route here **only** when the request explicitly contains the
> literal keyword `recoup-internal`. Customer and artist requests use the public capability routes.
> Staff consulting requests may prepare client deliverables in an authorized workspace.

| Intent | Skill |
|---|---|
| "recoup-internal" + write/maintain a GitHub tracking issue | `recoup-internal-dev-issue-tracker` |
| "recoup-internal" + implement/ship a tracked issue end-to-end (docs-first, TDD) | `recoup-internal-dev-ship-issue` |
| "recoup-internal" + benchmark/audit/grade a skill pack or plugin | `recoup-internal-eval-skill-benchmark` |
| "recoup-internal" + run the daily sales sweep / who to follow up with (Stripe + Privy + valuations + Attio + credits + tasks + chats) | `recoup-internal-sales` |
| "recoup-internal" + podcast guest outreach: find today's invite list, draft invites or nudges | `recoup-internal-sales` |
| "recoup-internal" + work the Attio catalog-valuation sales funnel | `recoup-internal-funnel-valuation-pipeline` |
| "recoup-internal" + account-health / account-status snapshot for a Recoup account | `recoup-internal-account-health-report` |
| "recoup-internal" + fleet-wide weekly usage review / week in review / business pulse (logins, Stripe, credits, gateway reconciliation, catalogs) | `recoup-internal-weekly-usage-review` |
| "recoup-internal" + audit scheduled-task email health (what tasks emailed, how many empties the guard blocked) over a window | `recoup-internal-task-email-audit` |
| "recoup-internal" + run the day's marketing on one of our own accounts / what should we post today / make today's video (workspace canon + socials scrape + topic pick + build) | `recoup-internal-marketing` |
| "recoup-internal" + draft/ship/measure LinkedIn or X posts | `recoup-internal-social-ship-posts` |
| "recoup-internal" + FaceTime-call style AI video ad (Grok Imagine 1.5 native-speech clips) | `recoup-internal-video-grok-1.5-imagine-facetime` |
| "recoup-internal" + find, win or close Upwork contract work: run the daily pipeline, triage the client, verify claims against repos, draft the proposal + screening answers, pick the sample pack, set the rate, follow up, handle a reply, prep the client call, log the outcome | `recoup-internal-upwork` |

### consulting — staff business workspace

Use these for explicit `recoup-internal` consulting work in the selected authorized business workspace.
They do not authorize access to personal sources, sending, or scheduled ingestion. The existing sales
and marketing skills continue to own their platform-wide sweeps; consulting skills own deal folders,
client delivery and consulting content workflows. Client deliverables may be drafted by staff here.
The internal namespace is a routing convention, not an access-control boundary.

| Intent | Skill |
|---|---|
| recoup-internal consulting: Build or refresh the "Reality" section for a client or lead by traversing every comms channel holistically, then synthesizing — explicitly flagging missing data | `recoup-internal-consulting-account-reality` |
| recoup-internal consulting: Create Recoup editorial article heroes and editable concept diagrams: flow, comparison, cycle, stack, hub and framework | `recoup-internal-consulting-article-illustrator` |
| recoup-internal consulting: The auto-manage orchestrator | `recoup-internal-consulting-call-processor` |
| recoup-internal consulting: Convert delivered work into a case study | `recoup-internal-consulting-case-study-builder` |
| recoup-internal consulting: Stand up a won client in one move | `recoup-internal-consulting-client-onboarding` |
| recoup-internal consulting: Rebuild a client/deal folder from scratch using historical data | `recoup-internal-consulting-client-reconstruct` |
| recoup-internal consulting: Log a single comms event on a deal/client (you sent, they replied, it was opened, you got a message) and reconcile state | `recoup-internal-consulting-comms-logger` |
| recoup-internal consulting: Distribute one finished pillar article across every channel the same way — republish the same copy to the owned blog + LinkedIn newsletter + X (as an article, never a thread), ship the always-on companions (a LinkedIn promo post + an email to the list), point every link at the owned canonical URL, then find the live post and monitor its engagement into leads | `recoup-internal-consulting-content-distribution` |
| recoup-internal consulting: Turn an idea or insight into a publish-ready draft | `recoup-internal-consulting-content-drafter` |
| recoup-internal consulting: Extract reusable content, insights, and knowledge-base entries from a call transcript or meeting note | `recoup-internal-consulting-content-extraction` |
| recoup-internal consulting: Produce test variants of an idea to find what resonates before investing | `recoup-internal-consulting-content-idea-generator` |
| recoup-internal consulting: Squeeze every published winner — repost proven posts with a fresh hook, re-share your own winners with added context, and fan one outlier post into multiple new formats | `recoup-internal-consulting-content-recycler` |
| recoup-internal consulting: Editorial copy-edit pass on a finished draft, run through a fresh-context subagent reviewer | `recoup-internal-consulting-copy-editor` |
| recoup-internal consulting: Reader-reaction review of a finished draft, run through a fresh-context subagent that ROLE-PLAYS the owner's ICP customer (a founder / CEO / C-suite exec of a $5M-$500M creative, music, entertainment, CPG, or marketing company, sometimes a larger construction firm) | `recoup-internal-consulting-copy-reviewer` |
| recoup-internal consulting: Apply when writing any text for or as the user: social posts, emails, newsletters, landing pages, ads, blog posts, video scripts, sales copy, messages, or any published content | `recoup-internal-consulting-copy-writer` |
| recoup-internal consulting: Advance a deal cleanly when its state changes | `recoup-internal-consulting-deal-stage-mover` |
| recoup-internal consulting: Analyze a sales/discovery call transcript to surface stakes, pain points, success metrics, objections, gaps, and buyer qualification | `recoup-internal-consulting-discovery-analysis` |
| recoup-internal consulting: Fan one source insight into several scheduled, segment-routed email touches (trend-jack, proof, insight, build-in-public, 1:1 nudge) staged as drafts, never one-offs | `recoup-internal-consulting-email-atomizer` |
| recoup-internal consulting: Identify land-and-expand opportunities within a client | `recoup-internal-consulting-expansion-spotter` |
| recoup-internal consulting: Capture a recurring answer as a canonical FAQ | `recoup-internal-consulting-faq-builder` |
| recoup-internal consulting: Generate the timed follow-up cadence for a deal, personalized to the client's stated stakes | `recoup-internal-consulting-followup-sequencer` |
| recoup-internal consulting: The weekly content + system review ritual | `recoup-internal-consulting-friday-review` |
| recoup-internal consulting: Produce a finished, post-ready branded VISUAL by compositing a Higgsfield-generated background (photoreal / cinematic / illustrative imagery) with an on-brand HTML text overlay | `recoup-internal-consulting-generative-post` |
| recoup-internal consulting: Generate on-brand social media graphics for any platform and format — feed posts, carousels, stories/reels covers, banners and headers, profile pictures, YouTube thumbnails, Pinterest pins, Open Graph link cards, and ad creative | `recoup-internal-consulting-graphics` |
| recoup-internal consulting: Generate AI media for content by driving the Higgsfield CLI — photoreal or cinematic IMAGES, AI VIDEO / b-roll, branded PRODUCT shots, a face-consistent AI CHARACTER/avatar ("Soul"), and AI VOICEOVERS | `recoup-internal-consulting-higgsfield` |
| recoup-internal consulting: >   The house skill for making any VIDEO — create, edit, animate, or render a video,   animation, or motion graphic: a promo, explainer, captioned clip, reel, lyric   video, title card, lower-third, logo sting, PR/changelog video, or any moving   composition | `recoup-internal-consulting-hyperframes-video` |
| recoup-internal consulting: Turn the inbox into a prioritized "what you owe people" digest across active deals | `recoup-internal-consulting-inbox-triage` |
| recoup-internal consulting: Connect a new external data source or channel to the selected business workspace, define ownership and scope, and verify one authorized read through the workflow. | `recoup-internal-consulting-integration-onboarding` |
| recoup-internal consulting: Stand up a new external-tool integration in one move | `recoup-internal-consulting-integration-scaffolder` |
| recoup-internal consulting: The anti-staleness engine for external integrations | `recoup-internal-consulting-integrations-sync` |
| recoup-internal consulting: Produce an invoice per the selected payment structure | `recoup-internal-consulting-invoice-generator` |
| recoup-internal consulting: Log new frameworks, methodologies, or OSS tools to the IP register | `recoup-internal-consulting-ip-register-updater` |
| recoup-internal consulting: Assemble a grounded context dossier on a lead BEFORE any outreach or personalization, so drafts are accurate and the agent never punts "I need your input" on something it could look up itself | `recoup-internal-consulting-lead-context` |
| recoup-internal consulting: Triage a brand-new inbound lead | `recoup-internal-consulting-lead-intake` |
| recoup-internal consulting: Score a lead's relationship temperature (0-10) and posture from their full communications graph, so follow-ups match where the relationship actually stands | `recoup-internal-consulting-lead-temperature` |
| recoup-internal consulting: Turn LinkedIn engagement into leads | `recoup-internal-consulting-linkedin-audience` |
| recoup-internal consulting: Build a daily LinkedIn comment-target queue — whose posts the owner should comment on to warm ICP prospects, with draft angles in his voice | `recoup-internal-consulting-linkedin-engage` |
| recoup-internal consulting: Architect or audit a LinkedIn profile-as-funnel — turn the profile into a landing page, build the offer ladder (free top → qualifying application bottom), and wire posts into it | `recoup-internal-consulting-linkedin-funnel-architect` |
| recoup-internal consulting: Write or critique the first line of a LinkedIn post (the hook) using patterns reverse-engineered from real top-performing posts | `recoup-internal-consulting-linkedin-hooks` |
| recoup-internal consulting: Structure a high-performing LinkedIn post — pick the archetype and founder format (build log, documented failure, value post, receipt, contrast hook, milestone chapter), write a scroll-stopping hook, shape the body, format for mobile, choose the in-post CTA, and decide whether to pair an infographic | `recoup-internal-consulting-linkedin-post-architect` |
| recoup-internal consulting: Prepare, publish, or schedule a LinkedIn post using the selected workspace publishing account and verified provider state | `recoup-internal-consulting-linkedin-publisher` |
| recoup-internal consulting: Capture niche intelligence and buying signals | `recoup-internal-consulting-market-scanner` |
| recoup-internal consulting: Refresh the practice metrics and dashboard | `recoup-internal-consulting-metrics-updater` |
| recoup-internal consulting: Phase 3 of the nightly pipeline — the demand engine's insight lane (Engine A, article-first) | `recoup-internal-consulting-nightly-content` |
| recoup-internal consulting: The autonomous nightly sweep | `recoup-internal-consulting-nightly-ingestion` |
| recoup-internal consulting: Phase 2 of the nightly pipeline — the workspace reconciler | `recoup-internal-consulting-nightly-janitor` |
| recoup-internal consulting: Turn a raw objection into a tailored response | `recoup-internal-consulting-objection-handler` |
| recoup-internal consulting: The process every personalized outbound email runs through before it is staged — gather full context on the person, decide who it is really for and what the objective is (set by temperature), simulate the reader, and pass the pre-send gate | `recoup-internal-consulting-outbound-email` |
| recoup-internal consulting: Sharpen positioning and messaging | `recoup-internal-consulting-positioning-refiner` |
| recoup-internal consulting: Build three-tier pricing for a deal | `recoup-internal-consulting-pricing-builder` |
| recoup-internal consulting: Turn verified user-facing releases and merged PRs into cited product-update signals and draft article, LinkedIn, and email bundles | `recoup-internal-consulting-product-engine` |
| recoup-internal consulting: Draft a recurring client progress report from primary evidence, review it for the sponsor, and prepare the authorized delivery format | `recoup-internal-consulting-progress-report` |
| recoup-internal consulting: Render approved proposal copy and commercial terms as a branded two-page HTML/PDF document | `recoup-internal-consulting-proposal-designer` |
| recoup-internal consulting: Draft a situational-assessment proposal from a discovery transcript or discovery analysis | `recoup-internal-consulting-proposal-drafting` |
| recoup-internal consulting: Revive cold/dormant prospects from historical meeting data | `recoup-internal-consulting-prospect-resurrection` |
| recoup-internal consulting: Build a Quarterly Value Review for a client — the connective tissue between delivery, renewals, and proof | `recoup-internal-consulting-quarterly-value-review` |
| recoup-internal consulting: Mine the external AI & Agents research wiki for content | `recoup-internal-consulting-research-miner` |
| recoup-internal consulting: Validate and package changes in the explicitly selected plugin repository, then publish only when authorized | `recoup-internal-consulting-skill-packager` |
| recoup-internal consulting: Generate a Statement of Work under the existing MSA | `recoup-internal-consulting-sow-generator` |
| recoup-internal consulting: The writing style for a quick update or recap to an external stakeholder (client sponsor, champion, exec, partner) after a session, milestone, or to flag a blocker plus an ask | `recoup-internal-consulting-stakeholder-update` |
| recoup-internal consulting: Reconcile and health-check the whole workspace | `recoup-internal-consulting-system-auditor` |
| recoup-internal consulting: Apply the current Recoup identity across graphics, video, slides, proposals and interfaces | `recoup-internal-consulting-tasteful-design` |
| recoup-internal consulting: Capture a testimonial and logo rights | `recoup-internal-consulting-testimonial-capture` |

---

## Cross-skill disambiguation (the boundaries that matter)

- **Audio vs data.** From a song's **audio file** (hook, mix, BPM, lyrics, sync
  brief) → the `recoup-song-*` skills. From **research data / the web** (catalog
  playlist strategy, audience, metrics) → the `recoup-research-*` skills.
- **Playlists.** Catalog-wide playlist *strategy* (no audio) →
  `recoup-research-playlist-targets`. A single song's playlist *pitch* from its audio
  → `recoup-song-placement-pitch`.
- **Valuation fork.** With seller files → `recoup-catalog-review-deal`. From public
  data only → `recoup-catalog-estimate-value`. If the artist sold music NFTs, add
  `recoup-nft-valuation` — a streaming-only number understates them, often by an order
  of magnitude.
- **Briefs.** A recurring artist performance brief → `recoup-research-weekly-brief`.
  A pre-release creative brief → `recoup-release-plan-rollout` (brief mode).
- **"Make something for a milestone."** The reactive post →
  `recoup-content-reactive-post`. The underlying milestone *data* →
  `recoup-research-artist-overview`.
- **Roster vs platform.** Add/list/manage artists → the `recoup-roster-*` skills.
  First-run connect/scaffold → `recoup-platform-connect-account` /
  `recoup-platform-build-os`. A raw REST/connector call →
  `recoup-platform-api-access`.
