from __future__ import annotations

import time
from pathlib import Path

from imgui_bundle import hello_imgui, imgui

_SPRITE_COLS = 6
_SLOT_W = 289
_SLOT_H = 208
_FRAME_IDLE = 0
_FRAMES_RUN = (1, 2, 3, 4, 5)
_RUN_FPS = 12.0
_SPEED = 400.0
_IDLE_DIST = 150.0
_SCALE = 0.25


class CatFollower:
    def __init__(self, sprite_path: Path | None = None) -> None:
        self._sprite_path = sprite_path or Path(__file__).parent / "cat_sprite.png"
        self._tex_id: int | None = None
        self._x = 0.0
        self._y = 0.0
        self._target_x = 0.0
        self._target_y = 0.0
        self._run_idx = 0
        self._frame_timer = 0.0
        self._last_t = time.monotonic()
        self._facing_right = True

    def load(self) -> None:
        data = self._sprite_path.read_bytes()
        img = hello_imgui.image_and_size_from_encoded_data(data, str(self._sprite_path))
        self._tex_id = img.texture_id
        io = imgui.get_io()
        self._x = io.mouse_pos.x
        self._y = io.mouse_pos.y

    def render(self) -> None:
        if self._tex_id is None:
            self.load()
        if self._tex_id is None:
            return

        now = time.monotonic()
        dt = min(now - self._last_t, 0.1)
        self._last_t = now

        io = imgui.get_io()
        mx, my = io.mouse_pos.x, io.mouse_pos.y

        # Skip frame if mouse position is invalid (outside window at startup)
        if abs(mx) > 100_000 or abs(my) > 100_000:
            return

        # Snap to mouse if cat is at an invalid/uninitialized position
        if abs(self._x) > 100_000 or abs(self._y) > 100_000:
            self._x, self._y = mx, my
            self._target_x, self._target_y = mx, my

        if imgui.is_mouse_clicked(imgui.MouseButton_.left):
            self._target_x, self._target_y = mx, my

        dx = self._target_x - self._x
        dy = self._target_y - self._y
        dist = (dx * dx + dy * dy) ** 0.5

        running = dist > _IDLE_DIST
        if running:
            step = min(_SPEED * dt, dist)
            self._x += dx / dist * step
            self._y += dy / dist * step
            self._facing_right = dx >= 0
            self._frame_timer += dt
            ticks = int(self._frame_timer * _RUN_FPS)
            if ticks:
                self._run_idx = (self._run_idx + ticks) % len(_FRAMES_RUN)
                self._frame_timer -= ticks / _RUN_FPS
            frame = _FRAMES_RUN[self._run_idx]
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
