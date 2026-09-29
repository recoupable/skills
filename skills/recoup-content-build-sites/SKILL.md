---
name: recoup-content-build-sites
description: Design and build engaging interactive websites using a curated library of 60 interactive experiences plus 104 visual, motion and game references, including games, creative tools, brand campaigns and digital experiences. Use when creating or improving a fan site, artist experience, brand activation, playable website, interactive microsite, or a Sites concept, creative direction, implementation or review. Helps choose an understandable activity, produce a worthwhile result and carry that interaction through the finished site.
---

# Build a worthwhile interactive site

Create a site people can understand and want to use. Use the reference library to improve judgment about the interaction and its execution, not as a list of templates to imitate.

Paths below are relative to this skill directory. Scripts ship alongside the skill. The host's requested output format, approved concept, tools, capabilities and user instructions take precedence over this default workflow.

## Enter at the right stage

- **Concept:** understand the audience and evidence, inspect relevant references, then propose a concrete activity and payoff.
- **Direction:** preserve the selected activity and specify the content, assets, controls and response needed to deliver it.
- **Build:** preserve the selected concept; use the references to improve craft and implement the actual interaction.
- **Review:** try the experience and compare its behavior with the promised activity and result. Recommend specific repairs.

Do not restart concept selection when asked only to implement or repair an approved direction. Do not rerun source analysis merely to use this skill. Reuse the provided brief and reusable analysis. If the request contains only a URL, use the host's existing context collection capability; do not invent song knowledge or unsupported retrieval tools.

## 1. Establish the intended experience

Identify the audience, situation, real source material, available assets, supported runtime capabilities and any explicit taste decisions. Separate evidence from interpretation and proposed fiction.

State the basic promise in plain language: **“You [action], and you get/see/hear [specific consequence].”** For example: “Draw one continuous line and see how close it is to a circle.” Avoid abstract promises such as “explore your sonic identity” unless the actual interaction immediately makes them concrete.

For song or artist work, identify a supported connection a visitor can recognize without reading the design rationale. The connection can come from a situation, joke, sound, performance, visual world or shared fan knowledge. Cover art may guide appearance without justifying the activity. Do not reduce every song to the same mood quiz.

## 2. Consult references selectively

Read `references/index.md` for the available categories and entries. Read `references/principles.md` for interpretation guidance. Retrieve a small set of relevant entries from `references/library.json`; an initial set of two to four is usually enough. Choose by the visitor's motivation and the interaction, not only by industry or visual style.

When Python is available, use the bundled helper from the skill directory:

```bash
python3 scripts/find_references.py --query drawing --limit 4
python3 scripts/find_references.py --category "Identity & personal output" --limit 4
python3 scripts/find_references.py --ids 17 20 39
```

The helper performs literal lookup, not semantic recommendation. If a query misses, consult the index or another relevant category. Without Python, read the index and the selected entries in the JSON directly. Do not load all 60 full entries by default.

For each reference used, identify:

- The concrete action and result worth studying.
- The part being adapted and why it fits this brief.
- The content, assets or services that make the reference work.
- The part that should not carry over.

The library contains documented behavior and separate design interpretations, not measured engagement rankings. Historical case studies may be the only surviving documentation. Inspect the linked source or experience when browsing is available and the decision depends on its visual or behavioral detail. If it is unavailable, describe the evidence limitation instead of claiming to have played it. Never copy proprietary code or media because a reference is listed here.

## 3. Make the proposal concrete

Produce only as many alternatives as the host requests or the decision needs. Where alternatives are useful, vary the core action rather than producing several skins of one questionnaire.

For each direction, provide a sample first action and its actual response. Include the premise, what the visitor controls, the worthwhile result, the obvious connection to the subject, the reference pattern and the required capabilities. Show real sample content, not just “a personalized reveal” or “an exciting game.”

A good activity can offer skill, creation, curiosity, humor, expression, participation or a well-told story. It need not have points, competition, replay or a download. Equally, a quiz, two buttons or a single tap can work when the specific content and response carry the experience. Judge the instance, not just the format.

If the concept depends on unavailable assets or services, adapt it while preserving the payoff or report the missing capability. Do not promise multiplayer, personal listening history, runtime generation, audio stems, camera recognition or a shared gallery unless the host can actually supply them.

## 4. Build the selected interaction

Read `references/build-and-review.md` and `references/visual-experiences/GUIDE.md`. For the selected direction, read the relevant motion, art or spatial-design chapter and two complementary examples from its 104-entry library. These are craft references, not fixed site templates. Work within the host's project and output contract. Use its available tools to implement, preview and revise the site; this skill does not create tools, runtime permissions or integrations.

Make the primary activity apparent on the first screen. Show enough context to make its purpose clear, then let the visitor act. Give immediate, appropriate feedback. Let the consequence visibly reflect the input; avoid generic results unrelated to the visitor's choices.

Invest in the content and response that make the selected reference work: authored writing, coherent sound, expressive motion, compatible components or interesting discoveries. A themed background is insufficient when the promised interaction depends on those elements.

If the host exposes other relevant skills, load those that fill an actual implementation need, such as frontend design, animation or accessibility. Use only skills advertised by that runtime, read them before applying them, and keep the chosen activity consistent. This skill remains usable on its own and does not require another named skill.

## 5. Review the outcome, not the pitch

Try the main interaction from entry to consequence when the runtime provides a preview. Check the meaningful user path and a small number of relevant failure cases. Keep verification proportional to the change.

Assess clarity, desire to participate, response quality, subject fit and execution separately. A screenshot can support visual assessment; it cannot demonstrate that a game is playable or an export contains the result. Explain any aspect you could not verify.

Use specific repairs: “the choice changes the label but leaves the scene identical” is actionable; “make it more fun” is not. Preserve a worthwhile mechanic while repairing its weak writing, controls or response. Revisit the concept only when the central payoff cannot be delivered or the user requests it.

## Handoff

Follow the host's required schema. If none is specified, return the completed artifact or concise proposal with:

- The chosen activity and concrete payoff.
- Which reference IDs informed which decisions.
- Needed assets/capabilities and any material limitation.
- What was actually built and tried, plus remaining work.

Record taste feedback as explicit user decisions, separately from the agent's assessment. A liked reference does not automatically approve every part of it. Do not deploy, publish or perform paid actions beyond the authorization supplied by the user and host.

For developers connecting this package to a model runtime, see `references/runtime-integration.md`. That document describes an integration approach; installing this skill alone does not change a separate Sites pipeline.

## Optional Spotify fan connection

When the customer requests paid Spotify fan capture, use the companion `recoup-content-connect-fans` skill if the host provides it. It handles customer authentication, site registration, activation and the public connection link. If unavailable, consult the live Recoup API documentation and confirm capability before promising capture. This build skill does not supply that integration by itself. Keep customer credentials out of site code and keep Spotify playback separate from fan capture.
