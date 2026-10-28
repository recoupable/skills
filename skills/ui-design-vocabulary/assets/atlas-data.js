window.ATLAS = [
  {
    "id": "tracking",
    "category": "Typography",
    "title": "Tracking",
    "states": [
      "Neutral",
      "Expanded"
    ],
    "look": "Spacing changes across the entire label.",
    "confusion": "Do not confuse tracking with pair-specific kerning.",
    "prompt": "Increase tracking on the short uppercase label only."
  },
  {
    "id": "leading",
    "category": "Typography",
    "title": "Line height",
    "states": [
      "Tight",
      "Comfortable",
      "Loose"
    ],
    "look": "The space between baselines changes, not the text size.",
    "confusion": "Paragraph spacing is a separate property.",
    "prompt": "Adjust body line height while preserving the type scale."
  },
  {
    "id": "measure",
    "category": "Typography",
    "title": "Line length",
    "states": [
      "Wide",
      "Constrained"
    ],
    "look": "The reading column changes width.",
    "confusion": "A narrower column does not require smaller text.",
    "prompt": "Constrain prose width; leave the surrounding layout flexible."
  },
  {
    "id": "hierarchy",
    "category": "Typography",
    "title": "Visual hierarchy",
    "states": [
      "Flat",
      "Ranked"
    ],
    "look": "Title, detail, and action have different emphasis.",
    "confusion": "Making everything larger does not create hierarchy.",
    "prompt": "Emphasize the decision and reduce secondary metadata weight."
  },
  {
    "id": "numbers",
    "category": "Typography",
    "title": "Tabular numerals",
    "states": [
      "Proportional",
      "Tabular",
      "Extra digit"
    ],
    "look": "Digit advance widths can be equal while total width still changes.",
    "confusion": "Tabular digits do not reserve room for an additional digit.",
    "prompt": "Use tabular numerals and reserve enough column width."
  },
  {
    "id": "overflow",
    "category": "Typography",
    "title": "Text overflow",
    "states": [
      "Clipped",
      "Ellipsis",
      "Wrapped"
    ],
    "look": "Compare lost text, a truncation signal, and fully wrapped text.",
    "confusion": "An ellipsis does not provide access to the full value by itself.",
    "prompt": "Wrap essential names; truncate only with an accessible full-text path."
  },
  {
    "id": "spacing",
    "category": "Layout",
    "title": "Grouping through space",
    "states": [
      "Uniform",
      "Grouped"
    ],
    "look": "Related controls are closer than separate groups.",
    "confusion": "Cramped can mean poor grouping rather than insufficient global padding.",
    "prompt": "Increase between-group spacing while retaining compact field groups."
  },
  {
    "id": "density",
    "category": "Layout",
    "title": "Information density",
    "states": [
      "Compact",
      "Spacious"
    ],
    "look": "The same records occupy different amounts of space.",
    "confusion": "Spacious is not universally better for frequent scanning.",
    "prompt": "Choose row density for the task and preserve usable targets."
  },
  {
    "id": "radius",
    "category": "Layout",
    "title": "Concentric corners",
    "states": [
      "Same radius",
      "Inset radius"
    ],
    "look": "The inset follows the outer curvature in the second example.",
    "confusion": "Outer radius minus inset is a starting geometry rule, not universal styling.",
    "prompt": "Coordinate nested radii with the actual inset."
  },
  {
    "id": "responsive",
    "category": "Layout",
    "title": "Responsive layout",
    "states": [
      "Wide",
      "Narrow"
    ],
    "look": "Columns become stacked regions as space decreases.",
    "confusion": "These are container demonstrations, not device verification.",
    "prompt": "Stack the summary below the content when columns stop fitting."
  },
  {
    "id": "shift",
    "category": "Layout",
    "title": "Reserved loading space",
    "states": [
      "Unreserved",
      "Reserved",
      "Loaded"
    ],
    "look": "A reserved media area keeps the action in place.",
    "confusion": "A still frame cannot measure cumulative layout shift.",
    "prompt": "Reserve media proportions before the image becomes available."
  },
  {
    "id": "tokens",
    "category": "Color",
    "title": "Semantic color tokens",
    "states": [
      "Light",
      "Dark"
    ],
    "look": "The same roles receive different values per theme.",
    "confusion": "Inverting every color does not produce a deliberate dark theme.",
    "prompt": "Map surface, border, text, and accent roles for each theme."
  },
  {
    "id": "status",
    "category": "Accessibility",
    "title": "Color and status",
    "states": [
      "Color only",
      "Text and symbol"
    ],
    "look": "The state remains understandable without interpreting hue.",
    "confusion": "An icon alone can also be ambiguous.",
    "prompt": "Pair status color with a concise visible label."
  },
  {
    "id": "target",
    "category": "Accessibility",
    "title": "Visible icon vs hit area",
    "states": [
      "Small",
      "Expanded"
    ],
    "look": "The outlined interactive region exceeds the icon bounds.",
    "confusion": "A large drawn icon does not establish the actual hit area.",
    "prompt": "Expand the control area without enlarging the icon."
  },
  {
    "id": "button",
    "category": "Components",
    "title": "Button states",
    "states": [
      "Default",
      "Hover",
      "Focus",
      "Pressed",
      "Loading",
      "Disabled"
    ],
    "look": "Focus, pointer hover, transient press, and availability are independent.",
    "confusion": "A painted focus example does not prove keyboard operation.",
    "prompt": "Specify each state; keep loading geometry stable and announce progress."
  },
  {
    "id": "selection",
    "category": "Components",
    "title": "Selected vs pressed",
    "states": [
      "Unselected",
      "Pressed",
      "Selected"
    ],
    "look": "Press is momentary; selection persists after release.",
    "confusion": "Do not use :active as persistent selection state.",
    "prompt": "Represent selection explicitly and expose its semantic state."
  },
  {
    "id": "field",
    "category": "Components",
    "title": "Input states",
    "states": [
      "Default",
      "Focus",
      "Error",
      "Disabled"
    ],
    "look": "The label persists; error text names a recovery action.",
    "confusion": "Placeholder text cannot replace the label.",
    "prompt": "Keep a persistent label and associate actionable error text."
  },
  {
    "id": "overlay",
    "category": "Components",
    "title": "Tooltip vs popover",
    "states": [
      "Tooltip",
      "Popover"
    ],
    "look": "The interactive share controls require a richer surface.",
    "confusion": "Shape alone cannot establish role or modality.",
    "prompt": "Use a tooltip for a hint and a popover for interactive controls."
  },
  {
    "id": "modality",
    "category": "Components",
    "title": "Panel modality",
    "states": [
      "Nonmodal",
      "Modal"
    ],
    "look": "Modality changes background availability, not just placement.",
    "confusion": "A dim backdrop does not prove inertness or a focus trap.",
    "prompt": "Specify whether background interaction remains available."
  },
  {
    "id": "choice",
    "category": "Components",
    "title": "Independent vs exclusive choices",
    "states": [
      "Checkboxes",
      "Radios",
      "Switch"
    ],
    "look": "Multiple choices, one choice, and immediate on/off settings differ.",
    "confusion": "Choose semantics from the effect rather than the visual shape.",
    "prompt": "Use radios for one shipping option and checkboxes for independent extras."
  },
  {
    "id": "loading",
    "category": "Components",
    "title": "Loading indicators",
    "states": [
      "Spinner",
      "Skeleton",
      "Progress"
    ],
    "look": "Unknown action wait, expected content shape, and measured completion differ.",
    "confusion": "Never invent a percentage for an indeterminate process.",
    "prompt": "Choose an indicator based on what is known about completion."
  },
  {
    "id": "empty",
    "category": "Copy",
    "title": "Empty states",
    "states": [
      "Unexplained",
      "First use",
      "No results",
      "Failure"
    ],
    "look": "No content, no matching content, and a failed request need different actions.",
    "confusion": "Do not present a failed fetch as an empty collection.",
    "prompt": "Explain the state and provide the appropriate recovery or first action."
  },
  {
    "id": "copy",
    "category": "Copy",
    "title": "Action labels",
    "states": [
      "Generic",
      "Specific"
    ],
    "look": "The label communicates the consequence of activation.",
    "confusion": "Specific wording must match the action actually performed.",
    "prompt": "Name the action in the primary button."
  },
  {
    "id": "wayfinding",
    "category": "Structure",
    "title": "Wayfinding",
    "states": [
      "Unoriented",
      "Oriented"
    ],
    "look": "Location and parent context become explicit.",
    "confusion": "Breadcrumbs show hierarchy, not necessarily browsing history.",
    "prompt": "Add a meaningful page title and hierarchical location cues."
  },
  {
    "id": "fade",
    "category": "Motion",
    "title": "Fade",
    "states": [
      "Start",
      "Middle",
      "End"
    ],
    "look": "Opacity changes without positional movement.",
    "confusion": "Static frames do not establish duration or easing.",
    "prompt": "Fade the status in without moving surrounding content."
  },
  {
    "id": "slide",
    "category": "Motion",
    "title": "Translate",
    "states": [
      "Start",
      "Middle",
      "End"
    ],
    "look": "The object changes position without resizing.",
    "confusion": "Translation is not a change to document layout.",
    "prompt": "Translate the notification into place from a small offset."
  },
  {
    "id": "scale",
    "category": "Motion",
    "title": "Origin-aware scale",
    "states": [
      "Start",
      "Middle",
      "End"
    ],
    "look": "The panel expands from the trigger-side corner.",
    "confusion": "Transform origin does not position the panel beside its trigger.",
    "prompt": "Anchor the panel, then align its transform origin to that anchor."
  },
  {
    "id": "crossfade",
    "category": "Motion",
    "title": "Crossfade",
    "states": [
      "Start",
      "Middle",
      "End"
    ],
    "look": "Two different surfaces overlap during replacement.",
    "confusion": "This is not the same object changing shape.",
    "prompt": "Crossfade between distinct summary states without moving the container."
  },
  {
    "id": "morph",
    "category": "Motion",
    "title": "Shape interpolation",
    "states": [
      "Start",
      "Middle",
      "End"
    ],
    "look": "One continuous surface changes its proportions.",
    "confusion": "Matching endpoints alone do not prove object continuity.",
    "prompt": "Animate the same surface between compact and expanded geometry."
  },
  {
    "id": "stagger",
    "category": "Motion",
    "title": "Stagger",
    "states": [
      "Start",
      "Middle",
      "End"
    ],
    "look": "Items begin at different times within one coordinated entrance.",
    "confusion": "Long lists should not accumulate excessive delay.",
    "prompt": "Stagger the first visible group and cap total entrance time."
  },
  {
    "id": "reduced",
    "category": "Motion",
    "title": "Reduced motion",
    "states": [
      "Spatial",
      "Reduced"
    ],
    "look": "The outcome stays visible with less spatial movement.",
    "confusion": "Reduced motion does not mean removing feedback or information.",
    "prompt": "Replace decorative movement with an immediate state update."
  },
  {
    "id": "easing",
    "category": "Motion",
    "title": "Easing curves",
    "states": [
      "Linear",
      "Ease in",
      "Ease out",
      "Ease in out"
    ],
    "look": "At the same elapsed time, progress depends on the speed curve.",
    "confusion": "A single frame cannot identify a curve from an arbitrary interface.",
    "prompt": "Use purpose-appropriate easing and verify the complete motion."
  }
];
