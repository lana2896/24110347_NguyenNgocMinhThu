import heapq
import math
import random
from collections import deque


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
        for j in range(i + 1, len(arr)):
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


CSP_COLORS = ['R', 'G', 'B', 'Y']
CSP_COLOR_MAP = {'R': '#ff6666', 'G': '#66ff66', 'Y': '#ffff66', 'B': '#6666ff'}
CSP_COLOR_NAME = {'R': 'Đỏ', 'G': 'Xanh lá', 'Y': 'Vàng', 'B': 'Xanh dương'}


def generate_csp_start():
    nums = list(range(9))
    random.shuffle(nums)
    return tuple(tuple(nums[i:i + 3]) for i in range(0, 9, 3))


def get_csp_variables():
    return [(r, c) for r in range(3) for c in range(3)]


def get_csp_neighbors(pos):
    r, c = pos
    neighbors = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr = r + dr
            nc = c + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                neighbors.append((nr, nc))
    return neighbors


def is_consistent_color(var, color, assignment):
    for neighbor in get_csp_neighbors(var):
        if assignment.get(neighbor) == color:
            return False
    return True


def forward_checking_step_by_step(assignment, domains, variables, var_idx=0):
    if var_idx == len(variables):
        yield assignment.copy(), "Đã tìm thấy lời giải hoàn chỉnh!"
        return True

    var = variables[var_idx]
    available_colors = domains[var][:]
    random.shuffle(available_colors)

    if not available_colors:
        yield (
            assignment.copy(),
            f"Bế tắc! Ô ({var[0]},{var[1]}) không còn màu nào hợp lệ để chọn.",
        )
        return False

    for color in available_colors:
        if is_consistent_color(var, color, assignment):
            assignment[var] = color
            local_failure = False
            pruned_info = []
            saved_domains = {v: d[:] for v, d in domains.items()}

            for neighbor in get_csp_neighbors(var):
                if neighbor not in assignment or assignment[neighbor] is None:
                    if color in domains[neighbor]:
                        domains[neighbor].remove(color)
                        pruned_info.append(
                            f"({neighbor[0]},{neighbor[1]}) mất màu {CSP_COLOR_NAME[color]}"
                        )
                        if not domains[neighbor]:
                            local_failure = True

            log_msg = f"Tô ô ({var[0]},{var[1]}) màu {CSP_COLOR_NAME[color]}."
            if pruned_info:
                log_msg += " -> [Forward Check cắt tỉa: " + ", ".join(pruned_info) + "]"
            if local_failure:
                log_msg += " -> PHÁT HIỆN THẤT BẠI SỚM (Hàng xóm bị trống màu)!"

            yield assignment.copy(), log_msg

            if not local_failure:
                matched = yield from forward_checking_step_by_step(
                    assignment, domains, variables, var_idx + 1
                )
                if matched:
                    return True

            domains.update({v: d[:] for v, d in saved_domains.items()})
            assignment[var] = None
            yield (
                assignment.copy(),
                f"Quay lui, hủy màu ô ({var[0]},{var[1]}) & Khôi phục lại miền giá trị.",
            )
        else:
            yield (
                assignment.copy(),
                f"Xung đột! Không thể đặt ô ({var[0]},{var[1]}) màu {CSP_COLOR_NAME[color]}",
            )

    return False


def is_solvable(start, goal_state):
    return inversion_count(start) % 2 == inversion_count(goal_state) % 2


def a_star(start, goal_state):
    start_g = inversion_count(start)
    start_h = manhattan(start)
    start_f = start_g + start_h

    frontier = []
    heapq.heappush(frontier, (start_f, start_g, start_h, start))
    best_f = {start: start_f}
    parent = {start: None}

    while frontier:
        f, g, h, state = heapq.heappop(frontier)
        if state == goal_state:
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


def greedy_search(start, goal_state):
    if start == goal_state:
        return [start]

    frontier = [start]
    reached = set()
    parent = {start: None}

    while frontier:
        current = min(frontier, key=manhattan)

        if current == goal_state:
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


def random_neighbor_with_action(state):
    action = random.choice(actions(state))
    return child_node(state, action), action


