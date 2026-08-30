import os
import flet as ft

def main(page: ft.Page):
    page.title = "農場グリッド管理"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.Colors.WHITE

    ROWS = 3
    COLS = 5
    CELL_W = 65
    CELL_H = 65
    LINE_THICK = 3
    HIT_BOX_EXT = 14  # タッチ反応の範囲を広げる余白
    TOTAL_W = CELL_W * COLS
    TOTAL_H = CELL_H * ROWS

    # パレットの設定
    PALETTE_INFO = [
        {"label": "木", "color": ft.Colors.GREEN_400, "data": "WOOD"},
        {"label": "レンガ", "color": ft.Colors.ORANGE_800, "data": "BRICK"},
        {"label": "石", "color": ft.Colors.GREY_800, "data": "STONE"},
        {"label": "畑", "color": ft.Colors.AMBER_400, "data": "FIELD"},
    ]

    current_mode = "COLOR"  # "COLOR" または "LINE"
    selected_color_data = "WOOD"
    selected_color = ft.Colors.GREEN_400

    horiz_line_dict = {}
    vert_line_dict = {}
    cell_dict = {}

    # --- 完全に囲まれた空間だけを数えるアルゴリズム ---
    def count_enclosed_spaces():
        visited = {(r, c): False for r in range(-1, ROWS + 1) for c in range(-1, COLS + 1)}
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
        # モード表記の更新
        if current_mode == "COLOR":
            active_label = ""
            for item in PALETTE_INFO:
                if item["data"] == selected_color_data:
                    active_label = item["label"]
            mode_text.value = f"現在のモード: 🎨 パネル配置中 ({active_label})"
            mode_text.color = ft.Colors.BLUE_700
            line_mode_btn.style = ft.ButtonStyle(bgcolor=ft.Colors.GREY_300, color=ft.Colors.BLACK,
                                                 shape=ft.RoundedRectangleBorder(radius=8))
        else:
            mode_text.value = "現在のモード: ✏️ 柵を選択中"
            mode_text.color = ft.Colors.BLACK
            line_mode_btn.style = ft.ButtonStyle(bgcolor=ft.Colors.BROWN_700, color=ft.Colors.WHITE,
                                                 shape=ft.RoundedRectangleBorder(radius=8))
            for c in palette_row.controls:
                c.content.controls[1].border = None

        # 柵空間の集計
        spaces = count_enclosed_spaces()
        space_count_text.value = f"📦 柵で囲まれた空間の数: {spaces} つ"

        # パネル枚数の集計
        counts = {"WOOD": 0, "BRICK": 0, "STONE": 0, "FIELD": 0}
        for cell in cell_dict.values():
            if cell.data in counts:
                counts[cell.data] += 1

        stats_controls = []
        label_map = {"WOOD": "木", "BRICK": "レンガ", "STONE": "石", "FIELD": "畑"}
        for key, cnt in counts.items():
            if cnt > 0:
                stats_controls.append(ft.Text(f"🔸 {label_map[key]}: {cnt}個", size=14, weight="bold", color=ft.Colors.GREY_800))
        stats_row.controls = stats_controls

        line_mode_btn.update()
        mode_text.update()
        palette_row.update()
        space_count_text.update()
        stats_row.update()
        stack_layout.update()

    def on_palette_click(e):
        nonlocal selected_color, selected_color_data, current_mode
        current_mode = "COLOR"
        selected_color_data = e.control.data["data"]
        selected_color = e.control.data["color"]
        for c in palette_row.controls:
            c.content.controls[1].border = None
        e.control.border = ft.border.all(3, ft.Colors.BLACK)
        update_mode_ui()

    def on_line_mode_click(e):
        nonlocal current_mode
        current_mode = "LINE"
        update_mode_ui()

    def on_cell_click(e):
        if current_mode == "COLOR":
            # すでに同じ色が塗られている場合は元のグレーに戻す（トグル機能）
            if e.control.bgcolor == selected_color:
                e.control.bgcolor = ft.Colors.GREY_100
                e.control.data = "EMPTY"
            else:
                e.control.bgcolor = selected_color
                e.control.data = selected_color_data
            update_mode_ui()

    def toggle_line(e):
        if current_mode == "LINE":
            # e.controlは外側の透明なhit_boxなので、content（実際のinner_line）の色を変える
            inner_line = e.control.content
            if inner_line.bgcolor == ft.Colors.BROWN_700:
                inner_line.bgcolor = ft.Colors.GREY_300
            else:
                inner_line.bgcolor = ft.Colors.BROWN_700
            update_mode_ui()

    # パレットUI（上に文字表示）
    palette_options = []
    for item in PALETTE_INFO:
        btn = ft.Container(
            width=40, height=40, bgcolor=item["color"], border_radius=20,
            data=item, on_click=on_palette_click
        )
        if item["data"] == "WOOD":
            btn.border = ft.border.all(3, ft.Colors.BLACK)
            
        palette_options.append(
            ft.Container(
                content=ft.Column([
                    ft.Text(item["label"], size=12, weight="bold", color=ft.Colors.GREY_700),
                    btn
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                alignment=ft.alignment.center
            )
        )

    palette_row = ft.Row(controls=palette_options, alignment=ft.MainAxisAlignment.CENTER, spacing=15)

    line_mode_btn = ft.ElevatedButton(
        text="✏️ 柵の建設",
        on_click=on_line_mode_click,
        style=ft.ButtonStyle(bgcolor=ft.Colors.GREY_300, color=ft.Colors.BLACK,
                             shape=ft.RoundedRectangleBorder(radius=8))
    )

    top_control_row = ft.Row(controls=[palette_row, ft.VerticalDivider(width=20), line_mode_btn],
                             alignment=ft.MainAxisAlignment.CENTER)
    mode_text = ft.Text("現在のモード: 🎨 パネル配置中 (木)", size=16, weight="bold", color=ft.Colors.BLUE_700)
    space_count_text = ft.Text("📦 柵で囲まれた空間の数: 0 つ", size=18, weight="bold", color=ft.Colors.GREEN_700)
    stats_row = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=15)

    stack_layout = ft.Stack(width=TOTAL_W, height=TOTAL_H)

    # マスの生成
    for r in range(ROWS):
        for c in range(COLS):
            cell = ft.Container(
                content=ft.Text(f"{r * COLS + c + 1}", color=ft.Colors.GREY_400, size=12),
                alignment=ft.alignment.center, bgcolor=ft.Colors.GREY_100,
                width=CELL_W, height=CELL_H, left=c * CELL_W, top=r * CELL_H,
                on_click=on_cell_click,
                data="EMPTY"
            )
            stack_layout.controls.append(cell)
            cell_dict[(r, c)] = cell

    # 横方向の境界線（水平線）
    for r in range(ROWS + 1):
        for c in range(COLS):
            left_pos = c * CELL_W
            top_pos = r * CELL_H - HIT_BOX_EXT

            inner_line = ft.Container(
                width=CELL_W, height=LINE_THICK, bgcolor=ft.Colors.GREY_300
            )
            horiz_line_dict[(r, c)] = inner_line

            hit_box = ft.Container(
                content=inner_line,
                width=CELL_W, height=LINE_THICK + (HIT_BOX_EXT * 2),
                bgcolor=ft.Colors.TRANSPARENT,
                left=left_pos, top=top_pos,
                alignment=ft.alignment.center,
                on_click=toggle_line
            )
            stack_layout.controls.append(hit_box)

    # 縦方向の境界線（垂直線）
    for c in range(COLS + 1):
        for r in range(ROWS):
            left_pos = c * CELL_W - HIT_BOX_EXT
            top_pos = r * CELL_H

            inner_line = ft.Container(
                width=LINE_THICK, height=CELL_H, bgcolor=ft.Colors.GREY_300
            )
            vert_line_dict[(c, r)] = inner_line

            hit_box = ft.Container(
                content=inner_line,
                width=LINE_THICK + (HIT_BOX_EXT * 2), height=CELL_H,
                bgcolor=ft.Colors.TRANSPARENT,
                left=left_pos, top=top_pos,
                alignment=ft.alignment.center,
                on_click=toggle_line
            )
            stack_layout.controls.append(hit_box)

    page.add(
        ft.Column([
            top_control_row,
            mode_text,
            ft.Divider(),
            ft.Container(content=stack_layout, border=ft.border.all(1, ft.Colors.GREY_300)),
            ft.Divider(),
            space_count_text,
            stats_row
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    ft.app(target=main, host="0.0.0.0", view=ft.AppView.WEB_BROWSER, port=port)
