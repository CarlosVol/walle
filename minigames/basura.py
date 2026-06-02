import math
import random
import pyray as pr

_TOXIC_CHANCE        = 0.25
_MAX_BASURAS         = 16
_AUTO_SPAWN_INTERVAL = 0.7   # la montaña suelta basura sola

# muchos puntos repartidos alrededor de la montaña
_SPAWN_OFFSETS = [
    (-160,  -70), (-270,   10), ( -80, -150), (-310,  -90),
    ( 130, -100), ( 110, -190), (-200, -200), (  40, -240),
    (-120,  -30), (-240, -140), (  90,  -40), ( -40, -300),
    (-330,    0), ( 160, -200), (-180, -260), (   0, -120),
    (-300,  -50), (  60, -160), (-100, -220), ( 180,  -80),
]


class BasuraMiniGame:
    TIMEOUT = 20.0
    WALLE_W, WALLE_H      = 210, 250
    WALLE_OPEN_W          = 270   # open sprite is narrower art, force wider render
    BASURA_W, BASURA_H    = 70,  70
    MTN_SIZES = [(333, 602), (320, 460), (300, 320), (280, 200)]
    PILA_W,  PILA_H  = 200, 230
    COOK_TIME         = 1.0
    TOXIC_PENALTY     = 10.0
    GRAVITY           = 0.30  # normalized units/sec²
    MAX_VY            = 0.45   # velocidad de caida tope (evita caida exponencial)
    SHAKE_AMP_DEG     = 5.0   # amplitud balanceo montaña (grados)
    SHAKE_SPEED       = 6.0   # velocidad balanceo
    PILA_EVERY        = 3     # basuras buenas por pila

    # swapped: walle right, pila left
    WALLE_NX, WALLE_NY = 340 / 1392, 629 / 768
    MTN_NX,   MTN_NY   = 1087 / 1392, 480 / 768
    PILA_NX,  PILA_NY  = 171 / 1392, 629 / 768

    def __init__(self, textures: dict) -> None:
        self._tex         = textures
        self._good_count  = 0
        self._elapsed     = 0.0
        self._won         = False
        self._walle_state = "rest"
        self._cook_timer  = 0.0

        # list of active basura pieces
        self._basuras:  list[dict] = []
        self._drag_idx: int | None = None
        self._drag_ox:  int = 0
        self._drag_oy:  int = 0
        self._auto_timer = 0.0

    # ------------------------------------------------------------------ helpers

    def _mountain_idx(self) -> int:
        return min(self._good_count // 3, 3)

    def _pila_idx(self) -> int:
        # una imagen de pila por cada 3 basuras: 3→0, 6→1, 9→2
        return min(self._good_count // self.PILA_EVERY - 1, 2)

    def _rect_px(self, nx, ny, w, h, sw, sh) -> pr.Rectangle:
        return pr.Rectangle(int(nx * sw) - w // 2, int(ny * sh) - h // 2, w, h)

    def _mtn_rect(self, sw, sh) -> pr.Rectangle:
        w, h = self.MTN_SIZES[self._mountain_idx()]
        return self._rect_px(self.MTN_NX, self.MTN_NY, w, h, sw, sh)

    def _walle_rect(self, sw, sh) -> pr.Rectangle:
        return self._rect_px(self.WALLE_NX, self.WALLE_NY, self.WALLE_W, self.WALLE_H, sw, sh)

    def _basura_rect(self, piece: dict, sw, sh) -> pr.Rectangle:
        return pr.Rectangle(
            int(piece["nx"] * sw) - self.BASURA_W // 2,
            int(piece["ny"] * sh) - self.BASURA_H // 2,
            self.BASURA_W, self.BASURA_H,
        )

    def _spawn_basura(self) -> None:
        dx, dy = random.choice(_SPAWN_OFFSETS)
        nx = (1087 + dx) / 1392
        ny = (430  + dy) / 768
        is_toxic = random.random() < _TOXIC_CHANCE
        btype = "toxica" if is_toxic else random.randint(1, 5)
        self._basuras.append({"type": btype, "nx": nx, "ny": ny,
                               "spawn_nx": nx, "spawn_ny": ny, "vy": 0.0})

    def _deliver(self, idx: int) -> None:
        piece = self._basuras.pop(idx)
        self._drag_idx = None
        if piece["type"] == "toxica":
            self._elapsed = min(self._elapsed + self.TOXIC_PENALTY, self.TIMEOUT)
        else:
            self._good_count += 1
            self._walle_state = "cooking"
            self._cook_timer  = self.COOK_TIME
            if self._good_count >= 9:
                self._won = True

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

        # cooking countdown
        if self._walle_state == "cooking":
            self._cook_timer -= dt
            if self._cook_timer <= 0:
                self._walle_state = "rest"

        # la montaña suelta basura sola
        self._auto_timer += dt
        if self._auto_timer >= _AUTO_SPAWN_INTERVAL:
            self._auto_timer = 0.0
            if len(self._basuras) < _MAX_BASURAS:
                self._spawn_basura()

        # click mountain → spawn up to 6
        if pressed and self._drag_idx is None:
            if len(self._basuras) < _MAX_BASURAS:
                if pr.check_collision_point_rec(mp, self._mtn_rect(sw, sh)):
                    self._spawn_basura()

        # drag start — pick topmost (last in list)
        if pressed and self._drag_idx is None:
            for i in range(len(self._basuras) - 1, -1, -1):
                br = self._basura_rect(self._basuras[i], sw, sh)
                if pr.check_collision_point_rec(mp, br):
                    self._drag_idx = i
                    cx = int(self._basuras[i]["nx"] * sw)
                    cy = int(self._basuras[i]["ny"] * sh)
                    self._drag_ox = cx - int(mp.x)
                    self._drag_oy = cy - int(mp.y)
                    break

        if self._drag_idx is not None:
            if self._walle_state != "cooking":
                self._walle_state = "open"
            p = self._basuras[self._drag_idx]
            p["vy"] = 0.0  # reset so no launch on release
            if down:
                p["nx"] = (int(mp.x) + self._drag_ox) / sw
                p["ny"] = (int(mp.y) + self._drag_oy) / sh
            if released:
                if self._walle_state == "open":
                    self._walle_state = "rest"
                br = self._basura_rect(p, sw, sh)
                wr = self._walle_rect(sw, sh)
                if pr.check_collision_recs(br, wr):
                    self._deliver(self._drag_idx)
                else:
                    self._drag_idx = None   # release into gravity
        else:
            if self._walle_state == "open":
                self._walle_state = "rest"

        # gravity + off-screen culling (reverse iterate to allow safe pop)
        for i in range(len(self._basuras) - 1, -1, -1):
            if i == self._drag_idx:
                continue
            p = self._basuras[i]
            p["vy"] = min(p["vy"] + self.GRAVITY * dt, self.MAX_VY)
            p["ny"] += p["vy"] * dt
            if p["ny"] > 1.15:
                self._basuras.pop(i)
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

        # mountain (con balanceo propio: rota desde la base)
        mi = self._mountain_idx()
        mtn_tex = self._tex["montana"][mi]
        mw, mh = self.MTN_SIZES[mi]
        angle = math.sin(self._elapsed * self.SHAKE_SPEED) * self.SHAKE_AMP_DEG
        mcx = int(self.MTN_NX * sw)
        mbase_y = int(self.MTN_NY * sh) + mh // 2   # pivote en la base
        pr.draw_texture_pro(
            mtn_tex,
            pr.Rectangle(0, 0, mtn_tex.width, mtn_tex.height),
            pr.Rectangle(mcx, mbase_y, mw, mh),
            pr.Vector2(mw / 2, mh),   # origen: centro-inferior
            angle, pr.WHITE,
        )

        # pila (cambia de imagen cada PILA_EVERY basuras)
        if self._good_count >= self.PILA_EVERY:
            pila_tex = self._tex["pila"][self._pila_idx()]
            blit(pila_tex, self.PILA_NX, self.PILA_NY, self.PILA_W, self.PILA_H)

        # all basura pieces
        for i, piece in enumerate(self._basuras):
            b_tex = (self._tex["toxica"] if piece["type"] == "toxica"
                     else self._tex["basura"][piece["type"] - 1])
            blit(b_tex, piece["nx"], piece["ny"], self.BASURA_W, self.BASURA_H)

        # walle
        walle_tex = self._tex[f"walle_{self._walle_state}"]
        ww = self.WALLE_OPEN_W if self._walle_state == "open" else self.WALLE_W
        blit(walle_tex, self.WALLE_NX, self.WALLE_NY, ww, self.WALLE_H)

        # timeout bar
        remaining = max(0.0, self.TIMEOUT - self._elapsed)
        bar_w = int((sw - 100) * remaining / self.TIMEOUT)
        color = pr.GREEN if remaining > 10 else (pr.ORANGE if remaining > 5 else pr.RED)
        pr.draw_rectangle(50, sh - 30, sw - 100, 20, pr.DARKGRAY)
        pr.draw_rectangle(50, sh - 30, bar_w, 20, color)

        # indicador: cuanta basura falta para la proxima pila
        in_cycle  = self._good_count % self.PILA_EVERY
        faltan    = self.PILA_EVERY - in_cycle
        ind_cx    = int(self.PILA_NX * sw)
        ind_y     = int(0.42 * sh)
        lbl       = f"Pila en {faltan}"
        pr.draw_text(lbl, ind_cx - pr.measure_text(lbl, 20) // 2, ind_y - 30, 20, pr.RAYWHITE)
        dot_r  = 12
        dot_gap = 34
        x0 = ind_cx - (self.PILA_EVERY - 1) * dot_gap // 2
        for d in range(self.PILA_EVERY):
            cx = x0 + d * dot_gap
            if d < in_cycle:
                pr.draw_circle(cx, ind_y, dot_r, pr.GREEN)
            else:
                pr.draw_circle_lines(cx, ind_y, dot_r, pr.RAYWHITE)

        # hud
        pilas = self._good_count // self.PILA_EVERY
        msg = f"Arrastra la basura a Walle!   Pilas {pilas}/3"
        pr.draw_text(msg, (sw - pr.measure_text(msg, 22)) // 2, 16, 22, pr.RAYWHITE)

        if self._drag_idx is not None:
            dragged = self._basuras[self._drag_idx]
            if dragged["type"] == "toxica":
                warn = "TOXICA - no se la des a Walle!"
                pr.draw_text(warn, (sw - pr.measure_text(warn, 20)) // 2, 46, 20, pr.RED)

        if len(self._basuras) >= _MAX_BASURAS:
            hint = "Entrega basura primero!"
            pr.draw_text(hint, (sw - pr.measure_text(hint, 18)) // 2, 46, 18, pr.ORANGE)

    @property
    def is_complete(self) -> bool:
        return self._won or self._elapsed >= self.TIMEOUT

    @property
    def passed(self) -> bool:
        return self._won
