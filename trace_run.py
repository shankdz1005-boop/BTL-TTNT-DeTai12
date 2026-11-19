# trace_run.py - In nhật ký từng bước của MỘT thuật toán trên MỘT mê cung.
# Dùng để lấy dữ liệu cho mục "Ví dụ chạy từng bước" trong báo cáo.
#
#   python trace_run.py --algo lrta_star --demo-trap          # mê cung nhỏ có bẫy chữ U
#   python trace_run.py --algo lrta_star --mssv 072206011102  # mê cung sinh từ MSSV
#   python trace_run.py --algo node_counting --demo-trap --max-lines 15
#
# Số bước KHÔNG do thuật toán tự đếm: mỗi lần gọi choose_action robot đi đúng 1 ô,
# vòng lặp ở đây (và trong maze_env.run_episode) đếm số lần robot thực sự di chuyển.

import argparse

from run_experiments import import_algo
from shared_api import DIRECTIONS
from maze_env import (MazeEnv, maze_size_from_mssv, seed_from_mssv,
                      generate_maze, shortest_path_length)

NAME = {(-1, 0): "UP", (0, 1): "RIGHT", (1, 0): "DOWN", (0, -1): "LEFT"}

# Mê cung minh họa 5x7: start nằm trong túi chữ U, goal ở ngay sau bức tường
TRAP = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 1, 0],
    [0, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0],
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--algo", required=True, help="tên file trong algorithms/, ví dụ lrta_star")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--mssv")
    g.add_argument("--demo-trap", action="store_true")
    ap.add_argument("--max-lines", type=int, default=0, help="chỉ in N bước đầu (0 = in hết)")
    ap.add_argument("--loop-prob", type=float, default=0.08)
    args = ap.parse_args()

    fn = import_algo(args.algo).choose_action
    if args.demo_trap:
        maze, start, goal = TRAP, (2, 2), (2, 6)
        title = "mê cung minh họa (bẫy chữ U) 5x7"
    else:
        r, c = maze_size_from_mssv(args.mssv)
        maze, start, goal = generate_maze(r, c, seed_from_mssv(args.mssv), args.loop_prob)
        title = f"mê cung MSSV {args.mssv} ({r}x{c})"
    best = shortest_path_length(maze, start, goal)
    limit = 10 * len(maze) * len(maze[0])

    env = MazeEnv(maze, start, goal)
    memory = {}
    print(f"{args.algo} trên {title}: start={start}, goal={goal}, đường ngắn nhất={best}")
    print(f"{'Bước':>5} | {'Vị trí':<9} | {'Hướng':<6} | Ghi chú")
    moves = 0
    while env.pos != goal and moves < limit:
        pos = env.pos
        h_old = memory.get("H", {}).get(pos) if isinstance(memory.get("H"), dict) else None
        action, memory = fn(pos, goal, env.view(), memory)
        if action is None or not env.step(action):
            print("Dừng: không có hướng đi hợp lệ")
            break
        moves += 1
        note = ""
        if isinstance(memory.get("H"), dict) and pos in memory["H"]:  # LRTA*: H cũ -> H mới
            h_new = memory["H"][pos]
            if h_old is None:  # lần đầu gặp ô: H ban đầu là Manhattan đến goal
                h_old = abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
            note = f"H{pos}: {h_old} -> {h_new}"
        if not args.max_lines or moves <= args.max_lines:
            print(f"{moves:>5} | {str(pos):<9} | {NAME[tuple(action)]:<6} | {note}")
    ok = env.pos == goal
    print(f"Kết thúc: {'THÀNH CÔNG' if ok else 'KHÔNG thành công'} sau {moves} bước "
          f"({moves / best:.2f}x đường ngắn nhất)" if ok else f"Kết thúc: không thành công sau {moves} bước")


if __name__ == "__main__":
    main()
