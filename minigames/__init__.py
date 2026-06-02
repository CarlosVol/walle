import random
from .base         import Minigame
from .stub_collect import CollectDotMinigame
from .stub_timer   import SurviveTimerMinigame

_maze_assets:       dict | None = None
_basura_assets:     dict | None = None
_memoria_assets:    dict | None = None
_recolector_assets: dict | None = None


def set_maze_assets(assets: dict) -> None:
    global _maze_assets
    _maze_assets = assets


def set_basura_assets(assets: dict) -> None:
    global _basura_assets
    _basura_assets = assets


def set_memoria_assets(assets: dict) -> None:
    global _memoria_assets
    _memoria_assets = assets


def set_recolector_assets(assets: dict) -> None:
    global _recolector_assets
    _recolector_assets = assets


def get_random_minigame() -> Minigame:
    from .maze       import MazeMiniGame
    from .basura     import BasuraMiniGame
    from .memoria    import MemoryMiniGame
    from .recolector import RecolectorMiniGame
    options: list = [CollectDotMinigame, SurviveTimerMinigame]
    if _maze_assets is not None:
        options.append(lambda: MazeMiniGame(**_maze_assets))
    if _basura_assets is not None:
        options.append(lambda: BasuraMiniGame(_basura_assets))
    if _memoria_assets is not None:
        options.append(lambda: MemoryMiniGame(_memoria_assets))
    if _recolector_assets is not None:
        options.append(lambda: RecolectorMiniGame(_recolector_assets))
    return random.choice(options)()


def get_minigame_by_name(name: str) -> Minigame:
    from .maze       import MazeMiniGame
    from .basura     import BasuraMiniGame
    from .memoria    import MemoryMiniGame
    from .recolector import RecolectorMiniGame
    match name:
        case "maze":
            return MazeMiniGame(**_maze_assets)
        case "basura":
            return BasuraMiniGame(_basura_assets)
        case "collect":
            return CollectDotMinigame()
        case "timer":
            return SurviveTimerMinigame()
        case "memoria":
            return MemoryMiniGame(_memoria_assets)
        case "recolector":
            return RecolectorMiniGame(_recolector_assets)
        case _:
            raise ValueError(f"Unknown minigame: {name}")


__all__ = ["Minigame", "get_random_minigame", "set_maze_assets", "set_basura_assets", "set_memoria_assets", "set_recolector_assets", "get_minigame_by_name"]
