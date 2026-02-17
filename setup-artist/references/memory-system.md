# Memory System Templates

Two files to create in `memory/`.

---

## `memory/README.md`

```markdown
---
name: Memory
description: "How the memory system works. Read this before writing to any memory file. This directory holds everything agents have LEARNED about {Artist Name} — not who the artist IS (that's context/), and not reference material (that's library/)."
---

# Memory

This directory is the artist's **learned knowledge** — what agents discover through doing the work. It grows over time as agents interact with the artist, create content, manage releases, and learn what works.

## Structure

memory/
├── README.md          ← You are here
├── MEMORY.md          ← Core index: always read first (keep under ~200 lines)
├── {topic}.md         ← Topic files: detailed notes (created as needed)
├── log/               ← Session logs: raw, append-only (created on first session)
│   └── YYYY-MM-DD.md
└── archive/           ← Past era memories (created when eras change)
    └── {era-slug}/

Only `README.md` and `MEMORY.md` ship at creation. Everything else is created by agents as they work.

## Files

### `MEMORY.md` — Core Index

The single most important file. **Read this first every session.**

- Contains curated, distilled knowledge about the artist
- Bounded: keep it under ~200 lines
- **Edit, don't just append** — update facts when they change, remove what's outdated
- When a section gets too detailed, move it into a topic file and leave a reference

### Topic Files (`{topic}.md`)

Created by agents when `MEMORY.md` sections grow too long. Examples:
- `content-learnings.md` — what works and doesn't for this artist's content
- `audience-insights.md` — patterns in audience behavior
- `process-notes.md` — how things work for this artist

**Format:**

---
name: {Topic Name}
description: "{What this file covers and when to read it.}"
era: {release-slug}
---

### `log/` — Session Logs

Raw, append-only logs of what happened each session. Created on first use.

**Format:** `log/YYYY-MM-DD.md`

Multiple entries per day are appended to the same file. Don't edit past entries.

### `archive/` — Past Era Memories

When an era changes, move old topic files and logs here to keep the active memory clean.

## Session Lifecycle

### Start of Session
1. Read `memory/MEMORY.md` — get current knowledge
2. Check for today's log (`memory/log/YYYY-MM-DD.md`) — resume context if exists
3. Read `context/era.json` — know the current phase

### During Session
- Learn something durable → **update** the relevant section in `MEMORY.md`
- Discover a correction → **edit** `MEMORY.md` (replace the old fact)
- Complete something or make a decision → **append** to today's log
- Need detailed history → **read** topic files or past logs

### End of Session
- Review: did anything important happen that's not in `MEMORY.md`?
- If `MEMORY.md` is getting long → move details into topic files

### Periodic Maintenance
- Review recent logs → promote key insights to `MEMORY.md`
- Remove or update outdated facts in `MEMORY.md`
- If era changed → archive old era memories

## What Goes Where

| I learned... | Write it to... |
|-------------|---------------|
| A durable fact about the artist or their work | `MEMORY.md` (edit/update) |
| Detailed performance data or analysis | A topic file (e.g., `content-learnings.md`) |
| What happened in today's session | `log/YYYY-MM-DD.md` (append) |
| Something that corrects a previous belief | `MEMORY.md` (replace the old fact) |

## What Does NOT Go Here

| This kind of information... | Goes in... |
|----------------------------|-----------|
| Who the artist is (identity, brand, voice) | `context/artist.md` |
| Who the audience is | `context/audience.md` |
| Current release and phase | `context/era.json` |
| Reference docs, research, reports | `library/` |
| To-do items and tasks | `context/tasks.md` |
```

---

## `memory/MEMORY.md`

```markdown
---
name: Memory
description: "Curated knowledge about {Artist Name}. Read this first every session. Keep concise — move details into topic files when sections grow."
---

# Memory

<!-- 
  This file is the core index of everything agents have learned about this artist.
  
  Guidelines:
  - Keep under ~200 lines
  - EDIT existing facts when they change — don't just append
  - When a section gets too detailed, move it to a topic file (e.g., content-learnings.md)
    and leave a one-line reference here
  - Delete or update anything that's no longer true
  
  Structure will emerge naturally. Let the work define what sections you need.
-->
```
