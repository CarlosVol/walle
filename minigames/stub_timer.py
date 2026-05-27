import pyray as pr

_DURATION = 3.0


class SurviveTimerMinigame:
    """Wait out the countdown without pressing anything."""

    def __init__(self):
        self._elapsed = 0.0

    def update(self, dt: float) -> None:
        self._elapsed += dt

    def draw(self, sw: int, sh: int) -> None:
        pr.clear_background(pr.Color(60, 10, 10, 255))
        msg = "¡Sobrevive!"
        mw  = pr.measure_text(msg, 56)
        pr.draw_text(msg, (sw - mw) // 2, int(sh * 0.30), 56, pr.RAYWHITE)
        remaining = max(0.0, _DURATION - self._elapsed)
        label = f"{remaining:.1f}"
        lw = pr.measure_text(label, 96)
        pr.draw_text(label, (sw - lw) // 2, int(sh * 0.45), 96, pr.GOLD)

    @property
    def is_complete(self) -> bool:
        return self._elapsed >= _DURATION

    @property
    def passed(self) -> bool:
        return True
