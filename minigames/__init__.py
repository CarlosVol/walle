import random
from .base import Minigame
from .stub_collect import CollectDotMinigame
from .stub_timer   import SurviveTimerMinigame

_REGISTRY: dict[str, type] = {
    "collect_dot":   CollectDotMinigame,
    "survive_timer": SurviveTimerMinigame,
}


def get_random_minigame() -> Minigame:
    cls = random.choice(list(_REGISTRY.values()))
    return cls()


def get_minigame(name: str) -> Minigame:
    return _REGISTRY[name]()


__all__ = ["Minigame", "get_random_minigame", "get_minigame"]
