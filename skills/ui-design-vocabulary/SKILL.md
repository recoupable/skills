---
name: ui-design-vocabulary
description: Translate vague UI feedback, screenshots, and interaction ideas into precise design vocabulary and actionable AI prompts. Use when someone asks what a UI pattern is called, wants to describe an animation, says an interface feels cramped or unpolished, or needs a clearer visual design brief. Covers typography, color, icons, layout, components, motion, accessibility, and interface copy. This is a vocabulary and specification tool, not an automatic redesign or implementation request.
---

# UI design vocabulary

Turn what the user sees or wants into language a designer or coding agent can act on. Name the relevant concept, explain it plainly, and connect it to a specific element and observable behavior. Use only as many terms as the task needs.

## Workflow

1. **Identify the task.** Answer a terminology question directly; translate informal feedback into a brief; or annotate a supplied interface. Do not turn a request for a name into a full audit.
2. **Establish the evidence.** Inspect the screenshot, URL, component, or description supplied. If a source cannot be read, say so. A still image establishes appearance, not timing, focus behavior, responsiveness, or implementation. Separate observations from proposed changes and assumptions.
3. **Choose the terms.** Read the relevant section of `references/vocabulary.md`. Distinguish neighboring concepts before selecting one. If two patterns fit, explain the deciding behavior rather than pretending the name is certain.
4. **Translate the intent.** Specify the element, property or behavior, desired change, and reason. Replace adjectives such as “premium,” “clean,” and “smooth” with concrete choices. Preserve the project's existing design system, tokens, content, and user constraints unless changing them is requested.
5. **Make it reviewable.** Describe how someone could tell the change worked. Include narrow-screen behavior, keyboard operation, failure states, or reduced motion only where relevant. Label suggested measurements as starting values, not observations or universal rules.

For implementation requests, use these terms to sharpen the specification, then follow the owning project's implementation and verification workflow. Vocabulary alone does not verify rendered behavior.

## Response patterns

**Name a pattern:** give the term, a one-sentence definition, and the closest alternative if it matters.

**Translate feedback:** return a short mapping of the user's phrase to the relevant terms, followed by a ready-to-use prompt. Keep observations and suggestions distinct.

**Describe an interface:** organize by composition, typography, surfaces/color, components, and visible states. Describe motion only if observed or explicitly proposed. Avoid claiming exact fonts, spacing, easing curves, or contrast ratios from visual estimates.

Use this prompt structure when helpful; omit irrelevant fields:

> In [view/component], change [specific property or behavior] to [desired result]. Use [existing token or proposed starting value]. Keep [constraint]. On [trigger], transition from [initial state] to [final state], using [timing/easing or spring behavior]. Handle [relevant alternate state]. Verify by [observable check].

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
