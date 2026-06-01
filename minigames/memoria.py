import random
import pyray as pr

REVEAL_DELAY = 0.7
_BASE_W, _BASE_H = 1392, 768
_CARD_W, _CARD_H = 140, 190
_GAP = 20
_COLS, _ROWS = 8, 2


class MemoryMiniGame:
    def __init__(self, assets: dict) -> None:
        self._assets = assets

        ids = list(range(8)) * 2
        random.shuffle(ids)

        grid_w = _COLS * _CARD_W + (_COLS - 1) * _GAP
        grid_h = _ROWS * _CARD_H + (_ROWS - 1) * _GAP
        ox = (_BASE_W - grid_w) // 2
        oy = (_BASE_H - grid_h) // 2

        self._cards: list[dict] = []
        for i, card_id in enumerate(ids):
            col = i % _COLS
            row = i // _COLS
            nx = (ox + col * (_CARD_W + _GAP)) / _BASE_W
            ny = (oy + row * (_CARD_H + _GAP)) / _BASE_H
            self._cards.append({
                "id": card_id,
                "face_up": False,
                "matched": False,
                "nx": nx,
                "ny": ny,
            })

        self._flipped: list[int] = []
        self._locked = False
        self._reveal_timer = 0.0
        self._complete = False

    def _card_rect(self, card: dict, sw: int, sh: int) -> pr.Rectangle:
        sx = sw / _BASE_W
        sy = sh / _BASE_H
        cw = int(_CARD_W * sx)
        ch = int(_CARD_H * sy)
        x = int(card["nx"] * sw)
        y = int(card["ny"] * sh)
        return pr.Rectangle(x, y, cw, ch)

    def update(self, dt: float) -> None:
        if self._complete:
            return

        if self._locked:
            self._reveal_timer -= dt
            if self._reveal_timer <= 0.0:
                a, b = self._flipped
                if self._cards[a]["id"] == self._cards[b]["id"]:
                    self._cards[a]["matched"] = True
                    self._cards[b]["matched"] = True
                else:
                    self._cards[a]["face_up"] = False
                    self._cards[b]["face_up"] = False
                self._flipped.clear()
                self._locked = False

        if all(c["matched"] for c in self._cards):
            self._complete = True

    def draw(self, sw: int, sh: int) -> None:
        esc = self._assets["escenario"]
        pr.draw_texture_pro(
            esc,
            pr.Rectangle(0, 0, esc.width, esc.height),
            pr.Rectangle(0, 0, sw, sh),
            pr.Vector2(0, 0), 0.0, pr.WHITE,
        )

        mx, my = pr.get_mouse_x(), pr.get_mouse_y()
        clicked = pr.is_mouse_button_pressed(pr.MOUSE_BUTTON_LEFT)

        back_tex = self._assets["carta_detras"]
        front_texs = self._assets["cartas"]

        for i, card in enumerate(self._cards):
            if card["matched"]:
                continue

            rect = self._card_rect(card, sw, sh)

            if card["face_up"]:
                tex = front_texs[card["id"]]
            else:
                tex = back_tex
                if (not self._locked
                        and len(self._flipped) < 2
                        and clicked
                        and pr.check_collision_point_rec(pr.Vector2(mx, my), rect)):
                    card["face_up"] = True
                    self._flipped.append(i)
                    if len(self._flipped) == 2:
                        self._locked = True
                        self._reveal_timer = REVEAL_DELAY

            pr.draw_texture_pro(
                tex,
                pr.Rectangle(0, 0, tex.width, tex.height),
                rect,
                pr.Vector2(0, 0), 0.0, pr.WHITE,
            )

        remaining = sum(1 for c in self._cards if not c["matched"])
        matched_pairs = (16 - remaining) // 2
        msg = f"Pares encontrados: {matched_pairs}/8"
        pr.draw_text(msg, 14, 14, 28, pr.GOLD)

    @property
    def is_complete(self) -> bool:
        return self._complete

    @property
    def passed(self) -> bool:
        return True
