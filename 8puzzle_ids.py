import random
import tkinter as tk
from tkinter import messagebox

goal = (
    (1, 2, 3),
    (8, 0, 4),
    (7, 6, 5)
)

def find_zero(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j

def actions(state):
    x, y = find_zero(state)

    moves = []
    if x > 0:
        moves.append((-1, 0))
    if x < 2:
        moves.append((1, 0))
    if y > 0:
        moves.append((0, -1))
    if y < 2:
        moves.append((0, 1))
    return moves

def child_node(state, action):
    x, y = find_zero(state)

    dx, dy = action
    nx, ny = x + dx, y + dy

    new_state = [list(row) for row in state]

    new_state[x][y], new_state[nx][ny] = \
        new_state[nx][ny], new_state[x][y]

    return tuple(tuple(row) for row in new_state)

def generate_random_start(steps=25):
    state = goal
    previous_action = None

    for _ in range(steps):
        possible_actions = actions(state)

        if previous_action is not None:
            opposite_action = (-previous_action[0], -previous_action[1])
            filtered_actions = [action for action in possible_actions if action != opposite_action]
            if filtered_actions:
                possible_actions = filtered_actions

        action = random.choice(possible_actions)
        state = child_node(state, action)
        previous_action = action

    return state


start = generate_random_start()

def print_state(state):
    for row in state:
        print(row)
    print()

def depth_limited_search(state, goal, limit, path):
    if state == goal:
        return path

    if limit == 0:
        return "cutoff"

    cutoff_occurred = False

    for action in actions(state):
        child = child_node(state, action)

        if child not in path:
            result = depth_limited_search(
                child,
                goal,
                limit - 1,
                path + [child]
            )

            if result == "cutoff":
                cutoff_occurred = True
            elif result != "failure":
                return result

    if cutoff_occurred:
        return "cutoff"

    return "failure"


def iterative_deepening_search(start, goal, max_depth=40):
    for depth in range(max_depth + 1):
        result = depth_limited_search(start, goal, depth, [start])

        if result == "cutoff":
            continue
        if result == "failure":
            return None
        return result

    return None


class PuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle IDS")
        self.root.resizable(False, False)

        self.solution = None
        self.step_index = 0
        self.auto_running = False

        title_label = tk.Label(
            root,
            text="8 Puzzle - Iterative Deepening Search",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(12, 6))

        self.board_frame = tk.Frame(root, padx=10, pady=10)
        self.board_frame.pack()

        self.cells = []
        for i in range(3):
            row = []
            for j in range(3):
                label = tk.Label(
                    self.board_frame,
                    text="",
                    width=4,
                    height=2,
                    font=("Arial", 24, "bold"),
                    relief="solid",
                    borderwidth=2,
                    bg="white"
                )
                label.grid(row=i, column=j, padx=4, pady=4)
                row.append(label)
            self.cells.append(row)

        self.info_label = tk.Label(
            root,
            text="Nhấn 'Giải IDS' để tìm lời giải.",
            font=("Arial", 11)
        )
        self.info_label.pack(pady=(6, 2))

        self.step_label = tk.Label(root, text="", font=("Arial", 11))
        self.step_label.pack(pady=(0, 8))

        button_frame = tk.Frame(root)
        button_frame.pack(pady=(0, 12))

        self.solve_button = tk.Button(
            button_frame,
            text="Giải IDS",
            width=12,
            command=self.solve
        )
        self.solve_button.grid(row=0, column=0, padx=4)

        self.prev_button = tk.Button(
            button_frame,
            text="Bước trước",
            width=12,
            command=self.prev_step,
            state="disabled"
        )
        self.prev_button.grid(row=0, column=1, padx=4)

        self.next_button = tk.Button(
            button_frame,
            text="Bước tiếp",
            width=12,
            command=self.next_step,
            state="disabled"
        )
        self.next_button.grid(row=0, column=2, padx=4)

        self.auto_button = tk.Button(
            button_frame,
            text="Tự chạy",
            width=12,
            command=self.auto_run,
            state="disabled"
        )
        self.auto_button.grid(row=0, column=3, padx=4)

        self.reset_button = tk.Button(
            button_frame,
            text="Reset",
            width=12,
            command=self.reset
        )
        self.reset_button.grid(row=0, column=4, padx=4)

        self.draw_state(start)

    def draw_state(self, state):
        for i in range(3):
            for j in range(3):
                value = state[i][j]
                if value == 0:
                    self.cells[i][j].config(text="", bg="#f0f0f0")
                else:
                    self.cells[i][j].config(text=str(value), bg="#cfe8ff")

    def solve(self):
        self.solution = iterative_deepening_search(start, goal)
        self.step_index = 0
        self.auto_running = False

        if self.solution:
            self.draw_state(self.solution[0])
            self.info_label.config(
                text=f"Tìm thấy lời giải với {len(self.solution) - 1} bước."
            )
            self.step_label.config(text=f"Bước 0 / {len(self.solution) - 1}")
            self.prev_button.config(state="disabled")
            self.next_button.config(state="normal" if len(self.solution) > 1 else "disabled")
            self.auto_button.config(state="normal" if len(self.solution) > 1 else "disabled")
        else:
            self.info_label.config(text="Không có lời giải.")
            self.step_label.config(text="")
            self.prev_button.config(state="disabled")
            self.next_button.config(state="disabled")
            self.auto_button.config(state="disabled")
            messagebox.showinfo("Kết quả", "Không có lời giải.")

    def next_step(self):
        if not self.solution:
            return

        if self.step_index < len(self.solution) - 1:
            self.step_index += 1
            self.draw_state(self.solution[self.step_index])
            self.step_label.config(
                text=f"Bước {self.step_index} / {len(self.solution) - 1}"
            )

        self.prev_button.config(state="normal" if self.step_index > 0 else "disabled")
        self.next_button.config(state="normal" if self.step_index < len(self.solution) - 1 else "disabled")

    def prev_step(self):
        if not self.solution:
            return

        if self.step_index > 0:
            self.step_index -= 1
            self.draw_state(self.solution[self.step_index])
            self.step_label.config(
                text=f"Bước {self.step_index} / {len(self.solution) - 1}"
            )

        self.prev_button.config(state="normal" if self.step_index > 0 else "disabled")
        self.next_button.config(state="normal" if self.step_index < len(self.solution) - 1 else "disabled")

    def auto_run(self):
        if not self.solution or self.auto_running:
            return

        self.auto_running = True
        self.solve_button.config(state="disabled")
        self.prev_button.config(state="disabled")
        self.next_button.config(state="disabled")
        self.auto_button.config(state="disabled")
        self.play_auto()

    def play_auto(self):
        if not self.auto_running or not self.solution:
            return

        if self.step_index < len(self.solution) - 1:
            self.step_index += 1
            self.draw_state(self.solution[self.step_index])
            self.step_label.config(
                text=f"Bước {self.step_index} / {len(self.solution) - 1}"
            )
            self.root.after(800, self.play_auto)
        else:
            self.auto_running = False
            self.solve_button.config(state="normal")
            self.prev_button.config(state="normal" if self.step_index > 0 else "disabled")
            self.next_button.config(state="disabled")
            self.auto_button.config(state="normal")

    def reset(self):
        global start

        self.auto_running = False
        start = generate_random_start()
        self.solution = None
        self.step_index = 0
        self.draw_state(start)
        self.info_label.config(text="Đã tạo đầu vào ngẫu nhiên mới. Nhấn 'Giải IDS' để tìm lời giải.")
        self.step_label.config(text="")
        self.solve_button.config(state="normal")
        self.prev_button.config(state="disabled")
        self.next_button.config(state="disabled")
        self.auto_button.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleGUI(root)
    root.mainloop()