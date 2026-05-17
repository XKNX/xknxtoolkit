from __future__ import annotations

import random
import time
from pathlib import Path

from imgui_bundle import hello_imgui, imgui

_SPRITE_COLS = 6
_SLOT_W = 289
_SLOT_H = 208
_FRAME_IDLE = 0
_FRAMES_RUN = (1, 2, 3, 4, 5)
_WANDER_SPEED = 60.0
_SPRINT_SPEED = 500.0
_WANDER_FPS = 6.0
_SPRINT_FPS = 14.0
_WANDER_DIST = 10.0
_WANDER_INTERVAL = (3.0, 8.0)
_MOUSE_MOVE_THRESHOLD = 5.0
_SCALE = 0.25


class CatFollower:
    def __init__(self, sprite_path: Path | None = None) -> None:
        self._sprite_path = sprite_path or Path(__file__).parent / "cat_sprite.png"
        self._tex_id: int | None = None
        self._x = float("inf")
        self._y = float("inf")
        self._target_x = 0.0
        self._target_y = 0.0
        self._run_idx = 0
        self._frame_timer = 0.0
        self._last_t = time.monotonic()
        self._facing_right = True
        self._wander_timer = 0.0
        self._next_wander = random.uniform(*_WANDER_INTERVAL)
        self._wandering = False
        self._returning = False
        self._sprinting = False
        self._last_mouse_x = 0.0
        self._last_mouse_y = 0.0

    def load(self) -> None:
        data = self._sprite_path.read_bytes()
        img = hello_imgui.image_and_size_from_encoded_data(data, str(self._sprite_path))
        self._tex_id = img.texture_id

    def render(self) -> None:
        if self._tex_id is None:
            self.load()
        if self._tex_id is None:
            return

        now = time.monotonic()
        dt = min(now - self._last_t, 0.1)
        self._last_t = now

        vp = imgui.get_main_viewport()
        margin = _SLOT_W * _SCALE * 0.5
        ground_y = vp.pos.y + vp.size.y - 24
        corner_x = vp.pos.x + margin

        if abs(self._x) > 100_000 or abs(self._y) > 100_000:
            self._x = corner_x
            self._y = ground_y
            self._target_x, self._target_y = self._x, self._y

        io = imgui.get_io()
        mx, my = io.mouse_pos.x, io.mouse_pos.y
        mouse_moved = (
            abs(mx - self._last_mouse_x) > _MOUSE_MOVE_THRESHOLD
            or abs(my - self._last_mouse_y) > _MOUSE_MOVE_THRESHOLD
        )
        if abs(mx) < 100_000 and abs(my) < 100_000:
            self._last_mouse_x, self._last_mouse_y = mx, my

        if mouse_moved and (self._wandering or self._returning) and not self._sprinting:
            self._sprinting = True
            self._wandering = False
            self._returning = False
            self._target_x = corner_x
            self._target_y = ground_y

        if not self._sprinting and not self._wandering and not self._returning:
            self._wander_timer += dt
            if self._wander_timer >= self._next_wander:
                self._wandering = True
                self._target_x = random.uniform(vp.pos.x + margin, vp.pos.x + vp.size.x - margin)
                self._target_y = ground_y

        dx = self._target_x - self._x
        dy = self._target_y - self._y
        dist = (dx * dx + dy * dy) ** 0.5

        if self._sprinting:
            if dist > _WANDER_DIST:
                step = min(_SPRINT_SPEED * dt, dist)
                self._x += dx / dist * step
                self._y += dy / dist * step
                self._facing_right = dx >= 0
                self._frame_timer += dt
                ticks = int(self._frame_timer * _SPRINT_FPS)
                if ticks:
                    self._run_idx = (self._run_idx + ticks) % len(_FRAMES_RUN)
                    self._frame_timer -= ticks / _SPRINT_FPS
                frame = _FRAMES_RUN[self._run_idx]
            else:
                self._sprinting = False
                self._wander_timer = 0.0
                self._next_wander = random.uniform(*_WANDER_INTERVAL)
                frame = _FRAME_IDLE
                self._run_idx = 0
                self._frame_timer = 0.0
        elif self._wandering:
            if dist > _WANDER_DIST:
                step = min(_WANDER_SPEED * dt, dist)
                self._x += dx / dist * step
                self._y += dy / dist * step
                self._facing_right = dx >= 0
                self._frame_timer += dt
                ticks = int(self._frame_timer * _WANDER_FPS)
                if ticks:
                    self._run_idx = (self._run_idx + ticks) % len(_FRAMES_RUN)
                    self._frame_timer -= ticks / _WANDER_FPS
                frame = _FRAMES_RUN[self._run_idx]
            else:
                self._wandering = False
                self._returning = True
                self._target_x = corner_x
                self._target_y = ground_y
                frame = _FRAMES_RUN[self._run_idx]
        elif self._returning:
            if dist > _WANDER_DIST:
                step = min(_WANDER_SPEED * dt, dist)
                self._x += dx / dist * step
                self._y += dy / dist * step
                self._facing_right = dx >= 0
                self._frame_timer += dt
                ticks = int(self._frame_timer * _WANDER_FPS)
                if ticks:
                    self._run_idx = (self._run_idx + ticks) % len(_FRAMES_RUN)
                    self._frame_timer -= ticks / _WANDER_FPS
                frame = _FRAMES_RUN[self._run_idx]
            else:
                self._returning = False
                self._wander_timer = 0.0
                self._next_wander = random.uniform(*_WANDER_INTERVAL)
                frame = _FRAME_IDLE
                self._run_idx = 0
                self._frame_timer = 0.0
        else:
            frame = _FRAME_IDLE
            self._run_idx = 0
            self._frame_timer = 0.0

        u0 = frame / _SPRITE_COLS
        u1 = (frame + 1) / _SPRITE_COLS

        draw_w = _SLOT_W * _SCALE
        draw_h = _SLOT_H * _SCALE
        px = self._x - draw_w * 0.5
        py = self._y - draw_h

        tex = imgui.ImTextureRef(self._tex_id)
        dl = imgui.get_foreground_draw_list()
        if self._facing_right:
            dl.add_image(tex, (px, py), (px + draw_w, py + draw_h), (u0, 0.0), (u1, 1.0))
        else:
            dl.add_image(tex, (px, py), (px + draw_w, py + draw_h), (u1, 0.0), (u0, 1.0))
