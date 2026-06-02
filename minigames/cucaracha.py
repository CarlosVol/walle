import math
import random
import pyray as pr


class CucarachaMiniGame:
    WIN_COUNT      = 3
    LIVES          = 2
    BASE_W, BASE_H = 1392, 768
    SLOTS          = [(473, 387), (695, 385), (920, 385)]
    HIT_RADIUS     = 65
    CAN_W, CAN_H   = 150, 157
    CUCA_W, CUCA_H = 95, 110
    FX_W, FX_H     = 120, 117
    REVEAL_TIME    = 1.5
    RESULT_TIME    = 1.5
    SWAP_DUR       = 0.22
    LIFT           = 70    # px levantar lata al revelar
    ARC_LIFT       = 50    # px arco durante swap

    def __init__(self, textures: dict) -> None:
        self._tex   = textures
        self._found = 0
        self._lives = self.LIVES
        self._round = 0
        self._won   = False
        self._done  = False
        self._start_round()

    # ------------------------------------------------------------------ helpers

    def _start_round(self) -> None:
        self._can_slot     = [0, 1, 2]            # can i ocupa slot can_slot[i]
        self._cuca_can     = random.randint(0, 2)
        self._cuca_variant = random.randint(0, 2)
        self._phase        = "reveal"
        self._timer        = 0.0
        # cola de swaps pendientes: (can_a, can_b)
        self._swaps        = self._build_swaps()
        self._swap_t       = 0.0
        self._swap_from    = None   # (slot_a, slot_b) origen de la animación
        self._guess_slot   = None   # slot clickeado en result
        self._guess_ok     = False

    def _build_swaps(self) -> list:
        n = 6 + self._round * 3
        swaps = []
        for _ in range(n):
            a, b = random.sample((0, 1, 2), 2)
            swaps.append((a, b))
        return swaps

    def _slot_px(self, slot: int, sw: int, sh: int) -> tuple:
        cx, cy = self.SLOTS[slot]
        return cx / self.BASE_W * sw, cy / self.BASE_H * sh

    def _can_pos(self, can: int, sw: int, sh: int) -> tuple:
        """Posición pixel (cx, cy) de la lata, interpolada si está en swap."""
        slot = self._can_slot[can]
        x, y = self._slot_px(slot, sw, sh)
        if self._phase == "shuffle" and self._swap_from is not None:
            ca, cb = self._swaps[0]
            if can in (ca, cb):
                t = min(1.0, self._swap_t / self.SWAP_DUR)
                fa, fb = self._swap_from
                src = fa if can == ca else fb
                dst = fb if can == ca else fa
                sx, sy = self._slot_px(src, sw, sh)
                dx, dy = self._slot_px(dst, sw, sh)
                x = sx + (dx - sx) * t
                y = sy + (dy - sy) * t - math.sin(t * math.pi) * self.ARC_LIFT * sh / self.BASE_H
        return x, y

    def _blit(self, tex, cx, cy, w, h, sw, sh) -> None:
        rw = w * sw / self.BASE_W
        rh = h * sh / self.BASE_H
        pr.draw_texture_pro(
            tex,
            pr.Rectangle(0, 0, tex.width, tex.height),
            pr.Rectangle(cx - rw / 2, cy - rh / 2, rw, rh),
            pr.Vector2(0, 0), 0.0, pr.WHITE,
        )

    # ------------------------------------------------------------------ protocol

    def update(self, dt: float) -> None:
        if self._done:
            return
        self._timer += dt

        if self._phase == "reveal":
            if self._timer >= self.REVEAL_TIME:
                self._phase  = "shuffle"
                self._timer  = 0.0
                self._begin_next_swap()

        elif self._phase == "shuffle":
            self._swap_t += dt
            if self._swap_t >= self.SWAP_DUR:
                ca, cb = self._swaps.pop(0)
                self._can_slot[ca], self._can_slot[cb] = self._can_slot[cb], self._can_slot[ca]
                if self._swaps:
                    self._begin_next_swap()
                else:
                    self._phase = "guess"
                    self._timer = 0.0

        elif self._phase == "guess":
            if pr.is_mouse_button_pressed(pr.MOUSE_BUTTON_LEFT):
                mp = pr.get_mouse_position()
                sw, sh = pr.get_screen_width(), pr.get_screen_height()
                slot = self._slot_at(mp, sw, sh)
                if slot is not None:
                    self._resolve_guess(slot)

        elif self._phase == "result":
            if self._timer >= self.RESULT_TIME:
                if self._found >= self.WIN_COUNT:
                    self._won, self._done = True, True
                elif self._lives <= 0:
                    self._won, self._done = False, True
                else:
                    self._round += 1
                    self._start_round()

    def _begin_next_swap(self) -> None:
        self._swap_t    = 0.0
        ca, cb          = self._swaps[0]
        self._swap_from = (self._can_slot[ca], self._can_slot[cb])

    def _slot_at(self, mp, sw: int, sh: int):
        r = self.HIT_RADIUS * sw / self.BASE_W
        for slot in range(3):
            sx, sy = self._slot_px(slot, sw, sh)
            if (mp.x - sx) ** 2 + (mp.y - sy) ** 2 <= r * r:
                return slot
        return None

    def _resolve_guess(self, slot: int) -> None:
        cuca_slot = self._can_slot[self._cuca_can]
        self._guess_slot = slot
        self._guess_ok   = (slot == cuca_slot)
        if self._guess_ok:
            self._found += 1
        else:
            self._lives -= 1
        self._phase = "result"
        self._timer = 0.0

    def draw(self, sw: int, sh: int) -> None:
        bg = self._tex["escenario"]
        pr.draw_texture_pro(
            bg,
            pr.Rectangle(0, 0, bg.width, bg.height),
            pr.Rectangle(0, 0, sw, sh),
            pr.Vector2(0, 0), 0.0, pr.WHITE,
        )

        cuca_slot = self._can_slot[self._cuca_can]

        # en reveal y result siempre se levanta la lata de la cucaracha
        # (en result revela donde estaba; si ademas fallo, X sobre la clickeada)
        lifted_slot = cuca_slot if self._phase in ("reveal", "result") else None

        # dibujar cucaracha primero (debajo de las latas)
        if self._phase in ("reveal", "result"):
            cx, cy = self._slot_px(cuca_slot, sw, sh)
            cuca_tex = self._tex["cucarachas"][self._cuca_variant]
            self._blit(cuca_tex, cx, cy + 10 * sh / self.BASE_H,
                       self.CUCA_W, self.CUCA_H, sw, sh)

        # latas (orden por slot para z razonable)
        cans = sorted(range(3), key=lambda c: self._can_slot[c])
        moving = self._phase == "shuffle"
        for can in cans:
            cx, cy = self._can_pos(can, sw, sh)
            slot   = self._can_slot[can]
            lift   = 0.0
            if lifted_slot is not None and slot == lifted_slot:
                lift = self.LIFT * sh / self.BASE_H
            tex = self._tex["lata_mov"] if moving else self._tex["lata"]
            self._blit(tex, cx, cy - lift, self.CAN_W, self.CAN_H, sw, sh)

        # feedback acierto/fallo en result
        if self._phase == "result" and self._guess_slot is not None:
            gx, gy = self._slot_px(self._guess_slot, sw, sh)
            fx_tex = self._tex["destello"] if self._guess_ok else self._tex["x"]
            self._blit(fx_tex, gx, gy - self.LIFT * sh / self.BASE_H,
                       self.FX_W, self.FX_H, sw, sh)

        # hud
        hud = f"Cucarachas {self._found}/{self.WIN_COUNT}    Vidas: {self._lives}"
        pr.draw_text(hud, (sw - pr.measure_text(hud, 26)) // 2, 16, 26, pr.RAYWHITE)

        if self._phase == "guess":
            hint = "Cual lata esconde la cucaracha? Click!"
            pr.draw_text(hint, (sw - pr.measure_text(hint, 22)) // 2, 52, 22, pr.GOLD)

    @property
    def is_complete(self) -> bool:
        return self._done

    @property
    def passed(self) -> bool:
        return self._won
