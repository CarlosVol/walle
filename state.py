from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional


class GamePhase(Enum):
    MENU     = auto()
    GRAPH    = auto()
    MINIGAME = auto()
    CASA     = auto()
    WIN      = auto()


@dataclass
class GameState:
    phase:           GamePhase      = GamePhase.MENU
    start_node:      Optional[str]  = None
    end_node:        Optional[str]  = None
    current_node:    Optional[str]  = None
    optimal_path:    list           = field(default_factory=list)
    visited_nodes:   set            = field(default_factory=set)
    active_minigame: Optional[object] = None
    minigame_result: Optional[bool] = None
    boots:           int             = 0
    map_index:       int             = 1
