# Visual atlas index

Original rendered examples, not screenshots of the source course. Every named state below has a JPEG under `assets/screenshots/`. Open the images using the available image tool; do not infer their pixels from filenames. The interactive atlas is `assets/atlas.html`.

Motion screenshots are deterministic sampled frames, not recordings. They illustrate geometry and opacity, not measured browser timing. Component state illustrations are labeled simulations, not proof of accessibility or production behavior.

## Tracking

- Look for: Spacing changes across the entire label.
- Avoid confusing: Do not confuse tracking with pair-specific kerning.
- Prompt: Increase tracking on the short uppercase label only.
- States: `assets/screenshots/tracking-0.jpg` (Neutral), `assets/screenshots/tracking-1.jpg` (Expanded)

## Line height

- Look for: The space between baselines changes, not the text size.
- Avoid confusing: Paragraph spacing is a separate property.
- Prompt: Adjust body line height while preserving the type scale.
- States: `assets/screenshots/leading-0.jpg` (Tight), `assets/screenshots/leading-1.jpg` (Comfortable), `assets/screenshots/leading-2.jpg` (Loose)

## Line length

- Look for: The reading column changes width.
- Avoid confusing: A narrower column does not require smaller text.
- Prompt: Constrain prose width; leave the surrounding layout flexible.
- States: `assets/screenshots/measure-0.jpg` (Wide), `assets/screenshots/measure-1.jpg` (Constrained)

## Visual hierarchy

- Look for: Title, detail, and action have different emphasis.
- Avoid confusing: Making everything larger does not create hierarchy.
- Prompt: Emphasize the decision and reduce secondary metadata weight.
- States: `assets/screenshots/hierarchy-0.jpg` (Flat), `assets/screenshots/hierarchy-1.jpg` (Ranked)

## Tabular numerals

- Look for: Digit advance widths can be equal while total width still changes.
- Avoid confusing: Tabular digits do not reserve room for an additional digit.
- Prompt: Use tabular numerals and reserve enough column width.
- States: `assets/screenshots/numbers-0.jpg` (Proportional), `assets/screenshots/numbers-1.jpg` (Tabular), `assets/screenshots/numbers-2.jpg` (Extra digit)

## Text overflow

- Look for: Compare lost text, a truncation signal, and fully wrapped text.
- Avoid confusing: An ellipsis does not provide access to the full value by itself.
- Prompt: Wrap essential names; truncate only with an accessible full-text path.
- States: `assets/screenshots/overflow-0.jpg` (Clipped), `assets/screenshots/overflow-1.jpg` (Ellipsis), `assets/screenshots/overflow-2.jpg` (Wrapped)

## Grouping through space

- Look for: Related controls are closer than separate groups.
- Avoid confusing: Cramped can mean poor grouping rather than insufficient global padding.
- Prompt: Increase between-group spacing while retaining compact field groups.
- States: `assets/screenshots/spacing-0.jpg` (Uniform), `assets/screenshots/spacing-1.jpg` (Grouped)

## Information density

- Look for: The same records occupy different amounts of space.
- Avoid confusing: Spacious is not universally better for frequent scanning.
- Prompt: Choose row density for the task and preserve usable targets.
- States: `assets/screenshots/density-0.jpg` (Compact), `assets/screenshots/density-1.jpg` (Spacious)

## Concentric corners

- Look for: The inset follows the outer curvature in the second example.
- Avoid confusing: Outer radius minus inset is a starting geometry rule, not universal styling.
- Prompt: Coordinate nested radii with the actual inset.
- States: `assets/screenshots/radius-0.jpg` (Same radius), `assets/screenshots/radius-1.jpg` (Inset radius)

## Responsive layout

- Look for: Columns become stacked regions as space decreases.
- Avoid confusing: These are container demonstrations, not device verification.
- Prompt: Stack the summary below the content when columns stop fitting.
- States: `assets/screenshots/responsive-0.jpg` (Wide), `assets/screenshots/responsive-1.jpg` (Narrow)

## Reserved loading space

