
import flet as ft

def main(page: ft.Page):
    page.title = "空間カウント付き 5×3 グリッド"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    CELL_W = 65
    CELL_H = 65
    ROWS = 3
    COLS = 5
    LINE_THICK = 6
    HIT_BOX_EXT = 14  # タッチ領域の拡張幅（片側）

    TOTAL_W = CELL_W * COLS
    TOTAL_H = CELL_H * ROWS

    current_mode = "COLOR"
    # 初期選択は「木」の緑色
    selected_color = ft.Colors.GREEN_400

    # パレットの色と名称のマッピング
    COLOR_MAP = {
        ft.Colors.GREEN_400: "木",
        ft.Colors.BROWN_400: "レンガ",
        ft.Colors.BLACK: "石",
        ft.Colors.AMBER_500: "畑"
    }
    PALETTE_COLORS = list(COLOR_MAP.keys())

    horiz_line_dict = {}
    vert_line_dict = {}
    cell_list = []

    # --- 完全に囲まれた空間だけを数えるアルゴリズム ---
    def count_enclosed_spaces():
        visited = { (r, c): False for r in range(-1, ROWS + 1) for c in range(-1, COLS + 1) }

        queue = []
        for r in range(-1, ROWS + 1):
            for c in range(-1, COLS + 1):
                if r == -1 or r == ROWS or c == -1 or c == COLS:
                    visited[(r, c)] = True
                    queue.append((r, c))

        while queue:
            curr_r, curr_c = queue.pop(0)

            # 上への移動
            if curr_r > -1:
                if 0 <= curr_r < ROWS + 1 and 0 <= curr_c < COLS:
                    if horiz_line_dict[(curr_r, curr_c)].bgcolor != ft.Colors.BROWN_700:
                        if not visited[(curr_r - 1, curr_c)]:
                            visited[(curr_r - 1, curr_c)] = True
                            queue.append((curr_r - 1, curr_c))

            # 下への移動
            if curr_r < ROWS:
                if 0 <= curr_r + 1 < ROWS + 1 and 0 <= curr_c < COLS:
                    if horiz_line_dict[(curr_r + 1, curr_c)].bgcolor != ft.Colors.BROWN_700:
                        if not visited[(curr_r + 1, curr_c)]:
                            visited[(curr_r + 1, curr_c)] = True
                            queue.append((curr_r + 1, curr_c))

            # 左への移動
            if curr_c > -1:
                if 0 <= curr_c < COLS + 1 and 0 <= curr_r < ROWS:
                    if vert_line_dict[(curr_c, curr_r)].bgcolor != ft.Colors.BROWN_700:
                        if not visited[(curr_r, curr_c - 1)]:
                            visited[(curr_r, curr_c - 1)] = True
                            queue.append((curr_r, curr_c - 1))

            # 右への移動
            if curr_c < COLS:
                if 0 <= curr_c + 1 < COLS + 1 and 0 <= curr_r < ROWS:
                    if vert_line_dict[(curr_c + 1, curr_r)].bgcolor != ft.Colors.BROWN_700:
                        if not visited[(curr_r, curr_c + 1)]:
                            visited[(curr_r, curr_c + 1)] = True
                            queue.append((curr_r, curr_c + 1))

        enclosed_count = 0
        for r in range(ROWS):
            for c in range(COLS):
                if not visited[(r, c)]:
                    enclosed_count += 1
                    inner_queue = [(r, c)]
                    visited[(r, c)] = True
                    while inner_queue:
                        curr_r, curr_c = inner_queue.pop(0)

                        if curr_r > 0 and horiz_line_dict[(curr_r, curr_c)].bgcolor != ft.Colors.BROWN_700:
                            if not visited[(curr_r - 1, curr_c)]:
                                visited[(curr_r - 1, curr_c)] = True
                                inner_queue.append((curr_r - 1, curr_c))
                        if curr_r < ROWS - 1 and horiz_line_dict[(curr_r + 1, curr_c)].bgcolor != ft.Colors.BROWN_700:
                            if not visited[(curr_r + 1, curr_c)]:
                                visited[(curr_r + 1, curr_c)] = True
                                inner_queue.append((curr_r + 1, curr_c))
                        if curr_c > 0 and vert_line_dict[(curr_c, curr_r)].bgcolor != ft.Colors.BROWN_700:
                            if not visited[(curr_r, curr_c - 1)]:
                                visited[(curr_r, curr_c - 1)] = True
                                inner_queue.append((curr_r, curr_c - 1))
                        if curr_c < COLS - 1 and vert_line_dict[(curr_c + 1, curr_r)].bgcolor != ft.Colors.BROWN_700:
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
            mode_text.value = "現在のモード: ✏️ 柵を選択中"
            mode_text.color = ft.Colors.BLACK
            line_mode_btn.style = ft.ButtonStyle(bgcolor=ft.Colors.BLACK, color=ft.Colors.WHITE,
                                                 shape=ft.RoundedRectangleBorder(radius=8))
            for item in palette_options:
                container = item.controls[1]
                container.border = None

        # 空間カウント更新
        spaces = count_enclosed_spaces()
        space_count_text.value = f"📦 柵で囲まれた空間の数: {spaces} つ"

        # パネル色の配置数を集計
        color_counts = {name: 0 for name in COLOR_MAP.values()}
        for cell in cell_list:
            if cell.bgcolor in COLOR_MAP:
                name = COLOR_MAP[cell.bgcolor]
                color_counts[name] += 1

        # カウント表示を更新（0個のものは非表示）
        panel_count_list.controls.clear()
        for name, count in color_counts.items():
            if count > 0:
                panel_count_list.controls.append(
                    ft.Text(f"🔸 {name}: {count}個", size=14, weight="bold")
                )

        line_mode_btn.update()
        mode_text.update()
        palette_row.update()
        space_count_text.update()
        stack_layout.update()
        panel_count_list.update()

    def on_palette_click(e):
        nonlocal selected_color, current_mode
        current_mode = "COLOR"
        selected_color = e.control.data
        for item in palette_options:
            container = item.controls[1]
            container.border = None
        e.control.border = ft.border.all(3, ft.Colors.BLUE_900 if selected_color == ft.Colors.AMBER_500 else ft.Colors.BLACK)
        update_mode_ui()

    def on_line_mode_click(e):
        nonlocal current_mode
        current_mode = "LINE"
        update_mode_ui()

    def on_cell_click(e):
        if current_mode == "COLOR":
            e.control.bgcolor = selected_color
            update_mode_ui()

    def toggle_line(e):
        if current_mode == "LINE":
            # e.controlは外側のヒットボックス(Container)
            # 実際の線は inner_line
            inner_line = e.control.content
            if inner_line.bgcolor == ft.Colors.BROWN_700:
                inner_line.bgcolor = ft.Colors.GREY_300
                e.control.bgcolor = ft.Colors.TRANSPARENT
            else:
                inner_line.bgcolor = ft.Colors.BROWN_700
                e.control.bgcolor = ft.Colors.BROWN_700
            update_mode_ui()

    # 各色の上に文字を表示するため、Column([Text, Container]) のリストにする
    palette_options = []
    for col in PALETTE_COLORS:
        name = COLOR_MAP[col]
        option = ft.Column(
            controls=[
                ft.Text(name, size=11, weight="bold", text_align=ft.TextAlign.CENTER),
                ft.Container(width=36, height=36, bgcolor=col, border_radius=18, data=col, on_click=on_palette_click)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2
        )
        palette_options.append(option)

    # 初期で「木」を選択状態にする
    palette_options[0].controls[1].border = ft.border.all(3, ft.Colors.BLACK)

    palette_row = ft.Row(controls=palette_options, alignment=ft.MainAxisAlignment.CENTER, spacing=12)

    line_mode_btn = ft.ElevatedButton(
        text="✏️ 柵の建設",
        on_click=on_line_mode_click,
        style=ft.ButtonStyle(bgcolor=ft.Colors.GREY_300, color=ft.Colors.BLACK,
                             shape=ft.RoundedRectangleBorder(radius=8))
    )

    top_control_row = ft.Row(controls=[palette_row, ft.VerticalDivider(width=10), line_mode_btn],
                             alignment=ft.MainAxisAlignment.CENTER)
    mode_text = ft.Text("現在のモード: 🎨 色塗り中", size=14, weight="bold", color=ft.Colors.BLUE_700)
    space_count_text = ft.Text("📦 柵で囲まれた空間の数: 0 つ", size=16, weight="bold", color=ft.Colors.GREEN_700)

    # パネル数の表示用コンテナ
    panel_count_list = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=15)

    stack_layout = ft.Stack(width=TOTAL_W, height=TOTAL_H)

    # セル配置 (3行5列)
    for r in range(ROWS):
        for c in range(COLS):
            cell = ft.Container(
                content=ft.Text(f"{r * COLS + c + 1}", color=ft.Colors.GREY_400, size=11),
                alignment=ft.alignment.center, bgcolor=ft.Colors.GREY_100,
                width=CELL_W, height=CELL_H, left=c * CELL_W, top=r * CELL_H,
                on_click=on_cell_click
            )
            stack_layout.controls.append(cell)
            cell_list.append(cell)

    # 横線配置 (二層カプセル構造)
    for r in range(ROWS + 1):
        for c in range(COLS):
            left_pos = c * CELL_W
            top_pos = r * CELL_H - (LINE_THICK / 2)
            if r == 0: top_pos = 0
            if r == ROWS: top_pos = TOTAL_H - LINE_THICK

            inner_line = ft.Container(
                width=CELL_W, height=LINE_THICK, bgcolor=ft.Colors.GREY_300
            )

            hit_box = ft.Container(
                content=inner_line,
                alignment=ft.alignment.center,
                width=CELL_W,
                height=LINE_THICK + (HIT_BOX_EXT * 2),
                bgcolor=ft.Colors.TRANSPARENT,
                alignment=ft.alignment.center,
                left=left_pos,
                top=top_pos - HIT_BOX_EXT if (0 < r < ROWS) else (top_pos if r == 0 else top_pos - (HIT_BOX_EXT * 2)),
                on_click=toggle_line
            )

            stack_layout.controls.append(hit_box)
            horiz_line_dict[(r, c)] = inner_line

    # 縦線配置 (二層カプセル構造)
    for c in range(COLS + 1):
        for r in range(ROWS):
            left_pos = c * CELL_W - (LINE_THICK / 2)
            top_pos = r * CELL_H
            if c == 0: left_pos = 0
            if c == COLS: left_pos = TOTAL_W - LINE_THICK

            inner_line = ft.Container(
                width=LINE_THICK, height=CELL_H, bgcolor=ft.Colors.GREY_300
            )

            hit_box = ft.Container(
                content=inner_line,
                alignment=ft.alignment.center,
                width=LINE_THICK + (HIT_BOX_EXT * 2),
                height=CELL_H,
                bgcolor=ft.Colors.TRANSPARENT,
                alignment=ft.alignment.center,
                left=left_pos - HIT_BOX_EXT if (0 < c < COLS) else (left_pos if c == 0 else left_pos - (HIT_BOX_EXT * 2)),
                top=top_pos,
                on_click=toggle_line
            )

            stack_layout.controls.append(hit_box)
            vert_line_dict[(c, r)] = inner_line

    page.add(
        ft.Column([
            top_control_row,
            mode_text,
            ft.Divider(height=10),
            ft.Container(content=stack_layout, border=ft.border.all(1, ft.Colors.GREY_300)),
            ft.Divider(height=10),
            space_count_text,
            panel_count_list
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8)
    )

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    ft.app(target=main, host="0.0.0.0", view=ft.AppView.WEB_BROWSER, port=port)
