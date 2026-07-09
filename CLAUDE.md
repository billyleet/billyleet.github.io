# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Personal brand site for Billy Leet, Senior UX Researcher. Deployed via GitHub Pages to **billyleet.com** (CNAME configured). No build step, no framework, no package manager — just files served directly.

## The live file

**`index.html` is the only file served as the homepage.** All CSS and JS live inline in that file. There is no external stylesheet or bundler involved.

## Repo structure

- `snapshots/` — previous design iterations preserved for reference (not served)
- `archive/` — legacy portfolio case study pages and their associated assets/CSS (not linked from current design)
- `stickers/` — PNG images: company logos used on career cards, plus WalterSticker.png (personal). Decorative Icons8 clip-art was removed in the board redesign.

## Design system (in `index.html`)

**Design concept:** the whole page is one live research board ("billy's board"). Canvas conventions — dot grid, a selected frame with corner handles, collaborator cursor chips, sticky notes, marker writing, highlighter swipes — carry the identity. Inspired by whiteboard tools generally; deliberately NOT a copy of FigJam's brand. Rationale: avoid the templated "AI design aesthetic" (cream bg + serif display + muted accent); every visual choice should derive from the board metaphor.

**Fonts** (Google Fonts):
- `Shantell Sans` — display (hero name, section headers, sticky pull quote, company names). Marker-drawn personality.
- `Caveat` — handwritten annotations, sticky titles, easter eggs, CTA
- `Inter` — body copy, cursor chip names
- `JetBrains Mono` — small meta only (dates, frame label, footer). Avoid reintroducing mono uppercase eyebrow labels — that's an AI-default tic we removed.

**CSS custom properties:**
```
--bg: #fbfbf9        canvas white
--text: #1c1d21      ink
--text-secondary: #4a4c53
--accent: #2f54d1    marker blue (links, frame, underlines, role labels)
--hl: rgba(245,230,66,0.55)  highlighter swipe behind section headers
--muted: #8b8d94
--rule: #dfe0e2
```

**Signature elements:** hero = a selected canvas frame (accent border, 4 corner `.handle` squares, mono `.frame-label`, two `.cursor-chip` collaborator cursors — billy + walter — hidden ≤640px). Section headers = Shantell Sans with a skewed `--hl` highlighter swipe via `::before`. Career track = hand-drawn wavy SVG path; card connectors are dashed with wonky-circle dots. Hand-drawn shapes use uneven `border-radius` (e.g. `255px 15px 225px 15px / …`).

**Deliberately absent (do not re-add):** pill/eyebrow badges, numbered section labels (01/02/03), scroll-triggered fade-up animations, bobbing chevron scroll hints, decorative stock clip-art. Sticky notes are absolutely positioned with per-note `--r` CSS custom property for rotation, composited in hover state as `rotate(var(--r)) scale(1.04) translateY(-3px)`.

**Sticky note fold effect:** Each sticky has a cut corner via `background: linear-gradient(315deg, transparent 17px, var(--sticky-bg) 0)` and a darker fold triangle via `::after` with `clip-path: polygon(0 0, 100% 0, 0 100%)` (24×24px). Shadows use `filter: drop-shadow()` (not `box-shadow`) so the cut corner is truly transparent and shows the page background through it.

## Key interactive behaviors

- **Draggable stickies:** Pointer Events (mouse/touch/pen) in the inline `<script>`; `.sticky` has `touch-action: none` above 640px. Position is set via inline `style.left`/`style.top`, which overrides the class-based position without affecting the rotation transform.
- **Easter eggs:** `.easter-egg` divs are positioned at `z-index: 0` underneath their corresponding `.sticky` (which is `z-index: 1`). Discovered by dragging a sticky aside.
- **Scroll hint:** Handwritten "the good stuff ↓" note below hero fades out after 50px of scroll.
- **Card swing:** timeline cards swing on hover with amplitude proportional to cursor velocity (Web Animations API; respects `prefers-reduced-motion`).

## Deployment

Push to `master` → GitHub Pages auto-deploys to billyleet.com. No CI, no build step.
