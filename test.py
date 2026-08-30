import flet as ft

def main(page: ft.Page):
    page.title = "空間カウント付き 5×3 グリッド"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # スマホ画面に収まるようサイズを調整
    CELL_W = 65
    CELL_H = 65
    ROWS = 3   # 5×3（横5マス、縦3マス）
    COLS = 5
    LINE_THICK = 6
    HIT_BOX_EXT = 14  # タッチ反応範囲を広げるためのマージン

    TOTAL_W = CELL_W * COLS
    TOTAL_H = CELL_H * ROWS

    current_mode = "COLOR"
    selected_color = ft.Colors.BLUE_400
    PALETTE_COLORS = [ft.Colors.BLUE_400, ft.Colors.GREEN_400, ft.Colors.ORANGE_400, ft.Colors.RED_400]

    horiz_line_dict = {}
    vert_line_dict = {}

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

            if curr_r > -1:
                if 0 <= curr_r < ROWS + 1 and 0 <= curr_c < COLS:
                    if horiz_line_dict[(curr_r, curr_c)].data.bgcolor != ft.Colors.BLACK:
                        if not visited[(curr_r - 1, curr_c)]:
                            visited[(curr_r - 1, curr_c)] = True
                            queue.append((curr_r - 1, curr_c))

            if curr_r < ROWS:
                if 0 <= curr_r + 1 < ROWS + 1 and 0 <= curr_c < COLS:
                    if horiz_line_dict[(curr_r + 1, curr_c)].data.bgcolor != ft.Colors.BLACK:
                        if not visited[(curr_r + 1, curr_c)]:
                            visited[(curr_r + 1, curr_c)] = True
                            queue.append((curr_r + 1, curr_c))

            if curr_c > -1:
                if 0 <= curr_c < COLS + 1 and 0 <= curr_r < ROWS:
                    if vert_line_dict[(curr_c, curr_r)].data.bgcolor != ft.Colors.BLACK:
                        if not visited[(curr_r, curr_c - 1)]:
                            visited[(curr_r, curr_c - 1)] = True
                            queue.append((curr_r, curr_c - 1))

            if curr_c < COLS:
                if 0 <= curr_c + 1 < COLS + 1 and 0 <= curr_r < ROWS:
                    if vert_line_dict[(curr_c + 1, curr_r)].data.bgcolor != ft.Colors.BLACK:
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

                        if curr_r > 0 and horiz_line_dict[(curr_r, curr_c)].data.bgcolor != ft.Colors.BLACK:
                            if not visited[(curr_r - 1, curr_c)]:
                                visited[(curr_r - 1, curr_c)] = True
                                inner_queue.append((curr_r - 1, curr_c))
                        if curr_r < ROWS - 1 and horiz_line_dict[(curr_r + 1, curr_c)].data.bgcolor != ft.Colors.BLACK:
                            if not visited[(curr_r + 1, curr_c)]:
                                visited[(curr_r + 1, curr_c)] = True
                                inner_queue.append((curr_r + 1, curr_c))
                        if curr_c > 0 and vert_line_dict[(curr_c, curr_r)].data.bgcolor != ft.Colors.BLACK:
                            if not visited[(curr_r, curr_c - 1)]:
                                visited[(curr_r, curr_c - 1)] = True
                                inner_queue.append((curr_r, curr_c - 1))
                        if curr_c < COLS - 1 and vert_line_dict[(curr_c + 1, curr_r)].data.bgcolor != ft.Colors.BLACK:
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
        space_count_text.value = f"📦 黒線で囲まれた空間の数: {spaces} つ"

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
        e.control.border = ft.border.all(3, ft.Colors.BLACK)
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
            # e.control は透明な透明ヒットボックス(Container)
            # data プロパティに実際の目視できる線コントロールを持たせて連動
            target_line = e.control.data
            if target_line.bgcolor == ft.Colors.BLACK:
                target_line.bgcolor = ft.Colors.GREY_300
            else:
                target_line.bgcolor = ft.Colors.BLACK
            update_mode_ui()

    palette_options = [
        ft.Container(width=35, height=35, bgcolor=col, border_radius=18, data=col, on_click=on_palette_click) for col in
        PALETTE_COLORS]

    palette_options[0].border = ft.border.all(3, ft.Colors.BLACK)
    palette_row = ft.Row(controls=palette_options, alignment=ft.MainAxisAlignment.CENTER, spacing=10)

    line_mode_btn = ft.ElevatedButton(
        text="✏️ 黒線を選択する",
        on_click=on_line_mode_click,
        style=ft.ButtonStyle(bgcolor=ft.Colors.GREY_300, color=ft.Colors.BLACK,
                             shape=ft.RoundedRectangleBorder(radius=8))
    )

    top_control_row = ft.Row(controls=[palette_row, ft.VerticalDivider(width=10), line_mode_btn],
                             alignment=ft.MainAxisAlignment.CENTER)
    mode_text = ft.Text("現在のモード: 🎨 色塗り中", size=14, weight="bold", color=ft.Colors.BLUE_700)
    space_count_text = ft.Text("📦 黒線で囲まれた空間の数: 0 つ", size=16, weight="bold", color=ft.Colors.GREEN_700)

    stack_layout = ft.Stack(width=TOTAL_W, height=TOTAL_H)

    for r in range(ROWS):
        for c in range(COLS):
            cell = ft.Container(
                content=ft.Text(f"{r * COLS + c + 1}", color=ft.Colors.GREY_400, size=11),
                alignment=ft.alignment.center, bgcolor=ft.Colors.GREY_100,
                width=CELL_W, height=CELL_H, left=c * CELL_W, top=r * CELL_H,
                on_click=on_cell_click
            )
            stack_layout.controls.append(cell)

    # 横線の配置 (見かけの線と、タッチ範囲を広げた透明なコンテナの二層構造)
    for r in range(ROWS + 1):
        for c in range(COLS):
            left_pos = c * CELL_W
            top_pos = r * CELL_H - (LINE_THICK / 2)
            if r == 0: top_pos = 0
            if r == ROWS: top_pos = TOTAL_H - LINE_THICK

            # 1. 実際に見える細い線
            horiz_line = ft.Container(
                width=CELL_W, height=LINE_THICK, bgcolor=ft.Colors.GREY_300,
                left=left_pos, top=top_pos
            )
            
            # 2. タッチの反応範囲を広くした透明なレイヤー (上に被せる)
            hit_box = ft.Container(
                width=CELL_W,
                height=LINE_THICK + (HIT_BOX_EXT * 2),
                bgcolor=ft.Colors.TRANSPARENT,
                left=left_pos,
                top=top_pos - HIT_BOX_EXT,
                on_click=toggle_line,
                data=horiz_line  # 見かけの線オブジェクトをデータとして紐付け
            )
            
            stack_layout.controls.append(horiz_line)
            stack_layout.controls.append(hit_box)
            horiz_line_dict[(r, c)] = hit_box

    # 縦線の配置
    for c in range(COLS + 1):
        for r in range(ROWS):
            left_pos = c * CELL_W - (LINE_THICK / 2)
            top_pos = r * CELL_H
            if c == 0: left_pos = 0
            if c == COLS: left_pos = TOTAL_W - LINE_THICK

            # 1. 実際に見える細い線
            vert_line = ft.Container(
                width=LINE_THICK, height=CELL_H, bgcolor=ft.Colors.GREY_300,
                left=left_pos, top=top_pos
            )
            
            # 2. タッチの反応範囲を広くした透明なレイヤー (上に被せる)
            hit_box = ft.Container(
                width=LINE_THICK + (HIT_BOX_EXT * 2),
                height=CELL_H,
                bgcolor=ft.Colors.TRANSPARENT,
                left=left_pos - HIT_BOX_EXT,
                top=top_pos,
                on_click=toggle_line,
                data=vert_line  # 見かけの線オブジェクトをデータとして紐付け
            )
            
            stack_layout.controls.append(vert_line)
            stack_layout.controls.append(hit_box)
            vert_line_dict[(c, r)] = hit_box

    page.add(
        ft.Column([
            top_control_row,
            mode_text,
            ft.Divider(),
            ft.Container(content=stack_layout, border=ft.border.all(1, ft.Colors.GREY_300), padding=0),
            ft.Divider(),
            space_count_text
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
    )

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    ft.app(target=main, host="0.0.0.0", view=ft.AppView.WEB_BROWSER, port=port)
