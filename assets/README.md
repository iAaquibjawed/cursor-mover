# Assets

| File | Purpose |
| --- | --- |
| `LOGO_BRIEF.md` | Full design brief, colour spec, and an image-generator prompt |
| `icon.svg` | Master app icon, 1024×1024 — a starting point, meant to be refined |
| `menubarTemplate.svg` | Monochrome menu bar icon (black on transparency) |
| `render_icon.py` | Renders `icon.png` from vector geometry, with real transparency |
| `make_icns.sh` | Converts a 1024×1024 PNG into `icon.icns` |
| `icon.icns` | *(generated)* picked up automatically by the PyInstaller spec |

## Workflow

1. Read `LOGO_BRIEF.md` and produce the artwork, or refine `icon.svg`.
2. Produce a 1024×1024 **RGBA** PNG at `assets/icon.png`:
   `python3 assets/render_icon.py` (needs `pip install -e ".[dev]"`).
3. Run `./assets/make_icns.sh` to generate `assets/icon.icns`.
4. Rebuild: `./packaging/build_app.sh`. The spec uses `icon.icns` when present
   and falls back to no icon when it is absent, so the build never breaks.

## Using the template icon in the menu bar

The app currently shows the text glyph `→`. To use artwork instead, export
`menubarTemplate.png` (22×22) and `menubarTemplate@2x.png` (44×44), add them to
the spec's `datas`, and in `src/cursor_mover/app.py` pass them to the superclass:

```python
super().__init__(APP_NAME, icon="menubarTemplate.png", template=True, ...)
```

`template=True` is what lets macOS recolour the icon for light and dark mode.

## Why `render_icon.py` exists

macOS rasterisers (`qlmanage`, Preview, "Export as PNG" in some tools) flatten
SVG output onto an **opaque white background**. An icon exported that way shows
a white square behind the squircle once macOS applies its own rounding and
shadow. Worse, some editors export the transparency *checkerboard* as real
pixels.

`render_icon.py` draws the same geometry as `icon.svg` directly, with a genuine
alpha channel and 4× supersampling. Verify any replacement artwork with:

```bash
python3 -c "from PIL import Image; im=Image.open('assets/icon.png'); \
print(im.mode, im.getpixel((1,1)))"
# want: RGBA (0, 0, 0, 0)
```
