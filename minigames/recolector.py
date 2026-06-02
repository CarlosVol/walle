import math
import random
import pyray as pr

_VALIOSO_CHANCE  = 0.25
_SPAWN_INTERVAL  = 0.09375


class RecolectorMiniGame:
    TIMEOUT        = 12.0
    N_VALIOSO      = 3       # tipos de valioso
    NEED_PER_TYPE  = 3       # cantidad requerida de cada uno
    ITEM_SPEED     = 160     # px/s en resolución base 1392
    GRAVITY        = 0.9     # normalized/s²
    TIME_PENALTY   = 5.0
    ITEM_W, ITEM_H = 70, 70
    BASE_W, BASE_H = 1392, 768

    # conveyor belt
    CONV_X1, CONV_Y1 = 128, 264
    CONV_X2, CONV_Y2 = 1190, 519

    # basket (centro + tamaño, mas grande y notorio)
    BASKET_CX, BASKET_CY = 1279, 690
    BASKET_W,  BASKET_H  = 170, 180   # zona de colision (base px)
    CESTA_W,   CESTA_H   = 210, 225   # render sprite

    def __init__(self, textures: dict) -> None:
        self._tex         = textures
        self._items:  list[dict] = []
        self._drag_idx: int | None = None
        self._drag_ox   = 0
        self._drag_oy   = 0
        self._counts    = [0] * self.N_VALIOSO   # recolectados por tipo
        self._elapsed   = 0.0
        self._spawn_timer = 0.0
        self._won       = False

    # ------------------------------------------------------------------ helpers

    def _conv_rect(self, sw: int, sh: int) -> pr.Rectangle:
        x = int(self.CONV_X1 / self.BASE_W * sw)
        y = int(self.CONV_Y1 / self.BASE_H * sh)
        w = int((self.CONV_X2 - self.CONV_X1) / self.BASE_W * sw)
        h = int((self.CONV_Y2 - self.CONV_Y1) / self.BASE_H * sh)
        return pr.Rectangle(x, y, w, h)

    def _basket_rect(self, sw: int, sh: int) -> pr.Rectangle:
        w = self.BASKET_W / self.BASE_W * sw
        h = self.BASKET_H / self.BASE_H * sh
        cx = self.BASKET_CX / self.BASE_W * sw
        cy = self.BASKET_CY / self.BASE_H * sh
        return pr.Rectangle(cx - w / 2, cy - h / 2, w, h)

    def _item_rect(self, p: dict, sw: int, sh: int) -> pr.Rectangle:
        return pr.Rectangle(
            int(p["nx"] * sw) - self.ITEM_W // 2,
            int(p["ny"] * sh) - self.ITEM_H // 2,
            self.ITEM_W, self.ITEM_H,
        )

    def _spawn(self) -> None:
        is_valioso = random.random() < _VALIOSO_CHANCE
        itype = random.randint(1, 3) if is_valioso else random.randint(1, 7)
        ny_min = self.CONV_Y1 / self.BASE_H
        ny_max = self.CONV_Y2 / self.BASE_H
        self._items.append({
            "is_valioso": is_valioso,
            "type":       itype,
            "nx":         self.CONV_X1 / self.BASE_W,
            "ny":         random.uniform(ny_min, ny_max),
            "vy":         0.0,
            "on_belt":    True,
        })

    def _deliver(self, idx: int) -> None:
        piece = self._items.pop(idx)
        self._drag_idx = None
        if piece["is_valioso"]:
            t = piece["type"] - 1
            if self._counts[t] < self.NEED_PER_TYPE:
                self._counts[t] += 1
            if all(c >= self.NEED_PER_TYPE for c in self._counts):
                self._won = True
        else:
            self._elapsed = min(self._elapsed + self.TIME_PENALTY, self.TIMEOUT)

    # ------------------------------------------------------------------ protocol

    def update(self, dt: float) -> None:
        self._elapsed += dt
        if self._won or self._elapsed >= self.TIMEOUT:
            return

        sw = pr.get_screen_width()
        sh = pr.get_screen_height()

        self._spawn_timer += dt
        if self._spawn_timer >= _SPAWN_INTERVAL:
            self._spawn_timer = 0.0
            self._spawn()

        mp       = pr.get_mouse_position()
        pressed  = pr.is_mouse_button_pressed(pr.MOUSE_BUTTON_LEFT)
        released = pr.is_mouse_button_released(pr.MOUSE_BUTTON_LEFT)
        down     = pr.is_mouse_button_down(pr.MOUSE_BUTTON_LEFT)

        # drag start
        if pressed and self._drag_idx is None:
            for i in range(len(self._items) - 1, -1, -1):
                ir = self._item_rect(self._items[i], sw, sh)
                if pr.check_collision_point_rec(mp, ir):
                    self._drag_idx = i
                    cx = int(self._items[i]["nx"] * sw)
                    cy = int(self._items[i]["ny"] * sh)
                    self._drag_ox = cx - int(mp.x)
                    self._drag_oy = cy - int(mp.y)
                    self._items[i]["on_belt"] = False
                    break

        # drag move
        if self._drag_idx is not None and down:
            p = self._items[self._drag_idx]
            p["vy"] = 0.0
            p["nx"] = (int(mp.x) + self._drag_ox) / sw
            p["ny"] = (int(mp.y) + self._drag_oy) / sh

        # drag release
        if self._drag_idx is not None and released:
            p  = self._items[self._drag_idx]
            ir = self._item_rect(p, sw, sh)
            br = self._basket_rect(sw, sh)
            cr = self._conv_rect(sw, sh)
            if pr.check_collision_recs(ir, br):
                self._deliver(self._drag_idx)
            elif pr.check_collision_recs(ir, cr):
                p["on_belt"] = True
                self._drag_idx = None
            else:
                p["on_belt"] = False
                self._drag_idx = None

        # autonomous movement
        belt_speed_nx = self.ITEM_SPEED / self.BASE_W * dt
        exit_nx = self.CONV_X2 / self.BASE_W

        for i in range(len(self._items) - 1, -1, -1):
            if i == self._drag_idx:
                continue
            p = self._items[i]
            if p["on_belt"]:
                p["nx"] += belt_speed_nx
                if p["nx"] > exit_nx:
                    self._items.pop(i)
                    if self._drag_idx is not None and self._drag_idx > i:
                        self._drag_idx -= 1
            else:
                p["vy"] += self.GRAVITY * dt
                p["ny"] += p["vy"] * dt
                if p["ny"] > 1.15:
                    self._items.pop(i)
                    if self._drag_idx is not None and self._drag_idx > i:
                        self._drag_idx -= 1

    def draw(self, sw: int, sh: int) -> None:
        def blit(tex, nx, ny, w, h):
            pr.draw_texture_pro(
                tex,
                pr.Rectangle(0, 0, tex.width, tex.height),
                pr.Rectangle(int(nx * sw) - w // 2, int(ny * sh) - h // 2, w, h),
                pr.Vector2(0, 0), 0.0, pr.WHITE,
            )

        # background
        bg = self._tex["escenario"]
        pr.draw_texture_pro(
            bg,
            pr.Rectangle(0, 0, bg.width, bg.height),
            pr.Rectangle(0, 0, sw, sh),
            pr.Vector2(0, 0), 0.0, pr.WHITE,
        )

        # items
        for i, p in enumerate(self._items):
            if p["is_valioso"]:
                tex = self._tex["valioso"][p["type"] - 1]
            else:
                tex = self._tex["basura"][p["type"] - 1]
            blit(tex, p["nx"], p["ny"], self.ITEM_W, self.ITEM_H)

        # halo pulsante detras de la cesta para destacarla
        br = self._basket_rect(sw, sh)
        bcx, bcy = br.x + br.width / 2, br.y + br.height / 2
        pulse = 0.5 + 0.5 * math.sin(self._elapsed * 4.0)
        ring_w = int(br.width * (1.15 + 0.12 * pulse))
        ring_h = int(br.height * (1.15 + 0.12 * pulse))
        pr.draw_ellipse(int(bcx), int(bcy), ring_w // 2, ring_h // 2,
                        pr.Color(255, 215, 0, int(70 + 60 * pulse)))
        pr.draw_ring(pr.Vector2(bcx, bcy), ring_w / 2 - 6, ring_w / 2,
                     0, 360, 64, pr.Color(255, 220, 40, 230))

        # cesta (mas grande)
        basket_cx = self.BASKET_CX / self.BASE_W
        basket_cy = self.BASKET_CY / self.BASE_H
        blit(self._tex["cesta"], basket_cx, basket_cy, self.CESTA_W, self.CESTA_H)

        label = "CESTA"
        pr.draw_text(label, int(bcx) - pr.measure_text(label, 24) // 2,
                     int(br.y - 34), 24, pr.GOLD)

        # timer bar
        remaining = max(0.0, self.TIMEOUT - self._elapsed)
        bar_w = int((sw - 100) * remaining / self.TIMEOUT)
        color = pr.GREEN if remaining > 7 else (pr.ORANGE if remaining > 3 else pr.RED)
        pr.draw_rectangle(50, sh - 30, sw - 100, 20, pr.DARKGRAY)
        pr.draw_rectangle(50, sh - 30, bar_w, 20, color)
        secs = f"{int(remaining)}s"
        pr.draw_text(secs, sw // 2 - pr.measure_text(secs, 18) // 2, sh - 29, 18, pr.BLACK)

        # hud objetivo: icono de cada valioso + progreso
        self._draw_objetivo(sw, sh)

        if self._drag_idx is not None and self._drag_idx < len(self._items):
            dragged = self._items[self._drag_idx]
            if not dragged["is_valioso"]:
                warn = "BASURA - no la pongas en la cesta!"
                pr.draw_text(warn, (sw - pr.measure_text(warn, 20)) // 2, 80, 20, pr.RED)

    def _draw_objetivo(self, sw: int, sh: int) -> None:
        title = "Recolecta 3 de cada valioso!"
        pr.draw_text(title, (sw - pr.measure_text(title, 24)) // 2, 14, 24, pr.RAYWHITE)

        # columna a la izquierda de la cesta, de arriba a abajo
        icon     = int(58 / self.BASE_W * sw)
        step     = 78 / self.BASE_H * sh
        col_cx   = (self.BASKET_CX - 200) / self.BASE_W * sw   # izquierda de la cesta
        basket_y = self.BASKET_CY / self.BASE_H * sh
        y0       = basket_y - step                            # centra los 3 sobre la cesta
        for t in range(self.N_VALIOSO):
            tex = self._tex["valioso"][t]
            iy  = int(y0 + t * step)
            ix  = int(col_cx - icon / 2)
            pr.draw_texture_pro(
                tex,
                pr.Rectangle(0, 0, tex.width, tex.height),
                pr.Rectangle(ix, iy - icon // 2, icon, icon),
                pr.Vector2(0, 0), 0.0, pr.WHITE,
            )
            done = self._counts[t] >= self.NEED_PER_TYPE
            txt  = f"{self._counts[t]}/{self.NEED_PER_TYPE}"
            col  = pr.GREEN if done else pr.RAYWHITE
            pr.draw_text(txt, ix + icon + 10, iy - 14, 30, col)

    @property
    def is_complete(self) -> bool:
        return self._won or self._elapsed >= self.TIMEOUT

    @property
    def passed(self) -> bool:
        return self._won
