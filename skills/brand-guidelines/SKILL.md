---
name: recoupable-brand-guidelines
description: Applies Recoupable's official brand identity to any artifact—presentations, UI, marketing materials, illustrations, or copy. Use when brand colors, typography, visual formatting, voice, or design standards apply.
version: 1.0.0
author: Recoupable
---

# Recoupable Brand Guidelines

## Overview

This skill provides Recoupable's complete brand identity system. Use it to ensure all generated artifacts—UI components, presentations, social graphics, marketing copy, or illustrations—align with the Recoupable brand 100% of the time.

**Keywords**: branding, visual identity, typography, colors, Recoupable, presentations, UI design, marketing, illustrations, voice, tone

---

## Brand Philosophy

Recoupable is building the new music industry—a world where humans do what they love, and AI agents handle the rest.

**We are NOT a sterile software company.** We live at the intersection of:
- A record label that helps creatives transcend into pop culture
- AI infrastructure and education
- Creative freedom

**Brand Mood**: Hopeful, warm, human-first, utopian but grounded. Never cold, corporate, or dystopian.

**Tagline**: "Spend more time doing what you love. Let agents handle the rest."

---

## Typography

### Font Stack

| Role | Font | Weight | Usage |
|------|------|--------|-------|
| **Headings (UI/Product)** | Plus Jakarta Sans | 600-700 (SemiBold/Bold) | UI headers, section titles, buttons |
| **Headings (Editorial)** | Instrument Serif | 400 (Italic) | Blog titles, display text, accent phrases |
| **Body Text** | Geist | 400-500 | Paragraphs, descriptions, UI text |
| **Monospace/Code** | Geist Mono | 400 | Code blocks, technical content |
| **Fallbacks** | system-ui, -apple-system, sans-serif | — | When primary fonts unavailable |

### Mixed Typography Pattern

Recoupable uses a distinctive **mixed typography** approach for headlines:

```
The next era of          ← Plus Jakarta Sans Bold
music business           ← Instrument Serif Italic (ACCENT)
is agentic               ← Plus Jakarta Sans Bold
```

**Rule**: Use Instrument Serif (italic) to highlight key words or phrases within a headline. This creates editorial elegance and draws attention to the most important concepts.

**Examples**:
- "Meet Your New AI *Record Label*"
- "Over 100+ pre-trained AI agents made for *music biz* operations"
- "*Fully customizable* for your business"

### Type Hierarchy

| Level | Font | Size | Weight |
|-------|------|------|--------|
| H1 (Display) | Plus Jakarta Sans | 48-72px | Bold |
| H2 (Section) | Plus Jakarta Sans | 32-40px | SemiBold |
| H3 (Subsection) | Plus Jakarta Sans | 24-28px | SemiBold |
| Body | Geist | 16-18px | Regular |
| Caption/Label | Geist | 12-14px | Medium |
| Accent Phrase | Instrument Serif | Matches parent | Italic |

---

## Color System

### Primary Palette (Monochrome)

The core UI uses a strict black/white/grey palette:

| Name | Hex | HSL | Usage |
|------|-----|-----|-------|
| **Black** | `#000000` | 0 0% 0% | Primary text (light mode), buttons |
| **Near-Black** | `#0A0A0A` | 0 0% 4% | Dark mode backgrounds |
| **Dark Grey** | `#71717A` | 240 4% 46% | Secondary text, muted elements |
| **Mid Grey** | `#A1A1AA` | 240 4% 65% | Tertiary text, placeholders |
| **Light Grey** | `#E6E6E6` | 0 0% 90% | Borders, dividers |
| **Off-White** | `#FAFAFA` | 0 0% 98% | Cards, surfaces (light mode) |
| **White** | `#FFFFFF` | 0 0% 100% | Backgrounds, text (dark mode) |

### Accent Palette (Illustration Colors)

Used sparingly for visual interest, illustrations, charts, and highlights:

| Name | Hex | Usage |
|------|-----|-------|
| **Fresh Green** | `#7FB875` | Nature, growth, positivity |
| **Teal Green** | `#345A5D` | Sophistication, depth |
| **Sky Blue** | `#BBDCF4` | Atmosphere, calm, openness |
| **Warm Yellow** | `#F5C66E` | Energy, creativity, warmth |
| **Warm Orange** | `#F5A14E` | Accents, calls-to-action |
| **Soft White** | `#F9F9F9` | Clouds, highlights |
| **Muted Grey** | `#D3D3D3` | Architecture, neutrality |
| **Lavender** | `#BD99B3` | Subtle accent, creativity |
| **Deep Purple** | `#720762` | Premium, bold accent |

