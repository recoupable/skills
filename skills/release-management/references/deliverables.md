# Deliverables Guide

This guide covers how to generate common deliverables from a RELEASE.md document.

---

## Table of Contents

1. [DSP Pitch](#dsp-pitch)
2. [Press One-Sheet](#press-one-sheet)
3. [Physical Production Spec](#physical-production-spec)
4. [Marketing Brief](#marketing-brief)
5. [Tour Marketing Brief](#tour-marketing-brief)
6. [Shareable Export](#shareable-export)
7. [Weekly Report](#weekly-report)

---

## DSP Pitch

**Purpose:** Submit to Spotify For Artists, Apple Music for Artists, Amazon Music for Artists

**Source Sections:** 1, 3, 4, 5, 6

### Spotify For Artists Format (500 character limit)

Pull from:
- Section 1: Artist name, project title, release date, genre
- Section 3.1: Elevator pitch
- Section 4.2: Key streaming stats, certifications
- Section 5.2: Top cities/countries
- Section 6.2: Focus track and why

**Template:**

```
[ARTIST] releases [PROJECT TITLE] on [DATE]. [2-3 SENTENCE PITCH FROM 3.1].

Key stats: [STREAMING HIGHLIGHTS FROM 4.2]
Top markets: [TOP 3 CITIES FROM 5.2]
Focus track: "[TRACK NAME]" - [RATIONALE FROM 6.2]

Genre: [PRIMARY GENRE] / [SUBGENRE]
```

### Apple Music Format (No strict limit)

Same content but can expand narrative from Section 3.2.

### Required Fields Checklist

- [ ] Artist name
- [ ] Project title
- [ ] Release date
- [ ] Genre(s)
- [ ] Pitch (2-3 sentences)
- [ ] Key streaming stats
- [ ] Top markets
- [ ] Focus track + rationale

---

## Press One-Sheet

**Purpose:** Media kit for publicists, journalists, outlets

**Source Sections:** 1, 3, 4, 9, 10

### Structure

```
═══════════════════════════════════════
[ARTIST NAME]
[PROJECT TITLE]
[RELEASE DATE]
═══════════════════════════════════════

ABOUT THE RELEASE
[Extended narrative from Section 3.2]

PROJECT HIGHLIGHTS
[Bullets from Section 3.3]

FOR FANS OF
[Comparables from Section 3.5]

ABOUT THE ARTIST
[Bio from Section 4.1]

STREAMING HIGHLIGHTS
[Stats from Section 4.2]

PRESS HIGHLIGHTS
[Coverage from Section 4.3]

ASSETS
Artwork: [Link from 10.2]
Press Photos: [Link from 9.3]
EPK: [Link from 9.3]

CONTACT
Publicist: [From Section 15 - only if sharing externally]

═══════════════════════════════════════
```

### Required Fields Checklist

- [ ] Artist name
- [ ] Project title
- [ ] Release date
- [ ] Extended narrative
- [ ] Artist bio
- [ ] At least 3 streaming stats
- [ ] Press photo link
- [ ] Publicist contact

---

## Physical Production Spec

**Purpose:** Manufacturing partner briefing (vinyl plant, CD plant)

**Source Sections:** 2, 11

### Structure

```
═══════════════════════════════════════
PHYSICAL PRODUCTION SPECIFICATION
[PROJECT TITLE] by [ARTIST NAME]
═══════════════════════════════════════

IDENTIFIERS
UPC: [From 2.1]
Street Date: [From Section 1]

AUDIO
Track count: [Count from 2.2]
Total runtime: [Sum of durations from 2.2]
Master WAVs: [Link from 2.3]

TRACKLIST
[Full tracklist from 2.2 with ISRCs]

VINYL SPECIFICATIONS
Quantity: [From 11.1]
Color: [From 11.1]
Packaging: [From 11.2]
Inserts: [From 11.2]

CD SPECIFICATIONS
Quantity: [From 11.1]
[Additional specs]

CASSETTE SPECIFICATIONS
Quantity: [From 11.1]
Color: [From 11.1]

TIMELINE
[Full timeline from 11.3]

PARTNERS
Manufacturer: [From 11.3]
Fulfillment: [From 11.3]

═══════════════════════════════════════
```

### Required Fields Checklist

- [ ] UPC
- [ ] Street date
- [ ] Full tracklist with ISRCs
- [ ] Master audio link
- [ ] Format quantities
- [ ] Packaging specs
- [ ] Manufacturing timeline
- [ ] Partner contacts

---

## Marketing Brief

**Purpose:** Internal campaign planning document

**Source Sections:** 1, 3, 5, 6, 7, 8

### Structure

```
═══════════════════════════════════════
MARKETING BRIEF
[PROJECT TITLE] by [ARTIST NAME]
Campaign Period: [ANNOUNCEMENT DATE] to [RELEASE DATE + 4 WEEKS]
═══════════════════════════════════════

RELEASE OVERVIEW
[Section 1 snapshot]

THE STORY
[Section 3.1 pitch]
[Section 3.3 highlights]

TARGET AUDIENCE
Demographics: [From 5.3]
Top markets: [From 5.2]
Core fanbase: [From 5.4]

CAMPAIGN GOALS
[From 7.1]

KEY KPIS
[Table from 7.2]

ROLLOUT PHASES
[From 7.3 - all three phases]

SOCIAL STRATEGY
[From 8.1 and 8.2]

PAID MEDIA PLAN
[From 8.4]

TOTAL BUDGET: [From 8.4]

═══════════════════════════════════════
```

---

## Tour Marketing Brief

**Purpose:** Geo-targeted marketing around tour dates

**Source Sections:** 1, 3, 5, 14

### Structure

```
═══════════════════════════════════════
TOUR MARKETING BRIEF
[TOUR NAME]
[ARTIST NAME] - [PROJECT TITLE]
═══════════════════════════════════════

TOUR OVERVIEW
Dates: [From 14.1]
Markets: [Count of cities from 14.2]
Agent: [From 14.1]

RELEASE TIE-IN
Release date: [From Section 1]
Pitch: [From 3.1]

MARKET PRIORITIES
[Based on overlap between 14.2 routing and 5.2 top cities]

HIGH-PRIORITY MARKETS (Top streaming + show date)
[List]

ROUTING
[Full table from 14.2]

GEO-TARGETING STRATEGY
[From 14.3]

LOCAL CONTENT PLAN
[From 14.3]

═══════════════════════════════════════
```

---

## Shareable Export

**Purpose:** Version of RELEASE.md safe for external partners

**Process:**

1. Copy full RELEASE.md
2. Remove all sections marked `[INTERNAL]`:
   - Section 7: Marketing Strategy
   - Section 8: Social & Digital Marketing
   - Section 12: Merch
   - Section 13: Experiential & OOH
   - Section 15: Team Contacts
   - Section 16: Budget Overview
   - Section 17: Performance Tracking
3. Remove `[INTERNAL]` subsections within `[OPS]` sections:
   - Section 2.3: Audio Asset Links
4. Keep all `[SHAREABLE]` and `[OPS]` sections
5. Rename to `RELEASE-EXTERNAL.md`

---

## Weekly Report

**Purpose:** Status update for stakeholders

**Source Sections:** 17, 7.2

### Structure

```
═══════════════════════════════════════
WEEKLY CAMPAIGN REPORT
[PROJECT TITLE] by [ARTIST NAME]
Week [N] | [DATE RANGE]
═══════════════════════════════════════

KPI SUMMARY
[Week's row from 17.1 vs targets from 7.2]

| Metric | This Week | Target | Status |
|--------|-----------|--------|--------|
| Spotify Streams | ___ | ___ | 🟢/🟡/🔴 |
| Apple Streams | ___ | ___ | 🟢/🟡/🔴 |
| TikTok Views | ___ | ___ | 🟢/🟡/🔴 |
| IG Engagement | ___ | ___ | 🟢/🟡/🔴 |

WINS THIS WEEK
[From 17.2]

ADJUSTMENTS
[From 17.2]

NEXT WEEK PRIORITIES
[Based on current phase from 7.3]

═══════════════════════════════════════
```

---

## Generating Any Deliverable

### Workflow

1. **Identify the deliverable type** from this guide
2. **Check source sections** for required data
3. **Note missing fields** - request from user or mark as TBD
4. **Generate output** following the template structure
5. **Verify sharing tags** — don't include [INTERNAL] data in external docs

### Handling Missing Data

When generating a deliverable with missing fields:

```
⚠️ MISSING INFORMATION

The following fields are required but not in RELEASE.md:
- [Field 1]
- [Field 2]

Please provide this information or confirm you want to proceed with gaps.
```

### Custom Deliverables

For deliverables not covered here:
1. Identify which sections contain relevant data
2. Check sharing tags for each section
3. Structure output appropriate to audience
4. Request user approval before sharing externally
