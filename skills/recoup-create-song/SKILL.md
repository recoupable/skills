---
name: recoup-create-song
description: Create an original song through the Recoup API with user approval at each stage — idea, genre, lyrics and prompt, then generation. Use for making a new song or a song for a video, including requests to choose a MiniMax Music 3 genre. Builds on recoup-minimax-music-3 production notes. Stops at the audio; does not make or publish a video.
---

# Create a song with Recoup

Work in four stages: **idea → genre → lyrics and prompt → Recoup API call**.
The user approves each stage before the next begins. Start at the earliest stage
whose current version has not been approved.

## Foundation and precedence

Model-specific foundation: [recoup-minimax-music-3](https://github.com/recoupable/skills/tree/main/skills/recoup-minimax-music-3), including its past-song prompt library.
Read `references/production-lessons.md` for the relevant local findings and their provenance.
Use these lessons to improve the draft, not to assume the user's musical choices.

This workflow replaces the foundation's direct-provider call and free re-roll advice:
**use the Recoup API only, and never generate or re-roll without approval for that call.**
A song idea is required; a finished video story or paper style is not. If the user
wants the music to determine the visuals, leave the visuals undecided until they approve the audio.

## Approval contract

- Present only the current stage's concrete proposal and a concise approval question.
  Stop and wait for the user's reply before doing the next stage's creative work.
- Explicit selection counts as approval of the selected proposal. Preserve prior approvals
  for unchanged material; don't ask again merely because the conversation resumed.
- A broad request to "make a song," silence, an assistant's own recommendation, or approval
  of a different stage is not approval of the current stage. A requested revision is not approval
  of the resulting revision: show it and wait.
- Keep a compact record of approved idea, genre, lyrics/prompt version, and generation scope.
  An upstream change invalidates approvals for the downstream material it changes.
- Gate 3 approves the exact creative inputs. Gate 4 separately approves spending credits
  on the reviewed request. Approval for one take never authorizes additional takes.
- Say that these pauses implement the user's requested four-stage workflow.
  If authorization is ambiguous, keep the action pending.

## 1. The idea

Ask for the idea if none was supplied, or propose one from the current brief. Present:
what the song is about, narrator or point of view, intended listener, emotional change,
and the central hook idea. Include the intended use, language, and approximate length
when known; mark suggested choices as proposals.

Do not silently reuse a previous song concept. Do not pick a genre or write lyrics yet.
Ask: **"Is this the song idea you want to develop, or what should change?"**
Wait for approval.

## 2. Genre — study, recommend, then let the user choose

Read the coverage table and relevant production lessons below before recommending a genre.
Show two or three plausible choices, one recommendation, and why each serves the approved idea.
Include tempo/groove, vocal or instrumental character, and core instrumentation as proposed
attributes. Respect an explicit user genre over template density.

"Top" here means **most represented in the official caption library**, not a measured ranking
of generation quality, training-data proportions, or commercial popularity. No genre-quality
leaderboard was established by the sources reviewed. Separate local listening results from coverage.
Use fit to the idea first, then local evidence and useful template support. Density is only a tie-breaker.

### MiniMax Music 3 genre coverage

Verified 2026-09-07: **1,000 cards across 18 families**, counted from the official family indexes
at commit `945655064d59b98004dd70002e7eb5c8c6e11373`. Every count matches its index header.
Source links and counting method are in `references/genre-sources.md`. Counts are a dated snapshot; refresh before
claiming they describe a newer library. The older Recoup note overstates the listed family counts
by two; this table uses the verified indexes.

| Genre family | Cards |
|---|---:|
| Metal & Heavy Rock | 78 |
| East Asian Modern Pop | 75 |
| Pop & Alternative Rock | 75 |
| Hip-Hop & Rap | 74 |
| East Asian Ballad & Heritage Pop | 72 |
| Modern R&B & Neo-Soul | 66 |
| Jazz, Swing & Big Band | 65 |
| Contemporary Folk & Acoustic | 64 |
| Electronic, Synth & Ambient Pop | 59 |
| Soul, Blues & Gospel | 59 |
| Cinematic Pop & Ballad | 54 |
| Country & Americana | 50 |
| Traditional Vocal & Stage | 43 |
| Cinematic Orchestral & Epic | 42 |
| Dance-Pop, Disco & Funk | 37 |
| Club, EDM, House & Trance | 29 |
| General Pop & Ballad | 29 |
| Roots, Traditional & Global | 29 |

For prompt development, consult the official genre router linked in `references/genre-sources.md`.
Choose one primary family, with a secondary only for an intentional blend. Mood words alone
are not genre evidence. Prefer the user's identity and groove over generic "pop" routing.

Ask: **"Which genre direction should we use?"** Wait for their choice or approval.
Do not draft the song's lyrics or full generation prompt before this gate passes.

## 3. Lyrics and prompt

Use the approved idea and genre. Draft original lyrics in the approved language with clear,
singable phrasing. Use section tags on their own lines, normally `[Intro]`, `[Verse]`,
`[Pre-Chorus]`, `[Chorus]`, `[Post-Chorus]`, `[Bridge]`, `[Instrumental]`, `[Solo]`, `[Outro]`.
Keep production prose in the prompt, not in lines that could be sung.

Reconcile syllable load, phrase lengths, section count, tempo, instrumental gaps, and duration.
The house estimate of ten sung lines per minute is only a starting heuristic: it is not a
model constraint and does not replace musical timing. Avoid both an overfilled short request
and a long empty outro. Keep repeated choruses stable unless variation is intentional.

Build the prompt using the [official music-caption-rewriter method](https://github.com/MiniMax-AI/MiniMax-Music3/tree/945655064d59b98004dd70002e7eb5c8c6e11373/skills/music-caption-rewriter):
read the primary family index, optionally one secondary, then at most three compatible
full templates linked from those indexes. Synthesize around this brief; do not copy template
sentences or inherit an unrelated vocalist, exact key, BPM, or emotional story. If source access
is unavailable, disclose the limitation and use the structure below; never claim template research occurred.

The exact `prompt` contains three sections:

- **Global Metadata:** approved genre, tempo/groove, meter and key when chosen, emotional arc,
  sonic character and production approach. Label deliberate proposals rather than presenting
  unchosen BPM/key as user requirements.
- **Vocal Details:** voice, register, delivery, harmonies and effects. Honor an instrumental
  request and identify the lead instrument instead of adding a vocalist.
- **Arrangement:** a timeline matching the lyric sections, with concrete instrument entrances,
  exits, energy changes, transitions and ending. Keep lyric lines out of the prompt.

Show the **entire lyrics and exact prompt**, plus requested duration and any optional seed.
Ask: **"Do you approve these exact lyrics, prompt and duration, or what should change?"**
Wait. Do not run the API or rewrite an approved prompt silently.

## 4. Recoup API call

Read `references/recoup-api.md`. Resolve authentication and the intended account using read-only
checks. Prepare the exact request with the approved prompt, lyrics and duration. Present:

- `POST https://api.recoupable.dev/api/music` and a sanitized request preview;
- the resolved account being charged, requested duration, and number of takes (default one);
- the current Recoup credit estimate and its source, or explicitly state if it cannot be verified.
  Do not substitute historical provider cost for the user's Recoup charge.

Ask: **"Approve this Recoup API request for one take on this account?"** Wait for explicit approval
of the displayed request and spending scope. Only then submit, record the returned generation ID,
and poll that same generation. Read-only polling is part of the approved call.

Do not re-POST because a request is slow, the network response was lost, or a take sounds wrong.
Reconcile pending requests first. A changed payload, a new take, or a different charged account
needs new approval for the affected material and call.

After completion, return the playable audio and generation ID, requested versus measured duration,
and reported cost when available. Measure the file and compare a timestamped transcript against
the approved lyrics when audio tooling is available; disclose anything not inspected. Report
omissions, repeats, pronunciation errors, cutoff or genre mismatch instead of calling an unreviewed
take finished. Ask the user to listen before using it for a video. Stop at the audio; do not
choose the paper style, storyboard, render a video, or publish without a subsequent request.
