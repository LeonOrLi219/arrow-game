import tkinter as tk
from tkinter import messagebox
import copy

# ============================================================
# 一箭又一箭 —— Python/Tkinter 基础版
# 运行：python arrow_game.py
# 无需安装第三方库
# ============================================================

CELL = 78
ROWS = COLS = 6
BOARD_X = 28
BOARD_Y = 145
CANVAS_W = BOARD_X * 2 + CELL * COLS
CANVAS_H = BOARD_Y + CELL * ROWS + 28

BG = "#101522"
PANEL = "#182235"
GRID = "#2d3b55"
TEXT = "#f5f7fb"
MUTED = "#a9b5c8"
BLUE = "#5bb8ff"
GREEN = "#55d98b"
RED = "#ff6472"
YELLOW = "#ffd166"
ARROW = "#edf5ff"
ARROW_SELECTED = "#75d6ff"
ARROW_BLOCKED = "#ff6b6b"

DIRS = {
    "U": (-1, 0),
    "D": (1, 0),
    "L": (0, -1),
    "R": (0, 1),
}
SYMBOLS = {"U": "↑", "D": "↓", "L": "←", "R": "→"}

# (行, 列, 方向)
# 三关均可正常通关，并覆盖上下左右四种箭头。
LEVELS = [
    [
        (0, 0, "R"), (0, 3, "U"),
        (1, 1, "D"), (1, 5, "L"),
        (2, 2, "R"), (3, 4, "D"),
        (4, 0, "U"), (5, 3, "R"),
    ],
    [
        (0, 1, "D"), (0, 4, "L"),
        (1, 4, "D"), (2, 0, "R"),
        (2, 3, "U"), (3, 3, "L"),
        (4, 1, "U"), (4, 5, "L"),
        (5, 2, "R"), (5, 5, "U"),
    ],
    [
        (0, 0, "D"), (0, 2, "L"), (0, 5, "D"),
        (1, 2, "U"), (1, 4, "L"),
        (2, 1, "R"), (2, 5, "U"),
        (3, 0, "R"), (3, 3, "D"),
        (4, 2, "U"), (4, 5, "L"),
        (5, 1, "R"), (5, 4, "U"),
    ],
]


