"""The Cursor Mover icon, drawn procedurally.

This is the single source of truth for the artwork. It is used two ways:

* the Windows/Linux tray frontend needs a ``PIL.Image`` at runtime, and
  generating it avoids shipping and locating an image file inside a frozen
  bundle;
* ``python -m cursor_mover.artwork`` writes ``assets/icon.png`` for the app
  bundle, the README, and ``assets/make_icns.sh``.

The geometry mirrors ``assets/icon.svg``. Drawing it here rather than
rasterising the SVG is deliberate: the usual macOS rasterisers (``qlmanage``,
Preview) flatten SVG output onto an opaque white background, which leaves a
white square around the squircle when used as an app icon.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw

CANVAS = 1024.0

# Apple's icon shape is a continuous-curvature squircle, not a rounded
# rectangle. A superellipse with this exponent is a close approximation.
SQUIRCLE_EXPONENT = 5.0

GRADIENT_START = (99, 102, 241)  # #6366F1 indigo, top left
GRADIENT_END = (139, 92, 246)  # #8B5CF6 violet, bottom right

POINTER_EDGE = (67, 56, 202)  # #4338CA
POINTER_EDGE_ALPHA = 64  # 25%
POINTER_EDGE_WIDTH = 7.0

# (centre x, centre y, radius, alpha) - the trail grows toward the pointer tip.
TRAIL_DOTS = [
    (238.0, 236.0, 16.0, 77),
    (295.0, 270.0, 21.0, 115),
    (353.0, 306.0, 26.0, 158),
    (408.0, 344.0, 31.0, 204),
]

# Classic macOS pointer in 17x27 units: vertical left edge, sharp tip at the
# top left, notched tail at the bottom right.
POINTER_UNITS = [(0, 0), (0, 24), (6, 18.5), (10, 27), (14, 25), (10, 17), (17, 17)]
POINTER_ORIGIN = (446.0, 362.0)
POINTER_SCALE = 14.0

#: Rendering multiplier; the result is downsampled for clean antialiasing.
SUPERSAMPLE = 4

#: Sizes embedded in the Windows .ico file.
ICO_SIZES = (16, 24, 32, 48, 64, 128, 256)


def squircle_outline(size: float, points: int = 2048) -> list[tuple[float, float]]:
    """Return a polygon approximating a superellipse inscribed in ``size``."""
    radius = size / 2.0
    power = 2.0 / SQUIRCLE_EXPONENT
    outline = []
    for i in range(points):
        theta = 2.0 * math.pi * i / points
        cos_t, sin_t = math.cos(theta), math.sin(theta)
        x = math.copysign(abs(cos_t) ** power, cos_t)
        y = math.copysign(abs(sin_t) ** power, sin_t)
        outline.append((radius + radius * x, radius + radius * y))
    return outline


def diagonal_gradient(size: int) -> Image.Image:
    """Build the 135-degree indigo-to-violet background."""
    # One pixel per gradient step along the diagonal, then stretched to fill.
    steps = size * 2 - 1
    strip = Image.new("RGB", (steps, 1))
    pixels = strip.load()
    for i in range(steps):
        t = i / (steps - 1)
        pixels[i, 0] = tuple(
            round(start + (end - start) * t)
            for start, end in zip(GRADIENT_START, GRADIENT_END, strict=True)
        )

    # Rotating a stretched strip by 45 degrees gives a clean diagonal ramp.
    gradient = Image.new("RGB", (size, size))
    draw_source = strip.resize((steps, steps), Image.Resampling.NEAREST)
    gradient.paste(
        draw_source.rotate(
            -45, resample=Image.Resampling.BICUBIC, center=(steps / 2, steps / 2)
        ).crop(
            (
                (steps - size) // 2,
                (steps - size) // 2,
                (steps - size) // 2 + size,
                (steps - size) // 2 + size,
            )
        )
    )
    return gradient


def scaled(points: list[tuple[float, float]], factor: float) -> list[tuple[float, float]]:
    return [(x * factor, y * factor) for x, y in points]


def render(size: int = 1024) -> Image.Image:
    """Render the icon at ``size`` x ``size`` with a transparent surround."""
    work = size * SUPERSAMPLE
    scale = work / CANVAS

    # Background: gradient clipped to the squircle, transparent outside it.
    mask = Image.new("L", (work, work), 0)
    ImageDraw.Draw(mask).polygon(squircle_outline(work), fill=255)

    icon = Image.new("RGBA", (work, work), (0, 0, 0, 0))
    icon.paste(diagonal_gradient(work).convert("RGBA"), (0, 0), mask)

    # Trail: each dot needs its own alpha, so composite them one at a time.
    for cx, cy, radius, alpha in TRAIL_DOTS:
        layer = Image.new("RGBA", (work, work), (0, 0, 0, 0))
        box = [
            (cx - radius) * scale,
            (cy - radius) * scale,
            (cx + radius) * scale,
            (cy + radius) * scale,
        ]
        ImageDraw.Draw(layer).ellipse(box, fill=(255, 255, 255, alpha))
        icon = Image.alpha_composite(icon, layer)

    pointer = [
        (POINTER_ORIGIN[0] + x * POINTER_SCALE, POINTER_ORIGIN[1] + y * POINTER_SCALE)
        for x, y in POINTER_UNITS
    ]
    pointer_px = scaled(pointer, scale)

    edge = Image.new("RGBA", (work, work), (0, 0, 0, 0))
    ImageDraw.Draw(edge).line(
        [*pointer_px, pointer_px[0]],
        fill=(*POINTER_EDGE, POINTER_EDGE_ALPHA),
        width=max(1, round(POINTER_EDGE_WIDTH * scale)),
        joint="curve",
    )
    icon = Image.alpha_composite(icon, edge)

    body = Image.new("RGBA", (work, work), (0, 0, 0, 0))
    ImageDraw.Draw(body).polygon(pointer_px, fill=(255, 255, 255, 255))
    icon = Image.alpha_composite(icon, body)

    return icon.resize((size, size), Image.Resampling.LANCZOS)


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="python -m cursor_mover.artwork",
        description="Render the Cursor Mover icon to a PNG with real transparency.",
    )
    parser.add_argument("--size", type=int, default=1024, help="output size in pixels")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("assets") / "icon.png",
        help="destination PNG",
    )
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)

    if args.output.suffix.lower() == ".ico":
        # Windows picks the closest size from a multi-resolution ICO.
        image = render(max(args.size, max(ICO_SIZES)))
        image.save(args.output, "ICO", sizes=[(s, s) for s in ICO_SIZES])
        print(f"✓ Wrote {args.output} (ICO, sizes {ICO_SIZES})")
        return 0

    image = render(args.size)
    image.save(args.output, "PNG", optimize=True)
    print(f"✓ Wrote {args.output} ({args.size}x{args.size}, RGBA)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


def tray_image(size: int = 64) -> Image.Image:
    """Return the icon at a size suitable for a system tray.

    Windows and most Linux panels display a 16-24px icon; rendering larger and
    letting the platform downscale keeps it crisp on high-DPI displays.
    """
    return render(size)
