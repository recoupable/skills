---
name: recoup-release-doc
description: >
  ARTIFACT: the release's master document (`RELEASE.md`) + generated deliverables
  (DSP pitch, press one-sheet, production spec). Use to create/maintain the single
  source-of-truth doc for an album/EP/single and pull deliverables from it.
  Triggers like "create a release doc", "set up a RELEASE.md", "update the release
  metadata/ISRCs", "generate a DSP pitch", "make a press one-sheet", "what's
  missing from the release". This is one of three release skills — for the CREATIVE
  DIRECTIONS use recoup-release-brief; for the DATED SCHEDULE use
  recoup-release-campaign; this one is the master DOC. For copy tone, use
  recoup-content-caption.
license: Proprietary
metadata:
  owner: agent@recoupable.com
  status: draft
  user-invocable: true
---

# Release Doc

Maintain `RELEASE.md` as the single source of truth for a release — one document
per release that every deliverable (DSP pitch, press one-sheet, production spec)
is generated from.

## Folder Structure

Keep each release in its own folder so the document and its assets travel
together. A simple, portable convention:

```text
releases/{artist-slug}/{release-slug}/
└── RELEASE.md
```

Use lowercase-kebab-case for both slugs (e.g. `gatsby-grace`, `blue-slide-park`).
This is the same `releases/{artist-slug}/{release-slug}/` workspace the
`recoup-release-start` orchestrator scaffolds, so standalone and bundled use
agree. The only hard rule: one `RELEASE.md` per release.

## Step 1: Identify the Release

When the user mentions a release, infer:

1. **Artist** — from the current workspace, conversation history, or ask
2. **Release name** — album title, EP name, or single title
3. **Release slug** — derive from the name (e.g. "Blue Slide Park" → `blue-slide-park`)

**If unclear, ask:**
> "Which artist and release are you referring to?"

## Step 2: Check if RELEASE.md Exists

Once the artist and release are identified:

```text
1. Navigate to the release folder: releases/{artist-slug}/{release-slug}/
2. Check if RELEASE.md exists
3. If YES -> read it and proceed
4. If NO  -> ask: "No RELEASE.md found for [Release]. Should I create one?"
```

## Step 3: Create, Update, or Pull

| User Intent | Action |
| --- | --- |
| Discussing a release | Read RELEASE.md, use as context |
| Adding information | Update the relevant section(s) |
| Asking for a deliverable | Pull data from RELEASE.md, generate output |
| Starting a new release | Create the folder + RELEASE.md from the template |

### Creating a New Release

```text
1. Create the release folder: releases/{artist-slug}/{release-slug}/
2. Copy the template (references/release-template.md) to RELEASE.md
3. Fill Section 1 (Project Snapshot) first
```

### Updating an Existing Release

1. Read the current RELEASE.md
2. Identify which section(s) need updates
3. Update only those sections
4. Note changes in Document History (Section 18)

## Core Principles

1. **Never fabricate data** — leave sections blank if information is missing
2. **Be proactive** — fill sections as information becomes available
3. **Respect sharing tags** — `[INTERNAL]`, `[SHAREABLE]`, `[OPS]` control distribution
4. **One document per release** — all release info lives in RELEASE.md
5. **Always confirm the release** — before making changes, confirm which release

## Sharing Tags

| Tag | Meaning |
| --- | --- |
| `[INTERNAL]` | Scrub before sharing externally |
| `[SHAREABLE]` | Safe for publicists, DSPs, management, agents |
| `[OPS]` | Operations/production team reference |

## Document Sections

| Section | Purpose | Sharing |
| --- | --- | --- |
| 1. Project Snapshot | Core release info | SHAREABLE |
| 2. Release Identifiers & Metadata | UPCs, ISRCs, track data | OPS |
| 3. Narrative & Positioning | Pitch, story, comparables | SHAREABLE |
| 4. Artist Background | Bio, streaming history | SHAREABLE |
| 5. Audience & Market Data | Demographics, geo data | SHAREABLE |
| 6. DSP & Streaming Strategy | Pitches, playlist targets | SHAREABLE |
| 7. Marketing Strategy | Campaign goals, KPIs | INTERNAL |
| 8. Social & Digital Marketing | Organic, paid, influencer | INTERNAL |
| 9. PR & Media Relations | Press targets, materials | SHAREABLE |
| 10. Visual & Creative Assets | Artwork, videos, canvases | SHAREABLE |
| 11. Physical Production | Vinyl, CD, cassette specs | OPS/INTERNAL |
| 12. Merch | Items, strategy | INTERNAL |
| 13. Experiential & OOH | Events, billboards | INTERNAL |
| 14. Touring & Live | Dates, venues, routing | SHAREABLE |
| 15. Team Contacts | All stakeholders | INTERNAL |
| 16. Budget Overview | Allocated/spent/remaining | INTERNAL |
| 17. Performance Tracking | Weekly KPIs, learnings | INTERNAL |
| 18. Links & Resources Hub | All asset links | — |

