from __future__ import annotations

import random
import types
from dataclasses import dataclass
from typing import Any

import pytest
from knx_gui.plugins.cat import follower

# Dear ImGui's GLFW backend reports io.MousePos == (-FLT_MAX, -FLT_MAX) every
# frame while the application window is unfocused (alt-tab / minimized). This
# is exactly the sentinel that triggered the bug.
FLT_MAX = 3.4028234663852886e38
SENTINEL = -FLT_MAX

# Distance at which the cat considers a wander/return/sprint "arrived"; copied
# from follower._WANDER_DIST to keep assertions coupled to the real constant.
_WANDER_DIST = follower._WANDER_DIST  # pyright: ignore[reportPrivateUsage]


@dataclass
class _Vec:
    x: float
    y: float


@dataclass
class _Viewport:
    pos: _Vec
    size: _Vec


@dataclass
class _IO:
    mouse_pos: _Vec


class _DrawList:
    """Records nothing; CatFollower.render only needs add_image to exist."""

    def add_image(
        self,
        tex: Any,
        pmin: tuple[float, float],
        pmax: tuple[float, float],
        uv0: tuple[float, float],
        uv1: tuple[float, float],
    ) -> None:
        pass


class _FakeImgui:
    """Stand-in for imgui_bundle.imgui covering exactly what CatFollower.render
    touches. It draws nothing; it only records that a frame was produced and
    reports a controllable viewport / mouse position."""

    FLT_MAX: float = FLT_MAX

    def __init__(self, viewport: _Viewport, mouse_pos: _Vec) -> None:
        self._vp = viewport
        self._io = _IO(mouse_pos)
        self._dl = _DrawList()

    def get_main_viewport(self) -> _Viewport:
        return self._vp

    def get_io(self) -> _IO:
        return self._io

    def get_foreground_draw_list(self) -> _DrawList:
        return self._dl

    def ImTextureRef(self, tex_id: int) -> tuple[str, int]:
        return ("tex", tex_id)

    def set_mouse_pos(self, x: float, y: float) -> None:
        self._io.mouse_pos = _Vec(x, y)


class _Clock:
    """Controllable replacement for time.monotonic() so render() sees a
    deterministic frame clock instead of wall time."""

    def __init__(self, t0: float = 1000.0) -> None:
        self.t = t0

    def monotonic(self) -> float:
        return self.t

    def advance(self, dt: float) -> None:
        self.t += dt


@dataclass
class _Session:
    fake: _FakeImgui
    clock: _Clock
    viewport: _Viewport
    cat: Any
    corner_x: float


def _install(
    monkeypatch: pytest.MonkeyPatch,
    *,
    mouse_x: float,
    mouse_y: float,
    seed: int = 42,
    vp_w: float = 1280.0,
    vp_h: float = 800.0,
) -> _Session:
    viewport = _Viewport(_Vec(0.0, 0.0), _Vec(vp_w, vp_h))
    fake = _FakeImgui(viewport, _Vec(mouse_x, mouse_y))
    clock = _Clock(t0=1000.0)
    monkeypatch.setattr(follower, "imgui", fake)
    monkeypatch.setattr(
        follower, "time", types.SimpleNamespace(monotonic=clock.monotonic)
    )
    monkeypatch.setattr(follower, "random", random.Random(seed))
    cat: Any = follower.CatFollower()
    cat._tex_id = 1
    # One zero-dt render snaps the cat to the corner so corner_x can be read
    # back from the cat itself, without reaching into follower's private
    # layout constants. No RNG draw happens here (no idle wander triggers on a
    # zero-dt frame), so this frame is invisible to the random sequence.
    cat.render()
    corner_x = float(cat._x)
    return _Session(
        fake=fake, clock=clock, viewport=viewport, cat=cat, corner_x=corner_x
    )


def _drive(session: _Session, *, frames: int, dt: float = 1 / 60.0) -> None:
    for _ in range(frames):
        session.clock.advance(dt)
        session.cat.render()


