# Recoup — Record Label in a Box

> **Generated bundle. Do not edit by hand.** This plugin is built from the
> individual Recoup plugins by `scripts/build_records_plugin.py`. Edit the source
> plugin, then re-run the generator.

The whole Recoup platform as a single plugin: artist setup and API access, music-industry research, catalog deal review, content creation, song audio analysis, and end-to-end release workflows — every skill, agent, and hook from the focused plugins, bundled together.

One install gives you everything below. Prefer a focused install? Install the
individual plugin instead — same skills, smaller surface.

| Source plugin | Status |
|---------------|--------|
| recoup-essentials | bundled |
| recoup-research | bundled |
| recoup-deals | bundled |
| recoup-content | bundled |
| recoup-song-analysis | bundled |
| recoup-releases | bundled |

## Install

```bash
/plugin marketplace add recoupable/skills
/plugin install recoup-records@recoup
```

## Regenerate

```bash
python3 scripts/build_records_plugin.py          # rebuild
python3 scripts/build_records_plugin.py --check   # verify no drift (CI)
```
