import flet as ft


def main(page: ft.Page):
    page.title = "牧場・資源管理グリッド"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # ページ全体を上下スクロール可能にする設定
    page.scroll = ft.ScrollMode.AUTO

    # スマホ向けにサイズを少しコンパクトに調整
    CELL_W = 65
    CELL_H = 65
    ROWS = 3
    COLS = 5
    LINE_THICK = 4
    HIT_BOX_EXT = 14  # タッチ反応範囲を広げるための余白

    # 最端の線が親要素（Stack）からはみ出してタップできなくなるのを防ぐ余白
    OFFSET = HIT_BOX_EXT

    TOTAL_W = CELL_W * COLS + (OFFSET * 2)
    TOTAL_H = CELL_H * ROWS + (OFFSET * 2)

    current_mode = "COLOR"
    
    # パレット情報を定義
    PALETTE_INFO = [
        {"name": "木の家", "color": ft.Colors.GREEN_400},
        {"name": "レンガの家", "color": ft.Colors.DEEP_ORANGE_700},
        {"name": "石の家", "color": ft.Colors.GREY_900},
        {"name": "畑", "color": ft.Colors.AMBER_500},
        {"name": "厩", "color": ft.Colors.LIGHT_BLUE_300},
    ]
    
    # 初期選択色を正しく取得
    selected_color = PALETTE_INFO[0]["color"]

    horiz_line_dict = {}
    vert_line_dict = {}
    cell_dict = {}

    # 2つ目の表の入力数値を管理する辞書（初期値はすべて0）
    agri_inputs = {"小麦": 0, "野菜": 0, "羊": 0, "猪": 0, "牛": 0, "家族の数": 2}

    # 3つ目の表（カードボーナス）の入力数値を管理する辞書（初期値はすべて0）
    card_inputs = {"職業": 0, "小さい進歩": 0, "大きい進歩": 0}

    # --- 牧場（閉空間）と未使用パネル、および柵に囲まれた厩を数えるアルゴリズム ---
    def analyze_grid():
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

        # 柵の外側（未使用）マスのうち、未着色の数をカウント
        unused_count = 0
        for r in range(ROWS):
            for c in range(COLS):
                if visited[(r, c)] and cell_dict[(r, c)].bgcolor == ft.Colors.GREY_100:
                    unused_count += 1

        # 内側に孤立した完全な閉鎖空間（牧場）と、その中の厩の空間数をカウント
        ranch_count = 0
        ranch_with_stable_count = 0

        for r in range(ROWS):
            for c in range(COLS):
                if not visited[(r, c)]:
                    ranch_count += 1
                    inner_queue = [(r, c)]
                    visited[(r, c)] = True
                    
                    has_stable = False

                    while inner_queue:
                        curr_r, curr_c = inner_queue.pop(0)

                        if cell_dict[(curr_r, curr_c)].bgcolor == ft.Colors.LIGHT_BLUE_300:
                            has_stable = True

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
                    
                    if has_stable:
                        ranch_with_stable_count += 1

        return ranch_count, unused_count, ranch_with_stable_count

    # 2つ目の表の現在の小計点を計算して返す関数
    def get_agri_subtotal():
        sub_total = 0
        for name, count in agri_inputs.items():
            score = -1
            if name == "小麦":
                if count==0: score = -1
                elif 1 <= count <= 3: score = 1
                elif 4 <= count <= 5: score = 2
                elif 6 <= count <= 7: score = 3
                elif count >= 8: score = 4
            elif name == "野菜":
                if count==0: score = -1
                elif count==1: score = 1
                elif count==2: score = 2
                elif count==3: score = 3  
                elif count >= 4: score = 4
            elif name == "羊":
                if count==0: score = -1
                elif 1 <= count <= 3: score = 1
                elif 4 <= count <= 5: score = 2
                elif 6 <= count <= 7: score = 3
                elif count >= 8: score = 4
            elif name == "猪":
                if count==0: score = -1
                elif 1 <= count <= 2: score = 1
                elif 3 <= count <= 4: score = 2
                elif 5 <= count <= 6: score = 3
                elif count >= 7: score = 4
            elif name == "牛":
                if count==0: score = -1
                elif count == 1: score = 1
                elif 2 <= count <= 3: score = 2
                elif 4 <= count <= 5: score = 3
                elif count >= 6: score = 4
            elif name == "家族の数":
                score = count * 3
            sub_total += score
        return sub_total

    # 集計情報を表形式（DataTable）で更新する関数
    def update_data_table(ranch_count, unused_count, ranch_stable_count):
        counts = {"木の家": 0, "レンガの家": 0, "石の家": 0, "畑": 0}
        
        for cell in cell_dict.values():
            for info in PALETTE_INFO:
                if info["name"] in counts and cell.bgcolor == info["color"]:
                    counts[info["name"]] += 1

        rows = []
        total_score = 0  # 総合点の計算
        
        # 1. 畑
        field_count = counts["畑"]
        field_color = ft.Colors.AMBER_700
        if field_count == 0: field_score = -1
        elif field_count == 1: field_score = -1
        elif field_count == 2: field_score = 1
        elif field_count == 3: field_score = 2
        elif field_count == 4: field_score = 3
        elif field_count >= 5: field_score = 4

        total_score += field_score
        rows.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("畑", size=16, weight="bold", color=field_color)),
                ft.DataCell(ft.Text(f"{field_count} 個", size=16, weight="bold", color=field_color)),
                ft.DataCell(ft.Text(f"{field_score} 点", size=16, weight="bold", color=field_color)),
            ])
        )

        # 2. 牧場
        ranch_color = ft.Colors.BROWN_700
        if ranch_count == 0:
            ranch_score = -1
        elif ranch_count <= 4:
            ranch_score = ranch_count * 1
        else:
            ranch_score = 4

        total_score += ranch_score
        rows.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("牧場", size=16, weight="bold", color=ranch_color)),
                ft.DataCell(ft.Text(f"{ranch_count} つ", size=16, weight="bold", color=ranch_color)),
                ft.DataCell(ft.Text(f"{ranch_score} 点", size=16, weight="bold", color=ranch_color)),
            ])
        )
            
        # 3. 厩
        limited_ranch_stable_count = min(ranch_stable_count, 4)
        if ranch_stable_count > 0:
            score = limited_ranch_stable_count * 1
            total_score += score
            display_count = f"{ranch_stable_count} つ"
            if ranch_stable_count > 4: display_count = f"{ranch_stable_count} つ (上限4)"

            rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("厩", size=16, weight="bold", color=ft.Colors.LIGHT_BLUE_700)),
                    ft.DataCell(ft.Text(display_count, size=16, weight="bold", color=ft.Colors.LIGHT_BLUE_700)),
                    ft.DataCell(ft.Text(f"{score} 点", size=16, weight="bold", color=ft.Colors.LIGHT_BLUE_700)),
                ])
            )
        
        # 4. 家の追加
        for info in PALETTE_INFO:
            name = info["name"]
            if name not in counts or name == "畑": continue
            count = counts[name]
            text_color = info["color"]
            if text_color == ft.Colors.GREEN_400: text_color = ft.Colors.GREEN_700

            if count > 0:
                score = 0
                if name == "木の家": score = count * 0
                elif name == "レンガの家": score = count * 1
                elif name == "石の家": score = count * 2

                total_score += score
                rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(name, size=16, weight="bold", color=text_color)),
                        ft.DataCell(ft.Text(f"{count} 個", size=16, weight="bold", color=text_color)),
                        ft.DataCell(ft.Text(f"{score} 点", size=16, weight="bold", color=text_color)),
                    ])
                )
        
        # 5. 未使用マス
        if unused_count > 0:
            score = unused_count * -1
            total_score += score
            rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("未使用", size=16, color=ft.Colors.BLUE_GREY_600, weight="bold")),
                    ft.DataCell(ft.Text(f"{unused_count} マス", size=16, color=ft.Colors.BLUE_GREY_600, weight="bold")),
                    ft.DataCell(ft.Text(f"{score} 点", size=16, color=ft.Colors.BLUE_GREY_600, weight="bold")),
                ])
            )

        # 6. 最下部にこの表だけの合計得点行を表示
        rows.append(
            ft.DataRow(
                color=ft.Colors.GREY_100,
                cells=[
                    ft.DataCell(ft.Text("合計点", size=18, weight="bold", color=ft.Colors.BLACK)),
                    ft.DataCell(ft.Text("", size=16)),
                    ft.DataCell(ft.Text(f"{total_score} 点", size=18, weight="bold", color=ft.Colors.RED_700 if total_score < 0 else ft.Colors.GREEN_700)),
                ]
            )
        )
        count_table.rows = rows

    # 2つ目の表（農作物・家畜）を計算・更新する関数
    def update_data_table2():
        rows = []
        sub_total = 0

        for name, count in agri_inputs.items():
            score = -1
            text_color = ft.Colors.BLACK

            # ーーー 🌾 各農畜産物のカラーをご指定通りに変更 ーーー
            if name == "小麦":
                text_color = ft.Colors.AMBER_700       # ⭕ 黄色系（濃い黄金色）
            elif name == "野菜":
                text_color = ft.Colors.DEEP_ORANGE_700 # ⭕ オレンジ（レンガの家と同系）
            elif name == "羊":
                text_color = ft.Colors.BLUE_GREY_500   # ⭕ 今のまま（ブルーグレー）
            elif name == "猪":
                text_color = ft.Colors.BLACK           # ⭕ 黒
            elif name == "牛":
                text_color = ft.Colors.BROWN_900       # ⭕ 濃い茶色
            elif name == "家族の数":
                text_color = ft.Colors.BLUE_700
         
            if name == "小麦":
                if count==0: score = -1
                elif 1 <= count <= 3: score = 1
                elif 4 <= count <= 5: score = 2
                elif 6 <= count <= 7: score = 3
                elif count >= 8: score = 4
            elif name == "野菜":
                if count==0: score = -1
                elif count==1: score = 1
                elif count==2: score = 2
                elif count==3: score = 3  
                elif count >= 4: score = 4
            elif name == "羊":
                if count==0: score = -1
                elif 1 <= count <= 3: score = 1
                elif 4 <= count <= 5: score = 2
                elif 6 <= count <= 7: score = 3
                elif count >= 8: score = 4
            elif name == "猪":
                if count==0: score = -1
                elif 1 <= count <= 2: score = 1
                elif 3 <= count <= 4: score = 2
                elif 5 <= count <= 6: score = 3
                elif count >= 7: score = 4
            elif name == "牛":
                if count==0: score = -1
                elif count == 1: score = 1
                elif 2 <= count <= 3: score = 2
                elif 4 <= count <= 5: score = 3
                elif count >= 6: score = 4
            elif name == "家族の数":
               score = count*3

            sub_total += score

            def make_on_change(k=name):
                return lambda e: on_input_change(k, e.control.value)

            input_field = ft.TextField(
                value=str(count),
                width=60,
                height=35,
                text_size=14,
                content_padding=5,
                text_align=ft.TextAlign.CENTER,
                keyboard_type=ft.KeyboardType.NUMBER,
                on_change=make_on_change()
            )

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(name, size=16, weight="bold", color=text_color)),
                        ft.DataCell(input_field),
                        ft.DataCell(ft.Text(f"{score} 点", size=16, weight="bold", color=text_color)),
                    ]
                )
            )

        rows.append(
            ft.DataRow(
                color=ft.Colors.GREY_100,  # 👈 1つ目の表と色を統一（薄いグレー）
                cells=[
                    ft.DataCell(ft.Text("合計点", size=18, weight="bold", color=ft.Colors.BLACK)),  # 👈 「合計点」に変更
                    ft.DataCell(ft.Text("", size=16)),
                    ft.DataCell(ft.Text(f"{sub_total} 点", size=18, weight="bold", color=ft.Colors.RED_700 if sub_total < 0 else ft.Colors.GREEN_700)), # 👈 サイズを18に拡大し、プラスマイナスで色分け
                ]
            )
        )
        count_table2.rows = rows

