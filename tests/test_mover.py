"""Tests for the pointer movement engine."""

from __future__ import annotations

import random

import pytest

from cursor_mover.constants import FALLBACK_SCREEN_SIZE, MOVE_DURATION_SECONDS
from cursor_mover.mover import AccessibilityPermissionError, CursorMover, random_point


class FakeBackend:
    """Records calls in place of pyautogui."""

    def __init__(self, screen=(800, 600), size_error=None, position_error=None):
        self._screen = screen
        self._size_error = size_error
        self._position_error = position_error
        self.moves: list[tuple[int, int, float]] = []

    def size(self):
        if self._size_error:
            raise self._size_error
        return self._screen

    def position(self):
        if self._position_error:
            raise self._position_error
        return (0, 0)

    def moveTo(self, x, y, duration=0.0):
        self.moves.append((x, y, duration))


class TestRandomPoint:
    def test_stays_inside_the_screen(self) -> None:
        rng = random.Random(0)
        for _ in range(500):
            x, y = random_point(1920, 1080, rng)
            assert 0 <= x < 1920
            assert 0 <= y < 1080

    def test_is_deterministic_for_a_seeded_rng(self) -> None:
        assert random_point(100, 100, random.Random(7)) == random_point(100, 100, random.Random(7))

    def test_single_pixel_screen(self) -> None:
        assert random_point(1, 1, random.Random(0)) == (0, 0)

    @pytest.mark.parametrize("size", [(0, 100), (100, 0), (-1, -1)])
    def test_rejects_non_positive_dimensions(self, size) -> None:
        with pytest.raises(ValueError):
            random_point(*size)


class TestCursorMover:
    def test_reads_screen_size_from_the_backend(self) -> None:
        assert CursorMover(FakeBackend(screen=(2560, 1440))).screen_size == (2560, 1440)

    def test_falls_back_when_screen_size_is_unavailable(self) -> None:
        mover = CursorMover(FakeBackend(size_error=RuntimeError("no display")))
        assert mover.screen_size == FALLBACK_SCREEN_SIZE

    def test_falls_back_on_a_zero_sized_screen(self) -> None:
        assert CursorMover(FakeBackend(screen=(0, 0))).screen_size == FALLBACK_SCREEN_SIZE

    def test_refresh_picks_up_a_new_resolution(self) -> None:
        backend = FakeBackend(screen=(800, 600))
        mover = CursorMover(backend)
        backend._screen = (1440, 900)
        assert mover.refresh_screen_size() == (1440, 900)

    def test_ensure_permission_passes_when_position_is_readable(self) -> None:
        CursorMover(FakeBackend()).ensure_permission()  # must not raise

    def test_ensure_permission_raises_when_blocked(self) -> None:
        mover = CursorMover(FakeBackend(position_error=OSError("not trusted")))
        with pytest.raises(AccessibilityPermissionError):
            mover.ensure_permission()

    def test_move_once_uses_the_backend(self) -> None:
        backend = FakeBackend(screen=(800, 600))
        mover = CursorMover(backend, rng=random.Random(1))

        target = mover.move_once()

        assert backend.moves == [(*target, MOVE_DURATION_SECONDS)]
        assert 0 <= target[0] < 800
        assert 0 <= target[1] < 600
