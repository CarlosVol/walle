import pyray as pr
import random

_TIMEOUT = 5.0


class CollectDotMinigame:
    """Click the dot before time runs out."""

    def __init__(self):
        self._dot_x   = random.randint(100, 700)
        self._dot_y   = random.randint(120, 480)
        self._elapsed = 0.0
        self._won     = False

    def update(self, dt: float) -> None:
        self._elapsed += dt
        if pr.is_mouse_button_pressed(pr.MOUSE_BUTTON_LEFT):
            dx = pr.get_mouse_x() - self._dot_x
            dy = pr.get_mouse_y() - self._dot_y
            if (dx * dx + dy * dy) ** 0.5 < 24:
                self._won = True

    def draw(self) -> None:
        pr.clear_background(pr.Color(20, 20, 60, 255))
        pr.draw_circle(self._dot_x, self._dot_y, 24, pr.YELLOW)
        pr.draw_text("¡Haz clic en el punto!", 220, 30, 26, pr.RAYWHITE)
        remaining = max(0.0, _TIMEOUT - self._elapsed)
        bar_w = int(700 * remaining / _TIMEOUT)
        pr.draw_rectangle(50, 560, 700, 16, pr.DARKGRAY)
        pr.draw_rectangle(50, 560, bar_w, 16, pr.ORANGE)

    @property
    def is_complete(self) -> bool:
        return self._won or self._elapsed >= _TIMEOUT

    @property
    def passed(self) -> bool:
        return self._won
