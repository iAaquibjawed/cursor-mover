#!/usr/bin/env python3
"""Deprecated shim. The artwork now lives in ``cursor_mover.artwork``.

Kept because ``assets/make_icns.sh`` and the docs referenced this path.
Prefer:

    python -m cursor_mover.artwork --size 1024 -o assets/icon.png
"""

from cursor_mover.artwork import main

if __name__ == "__main__":
    raise SystemExit(main())
