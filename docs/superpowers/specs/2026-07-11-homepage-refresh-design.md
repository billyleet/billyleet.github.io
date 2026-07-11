# Homepage refresh: hero, section order, work grid, stickers, level copy, work CTA

**Date:** 2026-07-11
**Scope:** `index.html` (all changes inline), `stickers/` (regenerated PNG assets), new `tools/make-stickers` script.
**Out of scope:** `work/` encrypted case pages, `work-src/`, resume PDF content, snapshots/archive.

## 1. Hero

### Headline

Replace the hero statement with:

> I help teams ask better questions, turning research into clearer product decisions.

Keep the existing two-line presentation via `<br>`, breaking after the comma:
line 1 "I help teams ask better questions," / line 2 "turning research into clearer product decisions."
Role line stays **"Staff UX Researcher"** unchanged.

### Secondary action row

Below the yellow "Email me →" sticky CTA, add a new deliberate secondary row:

```text
View résumé → · LinkedIn ↗
```

- Both links in Caveat, ~1.15rem, `var(--accent)`; middot separator in `var(--muted)`.
- "View résumé →" links to `Billy-Leet-Resume.pdf`; "LinkedIn ↗" links to
  `https://www.linkedin.com/in/wleet/` (`target="_blank" rel="noopener noreferrer"`).
  The ↗ arrow marks it as external; the résumé keeps →.
- Visually subordinate to the sticky (no background, no sticky styling) but clearly
  larger/more actionable than the old 0.68rem mono links.
- Gets its own `fadeUp` animation delay slotted between the CTA (0.7s) and the
  availability line.

### Availability line

`.hero-availability` returns to being just the sentence, links removed:

> Based in Pittsburgh. Open to staff or senior individual-contributor roles, contract or full-time.

## 2. Level copy ("staff or senior")

Everywhere availability/openness is stated, use the phrase **"staff or senior"**
(that order, no slash):

- Hero availability line (above).
- About section closing paragraph: "I'm available for **staff or senior UX Research
  roles, contract or full-time.**" (rest of the sentence about question-changing teams
  stays).

Identity references ("Staff UX Researcher" in hero role, `<title>`, meta description
if present) stay "Staff".

## 3. Section order

Move the `#work` section markup to directly after `#hero`. New order:

1. hero
2. selected work (`#work`)
3. about (`#about`)
4. what I do (`#capabilities`)
5. career (`#career`)

Markup move only. Verify nothing in CSS (e.g., adjacent-sibling selectors, section
padding rules) or the inline JS (scroll-hint fade, sticky dragging, card swing)
assumes the old document order.

## 4. Work grid: featured + two

- Duolingo ("Flattening the Tree") becomes the featured card: **first in the DOM**,
  spanning both grid columns (`grid-column: 1 / -1`) via a `work-card--featured`
  modifier class.
- Featured card styling: title ~1.7rem (vs 1.35), sticker slightly larger
  (~84px vs 70px), hook may run one sentence longer. Hook copy may be lightly
  expanded but the existing hook is acceptable as-is; height should stay close to
  the current card height — wider, not dramatically taller.
- Change.org and Instagram remain standard cards in the 2-up row beneath
  (Change.org first, preserving reverse-chronological order among the two).
- Mobile (existing single-column breakpoint): all three stack; the featured modifier's
  size overrides reset so it renders like the others.

## 5. Work card CTA

`.wc-open` text changes on all three cards from "password needed →" to:

> view study →

Styling unchanged (Caveat, accent, underline on hover). No lock glyph on the cards;
the case pages themselves disclose the password gate.

## 6. Sticker normalization system

New script `tools/make-stickers` (Python + Pillow, self-bootstrapping venv like
`tools/encrypt`, or plain script if Pillow is available) that regenerates normalized
sticker assets from the existing sources:

Inputs: `stickers/change-org-sticker.svg` (or .png), `stickers/icons8-duolingo-logo-100.png`,
`stickers/icons8-instagram-100.png`.

Per asset:

1. Trim to alpha bounding box.
2. Scale by **perceived visual mass** (not identical pixel dims) so the three read
   as the same size; tune factors by eye against all three side by side.
3. Composite onto a common square transparent canvas at 2x display resolution
   (~200px canvas for 70px display).
4. Bake in a uniform **off-white (#fbfbf9-adjacent, slightly whiter) die-cut border**:
   dilate the alpha silhouette by a shared thickness and fill with the border color
   beneath the artwork. One shared thickness value tuned against Instagram's
   rounded-square vs Duolingo's owl silhouette vs the Change mark.
5. Change mark only: regenerate from the SVG as a flatter, single-tone version of
   Change.org red — reduce gradient/dimensionality and saturation so it sits with
   the two Icons8 flat glyphs.

Outputs: `stickers/sticker-change.png`, `stickers/sticker-duolingo.png`,
`stickers/sticker-instagram.png` (new names; originals kept as sources).

Usage in `index.html`:

- Work cards (`.wc-sticker`) and career timeline (`.tc-logo`) both switch to the
  normalized assets.
- Drop shadow remains a single shared CSS rule (existing `filter: drop-shadow(...)`),
  not baked into the PNGs.
- Because visual-mass scaling is baked into the assets, each context uses one
  shared width (`.wc-sticker` 70px / featured ~84px, `.tc-logo` its current size).
  The existing per-sticker position/rotation classes stay.
- Footer attribution line stays (Icons8 + Wikimedia credit still applies to the
  derived assets).

The Google logo (`icons8-google-100.png`, career timeline only) is included in the
normalization pass so timeline logos are consistent with each other.

## Verification

- Visual pass at desktop and <900px/<640px widths: hero hierarchy (sticky dominant,
  secondary row legible, availability quiet), featured card proportions, stacked
  mobile grid, sticker consistency in both work cards and timeline.
- Confirm draggable stickies, easter eggs, scroll-hint fade, and card swing still
  work after the section reorder.
- Grep for remaining "senior" copy to confirm no stale availability phrasing.
