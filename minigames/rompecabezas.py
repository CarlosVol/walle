import random
import pyray as pr


class RompecabezasMiniGame:
    TIMEOUT    = 15.0
    GRID       = 3
    BASE_W, BASE_H = 1392, 768
    BOARD_CX, BOARD_CY = 731, 393
    BOARD_SIZE = 540
    SNAP_DIST  = 70           # px base
    HIT_HALF   = 80           # mitad zona de agarre (px base)

    def __init__(self, textures: dict) -> None:
        self._tex   = textures
        self._v     = random.randint(0, 2)           # variante elegida
        man         = textures["manifest"][self._v]
        self._img_w = man["img_w"]
        self._cell  = man["cell"]
        self._margin = man["margin"]
        # lado de dibujo de la pieza en px base (canvas imagen → tablero)
        canvas_img  = self._cell + 2 * self._margin
        self._draw  = canvas_img * self.BOARD_SIZE / self._img_w
        self._elapsed = 0.0
        self._won     = False

        # piezas regadas en franjas laterales, desordenadas
        scatter = self._scatter_points()
        random.shuffle(scatter)
        self._pieces: list[dict] = []
        k = 0
        for r in range(self.GRID):
            for c in range(self.GRID):
                sx, sy = scatter[k]; k += 1
                self._pieces.append({"r": r, "c": c, "nx": sx, "ny": sy,
                                     "placed": False})
        self._drag_idx: int | None = None
        self._drag_ox = 0.0
        self._drag_oy = 0.0

    # ------------------------------------------------------------------ helpers

    def _scatter_points(self) -> list:
        pts = []
        ys = [0.20, 0.42, 0.64, 0.84]
        for i in range(self.GRID + 2):                # izquierda
            pts.append((random.uniform(0.05, 0.18), ys[i % len(ys)] + random.uniform(-0.04, 0.04)))
        for i in range(self.GRID + 1):                # derecha
            pts.append((random.uniform(0.82, 0.95), ys[i % len(ys)] + random.uniform(-0.04, 0.04)))
        return pts[:self.GRID * self.GRID]

    def _cell_center_base(self, r: int, c: int) -> tuple:
        left = self.BOARD_CX - self.BOARD_SIZE / 2
        top  = self.BOARD_CY - self.BOARD_SIZE / 2
        step = self.BOARD_SIZE / self.GRID
        return left + (c + 0.5) * step, top + (r + 0.5) * step

    def _target_n(self, p: dict) -> tuple:
        cx, cy = self._cell_center_base(p["r"], p["c"])
        return cx / self.BASE_W, cy / self.BASE_H

    # ------------------------------------------------------------------ protocol

    def update(self, dt: float) -> None:
        self._elapsed += dt
        if self._won or self._elapsed >= self.TIMEOUT:
            return

        sw = pr.get_screen_width()
        sh = pr.get_screen_height()
        mp = pr.get_mouse_position()
        pressed  = pr.is_mouse_button_pressed(pr.MOUSE_BUTTON_LEFT)
        released = pr.is_mouse_button_released(pr.MOUSE_BUTTON_LEFT)
        down     = pr.is_mouse_button_down(pr.MOUSE_BUTTON_LEFT)

        hit_half_x = self.HIT_HALF / self.BASE_W * sw
        hit_half_y = self.HIT_HALF / self.BASE_H * sh

        # tomar pieza (topmost no colocada)
        if pressed and self._drag_idx is None:
            for i in range(len(self._pieces) - 1, -1, -1):
                p = self._pieces[i]
                if p["placed"]:
                    continue
                cx = p["nx"] * sw
                cy = p["ny"] * sh
                if abs(mp.x - cx) <= hit_half_x and abs(mp.y - cy) <= hit_half_y:
                    self._drag_idx = i
                    self._drag_ox = cx - mp.x
                    self._drag_oy = cy - mp.y
                    # mover al final para dibujar encima
                    self._pieces.append(self._pieces.pop(i))
                    self._drag_idx = len(self._pieces) - 1
                    break

        if self._drag_idx is not None and down:
            p = self._pieces[self._drag_idx]
            p["nx"] = (mp.x + self._drag_ox) / sw
            p["ny"] = (mp.y + self._drag_oy) / sh

        if self._drag_idx is not None and released:
            p = self._pieces[self._drag_idx]
            tnx, tny = self._target_n(p)
            dx = (p["nx"] - tnx) * self.BASE_W
            dy = (p["ny"] - tny) * self.BASE_H
            if (dx * dx + dy * dy) ** 0.5 < self.SNAP_DIST:
                p["nx"], p["ny"] = tnx, tny
                p["placed"] = True
            self._drag_idx = None
            if all(pc["placed"] for pc in self._pieces):
                self._won = True

    def draw(self, sw: int, sh: int) -> None:
        def blit(tex, nx, ny, w, h, tint=pr.WHITE):
            rw = w / self.BASE_W * sw
            rh = h / self.BASE_H * sh
            pr.draw_texture_pro(
                tex,
                pr.Rectangle(0, 0, tex.width, tex.height),
                pr.Rectangle(nx * sw - rw / 2, ny * sh - rh / 2, rw, rh),
                pr.Vector2(0, 0), 0.0, tint,
            )

        # fondo
        bg = self._tex["escenario"]
        pr.draw_texture_pro(
            bg,
            pr.Rectangle(0, 0, bg.width, bg.height),
            pr.Rectangle(0, 0, sw, sh),
            pr.Vector2(0, 0), 0.0, pr.WHITE,
        )

        # tablero: outline + guia fantasma
        left = (self.BOARD_CX - self.BOARD_SIZE / 2) / self.BASE_W * sw
        top  = (self.BOARD_CY - self.BOARD_SIZE / 2) / self.BASE_H * sh
        bw   = self.BOARD_SIZE / self.BASE_W * sw
        bh   = self.BOARD_SIZE / self.BASE_H * sh
        guide = self._tex["variantes"][self._v]
        pr.draw_texture_pro(
            guide,
            pr.Rectangle(0, 0, guide.width, guide.height),
            pr.Rectangle(left, top, bw, bh),
            pr.Vector2(0, 0), 0.0, pr.Color(255, 255, 255, 60),
        )
        pr.draw_rectangle_lines_ex(pr.Rectangle(left, top, bw, bh), 2.0,
                                   pr.Color(255, 220, 120, 120))

        # piezas (orden de lista; arrastrada al final)
        for p in self._pieces:
            tex = self._tex["piezas"][self._v][p["r"]][p["c"]]
            blit(tex, p["nx"], p["ny"], self._draw, self._draw)

        # barra de tiempo
        remaining = max(0.0, self.TIMEOUT - self._elapsed)
        bar_w = int((sw - 100) * remaining / self.TIMEOUT)
        color = pr.GREEN if remaining > 7 else (pr.ORANGE if remaining > 3 else pr.RED)
        pr.draw_rectangle(50, sh - 30, sw - 100, 20, pr.DARKGRAY)
        pr.draw_rectangle(50, sh - 30, bar_w, 20, color)
        secs = f"{int(remaining)}s"
        pr.draw_text(secs, sw // 2 - pr.measure_text(secs, 18) // 2, sh - 29, 18, pr.BLACK)

        # hud
        placed = sum(1 for p in self._pieces if p["placed"])
        msg = f"Arma el rompecabezas!   {placed}/{self.GRID * self.GRID}"
        pr.draw_text(msg, (sw - pr.measure_text(msg, 24)) // 2, 16, 24, pr.RAYWHITE)

    @property
    def is_complete(self) -> bool:
        return self._won or self._elapsed >= self.TIMEOUT

    @property
    def passed(self) -> bool:
        return self._won