## Generating Deliverables

See `references/deliverables.md` for output patterns:

- **DSP Pitch** — pull from Sections 1, 3, 4, 5, 6
- **Press One-Sheet** — pull from Sections 1, 3, 4, 9, 10
- **Physical Production Spec** — pull from Sections 2, 11
- **Marketing Brief** — pull from Sections 1, 3, 5, 6, 7, 8
- **Tour Marketing Brief** — pull from Sections 1, 3, 5, 14

When generating any deliverable:

1. Check RELEASE.md for required data
2. Identify missing fields
3. Request missing info from the user OR generate with gaps noted
4. Format per the deliverable spec

## Template

The full release template is in `references/release-template.md`. Copy this file
to start a new release.

## Section Deep-Dive

See `references/section-guide.md` for detailed guidance on each section,
including:

- What each field means
- Common data sources
- Best practices for filling out
- Red flags to watch for

## Workflows

### New Release Setup

1. Copy the template → RELEASE.md
2. Fill Section 1 (Project Snapshot)
3. Fill Section 2.2 (Track Metadata) as available
4. Draft Section 3 (Narrative & Positioning)
5. Pull artist data for Sections 4-5
6. Build DSP pitch (Section 6)
7. Continue through remaining sections as the timeline progresses

### Pre-Release Checklist

Before announcement, verify these sections are complete:

- [ ] Section 1: All dates confirmed
- [ ] Section 2: UPC assigned, ISRCs for all tracks
- [ ] Section 3: Pitch and narrative finalized
- [ ] Section 6: DSP pitch submitted
- [ ] Section 9: Press materials ready
- [ ] Section 10: All visual assets delivered

### Release Week Checklist

- [ ] Section 6: Pre-save links live
- [ ] Section 7: Phase 2 actions executing
- [ ] Section 8: Paid ads launched
- [ ] Section 9: Press embargo lifted
- [ ] Section 17: Tracking dashboard ready

### Post-Release

- [ ] Section 17: Weekly KPIs logged
- [ ] Section 17: Wins and learnings documented
- [ ] Document History updated

## Example Interactions

### Creating a new release

> **User:** "Create a RELEASE.md for the new album 'Decisions'"
>
> **Process:**
> 1. Release = "Decisions", slug = `decisions`
> 2. Create `releases/decisions/RELEASE.md` from the template
> 3. Ask: "What's the release date?" (to fill Section 1)

### Adding metadata

> **User:** "Update the 'Sunrise' RELEASE.md with these ISRCs"
>
> **Process:**
> 1. Release = "Sunrise", slug = `sunrise`
> 2. Open `releases/sunrise/RELEASE.md`
> 3. Update Section 2.2 with ISRC data
> 4. If file not found → "No RELEASE.md for 'Sunrise'. Should I create one?"

### Generating a deliverable

> **User:** "Generate a DSP pitch from the Midnights RELEASE.md"
>
> **Process:**
> 1. Read `releases/midnights/RELEASE.md`
> 2. Pull data from Sections 1, 3, 4, 5, 6
> 3. Format per the `references/deliverables.md` spec
> 4. If missing fields → "Missing [fields]. Proceed with gaps noted?"

### Checking release status

> **User:** "What's missing from the 'For All The Dogs' release doc?"
>
> **Process:**
> 1. Read `releases/for-all-the-dogs/RELEASE.md`
> 2. Run through the Pre-Release Checklist
> 3. Report incomplete sections

## Quality bar

The #1 failure mode is fabricating data to fill a section — leave it blank and
flag it instead. The document is only valuable if every field can be trusted.
