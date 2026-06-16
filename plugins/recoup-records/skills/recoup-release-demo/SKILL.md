---
name: recoup-release-demo
description: >
  Run the full release workflow end-to-end on a synthetic artist + release, so a
  teammate can see what the releases bundle produces before pointing it at a real
  release. Use when the user types /recoup-release-demo, says "show me the release
  workflow", "demo the release bundle", or "what does a release run produce". Do
  NOT use for a real release — use recoup-release-start.
license: Proprietary
metadata:
  owner: agent@recoupable.com
  status: draft
  user-invocable: true
---

# Release Demo

Runs the full `recoup-release-start` workflow against a **synthetic** artist and
release so a new user (or a teammate being shown the tool) can see the populated
workspace and artifacts without a real release.

## Workflow

1. Generate realistic synthetic release facts (do not use a real artist):
   - Artist: a clearly fictional name (e.g. "Demo Artist — Gatsby Grace style").
   - Release: a fictional single with a one-line creative direction, a release
     date ~4 weeks out, goal metric = streams, channels = IG/TikTok/Spotify.
2. State clearly in chat that **this is a demo with synthetic data** — no real
   API calls are required; where a stage would call the Recoup API, produce a
   representative sample output and label it `[demo sample]`.
3. Run the `recoup-release-start` phases against the synthetic facts, landing
   everything under `releases/demo-artist/{release-slug}/`.
4. End with the same landing-card recap `recoup-release-start` uses, prefixed
   with **"DEMO —"**.

## Rules

- **Label everything as demo.** Never let synthetic numbers leak into a real
  workspace or get presented as real performance data.
- **Use the `demo-artist/` workspace prefix** so it's obvious and easy to delete.
- This skill is for showing the shape of the output — not for producing a real
  release plan.
