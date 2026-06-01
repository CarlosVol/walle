import random
import pyray as pr

MAZE_CONFIGS = [
    {   # laberinto_1
        "starts": [(649 / 1392, 100 / 768)],
        "exit":   (803 / 1392, 115 / 768),
    },
    {   # laberinto_2
        "starts": [(791 / 1392, 204 / 768), (154 / 1392, 209 / 768)],
        "exit":   (701 / 1392, 743 / 768),
    },
    {   # laberinto_3
        "starts": [(845 / 1392, 108 / 768), (1120 / 1392, 236 / 768), (719 / 1392, 555 / 768)],
        "exit":   (730 / 1392, 750 / 768),
    },
]


class MazeMiniGame:
    SPEED       = 180   # screen px/sec
    SPRITE_SIZE = 40    # render px
    TIMEOUT     = 45.0

    def __init__(self, maze_imgs, maze_texs, walle_sprites):
        idx           = random.randint(0, 2)
        self._img     = maze_imgs[idx]
        self._tex     = maze_texs[idx]
        self._sprites = walle_sprites
        cfg           = MAZE_CONFIGS[idx]
        self._x, self._y = random.choice(cfg["starts"])
        self._exit    = cfg["exit"]
        self._dir     = "right"
        self._elapsed = 0.0
        self._won     = False

    def _is_wall(self, xr: float, yr: float) -> bool:
        ix = max(0, min(self._img.width  - 1, int(xr * self._img.width)))
        iy = max(0, min(self._img.height - 1, int(yr * self._img.height)))
        c = pr.get_image_color(self._img, ix, iy)
        return c.r < 80 and c.g < 80 and c.b < 80

    def _blocked(self, xr: float, yr: float, sw: int, sh: int) -> bool:
        hx = self.SPRITE_SIZE * 0.4 / sw
        hy = self.SPRITE_SIZE * 0.4 / sh
        return any(
            self._is_wall(xr + dx, yr + dy)
            for dx, dy in [(-hx, -hy), (hx, -hy), (-hx, hy), (hx, hy)]
        )

    def update(self, dt: float) -> None:
        self._elapsed += dt
        sw = pr.get_screen_width()
        sh = pr.get_screen_height()
        dx = dy = 0.0

        if pr.is_key_down(pr.KEY_RIGHT) or pr.is_key_down(pr.KEY_D):
            dx = +self.SPEED / sw * dt
            self._dir = "right"
        elif pr.is_key_down(pr.KEY_LEFT) or pr.is_key_down(pr.KEY_A):
            dx = -self.SPEED / sw * dt
            self._dir = "left"
        if pr.is_key_down(pr.KEY_DOWN) or pr.is_key_down(pr.KEY_S):
            dy = +self.SPEED / sh * dt
            self._dir = "down"
        elif pr.is_key_down(pr.KEY_UP) or pr.is_key_down(pr.KEY_W):
            dy = -self.SPEED / sh * dt
            self._dir = "up"

        if dx and not self._blocked(self._x + dx, self._y, sw, sh):
            self._x += dx
        if dy and not self._blocked(self._x, self._y + dy, sw, sh):
            self._y += dy

        ex, ey = self._exit
        if ((self._x - ex) * 1392) ** 2 + ((self._y - ey) * 768) ** 2 < 30 ** 2:
            self._won = True

    def draw(self, sw: int, sh: int) -> None:
        pr.draw_texture_pro(
            self._tex,
            pr.Rectangle(0, 0, self._tex.width, self._tex.height),
            pr.Rectangle(0, 0, sw, sh),
            pr.Vector2(0, 0), 0.0, pr.WHITE,
        )

        sp   = self._sprites[self._dir]
        half = self.SPRITE_SIZE // 2
        pr.draw_texture_pro(
            sp,
            pr.Rectangle(0, 0, sp.width, sp.height),
            pr.Rectangle(int(self._x * sw) - half, int(self._y * sh) - half,
                         self.SPRITE_SIZE, self.SPRITE_SIZE),
            pr.Vector2(0, 0), 0.0, pr.WHITE,
        )

        # exit marker
        ex, ey = self._exit
        pr.draw_circle(int(ex * sw), int(ey * sh), 10, pr.Color(0, 255, 100, 180))

        remaining = max(0.0, self.TIMEOUT - self._elapsed)
        bar_w = int((sw - 100) * remaining / self.TIMEOUT)
        color = pr.GREEN if remaining > 15 else (pr.ORANGE if remaining > 7 else pr.RED)
        pr.draw_rectangle(50, sh - 30, sw - 100, 20, pr.DARKGRAY)
        pr.draw_rectangle(50, sh - 30, bar_w, 20, color)

        msg = "Llega a la salida!   WASD / flechas"
        pr.draw_text(msg, (sw - pr.measure_text(msg, 22)) // 2, 16, 22, pr.RAYWHITE)

    @property
    def is_complete(self) -> bool:
        return self._won or self._elapsed >= self.TIMEOUT

    @property
    def passed(self) -> bool:
        return self._won
