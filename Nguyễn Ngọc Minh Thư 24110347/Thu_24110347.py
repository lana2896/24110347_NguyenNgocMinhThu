import heapq
from collections import deque
import random
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import time

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
    new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
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

def manhattan(state):
    goal_pos = {
        1: (0, 0), 2: (0, 1), 3: (0, 2),
        8: (1, 0), 0: (1, 1), 4: (1, 2),
        7: (2, 0), 6: (2, 1), 5: (2, 2)
    }
    total = 0
    for i in range(3):
        for j in range(3):
            val = state[i][j]
            if val != 0:
                gi, gj = goal_pos[val]
                total += abs(i - gi) + abs(j - gj)
    return total

def inversion_count(state):
    arr = [v for row in state for v in row if v != 0]
    inv = 0
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):
            if arr[i] > arr[j]:
                inv += 1
    return inv

def misplaced_tiles(state):
    total = 0
    for i in range(3):
        for j in range(3):
            val = state[i][j]
            if val != 0 and val != goal[i][j]:
                total += 1
    return total

def is_solvable(start, goal_state):
    return inversion_count(start) % 2 == inversion_count(goal_state) % 2

def a_star(start, goal):
    start_g = inversion_count(start)
    start_h = manhattan(start)
    start_f = start_g + start_h

    frontier = []
    heapq.heappush(frontier, (start_f, start_g, start_h, start))
    best_f = {start: start_f}
    parent = {start: None}

    while frontier:
        f, g, h, state = heapq.heappop(frontier)
        if state == goal:
            path = []
            cur = state
            while cur is not None:
                path.append(cur)
                cur = parent[cur]
            return path[::-1]
        for action in actions(state):
            child = child_node(state, action)
            g_c = inversion_count(child)
            h_c = manhattan(child)
            f_c = g_c + h_c
            if f_c < best_f.get(child, float('inf')):
                best_f[child] = f_c
                parent[child] = state
                heapq.heappush(frontier, (f_c, g_c, h_c, child))
    return None

def simple_hill_climbing(start, goal_state):
    path = [start]
    visited = {start}
    current_state = start

    while current_state != goal_state:
        current_value = misplaced_tiles(current_state)
        best_child = None

        for action in actions(current_state):
            child = child_node(current_state, action)
            if child in visited:
                continue

            child_value = misplaced_tiles(child)
            if child_value < current_value:
                best_child = child
                break

        if best_child is None:
            return {
                "path": path,
                "status": "local_maxima",
                "stuck_state": current_state,
                "stuck_value": current_value,
            }

        path.append(best_child)
        visited.add(best_child)
        current_state = best_child

    return {
        "path": path,
        "status": "goal",
        "stuck_state": None,
        "stuck_value": None,
    }

def ida_dfs(path, g, threshold):
    node = path[-1]
    f = g + manhattan(node)

    if f > threshold:
        return f

    if node == goal:
        return "FOUND"

    min_threshold = float('inf')

    for action in actions(node):
        child = child_node(node, action)
        if child in path:
            continue

        path.append(child)
        result = ida_dfs(path, g + 1, threshold)

        if result == "FOUND":
            return "FOUND"

        min_threshold = min(min_threshold, result)
        path.pop()

    return min_threshold

def ida_star(start):
    if start == goal:
        return [start]

    if not is_solvable(start, goal):
        return None

    threshold = manhattan(start)
    path = [start]

    while True:
        result = ida_dfs(path, 0, threshold)

        if result == "FOUND":
            return path.copy()

        if result == float('inf'):
            return None

        threshold = result

def zero_move_direction(curr_state, next_state):
    x1, y1 = find_zero(curr_state)
    x2, y2 = find_zero(next_state)
    dx, dy = x2 - x1, y2 - y1

    if dx == -1:
        return "Lên"
    if dx == 1:
        return "Xuống"
    if dy == -1:
        return "Trái"
    if dy == 1:
        return "Phải"
    return "Không đổi"

def direction_from_action(action):
    dx, dy = action
    if dx == -1:
        return "Lên"
    if dx == 1:
        return "Xuống"
    if dy == -1:
        return "Trái"
    if dy == 1:
        return "Phải"
    return "Không đổi"

