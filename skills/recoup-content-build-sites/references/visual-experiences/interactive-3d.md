# Interactive and 3D design

## Design an interaction people can discover

Name the user's verb: drag, rotate, cut, tune, assemble, explore, compare, or play. Make the first action apparent through composition, a short cue, or a restrained demonstration. A long instruction panel usually cannot rescue an unclear affordance.

Map input to a meaningful parameter. Then show both the immediate action and its consequence. In a lens explainer, changing focus should affect the optical explanation and displayed result; in a physical toy, a press should deform the touched region. Example 13 is a useful explainer reference, and 63 is a soft-body prompt reference.

Give each input one clear owner. Dragging the object should not also orbit the camera. Preserve normal page scrolling outside an immersive canvas; supply a way to leave pointer lock or immersive navigation. For touch, avoid interactions that depend solely on hover. Provide named controls and a usable keyboard path where the task permits it.

## Separate authored spectacle from a simulation

An animation can be excellent without simulating its subject. Choose honestly:

| Need | Suitable structure | Evidence to check |
|---|---|---|
| Explain a fixed sequence | Authored timeline with visible cause/effect | Correct order and understandable transitions |
| Let a user change parameters | State model driving the view | Different inputs produce the intended different outcome |
| Explore physical behavior | Solver with stated assumptions | Stable integration, contacts/constraints, recovery and meaningful limits |
| Present actual scientific claims | Validated model/data plus visualization | Units, sources, ranges and consistency |

Use a shared state object or equivalent authoritative model. Derive geometry, labels, plots, and readouts from it. Test reset after multiple interactions, not only on first load. Avoid hardcoded branches that appear general but only support the demo's first two states.

For fixed-step simulation, separate simulation time from display time. Bound catch-up work after a stalled frame; use interpolation when appropriate. For reproducible replays, keep the seed, inputs, and integration schedule deterministic. Arbitrary seeking in a stateful solver needs replay/checkpoints or a precomputed trajectory; merely setting a timestamp does not reconstruct physics. The [Horizon animation project](https://github.com/misbahsy/claude-horizon-animation) is a useful reference for physics-driven scenes and linked mathematical explanations.

## Make spatial scenes read well

- Block out camera, scale, major masses, and lighting before detailed materials.
- Use overlap, value separation, grounded contact, and atmospheric depth to make space legible.
- Ensure controls and labels remain readable against the moving scene. Attach explanatory labels to meaningful parts; resolve occlusion deliberately.
- Make exploration worth doing: reveal a cross-section, viewpoint, state, or relationship that a flat image cannot show.
- Keep camera speed and turn behavior appropriate to the scale. Offer a stable or guided view for people who do not want free navigation.

For water, translucency, or metallic surfaces, first decide which visual cues do the work. Reflections, refraction, absorption, caustics, and surface normals have distinct roles. A stylized solution can omit some while remaining coherent. [Clearwater](https://github.com/Aureliengmz/clearwater) and [Tidewater](https://github.com/dgreenheck/tidewater) expose implementation examples; do not infer that their settings are portable across all devices.

## Rendering choices with practical consequences

**Color:** Track input, working, and output color spaces. Three.js lighting uses a linear working space; color textures and numeric data maps need different treatment. Avoid fixing a conversion error with arbitrary exposure changes. Consult the [current Three.js color guide](https://threejs.org/manual/pages/color-management.html) for the installed version's API.

**Performance:** Set a target device and frame budget, then measure the actual interaction. Reduce internal render resolution, expensive passes, particle count, or shadow cost when the profile calls for it. High device-pixel ratios increase the rendered pixel workload quadratically. Batch repeated geometry where appropriate and release unused GPU resources. The [MDN WebGL guide](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices) covers back-buffer sizing, batching, memory, and portability.

**Fallback:** Detect required rendering capabilities. Offer a simpler renderer, static explanatory view, or clear unsupported message instead of a blank canvas. Do not claim a fallback exists until it has been exercised.

**Verification:** Check a typical input, an extreme input, an interrupted action, repeated reset, resize, and the most demanding scene. Capture key states for visual review, but test controls live. A simulated crowd or fluid demo is not evidence of real-world predictive accuracy.

## Reference routes

- Optical/mechanical explanation: 13, 14, 16, 17.
- Fields, fluids and emergent motion: 18, 23, 46, 51, 55, 94, 103.
- Spatial exploration and environmental art: 15, 20–22, 57, 74–75, 78, 93, 95, 101–104.
- Physical toys and machines: 19, 38–39, 63–64, 68, 77, 84, 99.
- Playable visual worlds: 47–50, 62, 65, 71, 73, 80, 90, 100.

Numbers refer to `examples.md` (examples.md). Some entries are comparisons or third-party posts; read the evidence notes before attributing them.