# 👇 【修正後】update_data_table3関数を丸ごと以下に置き換えます

    # 3つ目の表（カードボーナス）を計算・更新する関数
    def update_data_table3():
        rows = []
        sub_total = 0  # 3つ目の表だけの合計点

        for name, score in card_inputs.items():
            if name == "職業":
                text_color = ft.Colors.AMBER_100
            elif name == "小さい進歩":
                text_color = ft.Colors.AMBER_500
            elif name == "大きい進歩":
                text_color = ft.Colors.RED_900

            sub_total += score

            # 入力値を変更した時の共通処理
            def make_on_change(k=name):
                return lambda e: on_card_input_change(k, e.control.value)

            # 2列目用の入力フィールド
            input_field = ft.TextField(
                value=str(score),
                width=60,
                height=35,
                text_size=14,
                content_padding=5,
                text_align=ft.TextAlign.CENTER,
                keyboard_type=ft.KeyboardType.NUMBER,
                on_change=make_on_change()
            )

            # 3列目のプラス・マイナス調整ボタン（タップで1点ずつ増減）
            def make_adjust_click(k=name, val=1):
                return lambda e: on_card_adjust_click(k, val)

            btn_minus = ft.IconButton(
                icon=ft.Icons.REMOVE,
                icon_size=16,
                width=30,
                height=30,
                on_click=make_adjust_click(val=-1)
            )
            btn_plus = ft.IconButton(
                icon=ft.Icons.ADD,
                icon_size=16,
                width=30,
                height=30,
                on_click=make_adjust_click(val=1)
            )
            
            # プラス・マイナスを横並びにしたボタンセット
            action_buttons = ft.Row(
                controls=[btn_minus, btn_plus],
                spacing=2,
                alignment=ft.MainAxisAlignment.CENTER
            )

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(name, size=16, weight="bold", color=text_color)),
                        ft.DataCell(input_field),    # ⭕ 2列目：得点の直接入力
                        ft.DataCell(action_buttons),  # ⭕ 3列目：個別調整用プラスマイナスボタン
                    ]
                )
            )

        # 3つ目の表の最下部（合計点行。2列目の真下に合計を出力します）
        rows.append(
            ft.DataRow(
                color=ft.Colors.GREY_100,
                cells=[
                    ft.DataCell(ft.Text("合計点", size=18, weight="bold", color=ft.Colors.BLACK)),
                    ft.DataCell(ft.Text(f"{sub_total} 点", size=18, weight="bold", color=ft.Colors.RED_700 if sub_total < 0 else ft.Colors.GREEN_700)), # ⭕ 2列目で合計を計算
                    ft.DataCell(ft.Text("", size=16)), # 3列目は空欄
                ]
            )
        )
        count_table3.rows = rows

    # ボタンをポチッと押したときの増減ロジック
    def on_card_adjust_click(key, value):
        card_inputs[key] += value
        update_data_table3()
        table_container3.update()


    def on_input_change(key, val):
        try:
            agri_inputs[key] = int(val) if val != "" else 0
        except ValueError:
            agri_inputs[key] = 0
        
        ranch_c, unused_c, ranch_stable = analyze_grid()
        update_data_table(ranch_c, unused_c, ranch_stable)
        update_data_table2()
        table_container.update()
        table_container2.update()

    def update_mode_ui():
        if current_mode == "COLOR":
            line_mode_btn.style = ft.ButtonStyle(bgcolor=ft.Colors.GREY_300, color=ft.Colors.BLACK,
                                                 shape=ft.RoundedRectangleBorder(radius=8))
        else:
            line_mode_btn.style = ft.ButtonStyle(bgcolor=ft.Colors.BLACK, color=ft.Colors.WHITE,
                                                 shape=ft.RoundedRectangleBorder(radius=8))
            for p_col in palette_row.controls:
                p_col.controls.border = None

        ranch_c, unused_c, ranch_stable = analyze_grid()
        update_data_table(ranch_c, unused_c, ranch_stable)

        line_mode_btn.update()
        palette_row.update()
        table_container.update()
        table_container2.update()
        table_container3.update() 
        stack_layout.update()

    def on_palette_click(e):
        nonlocal selected_color, current_mode
        current_mode = "COLOR"
        selected_color = e.control.data
        for p_col in palette_row.controls:
            p_col.controls.border = None
        e.control.border = ft.border.all(3, ft.Colors.BLACK)
        update_mode_ui()

    def on_line_mode_click(e):
        nonlocal current_mode
        current_mode = "LINE"
        update_mode_ui()

    def on_cell_click(e):
        if current_mode == "COLOR":
            if e.control.bgcolor == selected_color:
                e.control.bgcolor = ft.Colors.GREY_100
            else:
                e.control.bgcolor = selected_color
            update_mode_ui()

    def toggle_line(e):
        if current_mode == "LINE":
            actual_line = e.control.content
            if actual_line.bgcolor == ft.Colors.BROWN_700:
                actual_line.bgcolor = ft.Colors.GREY_300
            else:
                actual_line.bgcolor = ft.Colors.BROWN_700
            update_mode_ui()

    palette_options = []
    for info in PALETTE_INFO:
        btn = ft.Container(width=40, height=40, bgcolor=info["color"], border_radius=20, data=info["color"], on_click=on_palette_click)
        lbl = ft.Text(info["name"], size=10, weight="bold")
        palette_options.append(ft.Column([btn, lbl], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2))

    palette_options[0].controls[0].border = ft.border.all(3, ft.Colors.BLACK)
    palette_row = ft.Row(controls=palette_options, alignment=ft.MainAxisAlignment.CENTER, spacing=10)

    line_mode_btn = ft.ElevatedButton(
        text="✏️ 柵の建設",
        on_click=on_line_mode_click,
        style=ft.ButtonStyle(bgcolor=ft.Colors.GREY_300, color=ft.Colors.BLACK, shape=ft.RoundedRectangleBorder(radius=8))
    )

    top_control_row = ft.Row(controls=[palette_row, ft.VerticalDivider(width=10), line_mode_btn], alignment=ft.MainAxisAlignment.CENTER)
    
    count_table = ft.DataTable(
        width=350,
        column_spacing=18,
        columns=[
            ft.DataColumn(ft.Text("項目", size=16, weight="bold")),
            ft.DataColumn(ft.Text("個数", size=16, weight="bold")),
            ft.DataColumn(ft.Text("得点", size=16, weight="bold")),
        ],
        rows=[]
    )
    table_container = ft.Container(content=count_table, alignment=ft.alignment.center, padding=10)

    count_table2 = ft.DataTable(
        width=350,
        column_spacing=18,
        columns=[
            ft.DataColumn(ft.Text("項目", size=16, weight="bold")),
            ft.DataColumn(ft.Text("個数", size=16, weight="bold")),
            ft.DataColumn(ft.Text("得点", size=16, weight="bold")),
        ],
        rows=[]
    )
    table_container2 = ft.Container(content=count_table2, alignment=ft.alignment.center, padding=10)

    # 👇 【変更後】count_table3 の列名を新レイアウト用に書き換え
    count_table3 = ft.DataTable(
        width=350,
        column_spacing=18,
        columns=[
            ft.DataColumn(ft.Text("カードボーナス", size=16, weight="bold")),
            ft.DataColumn(ft.Text("得点", size=16, weight="bold")),         # ⭕ 2列目
            ft.DataColumn(ft.Text("個別調整", size=16, weight="bold")),     # ⭕ 3列目
        ]
    )
    table_container3 = ft.Container(content=count_table3, alignment=ft.alignment.center, padding=10)


    stack_layout = ft.Stack(width=TOTAL_W, height=TOTAL_H)

    for r in range(ROWS):
        for c in range(COLS):
            cell = ft.Container(
                content=ft.Text(f"{r * COLS + c + 1}", color=ft.Colors.GREY_400, size=12),
                alignment=ft.alignment.center, bgcolor=ft.Colors.GREY_100,
                width=CELL_W, height=CELL_H, left=c * CELL_W + OFFSET, top=r * CELL_H + OFFSET,
                on_click=on_cell_click
            )
            stack_layout.controls.append(cell)
            cell_dict[(r, c)] = cell

    for r in range(ROWS + 1):
        for c in range(COLS):
            left_pos = c * CELL_W + OFFSET
            top_pos = r * CELL_H - (LINE_THICK / 2) + OFFSET
            if r == 0: top_pos = OFFSET
            if r == ROWS: top_pos = TOTAL_H - LINE_THICK - OFFSET

            horiz_line = ft.Container(width=CELL_W, height=LINE_THICK, bgcolor=ft.Colors.GREY_300)
            hit_box = ft.Container(
                content=horiz_line, width=CELL_W, height=LINE_THICK + (HIT_BOX_EXT * 2),
                bgcolor=ft.Colors.TRANSPARENT, alignment=ft.alignment.center,
                left=left_pos, top=top_pos - HIT_BOX_EXT, on_click=toggle_line
            )
            stack_layout.controls.append(hit_box)
            horiz_line_dict[(r, c)] = horiz_line

    for c in range(COLS + 1):
        for r in range(ROWS):
            left_pos = c * CELL_W - (LINE_THICK / 2) + OFFSET
            top_pos = r * CELL_H + OFFSET
            if c == 0: left_pos = OFFSET
            if c == COLS: left_pos = TOTAL_W - LINE_THICK - OFFSET

            vert_line = ft.Container(width=LINE_THICK, height=CELL_H, bgcolor=ft.Colors.GREY_300)
            hit_box = ft.Container(
                content=vert_line, width=LINE_THICK + (HIT_BOX_EXT * 2), height=CELL_H,
                bgcolor=ft.Colors.TRANSPARENT, alignment=ft.alignment.center,
                left=left_pos - HIT_BOX_EXT, top=top_pos, on_click=toggle_line
            )
            stack_layout.controls.append(hit_box)
            vert_line_dict[(c, r)] = vert_line

    page.add(
        ft.Column([
            top_control_row,
            ft.Divider(),
            ft.Container(content=stack_layout, border=ft.border.all(1, ft.Colors.GREY_300)),
            ft.Divider(),
            table_container,
            ft.Divider(),
            table_container2,
            ft.Divider(),    # 👈 区切り線を追加
            table_container3 # 👈 3つ目の表をここに追加
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    # ⭐️ 起動時に確実に両方の表のデータを組み立てて、ページ全体をリフレッシュします
    ranch_c, unused_c, ranch_stable = analyze_grid()
    update_data_table(ranch_c, unused_c, ranch_stable)
    update_data_table2()
    update_data_table3()
    
    page.update() 


if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    ft.app(target=main, host="0.0.0.0", view=ft.AppView.WEB_BROWSER, port=port)
