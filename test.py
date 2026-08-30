import flet as ft

def main(page: ft.Page):
    page.title = "空間カウント付き 5×3 グリッド"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.Colors.WHITE

    CELL_W = 65
    CELL_H = 65
    ROWS = 3
    COLS = 5
    LINE_THICK = 4
    HIT_BOX_EXT = 14

    TOTAL_W = CELL_W * COLS
    TOTAL_H = CELL_H * ROWS

    current_mode = "COLOR"
    PALETTE_CONFIG = [
        {"label": "木", "color": ft.Colors.GREEN_400},
        {"label": "レンガ", "color": ft.Colors.BROWN_400},
        {"label": "石", "color": ft.Colors.BLACK},
        {"label": "畑", "color": ft.Colors.AMBER_500},
    ]
    selected_color = PALETTE_CONFIG[0]["color"]

    horiz_line_dict = {}
    vert_line_dict = {}
    cell_dict = {}

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
                    if horiz_line_dict[(curr_r, curr_c)].content.bgcolor != ft.Colors.BROWN_700:
                        if not visited[(curr_r - 1, curr_c)]:
                            visited[(curr_r - 1, curr_c)] = True
                            queue.append((curr_r - 1, curr_c))
            if curr_r < ROWS:
                if 0 <= curr_r + 1 < ROWS + 1 and 0 <= curr_c < COLS:
                    if horiz_line_dict[(curr_r + 1, curr_c)].content.bgcolor != ft.Colors.BROWN_700:
                        if not visited[(curr_r + 1, curr_c)]:
                            visited[(curr_r + 1, curr_c)] = True
                            queue.append((curr_r + 1, curr_c))
            if curr_c > -1:
                if 0 <= curr_c < COLS + 1 and 0 <= curr_r < ROWS:
                    if vert_line_dict[(curr_c, curr_r)].content.bgcolor != ft.Colors.BROWN_700:
                        if not visited[(curr_r, curr_c - 1)]:
                            visited[(curr_r, curr_c - 1)] = True
                            queue.append((curr_r, curr_c - 1))
            if curr_c < COLS:
                if 0 <= curr_c + 1 < COLS + 1 and 0 <= curr_r < ROWS:
                    if vert_line_dict[(curr_c + 1, curr_r)].content.bgcolor != ft.Colors.BROWN_700:
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
                        if curr_r > 0 and horiz_line_dict[(curr_r, curr_c)].content.bgcolor != ft.Colors.BROWN_700:
                            if not visited[(curr_r - 1, curr_c)]:
                                visited[(curr_r - 1, curr_c)] = True
                                inner_queue.append((curr_r - 1, curr_c))
                        if curr_r < ROWS - 1 and horiz_line_dict[(curr_r + 1, curr_c)].content.bgcolor != ft.Colors.BROWN_700:
                            if not visited[(curr_r + 1, curr_c)]:
                                visited[(curr_r + 1, curr_c)] = True
                                inner_queue.append((curr_r + 1, curr_c))
                        if curr_c > 0 and vert_line_dict[(curr_c, curr_r)].content.bgcolor != ft.Colors.BROWN_700:
                            if not visited[(curr_r, curr_c - 1)]:
                                visited[(curr_r, curr_c - 1)] = True
                                inner_queue.append((curr_r, curr_c - 1))
                        if curr_c < COLS - 1 and vert_line_dict[(curr_c + 1, curr_r)].content.bgcolor != ft.Colors.BROWN_700:
                            if not visited[(curr_r, curr_c + 1)]:
                                visited[(curr_r, curr_c + 1)] = True
                                inner_queue.append((curr_r, curr_c + 1))
        return enclosed_count

    def update_mode_ui():
        if current_mode == "COLOR":
            mode_text.value = "現在のモード: 🎨 色塗り中"
            mode_text.color = ft.Colors.BLUE_700
            line_mode_btn.style = ft.ButtonStyle(bgcolor=ft.Colors.GREY_300, color=ft.Colors.BLACK, shape=ft.RoundedRectangleBorder(radius=8))
        else:
            mode_text.value = "現在のモード: ✏️ 柵を選択中"
            mode_text.color = ft.Colors.BLACK
            line_mode_btn.style = ft.ButtonStyle(bgcolor=ft.Colors.BLACK, color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=8))
            for item_col in palette_row.controls:
                item_col.controls[1].border = None

        spaces = count_enclosed_spaces()
        space_count_text.value = f"📦 柵で囲まれた空間の数: {spaces} つ"

        counts = {"木": 0, "レンガ": 0, "石": 0, "畑": 0}
        for cell in cell_dict.values():
            bg = cell.bgcolor
            for p in PALETTE_CONFIG:
                if p["color"] == bg:
                    counts[p["label"]] += 1
        
        count_items = []
        for label, cnt in counts.items():
            if cnt > 0:
                count_items.append(ft.Text(f"🔸 {label}: {cnt}個", size=14, weight="bold"))
        
        panel_count_row.controls = count_items

        line_mode_btn.update()
        mode_text.update()
        palette_row.update()
        space_count_text.update()
        panel_count_row.update()
        stack_layout.update()

    def on_palette_click(e):
        nonlocal selected_color, current_mode
        current_mode = "COLOR"
        selected_color = e.control.data
        for item_col in palette_row.controls:
            item_col.controls[1].border = None
        e.control.border = ft.border.all(3, ft.Colors.BLACK)
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
            inner_line = e.control.content
            if inner_line.bgcolor == ft.Colors.BROWN_700:
                inner_line.bgcolor = ft.Colors.GREY_300
            else:
                inner_line.bgcolor = ft.Colors.BROWN_700
            update_mode_ui()

    palette_options = []
    for p in PALETTE_CONFIG:
        container_circle = ft.Container(width=40, height=40, bgcolor=p["color"], border_radius=20, data=p["color"], on_click=on_palette_click)
        item_col = ft.Column([
            ft.Text(p["label"], size=12, weight="bold"),
            container_circle
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2)
        palette_options.append(item_col)
    
    palette_options[0].controls[1].border = ft.border.all(3, ft.Colors.BLACK)
    palette_row = ft.Row(controls=palette_options, alignment=ft.MainAxisAlignment.CENTER, spacing=15)

    line_mode_btn = ft.ElevatedButton(
        text="✏️ 柵の建設",
        on_click=on_line_mode_click,
        style=ft.ButtonStyle(bgcolor=ft.Colors.GREY_300, color=ft.Colors.BLACK, shape=ft.RoundedRectangleBorder(radius=8))
    )

    top_control_row = ft.Row(controls=[palette_row, ft.VerticalDivider(width=20), line_mode_btn], alignment=ft.MainAxisAlignment.CENTER)
    mode_text = ft.Text("現在のモード: 🎨 色塗り中", size=16, weight="bold", color=ft.Colors.BLUE_700)
    space_count_text = ft.Text("📦 柵で囲まれた空間の数: 0 つ", size=18, weight="bold", color=ft.Colors.GREEN_700)
    panel_count_row = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=15)

    stack_layout = ft.Stack(width=TOTAL_W, height=TOTAL_H)

    for r in range(ROWS):
        for c in range(COLS):
            cell = ft.Container(
                content=ft.Text(f"{r * COLS + c + 1}", color=ft.Colors.GREY_400, size=12),
                alignment=ft.alignment.center, bgcolor=ft.Colors.GREY_100,
                width=CELL_W, height=CELL_H, left=c * CELL_W, top=r * CELL_H,
                on_click=on_cell_click
            )
            stack_layout.controls.append(cell)
            cell_dict[(r, c)] = cell

    for r in range(ROWS + 1):
        for c in range(COLS):
            left_pos = c * CELL_W
            top_pos = r * CELL_H - (LINE_THICK / 2) - HIT_BOX_EXT
            if r == 0: top_pos = -HIT_BOX_EXT
            if r == ROWS: top_pos = TOTAL_H - (LINE_THICK / 2) - HIT_BOX_EXT

            inner_line = ft.Container(width=CELL_W, height=LINE_THICK, bgcolor=ft.Colors.GREY_300)
            horiz_line = ft.Container(
                content=inner_line,
                width=CELL_W, height=LINE_THICK + HIT_BOX_EXT * 2,
                bgcolor=ft.Colors.TRANSPARENT,
                alignment=ft.alignment.center,
                left=left_pos, top=top_pos, on_click=toggle_line
            )
            stack_layout.controls.append(horiz_line)
            horiz_line_dict[(r, c)] = horiz_line

    for c in range(COLS + 1):
        for r in range(ROWS):
            left_pos = c * CELL_W - (LINE_THICK / 2) - HIT_BOX_EXT
            top_pos = r * CELL_H
            if c == 0: left_pos = -HIT_BOX_EXT
            if c == COLS: left_pos = TOTAL_W - (LINE_THICK / 2) - HIT_BOX_EXT

            inner_line = ft.Container(width=LINE_THICK, height=CELL_H, bgcolor=ft.Colors.GREY_300)
            vert_line = ft.Container(
                content=inner_line,
                width=LINE_THICK + HIT_BOX_EXT * 2, height=CELL_H,
                bgcolor=ft.Colors.TRANSPARENT,
                alignment=ft.alignment.center,
                left=left_pos, top=top_pos, on_click=toggle_line
            )
            stack_layout.controls.append(vert_line)
            vert_line_dict[(c, r)] = vert_line

    page.add(
        ft.Column([
            top_control_row,
            mode_text,
            ft.Divider(),
            ft.Container(content=stack_layout, border=ft.border.all(1, ft.Colors.GREY_300)),
            ft.Divider(),
            space_count_text,
            panel_count_row
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    ft.app(target=main, host="0.0.0.0", view=ft.AppView.WEB_BROWSER, port=port)