### Color Application Rules

1. **UI elements**: Always monochrome (black/white/grey)
2. **Backgrounds**: Atmospheric (sky, clouds, stars) or illustrated scenes
3. **Accent colors**: Reserved for illustrations, charts, or intentional highlights
4. **Text**: Black on light, white on dark—never colored text in UI
5. **Buttons**: Black fill with white text (primary), grey outline (secondary)

---

## Backgrounds

### The Juxtaposition Technique

Recoupable's signature look combines:
- **Background**: Colorful, illustrated, Ghibli-inspired scenes—often **blurred**
- **Foreground**: Clean, modern, minimal UI elements

This creates warmth and humanity while maintaining usability.

### Background Types

| Type | Light Mode | Dark Mode | Usage |
|------|------------|-----------|-------|
| **Atmospheric** | Soft sky with clouds (faint blue-white) | Starry night sky | Default for pages |
| **Illustrated** | Blurred utopian city/nature scenes | Same, darker | Marketing, hero sections |
| **Solid** | `#FFFFFF` or `#FAFAFA` | `#0A0A0A` | Cards, modals, focus areas |
| **Gradient** | Subtle vertical sky gradient | Dark to darker | Sections, transitions |

### Background Colors

- **Light mode sky**: Faint blue-white, almost off-white (`~#F5F9FC`)
- **Dark mode night**: Near-black with subtle star texture

---

## UI Components

### Cards

```css
border-radius: 12px (0.75rem)
border: 1px solid #E6E6E6 (light) / #27272A (dark)
background: white (light) / #0A0A0A (dark)
padding: 24px
box-shadow: subtle, optional (0 1px 3px rgba(0,0,0,0.1))
```

### Pill Badges/Tags

```css
border-radius: 9999px (full)
border: 1px solid #E6E6E6
background: transparent or white
padding: 8px 16px
font-size: 14px
font-weight: 400-500
```

### Buttons

**Primary:**
```css
background: #000000
color: #FFFFFF
border-radius: 9999px (pill) or 8px (rounded)
padding: 12px 24px
font-weight: 500
```

**Secondary:**
```css
background: transparent
border: 1px solid #E6E6E6
color: #000000
```

### Inputs

```css
border-radius: 9999px (pill style) or 8px
border: 1px solid #E6E6E6
background: white
padding: 12px 20px
```

### Connector Lines (Diagrams)

```css
stroke: #000000
stroke-dasharray: 8 4 (dashed)
stroke-width: 1-2px
```

---

## Logo Usage

### Logo Components

1. **Icon**: Stylized musical note mark
2. **Wordmark**: "Recoupable" in Plus Jakarta Sans Bold
3. **Lockup**: Icon + Wordmark together

### Logo Colors

| Context | Icon | Wordmark |
|---------|------|----------|
| Light backgrounds | Black | Black |
| Dark backgrounds | White | White |
| Never | Colored | Colored |

### Logo Placement

- **Presentations**: Bottom-right corner
- **Headers**: Top-left
- **Favicons**: Icon only

### Clear Space

Maintain minimum clear space equal to the height of the icon on all sides.

---

## Illustration Style

### Visual Universe

The Recoupable world is a near-future creative urban city where nature and technology weave together seamlessly. Glass towers with rooftop gardens, flowing plazas with flowering trees, and warm human activity throughout.

### Style Reference

- **Aesthetic**: Semi-anime, semi-realistic painterly realism
- **References**: Studio Ghibli backgrounds, Makoto Shinkai films (Your Name, Weathering With You)
- **Mood**: Hopeful, contemplative, harmonious, utopian with dreamlike wonder

### Illustration Palette

| Color | Hex | Role |
|-------|-----|------|
| Fresh Green | `#7FB875` | Hills, vines, trees, nature |
| Sky Blue | `#BBDCF4` | Open sky, atmosphere |
| Warm Yellow | `#F5C66E` | Blossoms, sunlight, warmth |
| Warm Orange | `#F5A14E` | Flowers, human warmth |
| Soft White | `#F9F9F9` | Clouds, fabric, highlights |
| Muted Grey | `#D3D3D3` | Architecture, buildings |

### Lighting

- Soft natural daylight with diffused glow
- Light haze, gentle bloom on highlights
- Never harsh specular glare or neon
- Night: Lanterns and window glow, never harsh neon

