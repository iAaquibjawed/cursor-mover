"""Tests for interval validation and settings persistence."""

from __future__ import annotations

import json

import pytest

from cursor_mover.config import (
    InvalidIntervalError,
    Settings,
    SettingsStore,
    validate_interval,
)
from cursor_mover.constants import (
    DEFAULT_INTERVAL_SECONDS,
    MAX_INTERVAL_SECONDS,
    MIN_INTERVAL_SECONDS,
)


class TestValidateInterval:
    @pytest.mark.parametrize("value", [MIN_INTERVAL_SECONDS, 30, MAX_INTERVAL_SECONDS])
    def test_accepts_values_in_range(self, value: int) -> None:
        assert validate_interval(value) == value

    def test_accepts_padded_strings(self) -> None:
        assert validate_interval("  42  ") == 42

    @pytest.mark.parametrize("value", [MIN_INTERVAL_SECONDS - 1, 0, -5, MAX_INTERVAL_SECONDS + 1])
    def test_rejects_out_of_range(self, value: int) -> None:
        with pytest.raises(InvalidIntervalError):
            validate_interval(value)

    @pytest.mark.parametrize("value", ["", "abc", "10.5", None])
    def test_rejects_non_integers(self, value: object) -> None:
        with pytest.raises(InvalidIntervalError):
            validate_interval(value)


class TestSettingsStore:
    def test_missing_file_yields_defaults(self, tmp_path) -> None:
        settings = SettingsStore(tmp_path).load()
        assert settings == Settings()

    def test_round_trip(self, tmp_path) -> None:
        store = SettingsStore(tmp_path)
        store.save(Settings(interval_seconds=99, start_on_launch=True))

        loaded = store.load()
        assert loaded.interval_seconds == 99
        assert loaded.start_on_launch is True

    def test_creates_directory_on_save(self, tmp_path) -> None:
        store = SettingsStore(tmp_path / "nested" / "dir")
        store.save(Settings())
        assert store.path.is_file()

    def test_corrupt_json_yields_defaults(self, tmp_path) -> None:
        store = SettingsStore(tmp_path)
        store.path.parent.mkdir(parents=True, exist_ok=True)
        store.path.write_text("{not json", encoding="utf-8")
        assert store.load() == Settings()

    def test_non_object_json_yields_defaults(self, tmp_path) -> None:
        store = SettingsStore(tmp_path)
        store.path.parent.mkdir(parents=True, exist_ok=True)
        store.path.write_text("[1, 2, 3]", encoding="utf-8")
        assert store.load() == Settings()

    def test_out_of_range_stored_interval_falls_back(self, tmp_path) -> None:
        store = SettingsStore(tmp_path)
        store.path.parent.mkdir(parents=True, exist_ok=True)
        store.path.write_text(json.dumps({"interval_seconds": 1}), encoding="utf-8")
        assert store.load().interval_seconds == DEFAULT_INTERVAL_SECONDS

    def test_unwritable_directory_does_not_raise(self, tmp_path) -> None:
        blocker = tmp_path / "blocked"
        blocker.write_text("I am a file, not a directory", encoding="utf-8")
        SettingsStore(blocker).save(Settings())  # must not raise
