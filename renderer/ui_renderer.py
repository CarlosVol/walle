import pyray as pr

SCREEN_W = 800
SCREEN_H = 600


def draw_menu() -> bool:
    pr.clear_background(pr.BLACK)

    title = "WALLE"
    tw = pr.measure_text(title, 64)
    pr.draw_text(title, (SCREEN_W - tw) // 2, 160, 64, pr.RAYWHITE)

    btn_w, btn_h = 200, 60
    btn_x = (SCREEN_W - btn_w) // 2
    btn_y = 320

    mx = pr.get_mouse_x()
    my = pr.get_mouse_y()
    hovered = btn_x <= mx <= btn_x + btn_w and btn_y <= my <= btn_y + btn_h
    color = pr.GOLD if hovered else pr.DARKGRAY

    pr.draw_rectangle(btn_x, btn_y, btn_w, btn_h, color)
    pr.draw_rectangle_lines(btn_x, btn_y, btn_w, btn_h, pr.RAYWHITE)
    label = "INICIAR"
    lw = pr.measure_text(label, 28)
    pr.draw_text(label, btn_x + (btn_w - lw) // 2, btn_y + 16, 28, pr.RAYWHITE)

    return hovered and pr.is_mouse_button_pressed(pr.MOUSE_BUTTON_LEFT)


def draw_win_screen(steps: int) -> None:
    pr.clear_background(pr.DARKGREEN)
    msg = "¡LLEGASTE!"
    mw = pr.measure_text(msg, 56)
    pr.draw_text(msg, (SCREEN_W - mw) // 2, 200, 56, pr.GOLD)
    sub = f"Nodos visitados: {steps}"
    sw = pr.measure_text(sub, 28)
    pr.draw_text(sub, (SCREEN_W - sw) // 2, 290, 28, pr.RAYWHITE)
    hint = "Cierra la ventana para salir"
    hw = pr.measure_text(hint, 20)
    pr.draw_text(hint, (SCREEN_W - hw) // 2, 500, 20, pr.LIGHTGRAY)


def draw_hud(current_node: str, end_node: str, steps: int) -> None:
    pr.draw_text(f"Nodo actual: {current_node}", 10, 10, 18, pr.RAYWHITE)
    pr.draw_text(f"Destino: {end_node}", 10, 32, 18, pr.GOLD)
    pr.draw_text(f"Pasos: {steps}", 10, 54, 18, pr.LIGHTGRAY)
    pr.draw_text("Clic en nodo adyacente para moverte", 10, SCREEN_H - 28, 16, pr.GRAY)
