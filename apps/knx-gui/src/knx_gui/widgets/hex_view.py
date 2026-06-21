from __future__ import annotations

import struct

from imgui_bundle import imgui


class HexView:
    """Read-only hex viewer with options popup, data preview, and goto."""

    def __init__(self) -> None:
        self.cols: int = 16
        self.grey_zeros: bool = True
        self.uppercase: bool = True
        self.show_ascii: bool = True
        self._hover_addr: int | None = None
        self._goto_buf: str = ""
        self._scroll_to: float | None = None
        self._child_h: float = 300.0

    def draw(self, data: bytes, base_addr: int = 0) -> None:
        n = len(data)
        if n == 0:
            imgui.text_disabled("(empty)")
            return

        line_h = imgui.get_text_line_height()
        glyph_w = imgui.calc_text_size("F").x + 1.0
        addr_digits = max(4, len(f"{base_addr + n - 1:X}"))
        hex_cell_w = glyph_w * 3.0  # "XX "
        mid_gap = glyph_w * 0.75
        n_mid = self.cols // 2

        def hex_x(col: int) -> float:
            x = glyph_w * (addr_digits + 2) + col * hex_cell_w
            if col >= n_mid:
                x += mid_gap
            return x

        ascii_x0 = hex_x(self.cols) + glyph_w if self.show_ascii else 0.0
        n_rows = (n + self.cols - 1) // self.cols

        # Footer: options row + separator + 4 preview rows
        sp = imgui.get_style().item_spacing.y
        footer_h = imgui.get_frame_height_with_spacing() + sp + imgui.get_text_line_height_with_spacing() * 4 + sp

        # Scrolling child
        imgui.begin_child(
            "##hx",
            imgui.ImVec2(-1.0, -footer_h),
            imgui.ChildFlags_.none,
            imgui.WindowFlags_.no_move | imgui.WindowFlags_.no_nav,
        )
        self._child_h = imgui.get_content_region_avail().y

        if self._scroll_to is not None:
            imgui.set_scroll_y(self._scroll_to)
            self._scroll_to = None

        mouse = imgui.get_io().mouse_pos
        self._hover_addr = None

        fmt_b = "{:02X} " if self.uppercase else "{:02x} "
        fmt_a = f"{{:0{addr_digits}X}}:" if self.uppercase else f"{{:0{addr_digits}x}}:"

        imgui.push_style_var(imgui.StyleVar_.item_spacing, imgui.ImVec2(0.0, 0.0))
        imgui.push_style_var(imgui.StyleVar_.frame_padding, imgui.ImVec2(0.0, 0.0))

        clipper = imgui.ListClipper()
        clipper.begin(n_rows, line_h)
        while clipper.step():
            for row in range(clipper.display_start, clipper.display_end):
                start = row * self.cols
                chunk = data[start : start + self.cols]
                row_y = imgui.get_cursor_screen_pos().y
                row_x = imgui.get_cursor_screen_pos().x

                imgui.text_disabled(fmt_a.format(base_addr + start))

                for i, b in enumerate(chunk):
                    imgui.same_line(hex_x(i))
                    if b == 0 and self.grey_zeros:
                        imgui.text_disabled(fmt_b.format(b))
                    else:
                        imgui.text(fmt_b.format(b))

                    bx = row_x + hex_x(i)
                    if bx <= mouse.x < bx + glyph_w * 2 and row_y <= mouse.y < row_y + line_h:
                        self._hover_addr = start + i

                if self.show_ascii:
                    imgui.same_line(ascii_x0)
                    imgui.text_disabled("".join(chr(b) if 32 <= b < 128 else "." for b in chunk))

        imgui.pop_style_var(2)
        imgui.end_child()

        # Options line
        imgui.separator()
        if imgui.button("Options"):
            imgui.open_popup("##hx_opts")

        if imgui.begin_popup("##hx_opts"):
            col_options = [8, 16, 32]
            col_idx = col_options.index(self.cols) if self.cols in col_options else 1
            changed, col_idx = imgui.combo("Columns", col_idx, ["8", "16", "32"])
            if changed:
                self.cols = col_options[col_idx]
            _, self.grey_zeros = imgui.checkbox("Grey out zeros", self.grey_zeros)
            _, self.uppercase = imgui.checkbox("Uppercase hex", self.uppercase)
            _, self.show_ascii = imgui.checkbox("Show ASCII", self.show_ascii)
            imgui.end_popup()

        imgui.same_line()
        imgui.text_disabled("  Go to:")
        imgui.same_line()
        imgui.set_next_item_width(glyph_w * (addr_digits + 2))
        entered, self._goto_buf = imgui.input_text(
            "##hx_goto",
            self._goto_buf,
            imgui.InputTextFlags_.chars_hexadecimal | imgui.InputTextFlags_.enter_returns_true,
        )
        if entered and self._goto_buf:
            try:
                rel = max(0, int(self._goto_buf, 16) - base_addr)
                row = rel // self.cols
                self._scroll_to = max(0.0, row * line_h - self._child_h * 0.5)
            except ValueError:
                pass

        imgui.same_line()
        rng = f"  {base_addr:0{addr_digits}X}..{base_addr + n - 1:0{addr_digits}X}"
        if not self.uppercase:
            rng = rng.lower()
        imgui.text_disabled(rng)

        # Data preview
        imgui.separator()
        addr = self._hover_addr
        label_w = glyph_w * 16.0

        def _row(label: str, value: str | None) -> None:
            imgui.text_disabled(label)
            imgui.same_line(label_w)
            if value is not None:
                imgui.text(value)
            else:
                imgui.text_disabled("---")

        if addr is not None and addr < n:
            rem = n - addr
            b0 = data[addr]
            i8 = struct.unpack("b", bytes([b0]))[0]
            _row("Uint8 / Int8:", f"{b0} / {i8}  (0x{b0:02X})")
            if rem >= 2:
                u16, = struct.unpack_from(">H", data, addr)
                s16, = struct.unpack_from(">h", data, addr)
                _row("Uint16 / Int16:", f"{u16} / {s16}  (0x{u16:04X})")
            else:
                _row("Uint16 / Int16:", None)
            if rem >= 4:
                u32, = struct.unpack_from(">I", data, addr)
                f32, = struct.unpack_from(">f", data, addr)
                _row("Uint32:", f"{u32}  (0x{u32:08X})")
                _row("Float32:", f"{f32:.6g}")
            else:
                _row("Uint32:", None)
                _row("Float32:", None)
        else:
            _row("Uint8 / Int8:", None)
            _row("Uint16 / Int16:", None)
            _row("Uint32:", None)
            _row("Float32:", None)
