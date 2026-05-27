import pyray as pr
import random

_TIMEOUT = 5.0


class CollectDotMinigame:
    """Click the dot before time runs out."""

    def __init__(self):
        self._dot_x_ratio = random.uniform(0.15, 0.85)
        self._dot_y_ratio = random.uniform(0.20, 0.80)
        self._elapsed     = 0.0
        self._won         = False

    def update(self, dt: float) -> None:
        self._elapsed += dt
        if pr.is_mouse_button_pressed(pr.MOUSE_BUTTON_LEFT):
            sw = pr.get_screen_width()
            sh = pr.get_screen_height()
            dx = pr.get_mouse_x() - int(self._dot_x_ratio * sw)
            dy = pr.get_mouse_y() - int(self._dot_y_ratio * sh)
            if (dx * dx + dy * dy) ** 0.5 < 30:
                self._won = True

    def draw(self, sw: int, sh: int) -> None:
        dot_x = int(self._dot_x_ratio * sw)
        dot_y = int(self._dot_y_ratio * sh)
        pr.clear_background(pr.Color(20, 20, 60, 255))
        pr.draw_circle(dot_x, dot_y, 30, pr.YELLOW)
        msg = "¡Haz clic en el punto!"
        mw  = pr.measure_text(msg, 32)
        pr.draw_text(msg, (sw - mw) // 2, 40, 32, pr.RAYWHITE)
        remaining = max(0.0, _TIMEOUT - self._elapsed)
        bar_w = int((sw - 100) * remaining / _TIMEOUT)
        pr.draw_rectangle(50, sh - 30, sw - 100, 20, pr.DARKGRAY)
        pr.draw_rectangle(50, sh - 30, bar_w, 20, pr.ORANGE)

    @property
    def is_complete(self) -> bool:
        return self._won or self._elapsed >= _TIMEOUT

    @property
    def passed(self) -> bool:
        return self._won
