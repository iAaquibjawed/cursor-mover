"""Tests for the repeating-timer implementations."""

from __future__ import annotations

import threading
import time

import pytest

from cursor_mover.scheduler import ManualScheduler, ThreadScheduler, create_scheduler


class TestThreadScheduler:
    def test_fires_repeatedly_then_stops(self) -> None:
        scheduler = ThreadScheduler()
        hits: list[float] = []

        scheduler.start(0.05, lambda: hits.append(time.monotonic()))
        time.sleep(0.28)
        scheduler.stop()

        fired = len(hits)
        assert fired >= 3, f"expected at least 3 ticks, got {fired}"

        # Nothing more may fire once stopped.
        time.sleep(0.2)
        assert len(hits) == fired
        assert scheduler.is_active is False

    def test_is_not_active_before_start(self) -> None:
        assert ThreadScheduler().is_active is False

    def test_stop_is_idempotent(self) -> None:
        scheduler = ThreadScheduler()
        scheduler.stop()
        scheduler.stop()  # must not raise

    def test_restart_replaces_the_previous_timer(self) -> None:
        scheduler = ThreadScheduler()
        first: list[int] = []
        second: list[int] = []

        scheduler.start(0.05, lambda: first.append(1))
        time.sleep(0.12)
        scheduler.start(0.05, lambda: second.append(1))
        time.sleep(0.16)
        scheduler.stop()

        # The first callback must have been abandoned when the timer restarted.
        settled = len(first)
        time.sleep(0.15)
        assert len(first) == settled
        assert second, "the replacement callback never fired"

    def test_does_not_leak_threads(self) -> None:
        before = threading.active_count()
        scheduler = ThreadScheduler()
        scheduler.start(0.05, lambda: None)
        time.sleep(0.1)
        scheduler.stop()
        time.sleep(0.1)
        assert threading.active_count() <= before


class TestManualScheduler:
    def test_records_the_interval(self) -> None:
        scheduler = ManualScheduler()
        scheduler.start(30, lambda: None)
        assert scheduler.interval == 30
        assert scheduler.is_active is True

    def test_fire_invokes_the_callback(self) -> None:
        scheduler = ManualScheduler()
        hits: list[int] = []
        scheduler.start(10, lambda: hits.append(1))
        scheduler.fire(3)
        assert hits == [1, 1, 1]

    def test_fire_without_start_raises(self) -> None:
        with pytest.raises(RuntimeError):
            ManualScheduler().fire()

    def test_stop_clears_state(self) -> None:
        scheduler = ManualScheduler()
        scheduler.start(10, lambda: None)
        scheduler.stop()
        assert scheduler.is_active is False
        assert scheduler.stop_count == 1


class TestCreateScheduler:
    def test_non_darwin_gets_a_thread_scheduler(self) -> None:
        assert isinstance(create_scheduler("win32"), ThreadScheduler)
        assert isinstance(create_scheduler("linux"), ThreadScheduler)