class ArrowGame:
    def __init__(self, root):
        self.root = root
        self.root.title("一箭又一箭")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.level_index = 0
        self.arrows = {}
        self.mistakes = 3
        self.state = "start"  # start / playing / result
        self.animating = False
        self.feedback = ""
        self.feedback_kind = "normal"

        self.main = tk.Frame(root, bg=BG)
        self.main.pack(fill="both", expand=True)

        self.show_start()

    # ---------------- 基础界面 ----------------

    def clear_main(self):
        for widget in self.main.winfo_children():
            widget.destroy()

    def make_button(self, parent, text, command, width=16):
        return tk.Button(
            parent, text=text, command=command,
            font=("Microsoft YaHei UI", 12, "bold"),
            width=width, height=1,
            bg=BLUE, fg="#08111f",
            activebackground="#8bdcff",
            activeforeground="#08111f",
            relief="flat", bd=0, cursor="hand2",
        )

    def show_start(self):
        self.state = "start"
        self.clear_main()

        box = tk.Frame(self.main, bg=BG)
        box.pack(expand=True, padx=60, pady=60)

        tk.Label(
            box, text="一箭又一箭",
            font=("Microsoft YaHei UI", 30, "bold"),
            fg=TEXT, bg=BG
        ).pack(pady=(10, 8))

        tk.Label(
            box, text="点箭头，让没有障碍的箭头飞出棋盘！",
            font=("Microsoft YaHei UI", 14),
            fg=MUTED, bg=BG
        ).pack(pady=(0, 28))

        rules = (
            "玩法说明\n"
            "• 点击箭头检查它前进方向的路径\n"
            "• 路上没有其他箭头 → 飞出并消除\n"
            "• 路上有其他箭头 → 碰撞提示，并消耗 1 次失误\n"
            "• 清空全部箭头即可进入下一关\n"
            "• 失误次数为 0 时，本关失败"
        )
        tk.Label(
            box, text=rules, justify="left",
            font=("Microsoft YaHei UI", 11),
            fg=TEXT, bg=PANEL,
            padx=28, pady=22
        ).pack(pady=(0, 28))

        self.make_button(box, "开始游戏", self.start_game, 18).pack()

    def start_game(self):
        self.level_index = 0
        self.load_level()
        self.show_game()

    def load_level(self):
        self.arrows = {
            (r, c): {"dir": d}
            for r, c, d in copy.deepcopy(LEVELS[self.level_index])
        }
        self.mistakes = 3
        self.feedback = "请选择一个箭头"
        self.feedback_kind = "normal"
        self.animating = False

    def show_game(self):
        self.state = "playing"
        self.clear_main()

        top = tk.Frame(self.main, bg=BG)
        top.pack(fill="x", padx=22, pady=(18, 8))

        tk.Label(
            top, text=f"一箭又一箭    第 {self.level_index + 1} / {len(LEVELS)} 关",
            font=("Microsoft YaHei UI", 18, "bold"),
            fg=TEXT, bg=BG
        ).pack(side="left")

        self.restart_btn = self.make_button(
            top, "重新开始", self.restart_level, 11
        )
        self.restart_btn.pack(side="right")

        info = tk.Frame(self.main, bg=PANEL)
        info.pack(fill="x", padx=22, pady=(0, 10))

        self.count_label = tk.Label(
            info, font=("Microsoft YaHei UI", 11, "bold"),
            fg=TEXT, bg=PANEL
        )
        self.count_label.pack(side="left", padx=16, pady=9)

        self.mistake_label = tk.Label(
            info, font=("Microsoft YaHei UI", 11, "bold"),
            fg=YELLOW, bg=PANEL
        )
        self.mistake_label.pack(side="left", padx=16, pady=9)

        self.feedback_label = tk.Label(
            info, font=("Microsoft YaHei UI", 11, "bold"),
            fg=MUTED, bg=PANEL
        )
        self.feedback_label.pack(side="right", padx=16, pady=9)

        self.canvas = tk.Canvas(
            self.main, width=CANVAS_W, height=CANVAS_H,
            bg=BG, highlightthickness=0
        )
        self.canvas.pack(padx=22, pady=(0, 22))
        self.canvas.bind("<Button-1>", self.on_click)

        self.draw_board()

    def update_info(self):
        self.count_label.config(text=f"剩余箭头：{len(self.arrows)}")
        self.mistake_label.config(text=f"剩余失误：{'● ' * self.mistakes}".strip())

        color = MUTED
        if self.feedback_kind == "success":
            color = GREEN
        elif self.feedback_kind == "blocked":
            color = RED
        elif self.feedback_kind == "warning":
            color = YELLOW

        self.feedback_label.config(text=self.feedback, fg=color)

    # ---------------- 棋盘绘制 ----------------

    def cell_center(self, r, c):
        return (
            BOARD_X + c * CELL + CELL // 2,
            BOARD_Y + r * CELL + CELL // 2
        )

    def draw_board(self):
        self.canvas.delete("all")

        # 棋盘背景与网格
        x0, y0 = BOARD_X, BOARD_Y
        x1 = x0 + COLS * CELL
        y1 = y0 + ROWS * CELL

        self.canvas.create_rectangle(
            x0 - 3, y0 - 3, x1 + 3, y1 + 3,
            fill=PANEL, outline=GRID, width=2
        )

        for r in range(ROWS):
            for c in range(COLS):
                xa = x0 + c * CELL
                ya = y0 + r * CELL
                self.canvas.create_rectangle(
                    xa, ya, xa + CELL, ya + CELL,
                    fill=PANEL, outline=GRID, width=1
                )

        # 箭头
        for (r, c), data in self.arrows.items():
            self.draw_arrow(r, c, data["dir"])

        self.update_info()

    def draw_arrow(self, r, c, direction, color=ARROW, scale=1.0, offset=(0, 0)):
        cx, cy = self.cell_center(r, c)
        cx += offset[0]
        cy += offset[1]

        # 用大号字符作为箭头，清晰、稳定、无需图片资源
        font_size = max(22, int(43 * scale))
        self.canvas.create_text(
            cx, cy,
            text=SYMBOLS[direction],
            font=("Arial", font_size, "bold"),
            fill=color,
            tags="arrow_visual"
        )

    # ---------------- 游戏逻辑 ----------------

    def on_click(self, event):
        if self.state != "playing" or self.animating:
            return

        c = int((event.x - BOARD_X) // CELL)
        r = int((event.y - BOARD_Y) // CELL)

        if not (0 <= r < ROWS and 0 <= c < COLS):
            return

        if (r, c) not in self.arrows:
            return

        self.try_arrow((r, c))

    def path_is_clear(self, pos):
        r, c = pos
        direction = self.arrows[pos]["dir"]
        dr, dc = DIRS[direction]

        rr, cc = r + dr, c + dc
        while 0 <= rr < ROWS and 0 <= cc < COLS:
            if (rr, cc) in self.arrows:
                return False
            rr += dr
            cc += dc
        return True

    def try_arrow(self, pos):
        if self.path_is_clear(pos):
            self.fly_out(pos)
        else:
            self.collision_feedback(pos)

    # ---------------- 飞出动画 ----------------

    def fly_out(self, pos):
        if pos not in self.arrows:
            return

        self.animating = True
        r, c = pos
        direction = self.arrows[pos]["dir"]

        # 从数据中暂时删除，避免动画过程中重复点击
        del self.arrows[pos]
        self.feedback = "飞出成功！"
        self.feedback_kind = "success"
        self.draw_board()

        # 通过多个位置逐帧移动，形成飞出动画
        steps = 9
        dr, dc = DIRS[direction]

        def frame(i):
            if i >= steps:
                self.animating = False
                self.draw_board()
                if not self.arrows:
                    self.level_cleared()
                return

            self.draw_board()

            # 飞出箭头的中心从原格移动到棋盘外
            cx, cy = self.cell_center(r, c)
            travel = CELL * (i + 1) * 0.55
            fx = cx + dc * travel
            fy = cy + dr * travel

            self.canvas.create_text(
                fx, fy,
                text=SYMBOLS[direction],
                font=("Arial", 43, "bold"),
                fill=GREEN
            )
            self.root.after(35, lambda: frame(i + 1))

        frame(0)

    # ---------------- 碰撞动画 ----------------

    def collision_feedback(self, pos):
        if self.mistakes <= 0:
            return

        self.mistakes -= 1
        self.feedback = "前方有箭头阻挡！失误 -1"
        self.feedback_kind = "blocked"
        self.animating = True

        r, c = pos
        direction = self.arrows[pos]["dir"]
        dr, dc = DIRS[direction]

        # 前后轻微弹动 + 变红
        sequence = [
            (1.0, RED, 8),
            (1.0, RED, -8),
            (1.0, RED, 5),
            (1.0, RED, -5),
            (1.0, ARROW, 0),
        ]

        def frame(i):
            self.draw_board()

            if i < len(sequence):
                _, color, shift = sequence[i]
                # 重新绘制当前箭头为碰撞状态
                self.canvas.create_text(
                    self.cell_center(r, c)[0] + dc * shift,
                    self.cell_center(r, c)[1] + dr * shift,
                    text=SYMBOLS[direction],
                    font=("Arial", 43, "bold"),
                    fill=color
                )
                self.root.after(55, lambda: frame(i + 1))
            else:
                self.animating = False
                self.draw_board()
                if self.mistakes <= 0:
                    self.root.after(250, self.level_failed)

        frame(0)

    # ---------------- 关卡结果 ----------------

    def level_cleared(self):
        self.state = "result"
        self.clear_main()

        box = tk.Frame(self.main, bg=BG)
        box.pack(expand=True, padx=60, pady=60)

        tk.Label(
            box, text="🎉 本关通关！",
            font=("Microsoft YaHei UI", 28, "bold"),
            fg=GREEN, bg=BG
        ).pack(pady=(10, 10))

        if self.level_index + 1 < len(LEVELS):
            text = f"第 {self.level_index + 1} 关已清空，准备进入下一关。"
            tk.Label(
                box, text=text,
                font=("Microsoft YaHei UI", 13),
                fg=TEXT, bg=BG
            ).pack(pady=(0, 24))

            self.make_button(
                box, "进入下一关", self.next_level, 18
            ).pack()
        else:
            tk.Label(
                box, text="恭喜！你已经完成全部 3 个基础关卡。",
                font=("Microsoft YaHei UI", 13),
                fg=TEXT, bg=BG
            ).pack(pady=(0, 24))

            self.make_button(
                box, "重新挑战第 1 关", self.start_game, 18
            ).pack()

            tk.Button(
                box, text="返回开始界面", command=self.show_start,
                font=("Microsoft YaHei UI", 11),
                bg=PANEL, fg=TEXT, activebackground=GRID,
                activeforeground=TEXT, relief="flat", bd=0,
                cursor="hand2", width=18
            ).pack(pady=10)

    def level_failed(self):
        self.state = "result"
        self.clear_main()

        box = tk.Frame(self.main, bg=BG)
        box.pack(expand=True, padx=60, pady=60)

        tk.Label(
            box, text="💥 本关失败",
            font=("Microsoft YaHei UI", 28, "bold"),
            fg=RED, bg=BG
        ).pack(pady=(10, 10))

        tk.Label(
            box,
            text=f"第 {self.level_index + 1} 关的失误次数已经用完。",
            font=("Microsoft YaHei UI", 13),
            fg=TEXT, bg=BG
        ).pack(pady=(0, 24))

        self.make_button(
            box, "重新开始本关", self.restart_level, 18
        ).pack()

        tk.Button(
            box, text="返回开始界面", command=self.show_start,
            font=("Microsoft YaHei UI", 11),
            bg=PANEL, fg=TEXT, activebackground=GRID,
            activeforeground=TEXT, relief="flat", bd=0,
            cursor="hand2", width=18
        ).pack(pady=10)

    def next_level(self):
        self.level_index += 1
        self.load_level()
        self.show_game()

    def restart_level(self):
        self.load_level()
        self.show_game()


if __name__ == "__main__":
    root = tk.Tk()
    app = ArrowGame(root)
    root.mainloop()