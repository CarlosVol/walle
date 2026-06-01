import random
from .base         import Minigame
from .stub_collect import CollectDotMinigame
from .stub_timer   import SurviveTimerMinigame

_maze_assets: dict | None = None


def set_maze_assets(assets: dict) -> None:
    global _maze_assets
    _maze_assets = assets


def get_random_minigame() -> Minigame:
    from .maze import MazeMiniGame
    options: list = [CollectDotMinigame, SurviveTimerMinigame]
    if _maze_assets is not None:
        options.append(lambda: MazeMiniGame(**_maze_assets))
    return random.choice(options)()


__all__ = ["Minigame", "get_random_minigame", "set_maze_assets"]
