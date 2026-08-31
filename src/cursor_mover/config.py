"""Persisted user settings.

Settings live in the platform's conventional per-user location, resolved by
:mod:`cursor_mover.paths`, so they survive upgrades and are removed cleanly
with the app.

Every read is defensive: a missing, unreadable, or corrupt file falls back to
defaults rather than preventing the app from launching.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path

from cursor_mover.constants import (
    DEFAULT_INTERVAL_SECONDS,
    MAX_INTERVAL_SECONDS,
    MIN_INTERVAL_SECONDS,
)
from cursor_mover.paths import config_dir as default_config_dir

logger = logging.getLogger(__name__)

SETTINGS_FILENAME = "settings.json"


class InvalidIntervalError(ValueError):
    """Raised when an interval is outside the supported range."""


def validate_interval(value: object) -> int:
    """Coerce ``value`` to a valid interval in seconds.

    Raises:
        InvalidIntervalError: if the value is not a whole number of seconds inside
            ``[MIN_INTERVAL_SECONDS, MAX_INTERVAL_SECONDS]``.
    """
    try:
        seconds = int(str(value).strip())
    except (TypeError, ValueError):
        raise InvalidIntervalError("Please enter a whole number of seconds.") from None

    if seconds < MIN_INTERVAL_SECONDS:
        raise InvalidIntervalError(f"Interval must be at least {MIN_INTERVAL_SECONDS} seconds.")
    if seconds > MAX_INTERVAL_SECONDS:
        raise InvalidIntervalError(f"Interval must be at most {MAX_INTERVAL_SECONDS} seconds.")
    return seconds


@dataclass(slots=True)
class Settings:
    """User-tunable settings."""

    interval_seconds: int = DEFAULT_INTERVAL_SECONDS
    start_on_launch: bool = False

    @classmethod
    def from_mapping(cls, data: dict) -> Settings:
        """Build settings from raw JSON, ignoring unknown or invalid fields."""
        settings = cls()
        try:
            settings.interval_seconds = validate_interval(
                data.get("interval_seconds", DEFAULT_INTERVAL_SECONDS)
            )
        except InvalidIntervalError:
            logger.warning("Ignoring invalid stored interval; using the default.")
        settings.start_on_launch = bool(data.get("start_on_launch", False))
        return settings


class SettingsStore:
    """Loads and saves :class:`Settings` as JSON on disk."""

    def __init__(self, config_dir: Path | None = None) -> None:
        self.config_dir = config_dir if config_dir is not None else default_config_dir()
        self.path = self.config_dir / SETTINGS_FILENAME

    def load(self) -> Settings:
        """Read settings from disk, falling back to defaults on any problem."""
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return Settings()
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Could not read %s (%s); using defaults.", self.path, exc)
            return Settings()

        if not isinstance(raw, dict):
            logger.warning("Malformed settings in %s; using defaults.", self.path)
            return Settings()
        return Settings.from_mapping(raw)

    def save(self, settings: Settings) -> None:
        """Write settings to disk. Failures are logged, never raised."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")
            tmp.replace(self.path)
        except OSError as exc:
            logger.warning("Could not save settings to %s: %s", self.path, exc)
