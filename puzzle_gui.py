import time
import tkinter as tk
from tkinter import messagebox, ttk
import random

from puzzle_algorithms import (
    a_star,
    and_or_search,
    breadth_first_search,
    child_node,
    CSP_COLOR_MAP,
    CSP_COLORS,
    CSP_COLOR_NAME,
    depth_first_search,
    direction_from_action,
    find_zero,
    forward_checking_step_by_step,
    get_csp_variables,
    generate_csp_start,
    generate_random_start,
    goal,
    greedy_search,
    ida_star,
    inversion_count,
    iterative_deepening_search,
    manhattan,
    misplaced_tiles,
    random_child,
    simulated_annealing,
    simple_hill_climbing,
    step_cost,
    uniform_cost_search,
    zero_move_direction,
    actions,
)

# ─────────────────────────────────────────
#  MINIMAX / ALPHA-BETA cho Tic-Tac-Toe
# ─────────────────────────────────────────

def ttt_check_winner(board):
    lines = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]
    for l in lines:
        vals = [board[i] for i in l]
        if vals[0] and vals[0] == vals[1] == vals[2]:
            return vals[0]
    return None

def ttt_is_full(board):
    return all(c != '' for c in board)

def minimax(board, is_maximizing, log=None, depth=0):
    winner = ttt_check_winner(board)
    if winner == 'X':
        return 10 - depth
    if winner == 'O':
        return depth - 10
    if ttt_is_full(board):
        return 0

    if is_maximizing:
        best = -float('inf')
        for i in range(9):
            if board[i] == '':
                board[i] = 'X'
                score = minimax(board, False, log, depth+1)
                board[i] = ''
                if log is not None:
                    log.append(f"{'  '*depth}[MAX] ô {i} → score={score}")
                best = max(best, score)
        return best
    else:
        best = float('inf')
        for i in range(9):
            if board[i] == '':
                board[i] = 'O'
                score = minimax(board, True, log, depth+1)
                board[i] = ''
                if log is not None:
                    log.append(f"{'  '*depth}[MIN] ô {i} → score={score}")
                best = min(best, score)
        return best

def minimax_best_move(board, log=None):
    best_score = -float('inf')
    best_move = None
    for i in range(9):
        if board[i] == '':
            board[i] = 'X'
            score = minimax(board, False, log, 1)
            board[i] = ''
            if log is not None:
                log.append(f"[ROOT] ô {i} → score={score}")
            if score > best_score:
                best_score = score
                best_move = i
    return best_move, best_score

def alpha_beta(board, is_maximizing, alpha, beta, log=None, depth=0):
    winner = ttt_check_winner(board)
    if winner == 'X':
        return 10 - depth
    if winner == 'O':
        return depth - 10
    if ttt_is_full(board):
        return 0

    if is_maximizing:
        best = -float('inf')
        for i in range(9):
            if board[i] == '':
                board[i] = 'X'
                score = alpha_beta(board, False, alpha, beta, log, depth+1)
                board[i] = ''
                best = max(best, score)
                alpha = max(alpha, best)
                if log is not None:
                    log.append(f"{'  '*depth}[MAX] ô {i} score={score} α={alpha} β={beta}")
                if beta <= alpha:
                    if log is not None:
                        log.append(f"{'  '*depth}✂ Cắt tỉa beta tại ô {i}")
                    break
        return best
    else:
        best = float('inf')
        for i in range(9):
            if board[i] == '':
                board[i] = 'O'
                score = alpha_beta(board, True, alpha, beta, log, depth+1)
                board[i] = ''
                best = min(best, score)
                beta = min(beta, best)
                if log is not None:
                    log.append(f"{'  '*depth}[MIN] ô {i} score={score} α={alpha} β={beta}")
                if beta <= alpha:
                    if log is not None:
                        log.append(f"{'  '*depth}✂ Cắt tỉa alpha tại ô {i}")
                    break
        return best

def alpha_beta_best_move(board, log=None):
    best_score = -float('inf')
    best_move = None
    for i in range(9):
        if board[i] == '':
            board[i] = 'X'
            score = alpha_beta(board, False, -float('inf'), float('inf'), log, 1)
            board[i] = ''
            if log is not None:
                log.append(f"[ROOT] ô {i} → score={score}")
            if score > best_score:
                best_score = score
                best_move = i
    return best_move, best_score

# ─────────────────────────────────────────
#  EXPECTIMAX cho game xí ngầu
# ─────────────────────────────────────────

DICE_VALUES = [1, 2, 3, 4, 5, 6]
SAFE_SCORE = 2  # điểm nếu không quay xí ngầu

def expectimax_dice(current_total, rolls_left, memo=None):
    """
    Trả về giá trị kỳ vọng tối ưu.
    - current_total: điểm hiện tại
    - rolls_left: số lần quay còn lại
    """
    if memo is None:
        memo = {}
    key = (current_total, rolls_left)
    if key in memo:
        return memo[key]
    if rolls_left == 0:
        return current_total

    # Nút chance: kỳ vọng khi quay xí ngầu
    expected_if_roll = sum(
        expectimax_dice(current_total + d, rolls_left - 1, memo)
        for d in DICE_VALUES
    ) / len(DICE_VALUES)

    # Nút max: chọn giữa quay và dừng (nhận current_total)
    value = max(current_total, expected_if_roll)
    memo[key] = value
    return value


# ─────────────────────────────────────────
#  APP CHÍNH
# ─────────────────────────────────────────

