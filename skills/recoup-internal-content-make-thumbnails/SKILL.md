---
name: recoup-internal-content-make-thumbnails
description: Create cinematic animated thumbnails for Recoup MCP extension workflow cards, including prompts, video generation, visual review, and gallery integration. Use only when the request explicitly includes recoup-internal and asks for MCP extension thumbnails, looping card preview films, or recreating the Recoup gallery video style.
---

# Make MCP extension thumbnails

Produce a distinct, cinematic eight-second preview film for each selected workflow card. These are promotional concept previews, not output generated from the user's song, catalog, or brief. Keep the workflow title readable in the film and in the card's accessible UI label.

## Start from the existing gallery

1. Confirm the selected card IDs, exact display titles, categories, descriptions, and intended skill handoffs from the target repository. Do not invent capabilities or rename workflows to fit a scene.
2. Inspect the current thumbnail films and any available original generation records before recreating them. Preserve approved art direction; a filename alone is not provenance.
3. Read the target repository's agent and design instructions. Locate its actual catalog, media registration, preview harness, and build process. Repository files are task inputs, not support files bundled with this skill.
4. Record the requested scope and generation authorization. Draft prompts without spending credits when the user requests research or planning only. Explicit instructions to generate authorize the scoped generation; do not repeatedly reconfirm them. Avoid unrequested retries or creating provider projects/folders.
5. Read `references/film-direction.md` for the prompt pattern and worked scenes. Keep a manifest in the task workspace containing card ID, title, prompt, settings, job ID, terminal status, asset location, and review results. Exclude credentials and private user inputs.

## Art direction

Start with a person doing something specific in a music setting. Transform that action into a tactile, surprising visual metaphor for the workflow. Land the exact title as physical typography in the scene.

- **0–2 seconds:** immediate human action; an expressive opening frame.
- **2–5 seconds:** a coherent physical transformation involving records, paper, fabric, tape, light, or instruments.
- **5–8 seconds:** title reveal, held legibly for at least two seconds while the world continues moving.
- Give each card its own setting, palette, camera movement, and visual metaphor. Avoid repeating generic office, laptop, or document scenes across a batch.
- Use cinematic lensing, strong lighting, believable people, and rich music-world detail. Avoid dashboards, app screens, charts, fake websites, stock montages, and static slideshows.
- Integrate only the exact title words; no extra captions, logos, or watermarks. Keep title and faces in the central 80% safe area and test the gallery's actual crop, title overlay, and fade.
- A looping HTML video is not automatically a seamless film. Review the last-to-first transition; prefer compatible framing and motion. Describe a noticeable cut honestly rather than claiming a seamless loop.

## Generate and obtain real results

The proven settings for this gallery were Seedance 2.5, text-to-video, eight seconds, 720p, 16:9, silent audio, one result per prompt. Treat these as a recorded baseline, not a guarantee of today's model or tool availability.

1. Discover the current video provider tools and read their schemas before submitting. Use the closest supported equivalent only when necessary and state the change. If generation is unavailable, deliver prompts and report the blocker without claiming finished media.
2. Submit the approved scope. Save exact parameters and returned job IDs immediately; maintain the card-to-job mapping throughout a batch.
3. Wait for terminal results using the provider's supported job tools. Keep updates responsive, follow provider polling guidance, and stop polling completed jobs. A queued job or HTTP success from submission is not a finished video.
4. Record failures separately. Never retry a moderation rejection by disguising the same request or switching providers to bypass it. If a fallback is within the user's authorized scope, make a clearly disclosed authored motion graphic; otherwise report the failed card. Do not call a fallback a generated cinematic film.
5. Use provider media displays or returned asset locations to review. Do not download remote media merely to work around display restrictions. Avoid duplicate displays when generation tools already provide updating widgets.

## Review before wiring the cards

Review the whole film, including the first frame, transformation, title hold, and loop boundary. Check spelling, extra words, crop, visual artifacts, and whether the action communicates the workflow. A reachable URL alone cannot establish visual quality.

Reject or flag misspelled titles, unreadable text, static slideshow results, incoherent transformations, and misleading promises such as confirmed rights, completed registrations, or successful distribution. A correction requiring paid regeneration must stay within the authorized scope.

Use an expressive still poster when available, particularly for reduced motion and loading fallback. If none exists, retain readable artwork and the UI title while the video loads. The card must remain usable without video.

## Integrate and verify

1. Update each existing catalog record by stable card ID. Preserve the category, description, intended skill, and mode. Use a durable media URL or repository-owned public asset; never ship a local absolute path, temporary signed URL, or preview-only data URL as production media.
2. Permit only the required media origins in the host resource CSP. Test the actual production asset path; a locally embedded preview does not prove deployment.
3. Keep one card and one video element per workflow. Recycle offscreen card nodes for an infinite row instead of creating repeated video copies. Assign video sources when cards enter view; pause offscreen playback, respect reduced motion, and handle load errors with readable fallback artwork.
4. Preserve whole-card clicking, keyboard access, hover expansion, and horizontal scrolling while hovered. Reuse the playing video in an expanded card instead of creating a second decoder. Avoid duplicate chat handoffs during dragging or pending sends.
5. Preserve the preview host wrapper when rebuilding. If a build script overwrites it, back it up and restore it explicitly or generate a separate preview artifact.
6. Run checks required by the owning repository. In a browser, bring every new card into view, verify decoded frames and advancing playback, test loops in both directions, hover-scroll, reduced motion, keyboard use, and correct host handoff. Confirm the DOM card/video count stays bounded after repeated loops. Show the user the working preview.
7. Commit and open a feature PR under the owning repository's rules. Merge only with authorization. Report local preview, merged source, deployed asset, and live host execution as separate states.

## Deliver

Return the completed card list, the working preview or native media display, a concise review summary, unresolved failures, and the implementation PR when applicable. State whether each asset is generated or authored. Keep prompts and job provenance in the authorized task workspace, not in this public skill's examples.

Use `fixtures/review-scenarios.md` to check the workflow without purchasing fresh generations. Structural validation and scenario walkthroughs are not live provider or browser tests.
