# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Personal brand site for Billy Leet, Senior UX Researcher. Deployed via GitHub Pages to **billyleet.com** (CNAME configured). No build step, no framework, no package manager — just files served directly.

## The live file

**`index.html` is the only file served as the homepage.** All CSS and JS live inline in that file. There is no external stylesheet or bundler involved.

## Repo structure

- `snapshots/` — previous design iterations preserved for reference (not served)
- `archive/` — legacy portfolio case study pages and their associated assets/CSS (not linked from current design)

## Design system (in `index.html`)

**Fonts** (Google Fonts):
- `DM Serif Display` — display headings, pull quotes
- `Caveat` — handwritten/sticky note text, easter egg annotations
- `Inter` — body copy
- `JetBrains Mono` — labels, badges, monospace UI chrome

**CSS custom properties:**
```
--bg: #f5f0e8        warm off-white canvas
--text: #1a1a1a      near-black
--text-secondary: #4a4540
--accent: #0c6b6b    deep teal
--muted: #8a8580
--rule: #d0cbc2
```

**Aesthetic:** FigJam/Miro research board. Dot-grid background on `body` via `radial-gradient`. Sticky notes are absolutely positioned with per-note `--r` CSS custom property for rotation, composited in hover state as `rotate(var(--r)) scale(1.04) translateY(-3px)`.

## Key interactive behaviors

- **Draggable stickies:** `makeDraggable()` in the inline `<script>` handles mousedown/mousemove/mouseup. Position is set via inline `style.left`/`style.top`, which overrides the class-based position without affecting the rotation transform.
- **Easter eggs:** `.easter-egg` divs are positioned at `z-index: 0` underneath their corresponding `.sticky` (which is `z-index: 1`). Discovered by dragging a sticky aside.
- **Scroll animations:** `IntersectionObserver` adds `.visible` to `.animate-in` elements. Respects `prefers-reduced-motion`.
- **Side rail:** Fixed, `pointer-events: none`, `aria-hidden`. CSS `writing-mode: vertical-rl` + `@keyframes railScroll`.

## Deployment

Push to `master` → GitHub Pages auto-deploys to billyleet.com. No CI, no build step.
