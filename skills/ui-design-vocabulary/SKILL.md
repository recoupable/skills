---
name: ui-design-vocabulary
description: Translate vague UI feedback, screenshots, and interaction ideas into precise design vocabulary and actionable AI prompts. Use when someone asks what a UI pattern is called, wants to describe an animation, says an interface feels cramped or unpolished, or needs a clearer visual design brief. Covers typography, color, icons, layout, components, motion, accessibility, and interface copy. This is a vocabulary and specification tool, not an automatic redesign or implementation request.
---

# UI design vocabulary

Turn what the user sees or wants into language a designer or coding agent can act on. Name the relevant concept, explain it plainly, and connect it to a specific element and observable behavior. Use only as many terms as the task needs.

## Workflow

1. **Identify the task.** Answer a terminology question directly; translate informal feedback into a brief; or annotate a supplied interface. Do not turn a request for a name into a full audit.
2. **Establish the evidence.** Inspect the screenshot, URL, component, or description supplied. If a source cannot be read, say so. A still image establishes appearance, not timing, focus behavior, responsiveness, or implementation. Separate observations from proposed changes and assumptions.
3. **Choose the terms.** Read the relevant section of `references/vocabulary.md`. For visual questions, use `references/visual-index.md` to find and open the relevant screenshots before drawing a comparison. Distinguish neighboring concepts before selecting one. If two patterns fit, explain the deciding behavior rather than pretending the name is certain.
4. **Translate the intent.** Specify the element, property or behavior, desired change, and reason. Replace adjectives such as “premium,” “clean,” and “smooth” with concrete choices. Preserve the project's existing design system, tokens, content, and user constraints unless changing them is requested.
5. **Make it reviewable.** Describe how someone could tell the change worked. Include narrow-screen behavior, keyboard operation, failure states, or reduced motion only where relevant. Label suggested measurements as starting values, not observations or universal rules.

For implementation requests, use these terms to sharpen the specification, then follow the owning project's implementation and verification workflow. Vocabulary alone does not verify rendered behavior.

## Response patterns

**Name a pattern:** give the term, a one-sentence definition, and the closest alternative if it matters.

**Translate feedback:** return a short mapping of the user's phrase to the relevant terms, followed by a ready-to-use prompt. Keep observations and suggestions distinct.

**Describe an interface:** organize by composition, typography, surfaces/color, components, and visible states. Describe motion only if observed or explicitly proposed. Avoid claiming exact fonts, spacing, easing curves, or contrast ratios from visual estimates.

Use this prompt structure when helpful; omit irrelevant fields:

> In [view/component], change [specific property or behavior] to [desired result]. Use [existing token or proposed starting value]. Keep [constraint]. On [trigger], transition from [initial state] to [final state], using [timing/easing or spring behavior]. Handle [relevant alternate state]. Verify by [observable check].

## Use the visual atlas

The original atlas in `assets/atlas.html` contains 32 comparison cards and 87 named states. Each state has a literal browser screenshot listed in `references/visual-index.md`. These are our own teaching examples, not copies of the source lesson. The atlas covers selected high-confusion concepts; the text reference covers additional terminology.

1. Find the closest concept in the visual index and open at least the two contrasting images relevant to the question. Resolve all paths relative to this skill directory.
2. Name the visible difference and the feature that distinguishes the alternatives. Do not treat an image filename as visual evidence. If the harness cannot inspect images, use the text descriptions and disclose the limitation.
3. Separate **observed** facts from **inferred** behavior and **proposed** changes. A screenshot of a modal-looking surface does not prove modal behavior. A painted focus ring does not prove keyboard access.
4. Transfer the principle, not the sample styling. The atlas palette, dimensions, timings, and typography are teaching choices, not a replacement design system.
5. For motion, compare start, middle, and end. The replay control cycles illustrative states; it is not a recording or a calibrated simulation of timing, spring physics, or easing. Do not estimate real animation settings from these frames.

For a searchable overview, open `assets/atlas.html` directly in a browser; it has no network dependencies. Use its state buttons or replay controls. For a single card, append `?card=button&state=2` (the focus example). `assets/manifest.json` enumerates every card and named state. All named states are captured; continuous inputs and arbitrary intermediate times are not an infinite screenshot inventory.