- Look for: A reserved media area keeps the action in place.
- Avoid confusing: A still frame cannot measure cumulative layout shift.
- Prompt: Reserve media proportions before the image becomes available.
- States: `assets/screenshots/shift-0.jpg` (Unreserved), `assets/screenshots/shift-1.jpg` (Reserved), `assets/screenshots/shift-2.jpg` (Loaded)

## Semantic color tokens

- Look for: The same roles receive different values per theme.
- Avoid confusing: Inverting every color does not produce a deliberate dark theme.
- Prompt: Map surface, border, text, and accent roles for each theme.
- States: `assets/screenshots/tokens-0.jpg` (Light), `assets/screenshots/tokens-1.jpg` (Dark)

## Color and status

- Look for: The state remains understandable without interpreting hue.
- Avoid confusing: An icon alone can also be ambiguous.
- Prompt: Pair status color with a concise visible label.
- States: `assets/screenshots/status-0.jpg` (Color only), `assets/screenshots/status-1.jpg` (Text and symbol)

## Visible icon vs hit area

- Look for: The outlined interactive region exceeds the icon bounds.
- Avoid confusing: A large drawn icon does not establish the actual hit area.
- Prompt: Expand the control area without enlarging the icon.
- States: `assets/screenshots/target-0.jpg` (Small), `assets/screenshots/target-1.jpg` (Expanded)

## Button states

- Look for: Focus, pointer hover, transient press, and availability are independent.
- Avoid confusing: A painted focus example does not prove keyboard operation.
- Prompt: Specify each state; keep loading geometry stable and announce progress.
- States: `assets/screenshots/button-0.jpg` (Default), `assets/screenshots/button-1.jpg` (Hover), `assets/screenshots/button-2.jpg` (Focus), `assets/screenshots/button-3.jpg` (Pressed), `assets/screenshots/button-4.jpg` (Loading), `assets/screenshots/button-5.jpg` (Disabled)

## Selected vs pressed

- Look for: Press is momentary; selection persists after release.
- Avoid confusing: Do not use :active as persistent selection state.
- Prompt: Represent selection explicitly and expose its semantic state.
- States: `assets/screenshots/selection-0.jpg` (Unselected), `assets/screenshots/selection-1.jpg` (Pressed), `assets/screenshots/selection-2.jpg` (Selected)

## Input states

- Look for: The label persists; error text names a recovery action.
- Avoid confusing: Placeholder text cannot replace the label.
- Prompt: Keep a persistent label and associate actionable error text.
- States: `assets/screenshots/field-0.jpg` (Default), `assets/screenshots/field-1.jpg` (Focus), `assets/screenshots/field-2.jpg` (Error), `assets/screenshots/field-3.jpg` (Disabled)

## Tooltip vs popover

- Look for: The interactive share controls require a richer surface.
- Avoid confusing: Shape alone cannot establish role or modality.
- Prompt: Use a tooltip for a hint and a popover for interactive controls.
- States: `assets/screenshots/overlay-0.jpg` (Tooltip), `assets/screenshots/overlay-1.jpg` (Popover)

## Panel modality

- Look for: Modality changes background availability, not just placement.
- Avoid confusing: A dim backdrop does not prove inertness or a focus trap.
- Prompt: Specify whether background interaction remains available.
- States: `assets/screenshots/modality-0.jpg` (Nonmodal), `assets/screenshots/modality-1.jpg` (Modal)

## Independent vs exclusive choices

- Look for: Multiple choices, one choice, and immediate on/off settings differ.
- Avoid confusing: Choose semantics from the effect rather than the visual shape.
- Prompt: Use radios for one shipping option and checkboxes for independent extras.
- States: `assets/screenshots/choice-0.jpg` (Checkboxes), `assets/screenshots/choice-1.jpg` (Radios), `assets/screenshots/choice-2.jpg` (Switch)

## Loading indicators

- Look for: Unknown action wait, expected content shape, and measured completion differ.
- Avoid confusing: Never invent a percentage for an indeterminate process.
- Prompt: Choose an indicator based on what is known about completion.
- States: `assets/screenshots/loading-0.jpg` (Spinner), `assets/screenshots/loading-1.jpg` (Skeleton), `assets/screenshots/loading-2.jpg` (Progress)

## Empty states

