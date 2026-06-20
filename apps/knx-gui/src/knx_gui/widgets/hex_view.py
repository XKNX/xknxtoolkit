from __future__ import annotations

from imgui_bundle import imgui

_COLS = 16
_MID = 8  # extra gap after this many bytes


def draw_hex_contents(data: bytes, base_addr: int = 0) -> None:
    """Draw a read-only hex viewer for data inside the current window/child."""
    glyph_w = imgui.calc_text_size("F").x + 1.0
    hex_cell_w = glyph_w * 3.0  # "XX " per byte
    mid_gap = glyph_w * 0.5
    hex_start = glyph_w * 6.0  # "AAAA: "
    ascii_start = hex_start + _COLS * hex_cell_w + mid_gap + glyph_w

    n_rows = (len(data) + _COLS - 1) // _COLS

    clipper = imgui.ListClipper()
    clipper.begin(n_rows, imgui.get_text_line_height())
    while clipper.step():
        for row in range(clipper.display_start, clipper.display_end):
            start = row * _COLS
            chunk = data[start : start + _COLS]

            imgui.text_disabled(f"{base_addr + start:04X}:")

            for i, b in enumerate(chunk):
                x = hex_start + i * hex_cell_w
                if i >= _MID:
                    x += mid_gap
                imgui.same_line(x)
                if b == 0:
                    imgui.text_disabled(f"{b:02X}")
                else:
                    imgui.text(f"{b:02X}")

            imgui.same_line(ascii_start)
            imgui.text_disabled("".join(chr(b) if 32 <= b < 128 else "." for b in chunk))