def simulated_annealing(start_state, t0=100.0, t_min=0.001, alpha=0.95):
    current = start_state
    best = current
    temperature = t0
    step = 0

    history = [current]
    move_logs = []
    accepted_moves = 0
    worse_accepted = 0
    found_goal = (current == goal)

    while temperature > t_min:
        current_h = manhattan(current)
        if current_h == 0:
            found_goal = True
            break

        next_state, action = random_neighbor_with_action(current)
        next_h = manhattan(next_state)
        delta = next_h - current_h
        prob = 1.0 if delta < 0 else math.exp(-delta / temperature)

        accepted = False
        reason = ""
        if delta < 0:
            accepted = True
            reason = "Tốt hơn"
        else:
            r = random.random()
            if r < prob:
                accepted = True
                reason = "Chấp nhận theo xác suất"

        if accepted:
            if delta > 0:
                worse_accepted += 1
            current = next_state
            accepted_moves += 1
            history.append(current)

            if manhattan(current) < manhattan(best):
                best = current

        move_logs.append({
            "step": step,
            "temperature": temperature,
            "current_h": current_h,
            "next_h": next_h,
            "delta": delta,
            "probability": prob,
            "accepted": accepted,
            "reason": reason if accepted else "Từ chối",
            "direction": direction_from_action(action),
        })

        temperature *= alpha
        step += 1

    info = {
        "iterations": step,
        "accepted_moves": accepted_moves,
        "worse_accepted": worse_accepted,
        "best_h": manhattan(best),
        "final_h": manhattan(current),
        "found_goal": found_goal,
        "final_temperature": temperature,
    }
    return history, move_logs, info, best


def random_child(state):
    poss_actions = actions(state)
    if not poss_actions:
        return state
    return child_node(state, random.choice(poss_actions))


def and_or_search(start_state, max_depth=12):
    logs = []

    def or_search(state, visited, depth):
        if state == goal:
            return True
        if depth > max_depth or len(logs) > 1500:
            return False
        if state in visited:
            return False

        for action in actions(state):
            real_state = child_node(state, action)
            random_state2 = random_child(real_state)

            logs.append({
                "state": state,
                "action": action,
                "direction": direction_from_action(action),
                "and1": real_state,
                "and2": random_state2,
                "depth": depth,
                "h_current": manhattan(state),
                "h_and1": manhattan(real_state),
                "h_and2": manhattan(random_state2)
            })

            if and_search([real_state, random_state2], visited + [state], depth + 1):
                return True
        return False

    def and_search(states, visited, depth):
        for s in states:
            if not or_search(s, visited, depth):
                return False
        return True

    found_goal = or_search(start_state, [], 0)
    path = [log["state"] for log in logs]
    if found_goal:
        path.append(goal)
    elif len(path) == 0:
        path.append(start_state)
    else:
        path.append(logs[-1]["and1"])

    max_d = max([l["depth"] for l in logs]) if logs else 0
    info = {
        "iterations": len(logs),
        "found_goal": found_goal,
        "max_depth_reached": max_d,
    }
    return path, logs, info


def depth_first_search(start, goal_state):
    if start == goal_state:
        return [start]
    frontier = [start]
    frontier_set = {start}
    parent_map = {start: None}
    explored = set()
    while frontier:
        state = frontier.pop()
        frontier_set.remove(state)
        explored.add(state)
        if state == goal_state:
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


def depth_limited_search(state, goal_state, limit, path):
    if state == goal_state:
        return path
    if limit == 0:
        return "cutoff"
    cutoff_occurred = False
    for action in actions(state):
        child = child_node(state, action)
        if child not in path:
            result = depth_limited_search(child, goal_state, limit - 1, path + [child])
            if result == "cutoff":
                cutoff_occurred = True
            elif result != "failure":
                return result
    if cutoff_occurred:
        return "cutoff"
    return "failure"


def iterative_deepening_search(start, goal_state, max_depth=40):
    for depth in range(max_depth + 1):
        result = depth_limited_search(start, goal_state, depth, [start])
        if result == "cutoff":
            continue
        if result == "failure":
            return "failure"
        return result
    return "failure"


def breadth_first_search(start, goal_state):
    if start == goal_state:
        return [start]
    frontier = deque()
    frontier.append((start, []))
    frontier_set = {start}
    explored = set()
    while frontier:
        state, path = frontier.popleft()
        explored.add(state)
        if state == goal_state:
            return path + [state]
        for action in actions(state):
            child = child_node(state, action)
            in_frontier = child in frontier_set
            if child not in explored and not in_frontier:
                if child == goal_state:
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


def uniform_cost_search(start, goal_state):
    if start == goal_state:
        return [start], 0.0
    frontier = []
    heapq.heappush(frontier, (0.0, start, [start]))
    best_cost = {start: 0.0}
    while frontier:
        cost, state, path = heapq.heappop(frontier)
        if cost > best_cost.get(state, float('inf')):
            continue
        if state == goal_state:
            return path, cost
        for action in actions(state):
            child = child_node(state, action)
            new_cost = cost + step_cost(state, action)
            if new_cost < best_cost.get(child, float('inf')):
                best_cost[child] = new_cost
                heapq.heappush(frontier, (new_cost, child, path + [child]))
    return None, float('inf')