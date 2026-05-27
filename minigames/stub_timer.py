import pyray as pr

_DURATION = 3.0


class SurviveTimerMinigame:
    """Wait out the countdown without pressing anything."""

    def __init__(self):
        self._elapsed = 0.0

    def update(self, dt: float) -> None:
        self._elapsed += dt

    def draw(self) -> None:
        pr.clear_background(pr.Color(60, 10, 10, 255))
        pr.draw_text("¡Sobrevive!", 300, 180, 40, pr.RAYWHITE)
        remaining = max(0.0, _DURATION - self._elapsed)
        label = f"{remaining:.1f}"
        lw = pr.measure_text(label, 72)
        pr.draw_text(label, (800 - lw) // 2, 270, 72, pr.GOLD)

    @property
    def is_complete(self) -> bool:
        return self._elapsed >= _DURATION

    @property
    def passed(self) -> bool:
        return True
