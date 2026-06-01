import random
import pyray as pr

from state import GameState, GamePhase
from graph import NODES, EDGES, dijkstra, get_adjacent
from renderer.graph_renderer import draw_graph
from renderer.ui_renderer    import draw_menu, draw_win_screen, draw_hud, draw_casa_screen, draw_selector_screen
from minigames                import get_random_minigame, get_minigame_by_name, set_maze_assets, set_basura_assets


def _new_round(state: GameState) -> None:
    node_ids = list(NODES.keys())
    state.start_node, state.end_node = random.sample(node_ids, 2)
    state.current_node  = state.start_node
    state.visited_nodes = {state.start_node}
    state.optimal_path  = dijkstra(NODES, EDGES, state.start_node, state.end_node)
    state.minigame_result = None
    state.phase         = GamePhase.GRAPH


def _start_game(state: GameState) -> None:
    state.boots     = 0
    state.map_index = 1
    _new_round(state)


def _is_valid_move(state: GameState, node_id: str) -> bool:
    return (
        node_id in get_adjacent(EDGES, state.current_node)
        and node_id not in state.visited_nodes
    )


def _move_to(state: GameState, node_id: str) -> None:
    state.current_node = node_id
    state.visited_nodes.add(node_id)
    if node_id == state.end_node:
        state.boots += 1
        if state.boots >= 3:
            state.phase = GamePhase.WIN
        else:
            state.map_index += 1
            _new_round(state)
            state.phase = GamePhase.CASA
    else:
        state.active_minigame = get_random_minigame()
        state.phase = GamePhase.MINIGAME