## Resolve ambiguity before prescribing a fix

- **“Cramped”:** examine grouping, reading width, hierarchy, and density separately. More global padding can make a dense work tool worse. Compare the spacing and density cards.
- **“Popup”:** identify trigger, anchoring, interactive content, background availability, and dismissal. Ask about the deciding behavior only when it changes the specification and cannot be inspected.
- **“Active”:** distinguish pointer-down press, persistent selection, current navigation destination, and keyboard focus. Do not map all four to one style or semantic state.
- **“Empty”:** distinguish first use, zero search results, permission restrictions, and failed loading. Never prescribe a first-use action for an unverified failed request.
- **“Smooth”:** identify whether the issue is temporal stutter, discontinuity, excessive delay, or an inappropriate curve. Do not prescribe easing for a layout stability problem.
- **Existing system conflict:** prefer the documented owning source, then verify the shipped implementation. Preserve intentional rules; flag accidental inconsistencies and accessibility defects rather than blindly copying them. Separate a necessary fix from an optional style preference.

## Motion specification

An animation name is only the start. State:

- Trigger and target: what causes it, and what moves.
- Endpoints: position, scale, opacity, or shape before and after.
- Timing: duration and easing for a tween, or spring parameters in the chosen library's conventions. Do not invent a universal conversion between spring settings and milliseconds.
- Coordination: simultaneous, sequenced, or staggered; cap total delay for long lists.
- Interruption and exit: what happens on repeated input or dismissal.
- Reduced-motion alternative: preserve the state change while reducing spatial movement; a brief fade or immediate update may be appropriate.

Prefer movement that explains a change. Do not add bounce, blur, stagger, or scroll effects merely to signal polish. Avoid delaying access to content for decorative animation.

## Examples

**“The numbers keep wobbling when the revenue updates.”**

Likely term: **tabular numerals**, if the problem is changing digit widths. Proposed prompt: “Use tabular numerals for the revenue column and right-align amounts. Keep currency formatting consistent. Check that digit widths stay stable as values update.” If the whole card moves, investigate layout shift separately.

**“Make this popup feel like it comes from the button.”**

Terms: **origin-aware animation** and **transform origin**. Proposed prompt: “Anchor the share popover to its trigger. Start at slightly reduced scale and zero opacity, then settle at full size with ease-out. As a starting point, try 160ms and scale 0.97. Keep it redirectable on quick open/close, return focus on dismissal, and use an immediate change for reduced motion.” Do not call an interactive popover a tooltip.

**“This settings page feels cramped.”**

Terms to investigate: **negative space**, **grouping**, **hierarchy**, and **line height**. Proposed prompt: “Group related settings under clear headings. Increase spacing between groups more than spacing within each group, using the existing spacing scale. Keep labels close to their controls and allow helper text to wrap on narrow screens.” Do not prescribe globally larger type or padding without inspecting the page.

## Accuracy checks

- Keep defaults distinct from requirements. A preferred spacing value, corner shape, or easing curve is a design choice.
- Do not certify accessibility from a screenshot. Verify applicable criteria and actual keyboard, semantic, contrast, and motion behavior when implementation is in scope.
- Do not promise performance because an animation uses transforms. Profile the actual interaction when performance is the task.
- Do not infer user motivation from an analytics metric alone. Separate a hypothesis from measured evidence.
- Component names vary across libraries. State placement, modality, trigger, and dismissal behavior when “sheet,” “drawer,” or “dialog” is ambiguous.

## Source and scope

Inspired by the [AI for UI Vocabulary lesson](https://aiforui.dev/learn/vocabulary), accessed October 28, 2026. This is an original operational synthesis with selected terminology and new prompts, not a copy of the course, its interactive examples, or an exhaustive glossary. The reference includes technical qualifications where a short design maxim could otherwise be mistaken for a universal rule. No course login is required to use this skill.

## Local validation

Scripts ship alongside this skill. From the skill directory run `python3 scripts/validate_atlas.py` to verify screenshot coverage, state inventory, and captured-source hashes. This checks artifact integrity, not visual judgment or accessibility conformance. `references/interpretation-cases.md` provides review cases with expected distinctions; do not claim a model benchmark unless those cases were actually run.
