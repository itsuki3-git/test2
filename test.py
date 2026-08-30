import flet as ft

def main(page: ft.Page):
    page.title = "空間カウント付き 5×3 グリッド"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # スマホ向けにセルサイズを縮小 (100 -> 65)
    CELL_W = 65
    CELL_H = 65
    ROWS = 3
    COLS = 5
    LINE_THICK = 6
    
    # タッチ判定を広げるための拡張幅 (上下左右に14px拡張)
    HIT_BOX_EXT = 14

    TOTAL_W = CELL_W * COLS
    TOTAL_H = CELL_H * ROWS

    current_mode = "COLOR"
    
    # 指定された色の選択肢 (緑色、レンガ色、黒色)
    PALETTE_COLORS = [ft.Colors.GREEN_400, ft.Colors.BROWN_400, ft.Colors.BLACK]
    selected_color = PALETTE_COLORS[0]
    
    # 引いた線の色を「茶色」に変更
    ACTIVE_LINE_COLOR = ft.Colors.BROWN_700
    INACTIVE_LINE_COLOR = ft.Colors.GREY_300

    horiz_line_dict = {}
    vert_line_dict = {}

    # --- 完全に囲まれた空間だけを数えるアルゴリズム ---
    def count_enclosed_spaces():
        visited = { (r, c): False for r in range(-1, ROWS + 1) for c in range(-1, COLS + 1) }

        # 1. 盤面の外側（境界線の外）すべてを「外部空間」としてキューの初期値にする
        queue = []
        for r in range(-1, ROWS + 1):
            for c in range(-1, COLS + 1):
                if r == -1 or r == ROWS or c == -1 or c == COLS:
                    visited[(r, c)] = True
                    queue.append((r, c))

        # 2. 外部空間から「茶線（壁）」に阻まれないエリアをすべて探索
        while queue:
            curr_r, curr_c = queue.pop(0)

            # 上への移動
            if curr_r > -1:
                if 0 <= curr_r < ROWS + 1 and 0 <= curr_c < COLS:
                    if horiz_line_dict[(curr_r, curr_c)].bgcolor != ACTIVE_LINE_COLOR:
                        if not visited[(curr_r - 1, curr_c)]:
                            visited[(curr_r - 1, curr_c)] = True
                            queue.append((curr_r - 1, curr_c))

            # 下への移動
            if curr_r < ROWS:
                if 0 <= curr_r + 1 < ROWS + 1 and 0 <= curr_c < COLS:
                    if horiz_line_dict[(curr_r + 1, curr_c)].bgcolor != ACTIVE_LINE_COLOR:
                        if not visited[(curr_r + 1, curr_c)]:
                            visited[(curr_r + 1, curr_c)] = True
                            queue.append((curr_r + 1, curr_c))

            # 左への移動
            if curr_c > -1:
                if 0 <= curr_c < COLS + 1 and 0 <= curr_r < ROWS:
                    if vert_line_dict[(curr_c, curr_r)].bgcolor != ACTIVE_LINE_COLOR:
                        if not visited[(curr_r, curr_c - 1)]:
                            visited[(curr_r, curr_c - 1)] = True
                            queue.append((curr_r, curr_c - 1))

            # 右への移動
            if curr_c < COLS:
                if 0 <= curr_c + 1 < COLS + 1 and 0 <= curr_r < ROWS:
                    if vert_line_dict[(curr_c + 1, curr_r)].bgcolor != ACTIVE_LINE_COLOR:
                        if not visited[(curr_r, curr_c + 1)]:
                            visited[(curr_r, curr_c + 1)] = True
                            queue.append((curr_r, curr_c + 1))

        # 3. 外から到達できなかった閉じ込められた空間のグループ数をカウント
        enclosed_count = 0
        for r in range(ROWS):
            for c in range(COLS):
                if not visited[(r, c)]:
                    enclosed_count += 1
                    inner_queue = [(r, c)]
                    visited[(r, c)] = True
                    while inner_queue:
                        curr_r, curr_c = inner_queue.pop(0)

                        # 上
                        if curr_r > 0 and horiz_line_dict[(curr_r, curr_c)].bgcolor != ACTIVE_LINE_COLOR:
                            if not visited[(curr_r - 1, curr_c)]:
                                visited[(curr_r - 1, curr_c)] = True
                                inner_queue.append((curr_r - 1, curr_c))
                        # 下
                        if curr_r < ROWS - 1 and horiz_line_dict[(curr_r + 1, curr_c)].bgcolor != ACTIVE_LINE_COLOR:
                            if not visited[(curr_r + 1, curr_c)]:
                                visited[(curr_r + 1, curr_c)] = True
                                inner_queue.append((curr_r + 1, curr_c))
                        # 左
                        if curr_c > 0 and vert_line_dict[(curr_c, curr_r)].bgcolor != ACTIVE_LINE_COLOR:
                            if not visited[(curr_r, curr_c - 1)]:
                                visited[(curr_r, curr_c - 1)] = True
                                inner_queue.append((curr_r, curr_c - 1))
                        # 右
                        if curr_c < COLS - 1 and vert_line_dict[(curr_c + 1, curr_r)].bgcolor != ACTIVE_LINE_COLOR:
                            if not visited[(curr_r, curr_c + 1)]:
                                visited[(curr_r, curr_c + 1)] = True
                                inner_queue.append((curr_r, curr_c + 1))

        return enclosed_count

    def update_mode_ui():
        if current_mode == "COLOR":
            mode_text.value = "現在のモード: 🎨 色塗り中"
            mode_text.color = ft.Colors.BLUE_700
            line_mode_btn.style = ft.ButtonStyle(bgcolor=ft.Colors.GREY_300, color=ft.Colors.BLACK,
                                                 shape=ft.RoundedRectangleBorder(radius=8))
        else:
            mode_text.value = "現在のモード: ✏️ 線を選択中"
            mode_text.color = ft.Colors.BLACK
            line_mode_btn.style = ft.ButtonStyle(bgcolor=ft.Colors.BLACK, color=ft.Colors.WHITE,
                                                 shape=ft.RoundedRectangleBorder(radius=8))
            for c in palette_row.controls:
                c.border = None

        spaces = count_enclosed_spaces()
        space_count_text.value = f"📦 茶線で囲まれた空間の数: {spaces} つ"

        line_mode_btn.update()
        mode_text.update()
        palette_row.update()
        space_count_text.update()
        stack_layout.update()

    def on_palette_click(e):
        nonlocal selected_color, current_mode
        current_mode = "COLOR"
        selected_color = e.control.data
        for c in palette_row.controls:
            c.border = None
        e.control.border = ft.border.all(3, ft.Colors.BLUE_900)
        update_mode_ui()

    def on_line_mode_click(e):
        nonlocal current_mode
        current_mode = "LINE"
        update_mode_ui()

    def on_cell_click(e):
        if current_mode == "COLOR":
            e.control.bgcolor = selected_color
            e.control.update()

    def toggle_line(e):
        if current_mode == "LINE":
            # タッチ判定用の透明コンテナがタップされた場合、e.control は外側の Container
            # 実際に色を変えたい内側の線（content）の bgcolor を切り替える
            target_line = e.control.content
            if target_line.bgcolor == ACTIVE_LINE_COLOR:
                target_line.bgcolor = INACTIVE_LINE_COLOR
            else:
                target_line.bgcolor = ACTIVE_LINE_COLOR
            update_mode_ui()

    palette_options = [
        ft.Container(width=40, height=40, bgcolor=col, border_radius=20, data=col, on_click=on_palette_click) for col in
        PALETTE_COLORS]

    palette_options[0].border = ft.border.all(3, ft.Colors.BLUE_900)

    palette_row = ft.Row(controls=palette_options, alignment=ft.MainAxisAlignment.CENTER)

    line_mode_btn = ft.ElevatedButton(
        text="✏️ 茶線を選択する",
        on_click=on_line_mode_click,
        style=ft.ButtonStyle(bgcolor=ft.Colors.GREY_300, color=ft.Colors.BLACK,
                             shape=ft.RoundedRectangleBorder(radius=8))
    )

    top_control_row = ft.Row(controls=[palette_row, ft.VerticalDivider(width=20), line_mode_btn],
                             alignment=ft.MainAxisAlignment.CENTER)
    mode_text = ft.Text("現在のモード: 🎨 色塗り中", size=16, weight="bold", color=ft.Colors.BLUE_700)
    space_count_text = ft.Text("📦 茶線で囲まれた空間の数: 0 つ", size=18, weight="bold", color=ft.Colors.GREEN_700)

    stack_layout = ft.Stack(width=TOTAL_W, height=TOTAL_H)

    # セル配置 (3行5列)
    for r in range(ROWS):
        for c in range(COLS):
            cell = ft.Container(
                content=ft.Text(f"{r * COLS + c + 1}", color=ft.Colors.GREY_400, size=12),
                alignment=ft.alignment.center, bgcolor=ft.Colors.GREY_100,
                width=CELL_W, height=CELL_H, left=c * CELL_W, top=r * CELL_H,
                on_click=on_cell_click
            )
            stack_layout.controls.append(cell)

    # 横線配置 (タッチ判定拡張版)
    for r in range(ROWS + 1):
        for c in range(COLS):
            left_pos = c * CELL_W
            top_pos = r * CELL_H - (LINE_THICK / 2)
            if r == 0: top_pos = 0
            if r == ROWS: top_pos = TOTAL_H - LINE_THICK

            # 実際の見た目の線
            actual_line = ft.Container(
                width=CELL_W, height=LINE_THICK, bgcolor=INACTIVE_LINE_COLOR
            )
            
            # タッチ判定を広げるための透明な外枠コンテナ
            touch_hitbox = ft.Container(
                content=actual_line,
                alignment=ft.alignment.center,
                width=CELL_W,
                height=LINE_THICK + (HIT_BOX_EXT * 2),
                left=left_pos,
                top=top_pos - HIT_BOX_EXT if (0 < r < ROWS) else (top_pos if r == 0 else top_pos - (HIT_BOX_EXT * 2)),
                bgcolor=ft.Colors.TRANSPARENT,
                on_click=toggle_line
            )
            
            stack_layout.controls.append(touch_hitbox)
            horiz_line_dict[(r, c)] = actual_line

    # 縦線配置 (タッチ判定拡張版)
    for c in range(COLS + 1):
        for r in range(ROWS):
            left_pos = c * CELL_W - (LINE_THICK / 2)
            top_pos = r * CELL_H
            if c == 0: left_pos = 0
            if c == COLS: left_pos = TOTAL_W - LINE_THICK

            # 実際の見た目の線
            actual_line = ft.Container(
                width=LINE_THICK, height=CELL_H, bgcolor=INACTIVE_LINE_COLOR
            )
            
            # タッチ判定を広げるための透明な外枠コンテナ
            touch_hitbox = ft.Container(
                content=actual_line,
                alignment=ft.alignment.center,
                width=LINE_THICK + (HIT_BOX_EXT * 2),
                height=CELL_H,
                left=left_pos - HIT_BOX_EXT if (0 < c < COLS) else (left_pos if c == 0 else left_pos - (HIT_BOX_EXT * 2)),
                top=top_pos,
                bgcolor=ft.Colors.TRANSPARENT,
                on_click=toggle_line
            )

            stack_layout.controls.append(touch_hitbox)
            vert_line_dict[(c, r)] = actual_line

    page.add(
        ft.Column([
            top_control_row,
            mode_text,
            ft.Divider(),
            ft.Container(content=stack_layout, border=ft.border.all(1, ft.Colors.GREY_300)),
            ft.Divider(),
            space_count_text
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    ft.app(target=main, host="0.0.0.0", view=ft.AppView.WEB_BROWSER, port=port)
