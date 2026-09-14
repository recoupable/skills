# Port a demonstration into a reusable theme

Use a user-selected demonstration and a separate scratch project. Do not depend on a personal
Downloads folder or an unbundled archive.

1. Read the supplied demo HTML, final render, and any theme settings. Identify the body layout,
   entrances/exits, hero treatment, foreground effects, and their timing.
2. Compare those choices with `../scripts/make-theme.cjs` and the existing theme JSON files. Add
   reusable parameters only for behavior not already expressible.
3. Create or update the theme JSON alongside the other themes, using their schema. Use approved
   workspace fonts; preserve notices for any intentionally included demo assets.
4. Build a scratch project from supplied media or a synthetic test clip. Prepare its transcript,
   foreground/background frames, and safe-zone data with the existing scripts. Render preview
   frames at the important transitions, compare them with the selected demonstration, then render.
5. Re-render a representative existing theme in another scratch project to catch regressions.
   Record the media source, runtime version, inputs, and observed results. An unavailable historical
   fixture is a coverage gap, not a passing test.
