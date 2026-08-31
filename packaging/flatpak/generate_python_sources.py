#!/usr/bin/env python3
"""Pin the Linux runtime dependencies for the Flatpak manifest.

Flatpak builds run with no network, so every dependency must be listed as a
source with a verified checksum. This queries the PyPI JSON API (which publishes
sha256 digests, so nothing needs downloading) and writes
``python3-dependencies.json`` for the manifest to include.

Re-run after changing a dependency:

    python3 packaging/flatpak/generate_python_sources.py
"""

from __future__ import annotations

import json
import pathlib
import ssl
import sys
import urllib.request

# The Linux runtime closure, resolved by hand and kept small deliberately.
#   pyautogui  -> pymsgbox, pytweening, pyscreeze, pygetwindow, mouseinfo
#   pygetwindow-> pyrect
#   mouseinfo  -> pyperclip, Pillow
#   pystray    -> Pillow, python-xlib, six
# python-xlib satisfies `import Xlib` for both pyautogui and pystray; the older
# python3-Xlib fork is deliberately excluded to avoid two packages shipping the
# same module.
PACKAGES = [
    "pillow",
    "six",
    "python-xlib",
    "pyperclip",
    "pyrect",
    "pytweening",
    "pymsgbox",
    "pyscreeze",
    "pygetwindow",
    "mouseinfo",
    "pyautogui",
    "pystray",
]

# Only architecture-independent wheels are safe to pin: Flathub builds both
# x86_64 and aarch64, and a manylinux wheel is specific to one of them. Anything
# with compiled parts (Pillow) is taken as an sdist and built in the sandbox.
UNIVERSAL_WHEEL_TAGS = ("py3-none-any", "py2.py3-none-any")


def _ssl_context() -> ssl.SSLContext:
    """Verified TLS, using certifi when the system store is unavailable.

    Python installed from python.org on macOS ships no CA bundle, so the default
    context fails. Falling back to certifi keeps verification on rather than
    disabling it.
    """
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def best_distribution(name: str, context: ssl.SSLContext) -> dict:
    url = f"https://pypi.org/pypi/{name}/json"
    with urllib.request.urlopen(url, timeout=30, context=context) as response:
        data = json.load(response)

    version = data["info"]["version"]
    files = data["releases"][version]

    def score(f: dict) -> int:
        fn = f["filename"]
        if f["packagetype"] == "bdist_wheel":
            for i, tag in enumerate(UNIVERSAL_WHEEL_TAGS):
                if fn.endswith(f"-{tag}.whl"):
                    return i
            return 90  # arch-specific wheel: never pin one
        if f["packagetype"] == "sdist":
            return 10  # builds for whichever arch Flathub targets
        return 90

    usable = [f for f in files if not f.get("yanked")]
    if not usable:
        raise SystemExit(f"No usable distribution for {name} {version}")
    chosen = min(usable, key=score)
    return {
        "name": name,
        "version": version,
        "filename": chosen["filename"],
        "url": chosen["url"],
        "sha256": chosen["digests"]["sha256"],
    }


def main() -> int:
    sources = []
    context = _ssl_context()
    print("Resolving from PyPI:")
    for name in PACKAGES:
        dist = best_distribution(name, context)
        print(f"  {dist['name']:<14} {dist['version']:<10} {dist['filename']}")
        sources.append({"type": "file", "url": dist["url"], "sha256": dist["sha256"]})

    module = {
        "name": "python3-dependencies",
        "buildsystem": "simple",
        "build-commands": [
            # --no-deps because the closure is already pinned above; --no-index
            # because the build sandbox has no network.
            "pip3 install --verbose --exists-action=i --no-index "
            '--find-links="file://${PWD}" --prefix=${FLATPAK_DEST} '
            "--no-build-isolation --no-deps " + " ".join(PACKAGES)
        ],
        "sources": sources,
    }

    out = pathlib.Path(__file__).parent / "python3-dependencies.json"
    out.write_text(json.dumps(module, indent=4) + "\n", encoding="utf-8")
    print(f"\nWrote {out} ({len(sources)} pinned sources)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
