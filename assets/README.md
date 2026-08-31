# Assets

| File | Purpose |
| --- | --- |
| `LOGO_BRIEF.md` | Full design brief, colour spec, and an image-generator prompt |
| `icon.svg` | Master app icon, 1024×1024 — a starting point, meant to be refined |
| `menubarTemplate.svg` | Monochrome macOS menu bar icon (black on transparency) |
| `make_icns.sh` | Converts a 1024×1024 PNG into `icon.icns` |
| `render_icon.py` | Shim for `python -m cursor_mover.artwork` |
| `icon.png` | 1024×1024 RGBA — README, Linux `.desktop`, and the `.icns` source |
| `icon.ico` | Multi-resolution Windows icon (16–256px) |
| `icon.icns` | macOS app bundle icon |
| `platforms/` | Third-party OS logos used in the README (see below) |

The artwork itself is **not** in this folder — it is drawn procedurally by
[`src/cursor_mover/artwork.py`](../src/cursor_mover/artwork.py), which is also
what the Windows/Linux tray icon uses at runtime. That keeps one source of truth
for the geometry.

## Regenerating every format

```bash
make icons
```

Which is equivalent to:

```bash
python -m cursor_mover.artwork --size 1024 -o assets/icon.png   # macOS, Linux, README
python -m cursor_mover.artwork -o assets/icon.ico               # Windows
./assets/make_icns.sh                                           # macOS bundle
```

Then rebuild: `./packaging/build_macos.sh` (or the Windows/Linux equivalent).
Each spec uses its icon when present and falls back to none when absent, so a
missing icon never breaks a build.

## Replacing the artwork

1. Read `LOGO_BRIEF.md` and produce new artwork, or refine `icon.svg`.
2. Either port the geometry into `src/cursor_mover/artwork.py` (preferred — the
   tray icon then updates too), or export a 1024×1024 **RGBA** PNG over
   `assets/icon.png` and regenerate the derived formats.

## Why the icon is drawn in code

macOS rasterisers (`qlmanage`, Preview, and "Export as PNG" in some tools)
flatten SVG output onto an **opaque white background**. An icon exported that way
shows a white square behind the squircle once macOS applies its own rounding and
shadow. Some editors go further and export the transparency *checkerboard* as
real pixels.

Drawing it with Pillow sidesteps all of that, gives a genuine alpha channel with
4× supersampling, and means the tray frontend needs no image file inside a frozen
bundle. Verify any replacement with:

```bash
python -c "from PIL import Image; im=Image.open('assets/icon.png'); \
print(im.mode, im.getpixel((1,1)))"
# want: RGBA (0, 0, 0, 0)
```

## Using the template icon in the macOS menu bar

The macOS build shows the text glyph `→`. To use artwork instead, export
`menubarTemplate.png` (22×22) and `menubarTemplate@2x.png` (44×44), add them to
`packaging/macos.spec`'s `datas`, and pass them in
`src/cursor_mover/frontend/menubar.py`:

```python
super().__init__(APP_NAME, icon="menubarTemplate.png", template=True, ...)
```

`template=True` is what lets macOS recolour the icon for light and dark mode.
Windows and Linux already use the full-colour icon from `artwork.py`.

## Platform logos (`platforms/`)

The README shows real OS logos rather than emoji stand-ins. Each is vendored
locally so the README does not depend on a third-party CDN staying up, and each
ships in two variants:

| File | Used when |
| --- | --- |
| `*-on-light.svg` | light GitHub theme — ink `#1f2328` |
| `*-on-dark.svg` | dark GitHub theme — ink `#e6edf3` |

They are referenced with `<picture>` + `prefers-color-scheme`, which GitHub
honours in Markdown, so the row stays legible in both themes.

### Sources

| Logo | Source | Why |
| --- | --- | --- |
| Apple | [Simple Icons](https://simpleicons.org) (CC0) | single path, ~660 bytes |
| Linux (Tux) | [Simple Icons](https://simpleicons.org) (CC0) | monochrome, ~5 KB |
| Windows | [Devicon](https://devicon.dev) (MIT) | Simple Icons removed all Microsoft marks for trademark reasons |

Devicon's Tux was rejected: it is a 194 KB photorealistic trace with hundreds of
gradient stops, which is absurd for a 15px icon.

All three were recoloured to a single flat ink so the set reads as one system.
To regenerate or restyle them, re-run the download and recolour steps documented
in this file's git history, or edit the `fill` on the root `<svg>` element.

> Apple, Windows, and the Linux penguin are trademarks of their respective
> owners. They appear here solely to identify supported platforms — this project
> is not affiliated with or endorsed by any of them.
