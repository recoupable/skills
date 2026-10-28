# Vocabulary selection guide

Use this reference selectively. Pair the term with an element and intended outcome rather than listing vocabulary for its own sake.

## Appearance and structure

| Concern | Useful terms and distinctions | Specification cue |
|---|---|---|
| Letter spacing | Kerning adjusts a particular pair; tracking changes spacing across a text run. | Identify the heading or label; avoid changing body-text spacing to fix one pair. |
| Reading rhythm | Leading means line spacing; measure means line length; a type scale organizes sizes. | Specify readable line length and hierarchy with existing type tokens. |
| Perceived type size | Cap height and x-height describe letter proportions; font weight describes stroke heaviness. | Compare actual letterforms when pairing fonts or choosing fallbacks. |
| Numeric alignment | Tabular numerals give digits equal advance widths. | Combine with appropriate alignment and consistent numeric formatting. |
| Font loading | A font stack orders fallback choices; variable fonts expose axes such as weight. | Match fallback metrics; a variable font does not inherently prevent width changes. |
| Text fitting | Wrapping, hyphenation, truncation, and fluid sizing solve different constraints. | Preserve essential identifiers and provide access to shortened text. Test actual language and container sizes. |
| Surface colors | Semantic tokens name roles; tinted neutrals add a hue bias; alpha controls transparency. | Reuse roles such as surface, muted text, and border rather than inventing isolated colors. |
| Color models | sRGB and Display P3 describe gamuts; OKLCH describes perceptual lightness, chroma, and hue. | Palette generation still needs gamut and contrast checks; equal lightness is not an accessibility certificate. |
| Icon consistency | Stroke weight, cap style, optical alignment, and size variants shape an icon family. | Match surrounding type and preserve consistent meanings for selected and unselected states. |
| Composition | Negative space separates groups; hierarchy ranks importance; grids align regions. | Change spacing and emphasis according to task priority, not decorative symmetry alone. |
| Layout mechanics | Flexbox arranges along an axis; grid coordinates rows and columns; gap separates children. | Name alignment, wrapping, growth, and collapse behavior. |
| Responsive structure | Breakpoints change layout rules; max-width limits expansion; aspect ratio reserves proportions. | Choose changes where content stops fitting; include long labels and narrow screens. |
| Layers | Z-index operates within stacking contexts; overflow controls content outside bounds. | Inspect ancestor contexts before escalating z-index. Overflow can alter sticky scroll containment. |
| Screen edges | Safe-area insets accommodate obstructions; dynamic viewport units follow changing browser space. | Keep fixed actions reachable when browser chrome or keyboards change available space. |
| Shape and stability | Border radius controls corner curvature; layout shift is unexpected geometric movement. | For concentric corners, outer radius minus inset is a useful starting point, clamped at zero. Reserve loading space. |

## Components, input, and states

| Decision | Distinction to preserve |
|---|---|
| Button vs link | An action and navigation have different semantics, even if styled alike. |
| Tooltip vs popover | A tooltip provides supplementary, noninteractive explanation; a popover can contain controls. Support appropriate keyboard access. |
| Modal vs nonmodal panel | Modality determines background interaction and focus management. A panel's edge placement does not determine modality. |
| Drawer vs sheet | Library terminology differs. Specify the edge, size, modal behavior, dismissal, and return-focus target. |
| Select vs combobox | A select chooses from options; an editable combobox can narrow or suggest options as text is entered. |
| Radio vs checkbox vs switch | Radios express one choice in a group; checkboxes support independent choices; switches commonly apply on/off changes immediately. |
| Tabs vs accordion | Tabs change the active peer panel; accordions disclose sections. Neither automatically makes side-by-side comparison easy. |
| Badge vs tag | A badge annotates another object; a tag categorizes it and may expose selection or removal. |
| Spinner vs skeleton vs progress | Distinguish an indefinite wait, a content-shaped placeholder, and measured completion. Do not invent progress percentages. |
| Toast vs inline status | A toast is transient; inline status stays near its subject. Persistent errors need a discoverable recovery path. |
| Affordance and feedback | Make actions discoverable before input, then confirm focus, press, loading, success, or failure as appropriate. |
| Optimistic update | Show the proposed result before acknowledgment, with a defined reconciliation or rollback path. |
| Debounce | Wait for a pause in repeated input before acting; choose the delay for the task, not from a universal constant. |
| Hidden vs disabled | Opacity alone neither removes layout space nor reliably disables interaction. Specify visibility, semantics, focusability, and pointer handling deliberately. |

