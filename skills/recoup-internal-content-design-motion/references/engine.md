# Renderer-neutral motion helpers

The bundled original modules are adapted by copying them into the project's chosen renderer. Keep their sibling imports intact. They do not render footage, encode audio/video, call providers or create complete marketing assets by themselves.

- `assets/motion-kernel.mjs`: analytic springs, velocity-preserving releases, Hermite interpolation, deterministic waves and timing helpers.
- `assets/experience-kernel.mjs`: repeatable random samples, log zoom, envelopes, wind and contact-based gait.
- `assets/scene-kernel.mjs`: named dependent cues, property tracks, deterministic seeking, inner edit mapping, focal placement and hash-bound review freshness.
- `assets/choreography-kernel.mjs`: scene wrapper with cue relations and sampled hold bounds, plus press, visibility, focus and rejected-asset helpers.

Read the module and corresponding test before using an unfamiliar export; the tests provide executable examples. Preserve one writer per animated property. Use semantic cues such as attachment-ready, send, result and CTA-ready instead of scattering unexplained seconds.

`compileChoreography({scene, relations, holds})` resolves cues and checks minimum gaps. Relations use `{id, before, after, minGap}`. Holds use `{id, at, end, channels:[{target, property, min, max}]}` and half-open intervals. Render every frame through its `sample(t)` to enforce sampled bounds. Include camera/parent channels that affect the read. Numeric bounds cannot establish text legibility or attention.

`focusTreatment(t, {enter, ready, exit, gone, dim, blur})` returns emphasis, backdropShade and backdropBlur. Shade is fractional; blur is in output pixels. Apply these only to the background and draw the crisp focal content afterward. Extend filtered imagery beyond the crop to avoid blur seams.

`assertSelectedAssets(selectedHashes, rejectedHashes)` requires the adapter to hash the actual files; it cannot discover rejected assets itself. Review freshness likewise depends on honest hashes and recorded evidence, not a boolean self-rating.

Keep three clocks explicit: source media/inner edits, outer composition, and soundtrack. Map original lyric timestamps using the chosen soundtrack offset. If a lyric asset demonstrates a different song passage from the film soundtrack, label that distinction; do not claim synchronization or lip-sync. RMS can drive an audio-reactive graphic but is not a beat detector or listening review.

For encoded multi-shot media, retain source IDs, trims, order, timestamps and crop recipes. Test deterministic seeking, alternate copy lengths/aspect ratios and cut boundaries. Do not reset media because the outer camera moved. Verify actual encoded frames as timestamp rounding can introduce duplicates even when the abstract timeline passes.