def main() -> None:
    pr.set_config_flags(pr.FLAG_FULLSCREEN_MODE)
    pr.init_window(0, 0, "Walle")
    pr.set_target_fps(60)

    cover_texture = pr.load_texture("images/portada.jpeg")
    map_textures  = [
        pr.load_texture("images/mapa1.png"),
        pr.load_texture("images/mapa2.png"),
        pr.load_texture("images/mapa3.png"),
    ]
    casa_textures = [
        pr.load_texture("images/casa0.png"),
        pr.load_texture("images/casa1.png"),
        pr.load_texture("images/casa2.png"),
    ]

    _base = "images/minigame_laberinto/"
    maze_imgs = [pr.load_image(f"{_base}laberinto_{i}.png") for i in (1, 2, 3)]
    maze_texs = [pr.load_texture(f"{_base}laberinto_{i}.png") for i in (1, 2, 3)]
    walle_sprites = {d: pr.load_texture(f"{_base}walle_{d}.png") for d in ("up", "down", "left", "right")}
    set_maze_assets({"maze_imgs": maze_imgs, "maze_texs": maze_texs, "walle_sprites": walle_sprites})

    _bbase = "images/minigame_basura/"
    basura_textures = {
        "escenario":      pr.load_texture(f"{_bbase}escenario.png"),
        "montana":        [pr.load_texture(f"{_bbase}montaña_{i}.png") for i in (1, 2, 3, 4)],
        "pila":           [pr.load_texture(f"{_bbase}pila_{i}.png") for i in (1, 2, 3)],
        "basura":         [pr.load_texture(f"{_bbase}basura_{i}.png") for i in (1, 2, 3, 4, 5)],
        "toxica":         pr.load_texture(f"{_bbase}basura_toxica.png"),
        "walle_rest":     pr.load_texture(f"{_bbase}walle_rest.png"),
        "walle_open":     pr.load_texture(f"{_bbase}walle_open.png"),
        "walle_cooking":  pr.load_texture(f"{_bbase}walle_cooking.png"),
    }
    set_basura_assets(basura_textures)

    state = GameState()

    while not pr.window_should_close():
        dt          = pr.get_frame_time()
        sw          = pr.get_screen_width()
        sh          = pr.get_screen_height()

        if state.phase == GamePhase.MINIGAME and state.active_minigame:
            state.active_minigame.update(dt)
            if state.active_minigame.is_complete:
                state.minigame_result = state.active_minigame.passed
                state.active_minigame = None
                if state.from_selector:
                    state.from_selector = False
                    state.phase = GamePhase.SELECTOR
                else:
                    state.phase = GamePhase.GRAPH

        pr.begin_drawing()

        if state.phase == GamePhase.MENU:
            action = draw_menu(cover_texture, sw, sh)
            if action == "iniciar":
                _start_game(state)
            elif action == "selector":
                state.phase = GamePhase.SELECTOR

        elif state.phase == GamePhase.SELECTOR:
            clicked = draw_selector_screen(sw, sh)
            if clicked == "back":
                state.phase = GamePhase.MENU
            elif clicked:
                state.active_minigame = get_minigame_by_name(clicked)
                state.from_selector = True
                state.phase = GamePhase.MINIGAME

        elif state.phase == GamePhase.GRAPH:
            pr.clear_background(pr.Color(30, 30, 30, 255))
            tex = map_textures[state.map_index - 1]
            pr.draw_texture_pro(
                tex,
                pr.Rectangle(0, 0, tex.width, tex.height),
                pr.Rectangle(0, 0, sw, sh),
                pr.Vector2(0, 0), 0.0, pr.WHITE,
            )
            adjacent = get_adjacent(EDGES, state.current_node) if state.current_node else []
            clicked = draw_graph(
                NODES, EDGES,
                state.optimal_path,
                state.current_node,
                state.visited_nodes,
                state.start_node,
                state.end_node,
                adjacent,
                sw, sh,
            )
            draw_hud(state.current_node, state.end_node, len(state.visited_nodes), state.boots, sw, sh)

            if state.minigame_result is not None:
                msg = "Minijuego superado!" if state.minigame_result else "Fallaste el minijuego"
                color = pr.GREEN if state.minigame_result else pr.RED
                pr.draw_text(msg, 10, sh - 52, 18, color)

            if clicked == state.start_node:
                state.phase = GamePhase.CASA
            elif clicked and _is_valid_move(state, clicked):
                _move_to(state, clicked)

        elif state.phase == GamePhase.MINIGAME and state.active_minigame:
            state.active_minigame.draw(sw, sh)

        elif state.phase == GamePhase.CASA:
            tex = casa_textures[min(state.boots, 2)]
            continuar_btn = draw_casa_screen(tex, state.boots, sw, sh)
            if pr.is_mouse_button_pressed(pr.MOUSE_BUTTON_LEFT):
                mx, my = pr.get_mouse_x(), pr.get_mouse_y()
                if pr.check_collision_point_rec(pr.Vector2(mx, my), continuar_btn):
                    state.phase = GamePhase.GRAPH

        elif state.phase == GamePhase.WIN:
            draw_win_screen(len(state.visited_nodes), sw, sh)

        pr.end_drawing()

    pr.unload_texture(cover_texture)
    for tex in map_textures:
        pr.unload_texture(tex)
    for tex in casa_textures:
        pr.unload_texture(tex)
    for img in maze_imgs:
        pr.unload_image(img)
    for tex in maze_texs:
        pr.unload_texture(tex)
    for tex in walle_sprites.values():
        pr.unload_texture(tex)
    pr.unload_texture(basura_textures["escenario"])
    for tex in basura_textures["montana"]:
        pr.unload_texture(tex)
    for tex in basura_textures["pila"]:
        pr.unload_texture(tex)
    for tex in basura_textures["basura"]:
        pr.unload_texture(tex)
    pr.unload_texture(basura_textures["toxica"])
    pr.unload_texture(basura_textures["walle_rest"])
    pr.unload_texture(basura_textures["walle_open"])
    pr.unload_texture(basura_textures["walle_cooking"])
    pr.close_window()


if __name__ == "__main__":
    main()