PUZZLE_ALGOS = [
    "Breadth-First Search (BFS)",
    "Depth-First Search (DFS)",
    "Iterative Deepening Search (IDS)",
    "Uniform Cost Search (UCS)",
    "Greedy Search",
    "A* Search",
    "Simple Hill Climbing (SHC)",
    "Iterative Deepening A* (IDA*)",
    "Forward Checking Search",
    "Simulated Annealing",
    "AND-OR Search",
]
TTT_ALGOS = [
    "Minimax",
    "Alpha-Beta Pruning",
]
EXPECTIMAX_ALGO = "Expectimax (Xí Ngầu)"

ALL_ALGOS = PUZZLE_ALGOS + TTT_ALGOS + [EXPECTIMAX_ALGO]


class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle & Game Solver")
        self.root.geometry("900x550")
        self.root.resizable(False, False)

        self.mode = "puzzle"  # "puzzle", "ttt", "dice"

        # ── Puzzle state ──
        self.start_state = generate_random_start()
        self.current_state = self.start_state
        self.solution_path = []
        self.current_index = 0
        self.is_playing = False
        self.algo_details = {}
        self.search_logs = []
        self.csp_generator = None
        self.csp_history_states = []
        self.csp_history_logs = []
        self.search_ended = False

        # ── TicTacToe state ──
        self.ttt_board = [''] * 9
        self.ttt_algo = "Minimax"
        self.ttt_log = []
        self.player_turn = True  # True = người chơi (O), False = bot (X)
        self.ttt_game_over = False

        # ── Dice state ──
        self.dice_score = 0
        self.dice_rolls_left = 3
        self.dice_log = []

        self.create_widgets()
        self.update_board()

    # ══════════════════════════════════════
    #  WIDGET LAYOUT
    # ══════════════════════════════════════
    def create_widgets(self):
        self.left_frame = tk.Frame(self.root, width=500, height=550, padx=20, pady=20)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = tk.Frame(self.root, width=400, height=550, bg="#f0f0f0", padx=15, pady=20)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)

        # ── Top control ──
        control_frame = tk.Frame(self.left_frame)
        control_frame.pack(fill=tk.X, pady=10)

        tk.Label(control_frame, text="Thuật toán:", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
        self.algo_var = tk.StringVar()
        self.algo_menu = ttk.Combobox(control_frame, textvariable=self.algo_var, state="readonly", width=28)
        self.algo_menu['values'] = ALL_ALGOS
        self.algo_menu.current(0)
        self.algo_menu.pack(side=tk.LEFT, padx=5)
        self.algo_menu.bind("<<ComboboxSelected>>", self.on_algo_changed)

        self.btn_solve = tk.Button(control_frame, text="Giải", bg="#5FC862", fg="black",
                                   font=("Arial", 10, "bold"), command=self.solve_puzzle)
        self.btn_solve.pack(side=tk.LEFT, padx=10)

        self.btn_reset = tk.Button(control_frame, text="Reset", bg="#e46b63", fg="black",
                                   font=("Arial", 10, "bold"), command=self.reset_puzzle)
        self.btn_reset.pack(side=tk.LEFT, padx=5)

        # ── Dynamic board area ──
        self.board_container = tk.Frame(self.left_frame)
        self.board_container.pack(pady=10, fill=tk.BOTH, expand=True)

        # Puzzle board
        self.board_frame = tk.Frame(self.board_container, bg="gray", bd=2)
        self.cells = [[None]*3 for _ in range(3)]
        for i in range(3):
            for j in range(3):
                lbl = tk.Label(self.board_frame, text="", font=("Arial", 24, "bold"),
                               width=5, height=2, bd=1, relief="solid")
                lbl.grid(row=i, column=j, padx=3, pady=3)
                self.cells[i][j] = lbl
        self.board_frame.pack(pady=5)

        # Nav buttons (puzzle)
        self.nav_frame = tk.Frame(self.left_frame)
        self.nav_frame.pack(pady=10)

        self.btn_prev = tk.Button(self.nav_frame, text="Bước trước", font=("Arial", 10),
                                  width=12, state=tk.DISABLED, command=self.prev_step)
        self.btn_prev.pack(side=tk.LEFT, padx=5)

        self.btn_next = tk.Button(self.nav_frame, text="Bước tiếp theo", font=("Arial", 10),
                                  width=12, state=tk.DISABLED, command=self.next_step)
        self.btn_next.pack(side=tk.LEFT, padx=5)

        self.btn_auto = tk.Button(self.nav_frame, text="Tự chạy", font=("Arial", 10),
                                  bg="#67B1E6", fg="black", width=12, state=tk.DISABLED,
                                  command=self.toggle_auto)
        self.btn_auto.pack(side=tk.LEFT, padx=5)

        # TicTacToe board (hidden initially)
        self.ttt_frame = tk.Frame(self.board_container, bg="#dde")
        self.ttt_buttons = []
        for i in range(9):
            btn = tk.Button(self.ttt_frame, text="", font=("Arial", 28, "bold"),
                            width=4, height=2,
                            command=lambda idx=i: self.ttt_click(idx))
            btn.grid(row=i//3, column=i%3, padx=4, pady=4)
            self.ttt_buttons.append(btn)

        # Dice frame (hidden initially)
        self.dice_frame = tk.Frame(self.board_container, bg="#fff8e7")
        self._build_dice_ui()

        # Status
        self.status_var = tk.StringVar(value="Trạng thái: Sẵn sàng")
        lbl_status = tk.Label(self.left_frame, textvariable=self.status_var,
                              font=("Arial", 10, "italic"), fg="blue")
        lbl_status.pack(anchor="w", pady=2)

        # ── Right panel ──
        tk.Label(self.right_frame, text="THÔNG TIN CHI TIẾT",
                 font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=5)
        self.info_text = tk.Text(self.right_frame, font=("Courier New", 9),
                                 bg="white", bd=2, relief="sunken", wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True, pady=10)

    def append_log(self, msg):
        if self.info_text is not None:
            self.info_text.insert(tk.END, msg + "\n")
            self.info_text.see(tk.END)

    def _build_dice_ui(self):
        """Build the dice game UI inside self.dice_frame."""
        tk.Label(self.dice_frame, text="🎲 GAME XÍ NGẦU (Expectimax)", 
                 font=("Arial", 14, "bold"), bg="#fff8e7", fg="#b05000").pack(pady=8)

        score_frame = tk.Frame(self.dice_frame, bg="#fff8e7")
        score_frame.pack(pady=4)

        tk.Label(score_frame, text="Điểm hiện tại:", font=("Arial", 11), bg="#fff8e7").grid(row=0, column=0, padx=6)
        self.dice_score_var = tk.StringVar(value="0")
        tk.Label(score_frame, textvariable=self.dice_score_var,
                 font=("Arial", 20, "bold"), bg="#fff8e7", fg="#c00").grid(row=0, column=1, padx=6)

        tk.Label(score_frame, text="Lượt quay còn lại:", font=("Arial", 11), bg="#fff8e7").grid(row=1, column=0, padx=6)
        self.dice_rolls_var = tk.StringVar(value="3")
        tk.Label(score_frame, textvariable=self.dice_rolls_var,
                 font=("Arial", 20, "bold"), bg="#fff8e7", fg="#007").grid(row=1, column=1, padx=6)

        # Dice face display
        self.dice_face_var = tk.StringVar(value="⬜")
        tk.Label(self.dice_frame, textvariable=self.dice_face_var,
                 font=("Arial", 48), bg="#fff8e7").pack(pady=6)

        # Recommendation label
        self.dice_rec_var = tk.StringVar(value="")
        tk.Label(self.dice_frame, textvariable=self.dice_rec_var,
                 font=("Arial", 10, "italic"), bg="#fff8e7", fg="#555", wraplength=340).pack(pady=2)

        btn_frame = tk.Frame(self.dice_frame, bg="#fff8e7")
        btn_frame.pack(pady=8)

        self.btn_roll = tk.Button(btn_frame, text="🎲 Quay Xí Ngầu", font=("Arial", 11, "bold"),
                                  bg="#f0a000", fg="white", width=16, command=self.dice_roll)
        self.btn_roll.grid(row=0, column=0, padx=8, pady=4)

        self.btn_take = tk.Button(btn_frame, text="✋ Nhận 2 Điểm", font=("Arial", 11, "bold"),
                                  bg="#2a9d00", fg="white", width=16, command=self.dice_take)
        self.btn_take.grid(row=0, column=1, padx=8, pady=4)

        self.btn_dice_reset = tk.Button(self.dice_frame, text="Chơi lại", font=("Arial", 10),
                                        bg="#888", fg="white", command=self.dice_reset)
        self.btn_dice_reset.pack(pady=4)

    # ══════════════════════════════════════
    #  ALGO CHANGE HANDLER
    # ══════════════════════════════════════
    def on_algo_changed(self, event=None):
        algo = self.algo_var.get()
        if algo in TTT_ALGOS:
            self._switch_mode("ttt")
        elif algo == EXPECTIMAX_ALGO:
            self._switch_mode("dice")
        else:
            self._switch_mode("puzzle")

    def _switch_mode(self, mode):
        self.mode = mode
        # Hide all boards
        self.board_frame.pack_forget()
        self.nav_frame.pack_forget()
        self.ttt_frame.pack_forget()
        self.dice_frame.pack_forget()

        if mode == "puzzle":
            self.board_frame.pack(pady=5)
            self.nav_frame.pack(pady=10)
            self.btn_solve.config(text="Giải", state=tk.NORMAL)
            self.btn_reset.config(text="Reset")
            self.status_var.set("Trạng thái: Sẵn sàng (8 Puzzle)")
            self.info_text.delete("1.0", tk.END)

        elif mode == "ttt":
            self.ttt_frame.pack(pady=5)
            self.btn_solve.config(text="Bắt đầu mới", state=tk.NORMAL)
            self.btn_reset.config(text="Reset")
            algo = self.algo_var.get()
            self.ttt_algo = algo
            self.ttt_reset()

        elif mode == "dice":
            self.dice_frame.pack(pady=5, fill=tk.BOTH, expand=True)
            self.btn_solve.config(state=tk.DISABLED)
            self.btn_reset.config(text="Reset")
            self.dice_reset()

        elif mode == "puzzle":
            self.board_frame.pack(pady=5)
            self.nav_frame.pack(pady=10)
            self.btn_solve.config(text="Giải", state=tk.NORMAL)
            self.btn_reset.config(text="Reset")
            self.status_var.set("Trạng thái: Sẵn sàng (8 Puzzle)")
            self.info_text.delete("1.0", tk.END)
            self.reset_puzzle()

    # ══════════════════════════════════════
    #  PUZZLE MODE
    # ══════════════════════════════════════
    def update_board(self):
        algo = self.algo_var.get()
        if algo == "Forward Checking Search":
            assignment = self.csp_history_states[self.current_index] if self.csp_history_states else {}
            for i in range(3):
                for j in range(3):
                    val = self.current_state[i][j]
                    color = assignment.get((i, j))
                    bg = CSP_COLOR_MAP.get(color, "#dad6d6")
                    text_val = "" if val == 0 else str(val)
                    self.cells[i][j].config(text=text_val, bg=bg)
            return

        for i in range(3):
            for j in range(3):
                val = self.current_state[i][j]
                if val == 0:
                    self.cells[i][j].config(text="", bg="#C3C2C2")
                else:
                    self.cells[i][j].config(text=str(val), bg="#dad6d6")

    def reset_puzzle(self):
        if self.mode == "ttt":
            self.ttt_reset()
            return
        if self.mode == "dice":
            self.dice_reset()
            return
        if self.is_playing:
            self.toggle_auto()
        algo = self.algo_var.get()
        if algo == "Forward Checking Search":
            self.start_state = generate_csp_start()
            self.current_state = self.start_state
            variables = get_csp_variables()
            self.csp_generator = forward_checking_step_by_step(
                {}, {var: CSP_COLORS[:] for var in variables}, variables, 0
            )
            self.csp_history_states = [{}]
            self.csp_history_logs = ["Trạng thái ban đầu: Chưa tô màu."]
            self.current_index = 0
            self.solution_path = []
            self.algo_details = {}
            self.search_logs = []
            self.search_ended = False
            self.update_board()
            self.btn_prev.config(state=tk.DISABLED)
            self.btn_next.config(state=tk.NORMAL)
            self.btn_auto.config(state=tk.DISABLED, text="Tự chạy")
            self.status_var.set("Trạng thái: Reset CSP Forward Checking. Nhấn 'Bước tiếp' để xem.")
            self.info_text.delete("1.0", tk.END)
            self.info_text.insert(tk.END, self.csp_history_logs[0] + "\n")
            return
        self.start_state = generate_random_start()
        self.current_state = self.start_state
        self.solution_path = []
        self.current_index = 0
        self.algo_details = {}
        self.search_logs = []
        self.csp_generator = None
        self.csp_history_states = []
        self.csp_history_logs = []
        self.search_ended = False
        self.update_board()
        self.btn_prev.config(state=tk.DISABLED)
        self.btn_next.config(state=tk.DISABLED)
        self.btn_auto.config(state=tk.DISABLED, text="Tự chạy")
        self.status_var.set("Trạng thái: Đã reset ma trận ngẫu nhiên.")
        self.info_text.delete("1.0", tk.END)

    def solve_puzzle(self):
        algo = self.algo_var.get()
        if algo in TTT_ALGOS:
            self.ttt_reset()
            return
        if algo == EXPECTIMAX_ALGO:
            return

        if self.is_playing:
            self.toggle_auto()

        self.status_var.set("Trạng thái: Đang tính toán...")
        self.root.update()

        start_time = time.time()
        path = None
        cost = None
        search_result = None

        if algo == "Breadth-First Search (BFS)":
            path = breadth_first_search(self.start_state, goal)
        elif algo == "Depth-First Search (DFS)":
            path = depth_first_search(self.start_state, goal)
        elif algo == "Iterative Deepening Search (IDS)":
            path = iterative_deepening_search(self.start_state, goal)
            if path == "failure":
                path = None
        elif algo == "Uniform Cost Search (UCS)":
            path, cost = uniform_cost_search(self.start_state, goal)
            if cost == float('inf'):
                path = None
        elif algo == "Greedy Search":
            path = greedy_search(self.start_state, goal)
        elif algo == "A* Search":
            path = a_star(self.start_state, goal)
        elif algo == "Simple Hill Climbing (SHC)":
            search_result = simple_hill_climbing(self.start_state, goal)
            path = search_result["path"]
        elif algo == "Iterative Deepening A* (IDA*)":
            path = ida_star(self.start_state)
        elif algo == "Simulated Annealing":
            path, logs, sa_info, best_state = simulated_annealing(self.start_state)
            self.search_logs = logs
            self.algo_details = {
                "algo": algo,
                "duration": time.time() - start_time,
                "steps": len(path) - 1,
                "iterations": sa_info["iterations"],
                "accepted_moves": sa_info["accepted_moves"],
                "worse_accepted": sa_info["worse_accepted"],
                "best_h": sa_info["best_h"],
                "final_h": sa_info["final_h"],
                "found_goal": sa_info["found_goal"],
                "final_temperature": sa_info["final_temperature"],
                "best_state": best_state,
            }
        elif algo == "AND-OR Search":
            path, logs, ao_info = and_or_search(self.start_state)
            self.search_logs = logs
            self.algo_details = {
                "algo": algo,
                "duration": time.time() - start_time,
                "steps": len(path) - 1,
                "iterations": ao_info["iterations"],
                "found_goal": ao_info["found_goal"],
                "max_depth_reached": ao_info["max_depth_reached"],
            }
        elif algo == "Forward Checking Search":
            if self.csp_generator is None:
                self.reset_puzzle()
            self.next_step()
            return

        end_time = time.time()
        duration = end_time - start_time
        duration = end_time - start_time

        if path is None:
            self.status_var.set("Trạng thái: Không tìm thấy lời giải.")
            messagebox.showerror("Lỗi", "Không thể tìm thấy lời giải!")
            return

        self.solution_path = path
        self.current_index = 0
        self.current_state = self.solution_path[0]
        self.update_board()

        if algo in ("Simulated Annealing", "AND-OR Search"):
            self.algo_details = self.algo_details
        else:
            self.algo_details = {
                "algo": algo,
                "duration": duration,
                "steps": len(path) - 1,
                "total_cost": cost,
                "status": search_result["status"] if search_result else None,
                "stuck_state": search_result["stuck_state"] if search_result else None,
                "stuck_value": search_result["stuck_value"] if search_result else None,
            }

        self.btn_prev.config(state=tk.DISABLED)
        if len(path) > 1:
            self.btn_next.config(state=tk.NORMAL)
            self.btn_auto.config(state=tk.NORMAL)
        else:
            self.btn_next.config(state=tk.DISABLED)
            self.btn_auto.config(state=tk.DISABLED)

        if algo == "Simple Hill Climbing (SHC)":
            if self.algo_details["status"] == "goal":
                self.status_var.set("Trạng thái: Đã giải xong bằng SHC.")
            else:
                self.status_var.set("Trạng thái: SHC dừng ở cực trị cục bộ.")
        elif algo == "Simulated Annealing":
            self.status_var.set("Trạng thái: Simulated Annealing đã chạy xong.")
        elif algo == "AND-OR Search":
            self.status_var.set("Trạng thái: AND-OR Search hoàn thành.")
        else:
            self.status_var.set(f"Trạng thái: Đã giải xong bằng {algo.split(' (')[0]}.")
        self.display_info()

    def display_info(self):
        self.info_text.delete("1.0", tk.END)
        if not self.algo_details:
            return
        algo = self.algo_details["algo"]
        duration = self.algo_details["duration"]
        steps = self.algo_details["steps"]
        text = f"THUẬT TOÁN: {algo}\n"
        text += f"Thời gian giải: {duration:.4f} giây\n"
        text += f"Tổng số bước di chuyển: {steps}\n"
        if algo == "Uniform Cost Search (UCS)":
            text += f"Tổng chi phí đường đi: {self.algo_details['total_cost']:.1f}\n"
            text += "Chi phí bước đi:\n  Lên:1.0 Xuống:1.5 Trái:1.2 Phải:0.8\n"
        if algo == "Simple Hill Climbing (SHC)":
            st = self.algo_details.get("status")
            text += f"Trạng thái: {'tìm được lời giải' if st=='goal' else 'cực trị cục bộ'}\n"
        text += "=" * 35 + "\n"

        text += "\nCÁC HƯỚNG ĐI CÓ THỂ:\n"
        candidate_lines = []
        for action in actions(self.current_state):
            ch = child_node(self.current_state, action)
            direction = direction_from_action(action)
            if algo == "Greedy Search":
                candidate_lines.append((manhattan(ch), f"- {direction}: h={manhattan(ch)}"))
            elif algo == "Simple Hill Climbing (SHC)":
                candidate_lines.append((misplaced_tiles(ch), f"- {direction}: h={misplaced_tiles(ch)}"))
            elif algo == "Uniform Cost Search (UCS)":
                candidate_lines.append((len(candidate_lines), f"- {direction}: cost={step_cost(self.current_state, action):.1f}"))
            elif algo == "A* Search":
                g_c = inversion_count(ch); h_c = manhattan(ch)
                candidate_lines.append((g_c+h_c, f"- {direction}: g={g_c} h={h_c} f={g_c+h_c}"))
            elif algo == "Iterative Deepening A* (IDA*)":
                g_c = self.current_index + 1; h_c = manhattan(ch)
                candidate_lines.append((g_c+h_c, f"- {direction}: g={g_c} h={h_c} f={g_c+h_c}"))
            else:
                candidate_lines.append((len(candidate_lines), f"- {direction}"))

        if algo in ("Greedy Search","A* Search","Simple Hill Climbing (SHC)","Iterative Deepening A* (IDA*)"):
            candidate_lines.sort(key=lambda x: x[0])
        for _, line in candidate_lines:
            text += f"{line}\n"

        text += "\nHƯỚNG TIẾP THEO:\n"
        if algo == "Forward Checking Search":
            if self.current_index < len(self.csp_history_states) - 1:
                text += f"- Bước {self.current_index + 1} / {len(self.csp_history_states)-1}\n"
                text += f"- Văn bản hiện tại: {self.csp_history_logs[self.current_index]}\n"
            else:
                text += "- Đã hoàn thành bước kiểm tra trước\n"
        elif self.current_index < len(self.solution_path) - 1:
            next_state = self.solution_path[self.current_index + 1]
            next_direction = zero_move_direction(self.current_state, next_state)
            text += f"- {next_direction}\n"
            x1,y1 = find_zero(self.current_state)
            x2,y2 = find_zero(next_state)
            next_action = (x2-x1, y2-y1)
            if algo == "Uniform Cost Search (UCS)":
                text += f"- cost = {step_cost(self.current_state, next_action):.1f}\n"
            if algo == "Greedy Search":
                text += f"- h(n) chọn: {manhattan(next_state)}\n"
            if algo == "Simple Hill Climbing (SHC)":
                text += f"- h(n) chọn: {misplaced_tiles(next_state)}\n"
            if algo in ("A* Search",):
                g_n = inversion_count(next_state); h_n = manhattan(next_state)
                text += f"- g={g_n} h={h_n} f={g_n+h_n}\n"
            if algo == "Iterative Deepening A* (IDA*)":
                g_n = self.current_index+1; h_n = manhattan(next_state)
                text += f"- g={g_n} h={h_n} f={g_n+h_n}\n"
        else:
            text += "- Đã tới đích\n"

        text += "\n" + "-" * 35 + "\n"
        text += "ĐẶC TRƯNG THUẬT TOÁN:\n"
        if algo == "Breadth-First Search (BFS)":
            text += "- Tìm kiếm theo từng tầng.\n- Tối ưu về số bước (cạnh)."
        elif algo == "Depth-First Search (DFS)":
            text += "- Đi sâu một nhánh duy nhất.\n- Không tối ưu, đường dài."
        elif algo == "Iterative Deepening Search (IDS)":
            text += f"- Lặp DLS tăng dần độ sâu.\n- Độ sâu hiện tại >= {self.current_index}.\n- Tiết kiệm bộ nhớ, tối ưu bước."
        elif algo == "Uniform Cost Search (UCS)":
            current_cost = sum(
                step_cost(self.solution_path[k],
                    (find_zero(self.solution_path[k+1])[0]-find_zero(self.solution_path[k])[0],
                     find_zero(self.solution_path[k+1])[1]-find_zero(self.solution_path[k])[1]))
                for k in range(self.current_index)
            ) if self.current_index > 0 else 0.0
            text += f"- Mở rộng nút chi phí thấp nhất.\n- Chi phí tích lũy: {current_cost:.1f}\n- Tối ưu về tổng chi phí."
        elif algo == "Greedy Search":
            text += "- Chọn h(n) nhỏ nhất.\n- Nhanh nhưng không tối ưu."
        elif algo == "A* Search":
            g = inversion_count(self.current_state); h = manhattan(self.current_state)
            text += f"- Kết hợp g(n)+h(n).\n- Tối ưu nếu h admissible.\n- g={g}, h={h}, f={g+h}"
        elif algo == "Simple Hill Climbing (SHC)":
            text += "- Heuristic: số ô sai vị trí.\n- Chọn láng giềng đầu tiên tốt hơn.\n- Có thể bị kẹt cực trị."
        elif algo == "Iterative Deepening A* (IDA*)":
            g = self.current_index; h = manhattan(self.current_state)
            text += f"- Duyệt sâu theo ngưỡng f.\n- Tiết kiệm bộ nhớ hơn A*.\n- g={g}, h={h}, f={g+h}"
        elif algo == "Simulated Annealing":
            text += "- Thuật toán xác suất, có thể chấp nhận bước xấu.\n- Tìm kiếm theo nhiệt độ giảm dần.\n- Không đảm bảo tìm ra đích nhưng cải thiện dần."
        elif algo == "AND-OR Search":
            text += "- Duyệt máy OR/AND trong môi trường bất định.\n- Mỗi hành động OR phải chịu được mọi kịch bản AND.\n- Có thể dừng khi đạt giới hạn độ sâu." 
        elif algo == "Forward Checking Search":
            text += "- CSP Coloring với Forward Checking.\n- Giữ nguyên miền giá trị và cắt tỉa các màu không hợp lệ.\n- Hiển thị quá trình tìm kiếm từng bước."

        self.info_text.insert(tk.END, text)

    def next_step(self):
        algo = self.algo_var.get()
        if algo == "Forward Checking Search":
            if self.current_index < len(self.csp_history_states) - 1:
                self.current_index += 1
                self.update_board()
                self.display_info()
                self.btn_prev.config(state=tk.NORMAL)
                if self.current_index == len(self.csp_history_states) - 1:
                    self.btn_next.config(state=tk.DISABLED)
                return

            if not self.search_ended and self.csp_generator is not None:
                try:
                    next_assignment, log_msg = next(self.csp_generator)
                    self.csp_history_states.append(next_assignment)
                    self.csp_history_logs.append(log_msg)
                    self.current_index += 1
                    self.append_log(f"Bước {self.current_index}: {log_msg}")
                    if "hoàn chỉnh" in log_msg.lower():
                        self.search_ended = True
                        self.status_var.set("Trạng thái: Đã tìm ra lời giải Forward Checking!")
                    self.update_board()
                    self.display_info()
                    self.btn_prev.config(state=tk.NORMAL)
                    return
                except StopIteration:
                    self.search_ended = True
                    self.btn_next.config(state=tk.DISABLED)
                    messagebox.showinfo("Thông báo", "Forward Checking đã duyệt xong toàn bộ bước.")
                    return
            return

        if self.current_index < len(self.solution_path) - 1:
            self.current_index += 1
            self.current_state = self.solution_path[self.current_index]
            self.update_board()
            self.display_info()
            self.btn_prev.config(state=tk.NORMAL)
            if self.current_index == len(self.solution_path) - 1:
                self.btn_next.config(state=tk.DISABLED)
                if self.is_playing:
                    self.toggle_auto()

    def prev_step(self):
        algo = self.algo_var.get()
        if algo == "Forward Checking Search":
            if self.current_index > 0:
                self.current_index -= 1
                self.update_board()
                self.display_info()
                self.btn_next.config(state=tk.NORMAL)
                if self.current_index == 0:
                    self.btn_prev.config(state=tk.DISABLED)
            return

        if self.current_index > 0:
            self.current_index -= 1
            self.current_state = self.solution_path[self.current_index]
            self.update_board()
            self.display_info()
            self.btn_next.config(state=tk.NORMAL)
            if self.current_index == 0:
                self.btn_prev.config(state=tk.DISABLED)

    def toggle_auto(self):
        if self.is_playing:
            self.is_playing = False
            self.btn_auto.config(text="Tự chạy")
        else:
            if self.current_index == len(self.solution_path) - 1:
                self.current_index = 0
                self.current_state = self.solution_path[0]
                self.update_board()
                self.display_info()
            self.is_playing = True
            self.btn_auto.config(text="Dừng")
            self.auto_run()

    def auto_run(self):
        if self.is_playing:
            if self.current_index < len(self.solution_path) - 1:
                self.next_step()
                self.root.after(600, self.auto_run)
            else:
                self.is_playing = False
                self.btn_auto.config(text="Tự chạy")

    # ══════════════════════════════════════
    #  TIC-TAC-TOE MODE
    # ══════════════════════════════════════
    def ttt_reset(self):
        self.ttt_board = [''] * 9
        self.ttt_log = []
        self.ttt_game_over = False
        self.player_turn = True  # người chơi = O, đi trước
        algo = self.algo_var.get()
        self.ttt_algo = algo if algo in TTT_ALGOS else "Minimax"

        for btn in self.ttt_buttons:
            btn.config(text="", state=tk.NORMAL, bg="#dde", fg="black",
                       font=("Arial", 28, "bold"))

        self.status_var.set(f"Cờ Caro 3×3 — Bot: X ({self.ttt_algo}) | Bạn: O — Lượt của bạn!")
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert(tk.END,
            f"THUẬT TOÁN: {self.ttt_algo}\n"
            "Bot đánh X, Người chơi đánh O.\n"
            "Người chơi đi trước.\n"
            "=" * 30 + "\n"
        )

    def ttt_click(self, idx):
        if self.ttt_game_over:
            return
        if not self.player_turn:
            return
        if self.ttt_board[idx] != '':
            return

        # Người chơi đánh O
        self.ttt_board[idx] = 'O'
        self.ttt_buttons[idx].config(text='O', fg="#c00", state=tk.DISABLED, bg="#ffe0e0")
        self.ttt_log.append(f"[Người chơi] đánh ô {idx}")

        if self._ttt_check_end():
            return

        self.player_turn = False
        self.status_var.set("Bot đang suy nghĩ...")
        self.root.update()
        self.root.after(300, self._bot_move)

    def _bot_move(self):
        log = []
        if self.ttt_algo == "Minimax":
            move, score = minimax_best_move(self.ttt_board, log)
        else:
            move, score = alpha_beta_best_move(self.ttt_board, log)

        if move is not None:
            self.ttt_board[move] = 'X'
            self.ttt_buttons[move].config(text='X', fg="#006", state=tk.DISABLED, bg="#e0e0ff")
            self.ttt_log.append(f"[Bot {self.ttt_algo}] đánh ô {move} (score={score})")

        self._display_ttt_info(log)

        if self._ttt_check_end():
            return
        self.player_turn = True
        self.status_var.set("Lượt của bạn (O)!")

    def _ttt_check_end(self):
        winner = ttt_check_winner(self.ttt_board)
        if winner:
            self.ttt_game_over = True
            for btn in self.ttt_buttons:
                btn.config(state=tk.DISABLED)
            if winner == 'X':
                self.status_var.set("🤖 Bot (X) thắng! Nhấn 'Bắt đầu mới' để chơi lại.")
                messagebox.showinfo("Kết quả", "Bot (X) thắng! 🤖")
            else:
                self.status_var.set("🎉 Bạn (O) thắng! Nhấn 'Bắt đầu mới' để chơi lại.")
                messagebox.showinfo("Kết quả", "Bạn (O) thắng! 🎉")
            return True
        if ttt_is_full(self.ttt_board):
            self.ttt_game_over = True
            for btn in self.ttt_buttons:
                btn.config(state=tk.DISABLED)
            self.status_var.set("Hòa! Nhấn 'Bắt đầu mới' để chơi lại.")
            messagebox.showinfo("Kết quả", "Hòa! 🤝")
            return True
        return False

    def _display_ttt_info(self, move_log):
        self.info_text.delete("1.0", tk.END)
        algo = self.ttt_algo
        text = f"THUẬT TOÁN: {algo}\n"
        text += "Bot=X  |  Người=O\n"
        text += "=" * 30 + "\n"

        text += "\nLỊCH SỬ NƯỚC ĐI:\n"
        for entry in self.ttt_log:
            text += f"  {entry}\n"

        text += f"\nBÀN CỜ HIỆN TẠI:\n"
        symbols = {'' : '.', 'X': 'X', 'O': 'O'}
        for row in range(3):
            row_str = "  "
            for col in range(3):
                row_str += symbols[self.ttt_board[row*3+col]] + " "
            text += row_str + "\n"

        if move_log:
            text += f"\nPHÂN TÍCH {algo.upper()} (tóm tắt):\n"
            shown = move_log[:20]
            for line in shown:
                text += f"  {line}\n"
            if len(move_log) > 20:
                text += f"  ... ({len(move_log)-20} dòng nữa)\n"

        if algo == "Minimax":
            text += "\nĐẶC TRƯNG:\n"
            text += "- Duyệt toàn bộ cây game.\n"
            text += "- MAX = Bot (X), MIN = Người (O).\n"
            text += "- Đảm bảo nước đi tối ưu.\n"
            text += "- Phức tạp O(b^d) ≈ 9! nước.\n"
        else:
            text += "\nĐẶC TRƯNG:\n"
            text += "- Alpha-Beta cắt tỉa cây.\n"
            text += "- α: ngưỡng MAX, β: ngưỡng MIN.\n"
            text += "- Bỏ qua nhánh không ảnh hưởng.\n"
            text += "- Nhanh hơn Minimax ~2×.\n"

        self.info_text.insert(tk.END, text)

    # ══════════════════════════════════════
    #  DICE / EXPECTIMAX MODE
    # ══════════════════════════════════════
    def dice_reset(self):
        self.dice_score = 0
        self.dice_rolls_left = 3
        self.dice_log = []
        self.dice_score_var.set("0")
        self.dice_rolls_var.set("3")
        self.dice_face_var.set("⬜")
        self.dice_rec_var.set("Chọn: Quay xí ngầu hoặc nhận 2 điểm an toàn.")
        self.btn_roll.config(state=tk.NORMAL)
        self.btn_take.config(state=tk.NORMAL)
        self.status_var.set("Expectimax — Trò chơi xí ngầu")
        self._update_dice_info()

    DICE_FACES = {1:"⚀", 2:"⚁", 3:"⚂", 4:"⚃", 5:"⚄", 6:"⚅"}

    def dice_roll(self):
        if self.dice_rolls_left <= 0:
            return
        result = random.randint(1, 6)
        self.dice_score += result
        self.dice_rolls_left -= 1
        self.dice_score_var.set(str(self.dice_score))
        self.dice_rolls_var.set(str(self.dice_rolls_left))
        self.dice_face_var.set(self.DICE_FACES[result])
        self.dice_log.append(f"🎲 Quay → {result} (tổng: {self.dice_score})")

        if self.dice_rolls_left == 0:
            self.btn_roll.config(state=tk.DISABLED)
            self.btn_take.config(state=tk.DISABLED)
            self.status_var.set(f"Hết lượt! Tổng điểm: {self.dice_score}")
            self.dice_rec_var.set(f"Kết thúc! Điểm cuối: {self.dice_score}")
        else:
            # Tính expectimax
            ev_roll = expectimax_dice(self.dice_score, self.dice_rolls_left)
            ev_stop = self.dice_score
            rec = f"EV nếu quay tiếp: {ev_roll:.2f} | Nếu dừng: {ev_stop} → "
            if ev_roll > ev_stop + 0.01:
                rec += "📈 Nên QUAY tiếp"
            else:
                rec += "🛑 Nên DỪNG"
            self.dice_rec_var.set(rec)
            self.dice_log.append(f"   Expectimax: EV_roll={ev_roll:.2f}, EV_stop={ev_stop}")
        self._update_dice_info()

    def dice_take(self):
        ev_roll = expectimax_dice(self.dice_score, self.dice_rolls_left)
        self.dice_log.append(f"✋ Nhận 2 điểm an toàn (+2, tổng: {self.dice_score+2})")
        self.dice_log.append(f"   Expectimax: EV_roll={ev_roll:.2f}, EV_dừng={self.dice_score}")
        self.dice_score += 2
        self.dice_score_var.set(str(self.dice_score))
        self.btn_roll.config(state=tk.DISABLED)
        self.btn_take.config(state=tk.DISABLED)
        note = "tốt hơn" if self.dice_score >= ev_roll else f"EV quay={ev_roll:.2f} tốt hơn"
        self.dice_rec_var.set(f"Đã dừng! Điểm: {self.dice_score}. So với EV quay: {note}")
        self.status_var.set(f"Đã nhận 2 điểm. Tổng: {self.dice_score}")
        self._update_dice_info()

    def _update_dice_info(self):
        self.info_text.delete("1.0", tk.END)
        text = "THUẬT TOÁN: Expectimax\n"
        text += "=" * 32 + "\n"
        text += "\nMÔ TẢ:\n"
        text += "- Mỗi lượt: quay xí ngầu (1-6)\n"
        text += "  hoặc nhận 2 điểm an toàn.\n"
        text += "- Expectimax tính giá trị kỳ vọng\n"
        text += "  (Expected Value) để gợi ý.\n"
        text += f"- Điểm hiện tại: {self.dice_score}\n"
        text += f"- Lượt còn lại: {self.dice_rolls_left}\n"

        if self.dice_rolls_left > 0 and self.dice_score >= 0:
            memo = {}
            ev = expectimax_dice(self.dice_score, self.dice_rolls_left, memo)
            text += f"\nEXPECTIMAX ANALYSIS:\n"
            text += f"- EV tối ưu từ đây: {ev:.2f}\n"
            text += f"- Nếu dừng ngay: {self.dice_score}\n"
            text += f"- EV/lượt trung bình: {sum(DICE_VALUES)/len(DICE_VALUES):.1f}\n"
            text += "\nLỰA CHỌN THEO EV:\n"
            for rl in range(self.dice_rolls_left, 0, -1):
                ev_r = expectimax_dice(self.dice_score, rl, memo)
                text += f"  {rl} lượt còn lại: EV={ev_r:.2f}\n"

        if self.dice_log:
            text += "\nLỊCH SỬ:\n"
            for entry in self.dice_log[-12:]:
                text += f"  {entry}\n"

        text += "\n" + "-" * 32 + "\n"
        text += "Công thức:\n"
        text += " V(s,r) = max(score,\n"
        text += "   avg_d[V(score+d, r-1)])\n"
        self.info_text.insert(tk.END, text)


def main():
    root = tk.Tk()
    app = PuzzleApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()