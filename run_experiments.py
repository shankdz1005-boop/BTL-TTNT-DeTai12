# run_experiments.py - Chạy mọi thuật toán trên cùng bộ mê cung sinh từ MSSV.
#
# Cách dùng:
#   python run_experiments.py                       # đọc mssv_list.txt
#   python run_experiments.py --mssv 072206011102 --mssv 072206011103 ...
#   python run_experiments.py --csv ket_qua.csv --loop-prob 0.08
#
# Mỗi thuật toán là một file trong thư mục algorithms/ có hàm
#   choose_action(current, goal, known_map, memory) -> (action, memory)

import argparse
import csv
import importlib
import os
import sys

from shared_api import FREE, WALL, UNKNOWN, RIGHT, DIRECTIONS
from maze_env import (maze_size_from_mssv, seed_from_mssv, generate_maze,
                      shortest_path_length, run_episode)

# (tên hiển thị, tên module trong algorithms/, thành viên)
ALGORITHMS = [
    ("Online DFS", "online_dfs", "TV1"),
    ("LRTA*", "lrta_star", "TV2"),
    ("Node Counting", "node_counting", "TV3"),
    ("Edge Counting", "edge_counting", "TV4"),
    ("Min-LRTA*", "min_lrta_star", "TV5"),
]


def check_api(fn):
    """Kiểm tra nhanh hàm có tuân thủ API chung không. Trả về danh sách cảnh báo."""
    problems = []
    # Ca 1: chỉ có một ô kề FREE (bên phải) -> phải đi RIGHT
    km = [[WALL] * 3 for _ in range(3)]
    km[1][1] = FREE
    km[1][2] = FREE
    try:
        out = fn((1, 1), (9, 9), km, {})
        if not (isinstance(out, tuple) and len(out) == 2):
            problems.append("phải trả về đúng 2 giá trị (action, memory)")
        else:
            action, mem = out
            if action != RIGHT:
                problems.append(f"có đúng 1 ô kề FREE (RIGHT) nhưng trả về {action}")
            if not isinstance(mem, dict):
                problems.append("memory trả về không phải dict")
    except Exception as exc:
        problems.append(f"lỗi khi gọi: {type(exc).__name__}: {exc}")
        return problems
    # Ca 2: không có ô kề FREE nào -> phải trả về None
    km = [[UNKNOWN] * 3 for _ in range(3)]
    km[1][1] = FREE
    try:
        action, _ = fn((1, 1), (9, 9), km, {})
        if action is not None:
            problems.append(f"không có ô kề FREE nhưng trả về {action} thay vì None")
    except Exception as exc:
        problems.append(f"lỗi khi không có ô kề: {type(exc).__name__}: {exc}")
    return problems


def load_algorithms():
    loaded = []
    for label, module_name, owner in ALGORITHMS:
        try:
            module = importlib.import_module(f"algorithms.{module_name}")
        except ModuleNotFoundError as exc:
            if exc.name == f"algorithms.{module_name}":
                print(f"[THIẾU]  {label:<14} chưa có algorithms/{module_name}.py ({owner})")
                continue
            raise
        fn = getattr(module, "choose_action", None)
        if fn is None:
            print(f"[LỖI]    {label:<14} không có hàm choose_action")
            continue
        problems = check_api(fn)
        if problems:
            for p in problems:
                print(f"[CẢNH BÁO] {label:<14} {p}")
        else:
            print(f"[OK]     {label:<14} đúng API chung")
        loaded.append((label, fn))
    print()
    return loaded


def read_mssv_file(path):
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.split("#")[0].strip()
            if line:
                out.append(line)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mssv", action="append", help="MSSV dùng sinh mê cung (lặp lại nhiều lần)")
    ap.add_argument("--mssv-file", default="mssv_list.txt")
    ap.add_argument("--loop-prob", type=float, default=0.08)
    ap.add_argument("--csv", default="ket_qua.csv")
    args = ap.parse_args()

    mssv_list = args.mssv or read_mssv_file(args.mssv_file)
    if not mssv_list:
        sys.exit("Chưa có MSSV nào. Điền vào mssv_list.txt hoặc dùng --mssv.")
    if len(mssv_list) < 3:
        print(f"LƯU Ý: đề yêu cầu ít nhất 3 mê cung, hiện mới có {len(mssv_list)} MSSV.\n")

    algos = load_algorithms()
    if not algos:
        sys.exit("Không có thuật toán nào để chạy.")

    rows_out = []
    for mssv in mssv_list:
        r, c = maze_size_from_mssv(mssv)
        maze, start, goal = generate_maze(r, c, seed_from_mssv(mssv), args.loop_prob)
        best = shortest_path_length(maze, start, goal)
        print(f"=== MSSV {mssv}: lưới {r}x{c}, start={start}, goal={goal}, "
              f"đường ngắn nhất = {best} bước, giới hạn = {10 * r * c}")
        print(f"{'Thuật toán':<15}{'Kết quả':<12}{'Số bước':>8}{'Ô đã thăm':>11}{'Bước/tối ưu':>13}")
        for label, fn in algos:
            res = run_episode(fn, maze, start, goal)
            ratio = res["moves"] / best if res["success"] else None
            shown = {"success": "thành công", "limit": "hết bước", "stuck": "kẹt",
                     "invalid": "đi sai", "error": "lỗi code"}[res["status"]]
            print(f"{label:<15}{shown:<12}{res['moves']:>8}{res['unique_cells']:>11}"
                  f"{(f'{ratio:.2f}x' if ratio else '-'):>13}")
            rows_out.append({"mssv": mssv, "rows": r, "cols": c, "optimal": best,
                             "algorithm": label, "status": res["status"], "moves": res["moves"],
                             "unique_cells": res["unique_cells"],
                             "ratio": f"{ratio:.3f}" if ratio else ""})
        print()

    print("=== TỔNG HỢP (trung bình trên các mê cung mà thuật toán thành công) ===")
    print(f"{'Thuật toán':<15}{'Thành công':>11}{'Số bước TB':>12}{'Bước/tối ưu TB':>16}")
    for label, _ in algos:
        mine = [x for x in rows_out if x["algorithm"] == label]
        ok = [x for x in mine if x["status"] == "success"]
        avg = sum(x["moves"] for x in ok) / len(ok) if ok else None
        avg_ratio = sum(float(x["ratio"]) for x in ok) / len(ok) if ok else None
        print(f"{label:<15}{f'{len(ok)}/{len(mine)}':>11}"
              f"{(f'{avg:.1f}' if avg is not None else '-'):>12}"
              f"{(f'{avg_ratio:.2f}x' if avg_ratio is not None else '-'):>16}")

    with open(args.csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
        w.writeheader()
        w.writerows(rows_out)
    print(f"\nĐã lưu {args.csv}")


if __name__ == "__main__":
    main()
