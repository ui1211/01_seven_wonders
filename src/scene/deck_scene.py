from __future__ import annotations

from src.scene.base_scene import BaseScene, SceneRuntime


class DeckScene(BaseScene):
    def __init__(self):
        self.page = 0

    @staticmethod
    def _fmt_with_growth(value: int, growth: int) -> str:
        g = int(growth)
        if g == 0:
            return str(value)
        sign = "+" if g > 0 else ""
        return f"{value}({sign}{g})"

    def _layout(self, runtime: SceneRuntime):
        margin = 10
        table_x = margin
        table_y = 30
        table_w = runtime.width - margin * 2
        table_h = runtime.height - 86
        row_h = 24
        rows_per_page = max(3, (table_h - row_h) // row_h)

        cols = [
            ("カード名", 240),
            ("枚数", 56),
            ("ATK", 90),
            ("MGC", 90),
            ("TEC", 90),
            ("COST", 90),
            ("技能値", 74),
        ]

        # Expand name column to fit exact width
        used = sum(w for _, w in cols)
        cols[0] = (cols[0][0], cols[0][1] + (table_w - used))
        return table_x, table_y, table_w, table_h, row_h, rows_per_page, cols

    def _button_rects(self, runtime: SceneRuntime):
        back_w = 68
        back_h = 18
        back_x = runtime.width - back_w - 10
        back_y = runtime.height - back_h - 8

        prev_x = 10
        prev_y = back_y
        prev_w = 48
        prev_h = 18

        next_x = 62
        next_y = back_y
        next_w = 48
        next_h = 18
        return (back_x, back_y, back_w, back_h), (prev_x, prev_y, prev_w, prev_h), (next_x, next_y, next_w, next_h)

    def update(self, runtime: SceneRuntime, mx: int, my: int):
        pyxel = runtime.pyxel
        rows = runtime.game.get_owned_card_rows()
        _tx, _ty, _tw, _th, _rh, rows_per_page, _cols = self._layout(runtime)
        max_page = max(0, (len(rows) - 1) // rows_per_page)
        self.page = max(0, min(self.page, max_page))

        if pyxel.btnp(pyxel.KEY_UP):
            self.page = max(0, self.page - 1)
        if pyxel.btnp(pyxel.KEY_DOWN):
            self.page = min(max_page, self.page + 1)

        if not pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            return

        back, prev, nxt = self._button_rects(runtime)
        if runtime.hit_rect(mx, my, *back):
            runtime.game.close_deck_scene()
            return
        if runtime.hit_rect(mx, my, *prev):
            self.page = max(0, self.page - 1)
            return
        if runtime.hit_rect(mx, my, *nxt):
            self.page = min(max_page, self.page + 1)

    def draw(self, runtime: SceneRuntime):
        pyxel = runtime.pyxel
        game = runtime.game
        ui = runtime.renderer.ui
        text = runtime.renderer.text

        pyxel.cls(0)
        text.draw(12, 12, "DECK LIST", 10)

        tx, ty, tw, th, row_h, rows_per_page, cols = self._layout(runtime)

        rows = game.get_owned_card_rows()
        max_page = max(0, (len(rows) - 1) // rows_per_page)
        self.page = max(0, min(self.page, max_page))
        start = self.page * rows_per_page
        page_rows = rows[start : start + rows_per_page]

        # Table frame and grid
        pyxel.rect(tx, ty, tw, th, 0)
        pyxel.rectb(tx, ty, tw, th, 7)

        # Vertical lines + header
        cx = tx
        text_y = ty + 8
        for name, w in cols:
            pyxel.line(cx, ty, cx, ty + th, 5)
            text.draw(cx + 4, text_y, name, 7)
            cx += w
        pyxel.line(tx + tw, ty, tx + tw, ty + th, 5)

        # Header separator
        pyxel.line(tx, ty + row_h, tx + tw, ty + row_h, 7)

        # Row separators
        for i in range(1, rows_per_page + 1):
            y = ty + row_h + i * row_h
            if y <= ty + th:
                pyxel.line(tx, y, tx + tw, y, 5)

        # Data rows
        y = ty + row_h + 8
        for r in page_rows:
            cells = [
                str(r["name"]),
                str(r["count"]),
                self._fmt_with_growth(r["atk"], r.get("atk_growth", 0)),
                self._fmt_with_growth(r["mgc"], r.get("mgc_growth", 0)),
                self._fmt_with_growth(r["tec"], r.get("tec_growth", 0)),
                self._fmt_with_growth(r["cost"], r.get("cost_growth", 0)),
                self._fmt_with_growth(r["success"], r.get("success_growth", 0)),
            ]

            cx = tx
            for (col_name, w), cell in zip(cols, cells):
                _ = col_name
                s = cell
                if len(s) > 22:
                    s = s[:19] + "..."
                text.draw(cx + 4, y, s, 7)
                cx += w
            y += row_h

        back, prev, nxt = self._button_rects(runtime)
        ui.draw_button(*prev, "Prev")
        ui.draw_button(*nxt, "Next")
        ui.draw_button(*back, "戻る")
        text.draw(120, runtime.height - 24, f"Page {self.page + 1}/{max_page + 1}", 6)
