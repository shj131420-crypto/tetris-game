import random
import tkinter as tk

CELL_SIZE = 28
COLS = 10
ROWS = 20

SHAPES = {
    "I": [[(0, 1), (1, 1), (2, 1), (3, 1)], [(2, 0), (2, 1), (2, 2), (2, 3)]],
    "O": [[(1, 0), (2, 0), (1, 1), (2, 1)]],
    "T": [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "S": [[(1, 0), (2, 0), (0, 1), (1, 1)], [(1, 0), (1, 1), (2, 1), (2, 2)]],
    "Z": [[(0, 0), (1, 0), (1, 1), (2, 1)], [(2, 0), (1, 1), (2, 1), (1, 2)]],
    "J": [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    "L": [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}

COLORS = {
    "I": "#38bdf8",
    "O": "#facc15",
    "T": "#c084fc",
    "S": "#4ade80",
    "Z": "#f87171",
    "J": "#60a5fa",
    "L": "#fb923c",
}

LINE_SCORES = {1: 100, 2: 300, 3: 500, 4: 800}


class TetrisGame:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("改良版テトリス")
        self.root.resizable(False, False)

        self.board_canvas = tk.Canvas(
            root,
            width=COLS * CELL_SIZE,
            height=ROWS * CELL_SIZE,
            bg="#111827",
            highlightthickness=2,
            highlightbackground="#374151",
        )
        self.board_canvas.grid(row=0, column=0, padx=(12, 6), pady=12)

        side_panel = tk.Frame(root, padx=6, pady=12)
        side_panel.grid(row=0, column=1, sticky="n")

        tk.Label(side_panel, text="NEXT", font=("Arial", 12, "bold")).pack(anchor="w")
        self.next_canvas = tk.Canvas(
            side_panel,
            width=4 * CELL_SIZE,
            height=4 * CELL_SIZE,
            bg="#111827",
            highlightthickness=1,
            highlightbackground="#374151",
        )
        self.next_canvas.pack(pady=(4, 12))

        self.score_var = tk.StringVar()
        self.lines_var = tk.StringVar()
        self.level_var = tk.StringVar()
        self.status_var = tk.StringVar()

        tk.Label(side_panel, textvariable=self.score_var, font=("Arial", 11, "bold")).pack(anchor="w", pady=2)
        tk.Label(side_panel, textvariable=self.lines_var, font=("Arial", 11)).pack(anchor="w", pady=2)
        tk.Label(side_panel, textvariable=self.level_var, font=("Arial", 11)).pack(anchor="w", pady=2)
        tk.Label(side_panel, textvariable=self.status_var, font=("Arial", 11, "bold"), fg="#dc2626").pack(
            anchor="w", pady=(8, 12)
        )

        guide_text = (
            "操作方法\n"
            "←/→ : 移動\n"
            "↓   : 落下\n"
            "↑/Z : 回転\n"
            "P   : 一時停止\n"
            "R   : リスタート"
        )
        tk.Label(side_panel, text=guide_text, justify="left", font=("Arial", 10), fg="#374151").pack(anchor="w")

        self.root.bind("<KeyPress>", self.on_key_press)
        self.after_id = None
        self.reset_game()

    def reset_game(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.paused = False
        self.game_over = False
        self.next_kind = random.choice(list(SHAPES.keys()))
        self.spawn_piece()
        self.update_labels()
        self.draw()
        self.schedule_tick()

    def spawn_piece(self):
        self.kind = self.next_kind
        self.next_kind = random.choice(list(SHAPES.keys()))
        self.rotation = 0
        self.px = COLS // 2 - 2
        self.py = 0
        if not self.is_valid_position(self.px, self.py, self.rotation):
            self.game_over = True
            self.status_var.set("GAME OVER (Rで再開)")

    def current_cells(self, px=None, py=None, rotation=None):
        x0 = self.px if px is None else px
        y0 = self.py if py is None else py
        rot = self.rotation if rotation is None else rotation
        return [(x0 + dx, y0 + dy) for dx, dy in SHAPES[self.kind][rot]]

    def is_valid_position(self, px, py, rotation):
        for x, y in self.current_cells(px, py, rotation):
            if x < 0 or x >= COLS or y >= ROWS:
                return False
            if y >= 0 and self.grid[y][x] is not None:
                return False
        return True

    def lock_piece(self):
        for x, y in self.current_cells():
            if 0 <= y < ROWS and 0 <= x < COLS:
                self.grid[y][x] = self.kind
        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        remaining = [row for row in self.grid if any(cell is None for cell in row)]
        cleared = ROWS - len(remaining)
        if cleared > 0:
            empty_rows = [[None for _ in range(COLS)] for _ in range(cleared)]
            self.grid = empty_rows + remaining
            self.lines += cleared
            self.score += LINE_SCORES.get(cleared, cleared * 200) * self.level
            self.level = self.lines // 5 + 1

    def move(self, dx, dy):
        if self.paused or self.game_over:
            return False
        if self.is_valid_position(self.px + dx, self.py + dy, self.rotation):
            self.px += dx
            self.py += dy
            return True
        return False

    def rotate(self):
        if self.paused or self.game_over:
            return
        rotations = SHAPES[self.kind]
        next_rot = (self.rotation + 1) % len(rotations)
        for kick_x in (0, -1, 1, -2, 2):
            if self.is_valid_position(self.px + kick_x, self.py, next_rot):
                self.px += kick_x
                self.rotation = next_rot
                return

    def toggle_pause(self):
        if self.game_over:
            return
        self.paused = not self.paused
        self.status_var.set("PAUSED" if self.paused else "")
        if not self.paused:
            self.schedule_tick()
        self.draw()

    def on_key_press(self, event):
        key = event.keysym
        if key in ("r", "R"):
            self.reset_game()
            return
        if key in ("p", "P"):
            self.toggle_pause()
            return
        if self.paused or self.game_over:
            return

        if key in ("Left", "a", "A"):
            self.move(-1, 0)
        elif key in ("Right", "d", "D"):
            self.move(1, 0)
        elif key in ("Down", "s", "S"):
            if self.move(0, 1):
                self.score += 1
        elif key in ("Up", "w", "W", "z", "Z"):
            self.rotate()

        self.update_labels()
        self.draw()

    def get_tick_ms(self):
        return max(120, 650 - (self.level - 1) * 60)

    def schedule_tick(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
        if not self.paused and not self.game_over:
            self.after_id = self.root.after(self.get_tick_ms(), self.tick)

    def tick(self):
        if self.paused or self.game_over:
            return
        if not self.move(0, 1):
            self.lock_piece()
        self.update_labels()
        self.draw()
        self.schedule_tick()

    def update_labels(self):
        self.score_var.set(f"SCORE: {self.score}")
        self.lines_var.set(f"LINES: {self.lines}")
        self.level_var.set(f"LEVEL: {self.level}")

    def draw_cell(self, canvas, col, row, color):
        x1 = col * CELL_SIZE
        y1 = row * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#1f2937", width=1)

    def draw(self):
        self.board_canvas.delete("all")
        for y in range(ROWS):
            for x in range(COLS):
                kind = self.grid[y][x]
                if kind is not None:
                    self.draw_cell(self.board_canvas, x, y, COLORS[kind])

        if not self.game_over:
            for x, y in self.current_cells():
                if y >= 0:
                    self.draw_cell(self.board_canvas, x, y, COLORS[self.kind])

        self.next_canvas.delete("all")
        for dx, dy in SHAPES[self.next_kind][0]:
            self.draw_cell(self.next_canvas, dx, dy, COLORS[self.next_kind])


def main():
    root = tk.Tk()
    TetrisGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()