### The Robot Companions

Five main AI companions, all toddler-sized, rounded, and endearingly imperfect:

| Name | Role | Personality |
|------|------|-------------|
| **Hika** | Outreach | Bright, social, momentum-seeking |
| **Ken** | Research | Patient, observant, unflappable |
| **Hoko** | Reporting | Orderly, precise, reassuring |
| **Ka** | Creative | Playful, inventive, mischievous |
| **Kei** | Planning | Calm, structured, motivational |

All companions share: rounded edges, approachable faces, light wear/patina, and supportive (never starring) presence.

---

## Voice & Tone

### Core Principles

1. **Warm, not corporate**: Write like a thoughtful friend, not a press release
2. **Short sentences**: Keep it tight. Breathe between thoughts.
3. **Non-directive**: Guide, don't command
4. **Human-first**: The technology serves people, not the reverse

### Voice Examples

**Do:**
- "Welcome. You brought the weather with you."
- "Let's open the doors."
- "I'll keep time; you keep pace."

**Don't:**
- "Welcome to the Recoupable platform! Click here to get started."
- "Leverage our AI-powered solutions to optimize your workflow."
- "ACTION REQUIRED: Complete your profile now."

### Headlines

- Lead with benefit or vision
- Use Instrument Serif italic for the emotional anchor word
- Keep it punchy

**Examples:**
- "The next era of *music business* is agentic"
- "Meet Your New AI *Record Label*"
- "*Artist Intelligence* for the modern music company"

---

## Presentation Design

### Slide Structure

1. **Title/Hero slides**: Atmospheric background, bold headline, Instrument Serif accent
2. **Content slides**: Lighter background, cards for organized info
3. **Diagram slides**: Dashed connector lines, clear flow

### Consistent Elements

- Logo + wordmark: Bottom-right corner
- Section headers: Plus Jakarta Sans Bold with horizontal rule
- Cards: Rounded corners, subtle borders
- Connectors: Black dashed lines

### Slide Colors

| Element | Light Slides | Dark Slides |
|---------|--------------|-------------|
| Background | Faint sky/clouds | Starry night |
| Text | Black | White |
| Cards | White | Dark grey |
| Borders | Light grey | Dark grey |

---

## Quick Reference

### Do's ✓

- Use atmospheric/illustrated backgrounds
- Mix Plus Jakarta Sans with Instrument Serif accents
- Keep UI strictly monochrome
- Blur illustrations behind clean UI
- Write warmly and briefly
- Show humans first, technology supporting

### Don'ts ✗

- Use flat solid color backgrounds
- Use colored text in UI
- Write in corporate/marketing speak
- Make technology the hero over humans
- Use neon, harsh lighting, or dystopian imagery
- Clutter—always leave breathing room

---

## File Formats & Assets

### Recommended Formats

| Asset Type | Format |
|------------|--------|
| Logos | SVG (vector), PNG (raster) |
| Icons | SVG |
| Illustrations | PNG (with transparency) |
| Backgrounds | JPG or WebP (optimized) |
| Fonts | WOFF2, TTF |

### Font Files

- Plus Jakarta Sans: [Google Fonts](https://fonts.google.com/specimen/Plus+Jakarta+Sans)
- Instrument Serif: [Google Fonts](https://fonts.google.com/specimen/Instrument+Serif)
- Geist: [Vercel](https://vercel.com/font)
- Geist Mono: [Vercel](https://vercel.com/font)

---

## CSS Variables (Reference)

```css
:root {
  /* Typography */
  --font-heading: "Plus Jakarta Sans", system-ui, sans-serif;
  --font-body: "Geist", system-ui, sans-serif;
  --font-mono: "Geist Mono", monospace;
  --font-accent: "Instrument Serif", Georgia, serif;
  
  /* Primary Colors */
  --color-black: #000000;
  --color-white: #FFFFFF;
  --color-grey-dark: #71717A;
  --color-grey-mid: #A1A1AA;
  --color-grey-light: #E6E6E6;
  --color-off-white: #FAFAFA;
  
  /* Accent Colors */
  --color-green: #7FB875;
  --color-teal: #345A5D;
  --color-sky: #BBDCF4;
  --color-yellow: #F5C66E;
  --color-orange: #F5A14E;
  --color-lavender: #BD99B3;
  --color-purple: #720762;
  
  /* Radii */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;
}
```

---

*© 2025 Recoupable LLC. All rights reserved.*
