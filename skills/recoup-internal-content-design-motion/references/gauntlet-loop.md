# Film gauntlet: build, inspect, critique, revise

Adapted for this self-contained skill from Sidney Swift's [Gauntlet Loop v0.1.0](https://github.com/sidneyswift/skills/tree/main/gauntlet-loop), read October 8, 2026. No separate skill installation is required. This adaptation adds film evidence, generation, user-note tracking and honest capability limits.

## Establish the bar

Use the user's reference first. For Recoup launch films, begin with the Higgsfield reference entry points in `references/higgsfield-references.md`. Inspect actual moving footage, not just page copy or a thumbnail. Save the selected reference identity, URL, title/version, access date, duration, reviewed ranges and local hash when a permitted local copy exists. Compare useful passages rather than imposing the reference's total runtime on a different brief.

State the intended audience, outcome, approved strengths and current user acceptance requirements. Break the film into the smallest independently improvable pieces based on the actual weaknesses. Possible pieces include opening semantics, generated source actions, typography, payoff, transitions and sound; these are examples, not a mandatory department structure.

## Run the loop

1. **Build.** The lead or a builder produces real source assets and an encoded version. Keep editable recipes, hashes and a playable preview. Do not hand critics only source code, a storyboard or your description of the result.
2. **Delegate independent review.** Spawn a separate critic in a fresh context for each important comparison. Supply the brief, user requirements, actual artifact, reference, evidence locations and available inspection tools. Exclude builder rationalizations and prior verdicts. Use the harness's fresh-context option: for Codex collaboration, spawn with `fork_turns: "none"` and explicitly supply only the review packet. Start a new critic for a new verdict; do not reuse a builder or inherit the full conversation. Use blind A/B labels when practical. Never claim the builder's self-review is independent.
3. **Inspect both.** Critics inspect actual frames and transitions from both films and playback/audio where perceptible. Judge meaningful change, visible source action, creative variety, concurrency, hierarchy, text burden, typography, continuity, musical timing and CTA clarity as relevant. Every material finding needs a time range and visible evidence. Say when either artifact cannot be inspected; do not invent a winner.
4. **Choose the repair.** Ask which output better meets each relevant requirement and what the largest meaningful gap is. Route that gap to source generation, edit timing, composition or product-story correction. Fewer seconds or more cards alone do not resolve weak media or dull pacing.
5. **Apply notes.** Maintain a notes ledger with origin (user/critic), version, time range, problem, intended fix, status and verification evidence. Preserve approved strengths and rejected take hashes. Do not mark a note resolved merely because code changed.
6. **Rerender and rejudge.** Produce a new export, inspect the affected boundaries, then obtain a fresh critic on the new artifact. Compare against the reference and inspect for regressions across the whole film. Review hashes must match the new export. After separately repaired pieces are assembled, have a fresh critic inspect the complete final cut for coherence.
7. **Report progress.** Update a local progress page or document after each round with playable versions, reference, key notes, selected repairs, generation status/cost and unresolved gaps. Keep this in the private project. Show meaningful revisions to the user; do not require a reply before every authorized repair.

Do not prescribe a fixed number of rounds or stop merely because the first export passes technical tests. Every full film needs an initial independent comparison and a fresh complete-export review before delivery. If the first candidate already meets the bar, the final review may examine the same hash; do not manufacture needless edits. Any material critique or user note reopens the repair loop. Continue while meaningful gaps can be repaired within authorized resources. Stop when the bar is met on the stated dimensions, the user accepts/stops the work, or an actual resource/tool/input limit prevents progress. Diminishing changes can justify a review handoff only if no explicit user acceptance requirement remains unmet; record remaining reference advantages rather than claiming parity. Never convert budget exhaustion, unavailable playback or a stalled job into a pass.

If independent agents are unavailable, continue useful generation/build work and label self-review provisional. Report independent review as incomplete. If reference inspection is unavailable, record the limitation and seek an accessible copy; do not claim reference comparison from memory or webpage descriptions.

## Fresh critic prompt

Use this as a starting point, adjusting the scope to the actual film:

> Independently review these actual exported artifacts against this brief and its explicit user notes. Inspect the reference as well as the candidate. Do not infer quality from the builder's claims. Identify the better result for the relevant requirements; provide exact time ranges, observable evidence, the largest meaningful gap and a concrete next repair. Check pace, internal media action, semantic variety, concurrency, type/readability, transitions, workflow clarity and CTA where relevant. Report what you could not perceive, including audio. Distinguish brief acceptance from reference parity. Do not approve an unseen export or waive an explicit user requirement.

## Required round record

Use the existing project ledger or copy `templates/production-ledger.json`. Record each candidate hash, reference identity/ranges, critic identity and independence, inspection coverage/limits, verdict and notes, repairs, next export and stop reason. Scores are optional shorthand, never substitutes for evidence. User approval is a separate recorded event attached to a specific artifact.