- Look for: No content, no matching content, and a failed request need different actions.
- Avoid confusing: Do not present a failed fetch as an empty collection.
- Prompt: Explain the state and provide the appropriate recovery or first action.
- States: `assets/screenshots/empty-0.jpg` (Unexplained), `assets/screenshots/empty-1.jpg` (First use), `assets/screenshots/empty-2.jpg` (No results), `assets/screenshots/empty-3.jpg` (Failure)

## Action labels

- Look for: The label communicates the consequence of activation.
- Avoid confusing: Specific wording must match the action actually performed.
- Prompt: Name the action in the primary button.
- States: `assets/screenshots/copy-0.jpg` (Generic), `assets/screenshots/copy-1.jpg` (Specific)

## Wayfinding

- Look for: Location and parent context become explicit.
- Avoid confusing: Breadcrumbs show hierarchy, not necessarily browsing history.
- Prompt: Add a meaningful page title and hierarchical location cues.
- States: `assets/screenshots/wayfinding-0.jpg` (Unoriented), `assets/screenshots/wayfinding-1.jpg` (Oriented)

## Fade

- Look for: Opacity changes without positional movement.
- Avoid confusing: Static frames do not establish duration or easing.
- Prompt: Fade the status in without moving surrounding content.
- States: `assets/screenshots/fade-0.jpg` (Start), `assets/screenshots/fade-1.jpg` (Middle), `assets/screenshots/fade-2.jpg` (End)

## Translate

- Look for: The object changes position without resizing.
- Avoid confusing: Translation is not a change to document layout.
- Prompt: Translate the notification into place from a small offset.
- States: `assets/screenshots/slide-0.jpg` (Start), `assets/screenshots/slide-1.jpg` (Middle), `assets/screenshots/slide-2.jpg` (End)

## Origin-aware scale

- Look for: The panel expands from the trigger-side corner.
- Avoid confusing: Transform origin does not position the panel beside its trigger.
- Prompt: Anchor the panel, then align its transform origin to that anchor.
- States: `assets/screenshots/scale-0.jpg` (Start), `assets/screenshots/scale-1.jpg` (Middle), `assets/screenshots/scale-2.jpg` (End)

## Crossfade

- Look for: Two different surfaces overlap during replacement.
- Avoid confusing: This is not the same object changing shape.
- Prompt: Crossfade between distinct summary states without moving the container.
- States: `assets/screenshots/crossfade-0.jpg` (Start), `assets/screenshots/crossfade-1.jpg` (Middle), `assets/screenshots/crossfade-2.jpg` (End)

## Shape interpolation

- Look for: One continuous surface changes its proportions.
- Avoid confusing: Matching endpoints alone do not prove object continuity.
- Prompt: Animate the same surface between compact and expanded geometry.
- States: `assets/screenshots/morph-0.jpg` (Start), `assets/screenshots/morph-1.jpg` (Middle), `assets/screenshots/morph-2.jpg` (End)

## Stagger

- Look for: Items begin at different times within one coordinated entrance.
- Avoid confusing: Long lists should not accumulate excessive delay.
- Prompt: Stagger the first visible group and cap total entrance time.
- States: `assets/screenshots/stagger-0.jpg` (Start), `assets/screenshots/stagger-1.jpg` (Middle), `assets/screenshots/stagger-2.jpg` (End)

## Reduced motion

- Look for: The outcome stays visible with less spatial movement.
- Avoid confusing: Reduced motion does not mean removing feedback or information.
- Prompt: Replace decorative movement with an immediate state update.
- States: `assets/screenshots/reduced-0.jpg` (Spatial), `assets/screenshots/reduced-1.jpg` (Reduced)

## Easing curves

- Look for: At the same elapsed time, progress depends on the speed curve.
- Avoid confusing: A single frame cannot identify a curve from an arbitrary interface.
- Prompt: Use purpose-appropriate easing and verify the complete motion.
- States: `assets/screenshots/easing-0.jpg` (Linear), `assets/screenshots/easing-1.jpg` (Ease in), `assets/screenshots/easing-2.jpg` (Ease out), `assets/screenshots/easing-3.jpg` (Ease in out)
