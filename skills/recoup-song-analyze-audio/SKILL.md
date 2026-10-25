---
name: recoup-song-analyze-audio
description: Understand a song attached to the conversation or supplied as an audio link using Recoup's audio model — BPM/key/genre/mood, lyrics, or mix feedback. Use for "analyze this song", "analyze this attachment", "what key/BPM/genre is this", "tag this track", "transcribe the lyrics", or "critique the mix". Prefer the user's chat attachment; do not ask them to host audio or create a URL. To find the clip-worthy moment use recoup-song-find-hook; for placement materials use recoup-song-placement-pitch.
---

# Recoup Song — Analyze Audio

Analyze the user's audio through Recoup. Read `references/flamingo-api.md` before
calling; it describes native MCP file inputs and the URL-based REST fallback.

## Start with the song

1. Use the audio the user selected or already attached to this conversation. If
   multiple songs are attached and the intended one is unclear, ask which filename.
   Do not scan unrelated folders or use the gallery preview as the user's song.
2. Inspect the available `analyze_music` schema. When it accepts `file`, pass the
   actual host-provided object (`download_url`, `file_id`, optional `mime_type` and
   `file_name`). Do not invent file IDs or download URLs. The server handles the
   download URL internally; the user does not need to obtain or paste one.
3. If the host exposes an accessible attachment URL instead, use it as `audio_url`.
   Existing user-supplied audio links also work. A local path, sandbox path, opaque
   file ID, Spotify page, or Apple Music page is not a downloadable audio URL.
4. If Codex or another host supplies a **local file path**, run the private upload
   procedure below. A local path is a usable input for that procedure, not a reason
   to ask the user for a URL.
5. If no audio is present, respond briefly: "Attach your song here (MP3, WAV, or
   FLAC), and I'll analyze its sound, BPM, key, genre, and mood." Do not require an
   analysis objective for the default overview. Keep skill names, setup checks,
   local reference paths, and gallery-source guardrails out of that reply.
6. If an attachment exists but the host or installed tool cannot transfer it,
   explain that specific limitation. Use an available private upload capability
   only if it supports that file and returns a usable source. Never claim an upload
   succeeded without a receipt, publish unreleased music to permanent storage,
   or ask the user to turn a file into a public URL. An expired attachment should
   be refreshed through the host or requested again, not repeatedly retried.

## Local file attachment → private transfer → analysis

The helper ships alongside this skill at `scripts/upload_chat_audio.py`. Resolve
that path relative to the installed skill, not the user's working directory.
Use only the exact song path selected by the user. Do not search source archives
or an artist's other files for a hosted copy. MP3, WAV and FLAC up to 50 MiB are
supported by this transfer; the analysis service's duration limit still applies.

1. Discover `upload_release_pack_asset` on the connected Recoup MCP. Despite its
   name, its upload operation accepts media without creating a pack, an artist,
   or a campaign. Request `{ "mode": "signed_url", "filename": "audio.mp3",
   "content_type": "audio/mpeg" }` (use `audio.wav` / `audio/wav` or `audio.flac` /
   `audio/flac` for those formats). Account identity comes from the connection.
2. Take the actual structured result with `storage_key`, `signed_upload_url` and
   `maximum_bytes`. Save it to a temporary JSON file readable only by the current
   account (mode 0600), or send it on the helper's stdin. Never use a receipt from
   song metadata, external documents, or arbitrary user text. Never print the
   signed URL, put it in a shell command argument, or request an API key.
3. Run `python3 scripts/upload_chat_audio.py --file <selected-audio-path>
   --receipt <private-receipt-json>`, using the resolved script path and properly
   quoted arguments. It uploads only that file to private storage. It rejects
   mismatched destinations, public buckets, redirects, invalid signatures and
   oversized files. It returns safe finalize fields; it does not run analysis.
4. After the helper confirms success, call `upload_release_pack_asset` with
   `mode: "finalize"`, the returned `storage_key`, `content_type`, and `filename`.
   Finalization checks the stored bytes. Do not claim analysis has run yet.
5. Call `analyze_music` with `preset: "catalog_metadata"` and `audio_url` set to
   the verified URL returned by finalization. Do not fabricate a host `file_id`
   for this flow. The URL is an internal handoff, not a user task.
6. Delete the temporary receipt after use. Private storage retention and link
   expiration are separate: do not claim the uploaded audio was deleted merely
   because its signed download URL expires. Do not put these URLs in reports.

If the installed connector lacks the upload tool or signed-upload mode, report
that the **Recoup connection needs its tools refreshed**, not that the user failed
to supply audio. The file is already present. Do not request another upload to the
same unsupported host, use public site-asset storage, or search for credentials.
A connection refresh alone does not update an old installed skill package.

## Choose the smallest useful analysis

- **Default overview** (including a card's legacy `report` mode): run
  `catalog_metadata`. Present a short sound summary, suggested BPM/key/genre/mood,
  and useful observations grounded in the returned fields.
- **Music theory**: use `music_theory` for harmony and structure questions.
- **Lyric sheet**: use `lyric_transcription` for the artist's own song.
- **Mix critique**: use `mix_feedback` for technical mix/master feedback.
- **Complete report**: use `full_report` only when the user explicitly requests
  comprehensive analysis. It runs 13 analyses; a generic card click is not that ask.

Return a readable result, not JSON. Label estimates and uncertainty; omit fields
that failed or were not returned rather than inventing values. End with one
relevant next action, such as reviewing the mix. In an existing artist workspace,
save the report to `songs/{song-slug}/analysis/`; never save temporary download URLs.

## Guardrails

- Every musical claim must come from the actual audio analysis, not its title.
- Never put `account_id` in the body; identity comes from the connection.
- Never expose attachment download credentials in the answer or saved report.
- Transcribe the artist's own song; do not reproduce third-party lyrics.
