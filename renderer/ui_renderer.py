import pyray as pr


def _draw_button(label: str, bx: int, by: int, bw: int, bh: int,
                 font_size: int = 28, normal_color=None, hover_color=None) -> bool:
    if normal_color is None:
        normal_color = pr.Color(40, 40, 40, 200)
    if hover_color is None:
        hover_color = pr.Color(200, 160, 0, 220)
    mx, my = pr.get_mouse_x(), pr.get_mouse_y()
    hovered = bx <= mx <= bx + bw and by <= my <= by + bh
    bg = hover_color if hovered else normal_color
    pr.draw_rectangle(bx, by, bw, bh, bg)
    pr.draw_rectangle_lines_ex(pr.Rectangle(bx, by, bw, bh), 3, pr.RAYWHITE)
    lw = pr.measure_text(label, font_size)
    pr.draw_text(label, bx + (bw - lw) // 2, by + (bh - font_size) // 2, font_size, pr.RAYWHITE)
    return hovered and pr.is_mouse_button_pressed(pr.MOUSE_BUTTON_LEFT)


def draw_menu(cover_texture: pr.Texture, sw: int, sh: int) -> str | None:
    src  = pr.Rectangle(0, 0, cover_texture.width, cover_texture.height)
    dest = pr.Rectangle(0, 0, sw, sh)
    pr.draw_texture_pro(cover_texture, src, dest, pr.Vector2(0, 0), 0.0, pr.WHITE)
    pr.draw_rectangle(0, 0, sw, sh, pr.Color(0, 0, 0, 120))

    btn_w, btn_h = 260, 70
    btn_x = (sw - btn_w) // 2
    btn_y = int(sh * 0.70)

    if _draw_button("INICIAR", btn_x, btn_y, btn_w, btn_h, 34):
        return "iniciar"

    sel_w, sel_h = 300, 55
    sel_x = (sw - sel_w) // 2
    sel_y = btn_y + btn_h + 16
    if _draw_button("SELECTOR DE JUEGOS", sel_x, sel_y, sel_w, sel_h, 22,
                    pr.Color(30, 70, 130, 200), pr.Color(50, 120, 210, 230)):
        return "selector"

    return None


def draw_selector_screen(sw: int, sh: int) -> str | None:
    pr.clear_background(pr.Color(15, 15, 30, 255))

    title = "SELECTOR DE JUEGOS"
    tw = pr.measure_text(title, 48)
    pr.draw_text(title, (sw - tw) // 2, int(sh * 0.08), 48, pr.GOLD)

    games = [
        ("maze",    "Laberinto"),
        ("basura",  "Recoge la Basura"),
        ("collect", "Recoge el Punto"),
        ("timer",   "Sobrevive"),
        ("memoria",    "Memoria"),
        ("recolector", "Recolector"),
    ]

    btn_w, btn_h, gap = 340, 65, 20
    btn_x = (sw - btn_w) // 2
    total_h = len(games) * btn_h + (len(games) - 1) * gap
    start_y = (sh - total_h) // 2

    clicked = None
    for i, (key, label) in enumerate(games):
        by = start_y + i * (btn_h + gap)
        if _draw_button(label, btn_x, by, btn_w, btn_h, 30,
                        pr.Color(40, 60, 40, 210), pr.Color(60, 160, 80, 230)):
            clicked = key

    back_w, back_h = 240, 50
    back_x = (sw - back_w) // 2
    back_y = sh - 90
    if _draw_button("<- Volver al Menu", back_x, back_y, back_w, back_h, 22,
                    pr.Color(80, 30, 30, 200), pr.Color(180, 60, 60, 230)):
        clicked = "back"

    return clicked


def draw_win_screen(steps: int, sw: int, sh: int) -> None:
    pr.clear_background(pr.DARKGREEN)
    msg = "¡GANASTE! 3 botas conseguidas"
    mw = pr.measure_text(msg, 60)
    pr.draw_text(msg, (sw - mw) // 2, int(sh * 0.35), 60, pr.GOLD)
    sub = f"Nodos visitados: {steps}"
    sw2 = pr.measure_text(sub, 32)
    pr.draw_text(sub, (sw - sw2) // 2, int(sh * 0.52), 32, pr.RAYWHITE)
    hint = "Cierra la ventana para salir"
    hw = pr.measure_text(hint, 22)
    pr.draw_text(hint, (sw - hw) // 2, int(sh * 0.85), 22, pr.LIGHTGRAY)


def draw_hud(current_node: str, end_node: str, steps: int, boots: int, sw: int, sh: int) -> None:
    pr.draw_text(f"Nodo actual: {current_node}", 14, 14, 22, pr.RAYWHITE)
    pr.draw_text(f"Destino: {end_node}", 14, 40, 22, pr.GOLD)
    pr.draw_text(f"Pasos: {steps}", 14, 66, 22, pr.LIGHTGRAY)
    pr.draw_text(f"Botas: {boots}/3", 14, 92, 22, pr.GOLD)
    pr.draw_text("Clic en nodo adyacente para moverte", 14, sh - 32, 18, pr.GRAY)


def draw_casa_screen(texture: pr.Texture, boots: int, sw: int, sh: int) -> pr.Rectangle:
    src = pr.Rectangle(0, 0, texture.width, texture.height)
    dest = pr.Rectangle(0, 0, sw, sh)
    pr.draw_texture_pro(texture, src, dest, pr.Vector2(0, 0), 0.0, pr.WHITE)

    msg = f"Botas: {boots}/3"
    pr.draw_text(msg, 20, 20, 32, pr.GOLD)

    btn_w, btn_h = 200, 55
    btn_x = (sw - btn_w) // 2
    btn_y = sh - 100
    mx, my = pr.get_mouse_x(), pr.get_mouse_y()
    hovered = btn_x <= mx <= btn_x + btn_w and btn_y <= my <= btn_y + btn_h
    bg = pr.Color(0, 190, 130, 230) if hovered else pr.Color(0, 130, 90, 200)
    pr.draw_rectangle(btn_x, btn_y, btn_w, btn_h, bg)
    pr.draw_rectangle_lines_ex(pr.Rectangle(btn_x, btn_y, btn_w, btn_h), 3, pr.RAYWHITE)
    lbl = "Continuar"
    lw = pr.measure_text(lbl, 26)
    pr.draw_text(lbl, btn_x + (btn_w - lw) // 2, btn_y + 14, 26, pr.RAYWHITE)
    return pr.Rectangle(btn_x, btn_y, btn_w, btn_h)
