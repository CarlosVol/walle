import pyray as pr


def draw_menu(cover_texture: pr.Texture, sw: int, sh: int) -> bool:
    # stretch image to fill screen
    src  = pr.Rectangle(0, 0, cover_texture.width, cover_texture.height)
    dest = pr.Rectangle(0, 0, sw, sh)
    pr.draw_texture_pro(cover_texture, src, dest, pr.Vector2(0, 0), 0.0, pr.WHITE)

    # dark overlay so button is readable
    pr.draw_rectangle(0, 0, sw, sh, pr.Color(0, 0, 0, 120))

    btn_w, btn_h = 260, 70
    btn_x = (sw - btn_w) // 2
    btn_y = int(sh * 0.70)

    mx = pr.get_mouse_x()
    my = pr.get_mouse_y()
    hovered = btn_x <= mx <= btn_x + btn_w and btn_y <= my <= btn_y + btn_h
    bg = pr.Color(200, 160, 0, 220) if hovered else pr.Color(40, 40, 40, 200)

    pr.draw_rectangle(btn_x, btn_y, btn_w, btn_h, bg)
    pr.draw_rectangle_lines_ex(pr.Rectangle(btn_x, btn_y, btn_w, btn_h), 3, pr.RAYWHITE)
    label = "INICIAR"
    lw = pr.measure_text(label, 34)
    pr.draw_text(label, btn_x + (btn_w - lw) // 2, btn_y + 18, 34, pr.RAYWHITE)

    return hovered and pr.is_mouse_button_pressed(pr.MOUSE_BUTTON_LEFT)


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
