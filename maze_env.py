# maze_env.py - Sinh mê cung theo MSSV + môi trường quan sát một phần.
#
# Môi trường giữ maze thật. Thuật toán chỉ nhận known_map (UNKNOWN/FREE/WALL)
# sau khi robot quan sát 4 ô kề. Quan sát tại chỗ không tính là bước đi.

import random
from collections import deque

from shared_api import UNKNOWN, WALL, FREE, DIRECTIONS


# ---------------------------------------------------------------- MSSV -> mê cung
def maze_size_from_mssv(mssv):
    """Quy ước kích thước (nhóm cần thống nhất và ghi vào báo cáo):

    Coi MSSV là một số nguyên N (bỏ số 0 đầu), seed = N.
    - Số ô-đường theo hàng = 6 + N mod 7          -> 6..12
    - Số ô-đường theo cột  = 6 + (N // 7) mod 7   -> 6..12
    - Lưới thật = 2*n + 1 (ô đường xen kẽ tường), nên 13..25 mỗi chiều.

    Dùng N thay vì tổng chữ số vì MSSV cùng lớp thường trùng các số đầu,
    chỉ khác số cuối; cách này làm kích thước khác nhau giữa các thành viên.
    """
    n = seed_from_mssv(mssv)
    n_rows = 6 + n % 7
    n_cols = 6 + (n // 7) % 7
    return 2 * n_rows + 1, 2 * n_cols + 1


def seed_from_mssv(mssv):
    return int("".join(ch for ch in str(mssv) if ch.isdigit()))


def generate_maze(rows, cols, seed, loop_prob=0.08):
    """Mê cung ngẫu nhiên có seed cố định, luôn có đường từ start tới goal.

    Bước 1: DFS quay lui tạo mê cung "hoàn hảo" (chỉ có một đường giữa 2 ô).
    Bước 2: phá ngẫu nhiên một số tường trong để tạo vòng lặp (loop_prob),
            nhờ đó mê cung có nhiều lối đi vòng và nhiều bẫy hơn.
    Start = (1,1), goal = (rows-2, cols-2).
    """
    assert rows % 2 == 1 and cols % 2 == 1 and rows >= 5 and cols >= 5
    rng = random.Random(seed)
    maze = [[WALL] * cols for _ in range(rows)]
    maze[1][1] = FREE
    stack = [(1, 1)]
    while stack:
        r, c = stack[-1]
        options = []
        for dr, dc in DIRECTIONS:
            nr, nc = r + 2 * dr, c + 2 * dc
            if 1 <= nr < rows - 1 and 1 <= nc < cols - 1 and maze[nr][nc] == WALL:
                options.append((dr, dc, nr, nc))
        if options:
            dr, dc, nr, nc = rng.choice(options)
            maze[r + dr][c + dc] = FREE
            maze[nr][nc] = FREE
            stack.append((nr, nc))
        else:
            stack.pop()
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            if maze[r][c] == WALL and (r % 2) != (c % 2):  # tường nằm giữa 2 ô đường
                if rng.random() < loop_prob:
                    maze[r][c] = FREE
    return maze, (1, 1), (rows - 2, cols - 2)


def shortest_path_length(maze, start, goal):
    """BFS trên maze thật. Chỉ để làm mốc so sánh, thuật toán không được dùng."""
    rows, cols = len(maze), len(maze[0])
    dist = {start: 0}
    queue = deque([start])
    while queue:
        cur = queue.popleft()
        if cur == goal:
            return dist[cur]
        for dr, dc in DIRECTIONS:
            nxt = (cur[0] + dr, cur[1] + dc)
            if (0 <= nxt[0] < rows and 0 <= nxt[1] < cols
                    and maze[nxt[0]][nxt[1]] == FREE and nxt not in dist):
                dist[nxt] = dist[cur] + 1
                queue.append(nxt)
    return None


# ---------------------------------------------------------------- Môi trường
class MazeEnv:
    def __init__(self, maze, start, goal):
        self.maze, self.start, self.goal = maze, start, goal
        self.rows, self.cols = len(maze), len(maze[0])
        self.pos = start
        self.known = [[UNKNOWN] * self.cols for _ in range(self.rows)]
        self._observe()

    def _observe(self):
        r, c = self.pos
        self.known[r][c] = FREE
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                self.known[nr][nc] = self.maze[nr][nc]

    def view(self):
        """Bản sao known_map đưa cho thuật toán (không lộ maze thật)."""
        return [row[:] for row in self.known]

    def step(self, action):
        """Trả về True nếu bước đi hợp lệ và đã thực hiện."""
        if action is None or tuple(action) not in DIRECTIONS:
            return False
        nr, nc = self.pos[0] + action[0], self.pos[1] + action[1]
        if not (0 <= nr < self.rows and 0 <= nc < self.cols) or self.maze[nr][nc] != FREE:
            return False
        self.pos = (nr, nc)
        self._observe()
        return True


def run_episode(choose_action, maze, start, goal, max_steps=None):
    """Chạy một lượt. Thành công chỉ khi robot thực sự đứng ở goal."""
    env = MazeEnv(maze, start, goal)
    limit = max_steps or 10 * env.rows * env.cols
    memory = {}
    visited = {start}
    moves = 0
    status, error = "limit", ""
    while True:
        if env.pos == goal:
            status = "success"
            break
        if moves >= limit:
            status = "limit"
            break
        try:
            action, memory = choose_action(env.pos, goal, env.view(), memory)
        except Exception as exc:  # lỗi trong code thuật toán
            status, error = "error", f"{type(exc).__name__}: {exc}"
            break
        if action is None:
            status = "stuck"
            break
        if not env.step(action):
            status = "invalid"
            break
        moves += 1
        visited.add(env.pos)
    return {"status": status, "success": status == "success", "moves": moves,
            "unique_cells": len(visited), "error": error}
