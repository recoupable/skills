# Interpretation review cases

These are review scenarios, not a completed model benchmark. Inspect the cited images before answering. Grade the distinction, evidence limits, and proposed action; do not reward merely repeating a term.

| Prompt | Images | Expected reasoning | Failure signal |
|---|---|---|---|
| “Make this active button accessible.” | `assets/screenshots/button-2.jpg`, `assets/screenshots/selection-2.jpg` | Ask whether active means focus or selected; distinguish visual appearance from semantics. | Adds a focus trap or treats selected as pressed. |
| “The numbers are tabular but the column still jumps.” | `assets/screenshots/numbers-1.jpg`, `assets/screenshots/numbers-2.jpg` | Extra digits change total width; inspect reserved width and alignment. | Recommends tabular digits as the complete fix again. |
| “Make our operations table less cramped.” | `assets/screenshots/density-0.jpg`, `assets/screenshots/spacing-1.jpg` | Consider scan density and grouping separately; preserve useful information. | Adds large card padding everywhere without inspecting task needs. |
| “This screenshot proves our drawer is modal.” | `assets/screenshots/modality-1.jpg` | Backdrop is appearance only; inspect background inertness, focus and dismissal. | Certifies modality from the dim surface. |
| “There are no recordings, add a create button.” | `assets/screenshots/empty-3.jpg` | It is a load failure; suggest recovery and retain any existing data. | Converts failure to first-use empty state. |
| “What spring settings made this?” | `assets/screenshots/morph-1.jpg` | A still frame cannot establish spring settings; request motion evidence or propose labeled starting settings. | Invents stiffness and damping as observed measurements. |
| “Give the tooltip a copy-link button.” | `assets/screenshots/overlay-0.jpg`, `assets/screenshots/overlay-1.jpg` | Interactive content requires an appropriate interactive overlay pattern. | Places an interactive action in a tooltip without changing the model. |
| “Disable all feedback for reduced motion.” | `assets/screenshots/reduced-1.jpg` | Preserve completion feedback while reducing spatial movement. | Hides success or leaves the user uncertain. |

Suggested rubric per case: correct distinction (0–2), evidence limits (0–2), actionable and scoped response (0–2). Use independent evaluation when available; authored cases alone are not evidence of performance.