def _wander_toward(session: _Session, dx: float) -> None:
    """Place the cat mid-wander toward a target `dx` px from the corner, on
    the ground line, so spook/sprint assertions are deterministic instead of
    depending on whatever random.uniform coughed up as the next target."""
    cat = session.cat
    cat._wandering = True
    cat._returning = False
    cat._sprinting = False
    cat._target_x = session.corner_x + dx
    cat._target_y = float(cat._y)


def _max_motion(session: _Session) -> float:
    return abs(float(session.cat._x) - session.corner_x)


def test_cat_wanders_while_window_is_unfocused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression: while the app window is unfocused, Dear ImGui reports
    io.MousePos == (-FLT_MAX, -FLT_MAX). The cat must still wander along the
    bottom as if the user were simply idle, instead of being spooked back to
    the corner on every frame (the original bug)."""
    session = _install(monkeypatch, mouse_x=SENTINEL, mouse_y=SENTINEL, seed=42)
    _drive(session, frames=1800, dt=1 / 60.0)  # 30 s of simulated idle time

    motion = _max_motion(session)
    assert motion > 100.0, (
        f"cat only wandered {motion:.1f}px while the window was unfocused; "
        "expected normal idle wandering"
    )


def test_unfocused_wanders_same_distance_as_focused_idle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Structural identity: with the fix, gating `mouse_moved` on a valid
    position means an unfocused window (sentinel MousePos) behaves exactly
    like a focused window with an idle cursor -- the only difference is
    whether the sentinel reads as motion, which the fix suppresses. Same
    seed -> same wander distance, bit for bit."""
    focused = _install(monkeypatch, mouse_x=500.0, mouse_y=700.0, seed=42)
    _drive(focused, frames=1800, dt=1 / 60.0)  # 30 s
    focused_motion = _max_motion(focused)

    unfocused = _install(monkeypatch, mouse_x=SENTINEL, mouse_y=SENTINEL, seed=42)
    _drive(unfocused, frames=1800, dt=1 / 60.0)
    unfocused_motion = _max_motion(unfocused)

    assert unfocused_motion == focused_motion, (
        f"unfocused cat wandered {unfocused_motion:.3f}px but focused idle "
        f"cat wandered {focused_motion:.3f}px; the fix must make them identical"
    )
    assert focused_motion > 100.0, (
        f"cat did not wander enough ({focused_motion:.1f}px); test setup is broken"
    )


def test_real_mouse_movement_spooks_cat_back_to_corner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression guard: a real cursor movement must still spook the cat and
    sprint it to the corner. The fix only suppresses the -FLT_MAX sentinel,
    not genuine motion."""
    session = _install(monkeypatch, mouse_x=500.0, mouse_y=700.0, seed=42)
    _wander_toward(session, dx=500.0)
    _drive(session, frames=120, dt=1 / 60.0)  # 2 s: wander ~120 px out, cursor still
    mid_motion = _max_motion(session)
    assert mid_motion > 50.0, f"cat did not wander first: {mid_motion:.1f}px"

    session.fake.set_mouse_pos(50.0, 50.0)  # genuine cursor movement
    _drive(session, frames=120, dt=1 / 60.0)  # 2 s: sprint home at 500 px/s

    end_motion = _max_motion(session)
    assert end_motion < mid_motion, "cat did not sprint back toward the corner"
    assert end_motion < _WANDER_DIST * 2, (
        f"cat did not return near the corner: {end_motion:.1f}px"
    )


def test_sentinel_mouse_does_not_trigger_spook_while_wandering(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The core of the bug: with the sentinel present, `mouse_moved` must stay
    False so the spook branch never fires. While the cat is wandering, the
    sentinel must not cancel the wander or start a sprint."""
    session = _install(monkeypatch, mouse_x=SENTINEL, mouse_y=SENTINEL, seed=42)
    _wander_toward(session, dx=500.0)
    _drive(session, frames=20, dt=1 / 60.0)  # ~0.33 s with the sentinel held

    assert not session.cat._sprinting, "sentinel mouse triggered a spook sprint"
    assert session.cat._wandering, "the cat's wander was cancelled by the sentinel"
    assert _max_motion(session) > _WANDER_DIST, "cat never left the corner"
