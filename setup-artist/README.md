# Recoup Setup Artist Skill

An LLM skill for scaffolding a complete artist workspace inside a sandbox environment.

## What It Does

- Creates the full directory structure for an artist workspace
- Populates context files (identity, audience, era, services)
- Sets up the memory system (MEMORY.md + instructions)
- Creates README files for every directory so agents know what goes where
- Fills in artist data when available, uses placeholders when not

## Prerequisites

Run the `setup-sandbox` skill first to create the org/artist folder structure.

## Usage

> "Set up the workspace for [Artist Name]"

> "Create artist directory for [Artist Name]"

> "Initialize [Artist Name]'s artist workspace"

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Core skill instructions |
| `references/context-files.md` | Templates for all `context/` files |
| `references/memory-system.md` | Templates for the `memory/` directory |
| `references/directory-readmes.md` | Templates for `songs/`, `releases/`, `config/`, `library/`, `apps/` READMEs |
| `references/root-readme.md` | Template for the root `README.md` |