## Motion vocabulary

| Intent | Terms | What to specify |
|---|---|---|
| Appear or disappear | Fade, slide, scale, reveal, enter/exit | Opacity or geometry endpoints; clipping vs movement; exit completion before removal. |
| Change speed | Linear, ease-in, ease-out, ease-in-out, cubic-bezier | Linear suits constant progress; ease-out often suits arrival; ease-in can suit departure. Choose by purpose. |
| Coordinate items | Duration, delay, stagger, sequence, choreography | Individual timing and total wait; avoid stretching long lists into slow entrances. |
| Define a timeline | Keyframes, interpolation, steps, fill mode | Intermediate states, continuous vs discrete progression, and state before/after playback. |
| Use physical response | Spring, stiffness, damping, mass, velocity | Responsiveness, overshoot, settling, and how interrupted movement carries into the next target. |
| Transform geometry | Translate, scale, rotate, skew, perspective, transform origin | Axis, distance, angle, anchor, and whether surrounding layout should move too. |
| Preserve continuity | Shared element, layout animation, morph, crossfade | Whether the same object changes geometry or separate objects overlap visually. |
| Navigate spatially | Shared axis, direction-aware transition | A consistent forward/back relationship appropriate to the flow and reading direction. |
| React to scrolling | Scroll reveal vs scroll-driven animation | A visibility-triggered event vs progress continuously linked to scroll position. |
| Confirm input | Press feedback, ripple, hold-to-confirm, shake | Meaning, non-motion feedback, cancellation, and keyboard-equivalent operation. |
| Add effects | Blur, mask, clip-path, shimmer, ticker, typewriter | A concrete communication purpose and a simpler reduced-motion alternative. |

## Accessibility and performance language

**Semantic HTML, accessible names, label association, DOM order, and focus order** describe operation as well as appearance. For a modal, specify initial focus, containment, dismissal, and restoration. For nonmodal content, do not impose a focus trap by default. Supplement color-coded status with understandable text or symbols.

**Reduced motion** is a preference to respect, not an instruction to hide outcomes. **Touch target** is the interactive area, which can exceed the icon's bounds. Treat suggested dimensions as design targets; check the applicable platform guidance and accessibility criterion before claiming conformance. **Contrast ratio** and **APCA** name different models; do not silently substitute one compliance method for another.

**Frame rate, dropped frames, and jank** describe rendering cadence and visible disruption. **Compositing** combines rendered layers. Transform and opacity often avoid layout work, but smoothness still depends on content and device. **Layout thrashing** specifically involves repeated forced layout, commonly from interleaved geometry reads and writes; it is not simply a synonym for all size animation.

## Product language and supporting evidence

- **Information architecture:** navigation and labels organize destinations; wayfinding and breadcrumbs establish location; progressive disclosure stages complexity. Mental models, card sorting, and content inventories help investigate whether the structure matches users' tasks.
- **Interface copy:** microcopy covers small functional text. Voice stays recognizable while tone adapts to context. Front-load the action; distinguish a persistent label from a placeholder. Empty, error, and success states should explain what happened and the relevant next step.
- **Design collaboration:** tokens encode repeatable decisions; a design system combines those decisions with components and usage guidance. Prototypes test a question; annotations and handoff make intent implementable. Identify the actual source of truth rather than assuming the latest mockup governs production.
- **Analysis:** conversion, retention, churn, and funnels need explicit events, populations, and time windows. Heatmaps, recordings, and scroll depth can reveal patterns without proving causes. A/B tests need a defined outcome and sound experiment design. NPS is the percentage of promoters minus detractors, not the original 0–10 response scale. Bounce-rate definitions depend on the analytics system.

Source inspiration: [AI for UI — Vocabulary](https://aiforui.dev/learn/vocabulary), accessed October 28, 2026. Definitions and specification cues here are selectively synthesized and qualified; interactive course content is not reproduced.