def greedy_search(start, goal):
    if start == goal:
        return [start]

    frontier = [start]
    reached = set()
    parent = {start: None}

    while frontier:
        current = min(frontier, key=manhattan)

        if current == goal:
            path = []
            while current is not None:
                path.append(current)
                current = parent[current]
            return path[::-1]

        frontier.remove(current)
        reached.add(current)

        for action in actions(current):
            child = child_node(current, action)
            if child not in reached and child not in frontier:
                parent[child] = current
                frontier.append(child)

    return None

def depth_first_search(start, goal):
    if start == goal:
        return [start]
    frontier = [start]
    frontier_set = {start}
    parent_map = {start: None}
    explored = set()
    while frontier:
        state = frontier.pop()
        frontier_set.remove(state)
        explored.add(state)
        if state == goal:
            path = []
            curr = state
            while curr is not None:
                path.append(curr)
                curr = parent_map[curr]
            return path[::-1]
        for action in actions(state):
            child = child_node(state, action)
            if child not in explored and child not in frontier_set:
                parent_map[child] = state
                frontier.append(child)
                frontier_set.add(child)
    return None


def depth_limited_search(state, goal, limit, path):
    if state == goal:
        return path
    if limit == 0:
        return "cutoff"
    cutoff_occurred = False
    for action in actions(state):
        child = child_node(state, action)
        if child not in path:
            result = depth_limited_search(child, goal, limit - 1, path + [child])
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
            return "failure"
        return result
    return "failure"

def breadth_first_search(start, goal):
    if start == goal:
        return [start]
    frontier = deque()
    frontier.append((start, []))
    frontier_set = {start}
    explored = set()
    while frontier:
        state, path = frontier.popleft()
        explored.add(state)
        if state == goal:
            return path + [state]
        for action in actions(state):
            child = child_node(state, action)
            in_frontier = child in frontier_set
            if child not in explored and not in_frontier:
                if child == goal:
                    return path + [state, child]
                frontier.append((child, path + [state]))
                frontier_set.add(child)
    return None

def step_cost(state, action):
    if action == (-1, 0):
        return 1.0
    if action == (1, 0):
        return 1.5
    if action == (0, -1):
        return 1.2
    if action == (0, 1):
        return 0.8
    return 1.0

def uniform_cost_search(start, goal):
    if start == goal:
        return [start], 0.0
    frontier = []
    heapq.heappush(frontier, (0.0, start, [start]))
    best_cost = {start: 0.0}
    while frontier:
        cost, state, path = heapq.heappop(frontier)
        if cost > best_cost.get(state, float('inf')):
            continue
        if state == goal:
            return path, cost
        for action in actions(state):
            child = child_node(state, action)
            new_cost = cost + step_cost(state, action)
            if new_cost < best_cost.get(child, float('inf')):
                best_cost[child] = new_cost
                heapq.heappush(frontier, (new_cost, child, path + [child]))
    return None, float('inf')

