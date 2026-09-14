---
name: recoup-internal-consulting-linkedin-funnel-architect
description: "INTERNAL — Recoup staff consulting workflow. Use for recoup-internal consulting requests. Architect or audit a LinkedIn profile-as-funnel — turn the profile into a landing page, build the offer ladder (free top → qualifying application bottom), and wire posts into it. Use on \"audit my LinkedIn funnel/profile\", \"turn my profile into a funnel\", \"fix my LinkedIn profile\", \"build my offer ladder\", \"set up a waitlist/application\", \"where are the gaps in my funnel\". Audit mode scores the current setup and lists fixes; build mode gives templates for each piece."
---

# Consulting LinkedIn Funnel Architect

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

Treat the LinkedIn profile as a **landing page**, not a résumé. Every section routes a visitor toward
one of two offers: a free top-of-funnel (newsletter / community waitlist) and a high-ticket bottom
(qualifying application). Posts feed it via soft PS-CTAs. Origin evidence (a real operator's working
funnel, screenshots + teardown): `swipe/funnels/magali-dereu/README.md`.

## The one rule: steal structure, not persona
Adopt the funnel *architecture*; keep the owner's voice (`recoup-internal-consulting-copy-writer`) and substance
(`positioning/` — AI/agents enablement for music & media). Benchmark against the owner's own funnel docs:
`integrations/linkedin/linkedin-funnel-strategy.md` and the selected workspace workflow specification (if available).

## Two modes
- **Audit** — score the current profile/funnel against the checklist below; output a ranked gap list
  with concrete fixes. Start here for "audit my funnel".
- **Build** — produce the actual copy/assets for each missing piece. Use after an audit, or for "build
  my offer ladder / set up the application".

## The profile-as-landing-page checklist
Score each as present / weak / missing, with the fix:
1. **Banner** = the positioning line + proof, not a stock graphic. One outcome sentence ("Turn X into
   Y"), a **logo wall** of recognizable names/clients, and a visual cue (arrow) pointing to Featured.
2. **Headline** = outcome + proof + next step, not a job title. Formula: `[who I help] [achieve Y] |
   [proof/credential] | [→ destination URL]`.
3. **Featured** = the conversion hub. **Two branded "ad" cards** (look like creative, not links): one
   **free** (newsletter/community), one **paid** (work-with-me → application).
4. **Services module** (LinkedIn-native) = service tags + **testimonials from recognizable names** +
   star rating, with the "Request services" path enabled.
5. **About** = a hook-first story (open with failure, not credentials), then what you do + proof + CTA.
6. **Activity** = consistent posting visible (handled by the posting skills).

## The offer ladder
- **Free top (capture email):** a newsletter opt-in and/or a **community waitlist** with availability stated truthfully (use a waitlist only when enrollment is actually closed). Low friction, name + email only.
- **Paid bottom (qualify hard):** a **qualifying application** (Google Form/Typeform), not a "book a
  call" link. Gate by fit + budget so only real prospects reach a call. Fields that work: role,
  revenue band, "done-for-me vs. learn-it", prior-partner experience, and an explicit
  "ready to invest a premium" yes/no. (Use this original field list as a starting schema; adapt it to the actual offer. No external form file is required.)
- **Map it to the owner's offers** in `positioning/offers.md` + `library/productized-offers/` — don't invent
  offers; wire existing ones into the ladder.

## Wire posts into the funnel
The bottom of every applicable post is a **soft PS → a funnel entry** (see
`recoup-internal-consulting-linkedin-post-architect` CTA system). Free top-of-funnel for cold readers; the application
only for warm/high-intent. Keep the ask casual and optional.

## Output
- **Audit:** a short ranked gap report (`present/weak/missing` per checklist item + the fix), saved
  where the user wants it (e.g. alongside `integrations/linkedin/linkedin-funnel-strategy.md`).
- **Build:** the drafted banner line, headline, two Featured cards, About rewrite, and application
  form — each in the owner's voice, ready to paste. Run copy through `recoup-internal-consulting-copy-writer` first.

## Guardrails
Confirm any client/proof claims before they go on the profile (evidence discipline — no invented logo
walls or testimonials). Never publish profile changes automatically; produce the copy for the owner to apply.
