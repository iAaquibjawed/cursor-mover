# Cursor Mover — Logo & Icon Brief

Everything a designer (or an image model) needs to produce the app icon. Drop
the finished files into this folder as `icon.icns` and `icon.png`; the
PyInstaller spec picks up `assets/icon.icns` automatically.

---

## 1. What the product is

Cursor Mover is a **macOS menu bar utility**. It sits quietly in the menu bar and
moves the mouse pointer to a random spot on screen every N seconds, so the Mac
never registers as idle — no sleep, no screen lock, no "away" status.

The feeling to convey: **quiet, automatic, precise, trustworthy.** It is a small
system utility, not a game or a toy. It should look like it belongs next to
Raycast, Rectangle, Bartender, and CleanShot X — not next to a cartoon app.

## 2. The core idea

> **A pointer that moves by itself.**

The whole concept is one arrow plus evidence of motion. Nothing else is needed.
Resist adding a mouse, a computer, a clock, or a coffee cup — those describe the
side effect, not the app.

## 3. Composition

- **Container:** the macOS Big Sur "squircle" — a rounded superellipse, not a
  plain rounded rectangle. Corner radius ≈ 22.5% of the canvas.
- **Safe area:** the artwork occupies the centre ~72% of the canvas. macOS
  already shrinks and shadows the squircle, so do not add your own drop shadow
  or outer glow.
- **Subject:** a single classic macOS arrow pointer, tilted about 20° clockwise
  from vertical, sitting slightly below and right of centre.
- **Motion:** a dotted or dashed arc sweeping in from the upper left and landing
  at the pointer's tip, with the dots growing in size and opacity along the path.
  Three to four dots is enough — this is the entire "it moves on its own" idea.
- **Optical balance:** the pointer's visual mass should sit at the centre, which
  means nudging it slightly up and left of the true geometric centre.

## 4. Colour

| Role | Colour | Notes |
| --- | --- | --- |
| Background gradient, top-left | `#6366F1` indigo | |
| Background gradient, bottom-right | `#8B5CF6` violet | 135° linear gradient |
| Pointer fill | `#FFFFFF` | solid, full opacity |
| Pointer edge | `#4338CA` at 25% | a hairline, for definition only |
| Motion trail | `#FFFFFF` at 35–75% | opacity ramps up toward the pointer |

An indigo-to-violet gradient reads as "system utility" on macOS without
colliding with the blue that Apple's own apps occupy. If you want an alternative,
try slate `#334155` → `#0F172A` with a **cyan** `#22D3EE` pointer for a darker,
more technical feel.

## 5. Style rules

- Flat with a **single** soft gradient. No skeuomorphism, no bevels, no glass,
  no inner shadows, no 3D perspective.
- No text, no letters, no numerals anywhere in the icon.
- No thin hairlines other than the pointer edge — everything must survive being
  scaled to 16×16.
- The design must be legible in **greyscale**, since that is a good proxy for
  small sizes and accessibility.

## 6. The macOS menu bar icon is a separate deliverable

macOS menu bar icons are **template images**: pure black shapes on transparency,
which the system automatically inverts for dark mode and dims when inactive.

- File: `assets/menubar-icon.png` at 22×22, plus `menubar-icon@2x.png` at 44×44.
- Content: the pointer outline **only** — no squircle, no gradient, no colour.
- Stroke weight ≈ 1.5pt at 1× so it stays crisp.
- Name the file with a `Template` suffix (`menubarTemplate.png`) if you wire it
  into `rumps.App(icon=..., template=True)`; that is what tells AppKit to treat
  it as a template image.

Today the app uses the text glyph `→` as its menu bar title. Swapping to a
template icon is a one-line change in `src/cursor_mover/app.py`.

## 7. Deliverables checklist

- [ ] `icon.svg` — the master, vector, 1024×1024 artboard
- [ ] `icon.png` — 1024×1024 RGBA, for the README and the Linux desktop entry
- [ ] `icon.icns` — the macOS app bundle icon (`make_icns.sh`)
- [ ] `icon.ico` — the Windows icon, 16–256px in one file
- [ ] `menubarTemplate.png` + `menubarTemplate@2x.png` — black-on-transparent,
      macOS menu bar only
- [ ] A 16×16 export, checked by eye — this is the size Windows shows in the
      notification area, and the current trail dissolves there. Reducing to two
      larger dots is the known fix.

---

## 8. Prompt for an image generator

Paste this verbatim into Midjourney, DALL·E, Ideogram, or similar.

```
A macOS application icon for a menu bar utility called "Cursor Mover".

Subject: a single classic white mouse pointer arrow, tilted about 20 degrees
clockwise, centred in the frame. Behind it, a dotted arc sweeps in from the
upper left and ends at the arrow's tip — four round dots that grow larger and
more opaque as they approach the arrow, showing that the pointer moved there by
itself.

Container: a rounded-square "squircle" in the Apple Big Sur / Sonoma icon style,
filled with a smooth 135-degree linear gradient from indigo #6366F1 at the top
left to violet #8B5CF6 at the bottom right.

Style: modern flat vector, minimal, clean geometry, a single soft gradient, no
bevels, no glass or skeuomorphic effects, no 3D, no drop shadow, no outer glow.
The arrow is pure white with a very subtle darker indigo edge for definition.

Composition: the artwork sits inside the central 72% of the canvas with generous
even padding. Absolutely no text, letters, or numbers anywhere in the image.

Output: 1024x1024, centred, on a transparent background outside the squircle.

Negative prompt: text, letters, words, watermark, computer mouse hardware,
monitor, screen, desk, hand, clock, coffee cup, photorealism, gradient mesh
noise, drop shadow, glossy reflection, busy background, multiple icons, border.
```

### If the first result is close but not right

- Trail reads as decoration rather than motion → *"make the dots clearly follow a
  single curved path that terminates exactly at the arrow tip"*
- Too busy → *"reduce to three dots, increase spacing, simplify"*
- Arrow shape looks generic → *"use the exact classic macOS pointer silhouette:
  a sharp triangular tip with a notched tail"*
- Gradient looks muddy → *"flat two-stop linear gradient only, no mesh, no noise"*

## 9. Building it by hand instead

`icon.svg` in this folder is a working starting point built to this brief. The
authoritative version is drawn in code by `src/cursor_mover/artwork.py`, which
also supplies the Windows/Linux tray icon at runtime. Open the SVG in Figma,
Sketch, or Illustrator, refine the pointer silhouette, port the geometry back
into `artwork.py`, then run `make icons`.

**Export transparency, not a checkerboard.** Whatever tool you use, confirm the
corner pixel of the exported PNG is `(0, 0, 0, 0)` and not white or grey. An
opaque surround produces a white square behind the icon on macOS.