class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8 Puzzle Solver")
        self.root.geometry("900x550")
        self.root.resizable(False, False)
        
        self.start_state = generate_random_start()
        self.current_state = self.start_state
        self.solution_path = []
        self.current_index = 0
        self.is_playing = False
        self.algo_details = {}
        self.greedy_details = {}
        
        self.create_widgets()
        self.update_board()

    def create_widgets(self):
        left_frame = tk.Frame(self.root, width=500, height=550, padx=20, pady=20)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_frame = tk.Frame(self.root, width=400, height=550, bg="#f0f0f0", padx=15, pady=20)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
        
        control_frame = tk.Frame(left_frame)
        control_frame.pack(fill=tk.X, pady=10)

        tk.Label(control_frame, text="Thuật toán:", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
        self.algo_var = tk.StringVar()
        self.algo_menu = ttk.Combobox(control_frame, textvariable=self.algo_var, state="readonly", width=25)
        self.algo_menu['values'] = (
            "Breadth-First Search (BFS)",
            "Depth-First Search (DFS)",
            "Iterative Deepening Search (IDS)",
            "Uniform Cost Search (UCS)",
            "Greedy Search",
            "A* Search",
            "Simple Hill Climbing (SHC)",
            "Iterative Deepening A* (IDA*)",
        )
        self.algo_menu.current(0)
        self.algo_menu.pack(side=tk.LEFT, padx=5)
        
        self.btn_solve = tk.Button(control_frame, text="Giải", bg="#87C589", fg="white", font=("Arial", 10, "bold"), command=self.solve_puzzle)
        self.btn_solve.pack(side=tk.LEFT, padx=10)
        
        self.btn_reset = tk.Button(control_frame, text="Reset", bg="#db8a84", fg="white", font=("Arial", 10, "bold"), command=self.reset_puzzle)
        self.btn_reset.pack(side=tk.LEFT, padx=5)
        
        self.board_frame = tk.Frame(left_frame, bg="gray", bd=2)
        self.board_frame.pack(pady=20)
        
        self.cells = [[None for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                lbl = tk.Label(self.board_frame, text="", font=("Arial", 24, "bold"), width=5, height=2, bd=1, relief="solid")
                lbl.grid(row=i, column=j, padx=3, pady=3)
                self.cells[i][j] = lbl
                
        nav_frame = tk.Frame(left_frame)
        nav_frame.pack(pady=10)
        
        self.btn_prev = tk.Button(nav_frame, text="Bước trước", font=("Arial", 10), width=12, state=tk.DISABLED, command=self.prev_step)
        self.btn_prev.pack(side=tk.LEFT, padx=5)
        
        self.btn_next = tk.Button(nav_frame, text="Bước tiếp theo", font=("Arial", 10), width=12, state=tk.DISABLED, command=self.next_step)
        self.btn_next.pack(side=tk.LEFT, padx=5)
        
        self.btn_auto = tk.Button(nav_frame, text="Tự chạy", font=("Arial", 10), bg="#B9D6EB", fg="white", width=12, state=tk.DISABLED, command=self.toggle_auto)
        self.btn_auto.pack(side=tk.LEFT, padx=5)
        
        tk.Label(right_frame, text="THÔNG TIN CHI TIẾT", font=("Arial", 14, "bold"), bg="#f0f0f0").pack(pady=5)
        
        self.info_text = tk.Text(right_frame, font=("Courier New", 10), bg="white", bd=2, relief="sunken", wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.status_var = tk.StringVar(value="Trạng thái: Sẵn sàng")
        lbl_status = tk.Label(left_frame, textvariable=self.status_var, font=("Arial", 10, "italic"), fg="blue")
        lbl_status.pack(anchor="w", pady=5)

    def update_board(self):
        for i in range(3):
            for j in range(3):
                val = self.current_state[i][j]
                if val == 0:
                    self.cells[i][j].config(text="", bg="#C3C2C2")
                else:
                    self.cells[i][j].config(text=str(val), bg="#dad6d6")

    def reset_puzzle(self):
        if self.is_playing:
            self.toggle_auto()
        self.start_state = generate_random_start()
        self.current_state = self.start_state
        self.solution_path = []
        self.current_index = 0
        self.algo_details = {}
        self.greedy_details = {}
        self.update_board()
        self.btn_prev.config(state=tk.DISABLED)
        self.btn_next.config(state=tk.DISABLED)
        self.btn_auto.config(state=tk.DISABLED, text="Tự chạy")
        self.status_var.set("Trạng thái: Đã reset ma trận ngẫu nhiên.")
        self.info_text.delete("1.0", tk.END)

    def solve_puzzle(self):
        if self.is_playing:
            self.toggle_auto()
            
        algo = self.algo_var.get()
        self.status_var.set("Trạng thái: Đang tính toán...")
        self.root.update()
        
        start_time = time.time()
        path = None
        cost = None
        
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
                
        end_time = time.time()
        duration = end_time - start_time
        
        if path is None:
            self.status_var.set("Trạng thái: Không tìm thấy lời giải.")
            messagebox.showerror("Lỗi", "Không thể tìm thấy lời giải cho trạng thái này!")
            return
            
        self.solution_path = path
        self.current_index = 0
        self.current_state = self.solution_path[0]
        self.update_board()
        
        self.algo_details = {
            "algo": algo,
            "duration": duration,
            "steps": len(path) - 1,
            "total_cost": cost,
            "status": search_result["status"] if algo == "Simple Hill Climbing (SHC)" else None,
            "stuck_state": search_result["stuck_state"] if algo == "Simple Hill Climbing (SHC)" else None,
            "stuck_value": search_result["stuck_value"] if algo == "Simple Hill Climbing (SHC)" else None,
        }

        if algo == "Greedy Search":
            self.greedy_details = {
                "duration": duration,
                "steps": len(path) - 1
            }
        else:
            self.greedy_details = {}
        
        self.btn_prev.config(state=tk.DISABLED)
        if len(path) > 1:
            self.btn_next.config(state=tk.NORMAL)
            self.btn_auto.config(state=tk.NORMAL)
        else:
            self.btn_next.config(state=tk.DISABLED)
            self.btn_auto.config(state=tk.DISABLED)

        if algo == "Simple Hill Climbing (SHC)":
            if self.algo_details["status"] == "goal":
                self.status_var.set("Trạng thái: Đã giải xong bằng Simple Hill Climbing.")
            else:
                self.status_var.set("Trạng thái: SHC dừng ở cực trị cục bộ.")
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
            text += "Chi phí bước đi quy định:\n"
            text += "  - Lên: 1.0   - Xuống: 1.5\n"
            text += "  - Trái: 1.2  - Phải: 0.8\n"
        if algo == "Simple Hill Climbing (SHC)":
            if self.algo_details.get("status") == "goal":
                text += "Trạng thái thuật toán: đã tìm thấy lời giải\n"
            else:
                text += "Trạng thái thuật toán: dừng ở cực trị cục bộ\n"
        text += "=" * 35 + "\n"

        # Removed step counter display per request

        text += "\nCÁC HƯỚNG ĐI CÓ THỂ TIẾP THEO:\n"
        candidate_lines = []
        for action in actions(self.current_state):
            child = child_node(self.current_state, action)
            direction = direction_from_action(action)
            if algo == "Greedy Search":
                candidate_lines.append((manhattan(child), f"- {direction}: h(n) = {manhattan(child)}"))
            elif algo == "Simple Hill Climbing (SHC)":
                candidate_lines.append((misplaced_tiles(child), f"- {direction}: h(n) = {misplaced_tiles(child)}"))
            elif algo == "Uniform Cost Search (UCS)":
                candidate_lines.append((len(candidate_lines), f"- {direction}: cost = {step_cost(self.current_state, action):.1f}"))
            elif algo == "A* Search":
                g_c = inversion_count(child)
                h_c = manhattan(child)
                f_c = g_c + h_c
                candidate_lines.append((f_c, f"- {direction}: g={g_c}, h={h_c}, f={f_c}"))
            elif algo == "Iterative Deepening A* (IDA*)":
                g_c = self.current_index + 1
                h_c = manhattan(child)
                f_c = g_c + h_c
                candidate_lines.append((f_c, f"- {direction}: g={g_c}, h={h_c}, f={f_c}"))
            else:
                candidate_lines.append((len(candidate_lines), f"- {direction}"))

        if algo in ("Greedy Search", "A* Search", "Simple Hill Climbing (SHC)", "Iterative Deepening A* (IDA*)"):
            candidate_lines.sort(key=lambda item: item[0])
        for _, line in candidate_lines:
            text += f"{line}\n"

        text += "\nHƯỚNG ĐI TIẾP THEO:\n"
        if self.current_index < len(self.solution_path) - 1:
            next_state = self.solution_path[self.current_index + 1]
            next_action = None
            x1, y1 = find_zero(self.current_state)
            x2, y2 = find_zero(next_state)
            next_action = (x2 - x1, y2 - y1)
            next_direction = zero_move_direction(self.current_state, next_state)
            text += f"- {next_direction}\n"
            if algo == "Uniform Cost Search (UCS)" and next_action is not None:
                text += f"- cost = {step_cost(self.current_state, next_action):.1f}\n"
                total_cost = 0.0
                for k in range(self.current_index + 1):
                    s_curr = self.solution_path[k]
                    s_next = self.solution_path[k + 1]
                    x1, y1 = find_zero(s_curr)
                    x2, y2 = find_zero(s_next)
                    act = (x2 - x1, y2 - y1)
                    total_cost += step_cost(s_curr, act)
                text += f"- tổng cost = {total_cost:.1f}\n"
            if algo == "Greedy Search":
                text += f"- h(n) của trạng thái được chọn: {manhattan(next_state)}\n"
            if algo == "Simple Hill Climbing (SHC)":
                text += f"- h(n) của trạng thái được chọn: {misplaced_tiles(next_state)}\n"
            if algo == "A* Search":
                g_next = inversion_count(next_state)
                h_next = manhattan(next_state)
                f_next = g_next + h_next
                text += f"- g(n) = {g_next}, h(n) = {h_next}, f(n) = {f_next}\n"
            if algo == "Iterative Deepening A* (IDA*)":
                g_next = self.current_index + 1
                h_next = manhattan(next_state)
                f_next = g_next + h_next
                text += f"- g(n) = {g_next}, h(n) = {h_next}, f(n) = {f_next}\n"
        else:
            text += "- Đã tới đích\n"

        text += "\n" + "-" * 35 + "\n"
        text += "ĐẶC TRƯNG BƯỚC ĐI CỦA THUẬT TOÁN:\n"

        if algo == "Breadth-First Search (BFS)":
            text += "- BFS tìm kiếm theo từng tầng.\n"
            text += f"- Đảm bảo số bước đi ({self.current_index}) luôn là tối ưu ngắn nhất về mặt số cạnh."
        elif algo == "Depth-First Search (DFS)":
            text += "- DFS đi sâu vào một nhánh duy nhất.\n"
            text += "- Thường tìm thấy đường đi rất dài và không tối ưu."
        elif algo == "Iterative Deepening Search (IDS)":
            text += "- IDS lặp lại DLS tăng dần độ sâu.\n"
            text += f"- Hiện tại đang ở độ sâu giới hạn >= {self.current_index}.\n"
            text += "- Tiết kiệm bộ nhớ như DFS và tối ưu bước như BFS."
        elif algo == "Uniform Cost Search (UCS)":
            text += "- UCS luôn mở rộng nút có chi phí thấp nhất.\n"
            current_cost = 0.0
            for k in range(self.current_index):
                s_curr = self.solution_path[k]
                s_next = self.solution_path[k + 1]
                x1, y1 = find_zero(s_curr)
                x2, y2 = find_zero(s_next)
                act = (x2 - x1, y2 - y1)
                current_cost += step_cost(s_curr, act)
            text += f"- Chi phí tích lũy đến bước này: {current_cost:.1f}\n"
            text += "- Đảm bảo tối ưu hóa về mặt tổng chi phí."
        elif algo == "Greedy Search":
            text += "- Luôn chọn trạng thái có h(n) nhỏ nhất.\n"
            text += "- Chạy nhanh nhưng không đảm bảo tối ưu."
        elif algo == "A* Search":
            text += "- Kết hợp g(n) và h(n) để chọn nút mở rộng.\n"
            text += f"- Đảm bảo tối ưu nếu h(n) là admissible.\n"
            text += f"- Hiện tại g(n) = {inversion_count(self.current_state)}, h(n) = {manhattan(self.current_state)}, f(n) = {inversion_count(self.current_state) + manhattan(self.current_state)}\n"
        elif algo == "Simple Hill Climbing (SHC)":
            text += "- Dùng số ô sai vị trí làm heuristic.\n"
            text += "- Chọn láng giềng đầu tiên tốt hơn trạng thái hiện tại.\n"
            text += "- Có thể dừng ở cực trị cục bộ.\n"
        elif algo == "Iterative Deepening A* (IDA*)":
            text += "- Duyệt sâu dần theo ngưỡng f(n) = g(n) + h(n).\n"
            text += "- Tiết kiệm bộ nhớ hơn A*.\n"
            text += f"- Hiện tại g(n) = {self.current_index}, h(n) = {manhattan(self.current_state)}, f(n) = {self.current_index + manhattan(self.current_state)}\n"

        self.info_text.insert(tk.END, text)

    def next_step(self):
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

if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleApp(root)
    root.mainloop()