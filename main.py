import random
import pyray as pr

from state import GameState, GamePhase
from graph import NODES, EDGES, dijkstra, get_adjacent
from renderer.graph_renderer import draw_graph
from renderer.ui_renderer    import draw_menu, draw_win_screen, draw_hud
from minigames                import get_random_minigame

SCREEN_W = 800
SCREEN_H = 600


def _start_game(state: GameState) -> None:
    node_ids = list(NODES.keys())
    state.start_node, state.end_node = random.sample(node_ids, 2)
    state.current_node  = state.start_node
    state.visited_nodes = {state.start_node}
    state.optimal_path  = dijkstra(NODES, EDGES, state.start_node, state.end_node)
    state.minigame_result = None
    state.phase         = GamePhase.GRAPH


def _is_valid_move(state: GameState, node_id: str) -> bool:
    return (
        node_id in get_adjacent(EDGES, state.current_node)
        and node_id not in state.visited_nodes
    )


def _move_to(state: GameState, node_id: str) -> None:
    state.current_node = node_id
    state.visited_nodes.add(node_id)
    if node_id == state.end_node:
        state.phase = GamePhase.WIN
    else:
        state.active_minigame = get_random_minigame()
        state.phase = GamePhase.MINIGAME


def main() -> None:
    pr.init_window(SCREEN_W, SCREEN_H, "Walle")
    pr.set_target_fps(60)

    state = GameState()

    while not pr.window_should_close():
        dt = pr.get_frame_time()

        if state.phase == GamePhase.MINIGAME and state.active_minigame:
            state.active_minigame.update(dt)
            if state.active_minigame.is_complete:
                state.minigame_result = state.active_minigame.passed
                state.active_minigame = None
                state.phase = GamePhase.GRAPH

        pr.begin_drawing()

        if state.phase == GamePhase.MENU:
            if draw_menu():
                _start_game(state)

        elif state.phase == GamePhase.GRAPH:
            pr.clear_background(pr.Color(30, 30, 30, 255))
            adjacent = get_adjacent(EDGES, state.current_node) if state.current_node else []
            clicked = draw_graph(
                NODES, EDGES,
                state.optimal_path,
                state.current_node,
                state.visited_nodes,
                state.start_node,
                state.end_node,
                adjacent,
            )
            draw_hud(state.current_node, state.end_node, len(state.visited_nodes))

            if state.minigame_result is not None:
                msg = "Minijuego superado!" if state.minigame_result else "Fallaste el minijuego"
                color = pr.GREEN if state.minigame_result else pr.RED
                pr.draw_text(msg, 10, SCREEN_H - 52, 18, color)

            if clicked and _is_valid_move(state, clicked):
                _move_to(state, clicked)

        elif state.phase == GamePhase.MINIGAME and state.active_minigame:
            state.active_minigame.draw()

        elif state.phase == GamePhase.WIN:
            draw_win_screen(len(state.visited_nodes))

        pr.end_drawing()

    pr.close_window()


if __name__ == "__main__":
    main()
