"""
min_lrta_star.py - Thanh vien 5: Min-LRTA*

Tai lieu tham khao (dinh nghia goc cua Min-LRTA*):
    Sven Koenig & Reid G. Simmons (1996). "Easy and Hard Testbeds for
    Real-Time Search Algorithms". Proceedings of AAAI-96, trang 279-285.
    Min-LRTA* = "LRTA* with minimalistic lookahead" (LRTA* nhin truoc 1 buoc),
    luu gia tri V(s, a) tren cac CAP (trang thai, hanh dong) thay vi V(s).

Giao ma goc (moi lan lap, s = trang thai hien tai):
    1. s := trang thai hien tai
    2. Neu s la dich -> dung
    3. a := mot phan tu cua argmin_{a' thuoc A(s)} V(s, a')
    4. V(s, a) := 1 + min_{a' thuoc A(succ(s, a))} V(succ(s, a), a')
    5. Thuc hien a; s := succ(s, a)

Khoi tao trong bai bao: V(s, a) = 0 voi moi (s, a) (khong dung heuristic).

Ghi chu trien khai trong moi truong quan sat mot phan:
    * A(s) la tap huong den o ke da BIET la FREE trong known_map.
    * Buoc 4 can A(succ(s, a)), nhung tai thoi diem chon a robot CHUA nhin
      thay cac o ke cua succ(s, a). Vi vay buoc 4 duoc hoan lai den lan goi
      tiep theo, khi robot da dung o succ(s, a) va quan sat xong. Ket qua
      giong het: V(succ, .) khong doi giua hai thoi diem do.
    * goal chi dung de nhan biet dich (V(goal, .) = 0) va, neu bat che do
      mo rong "manhattan", de khoi tao V. Thuat toan KHONG doc maze that.

Che do khoi tao (INIT_MODE hoac memory["init_mode"]):
    "zero"      : dung nhu bai bao (mac dinh).
    "manhattan" : MO RONG cua nhom, khong phai dinh nghia goc:
                  V(s, a) ban dau = 1 + Manhattan(succ(s, a), goal).
"""

UNKNOWN = -1
WALL = 1
FREE = 0

UP = (-1, 0)
RIGHT = (0, 1)
DOWN = (1, 0)
LEFT = (0, -1)
DIRECTIONS = [UP, RIGHT, DOWN, LEFT]

INIT_MODE = "zero"


def _in_bounds(position, known_map):
    """Kiem tra toa do nam trong pham vi known_map."""
    row, col = position
    return (
        0 <= row < len(known_map)
        and 0 <= col < len(known_map[row])
    )


def _manhattan(position, goal):
    return abs(position[0] - goal[0]) + abs(position[1] - goal[1])


def _available_actions(position, known_map):
    """A(s): cac (chi_so_huong, huong, o_ke) ma o ke da biet la FREE."""
    actions = []
    for direction_index, direction in enumerate(DIRECTIONS):
        next_position = (
            position[0] + direction[0],
            position[1] + direction[1],
        )
        if not _in_bounds(next_position, known_map):
            continue
        if known_map[next_position[0]][next_position[1]] != FREE:
            continue
        actions.append((direction_index, direction, next_position))
    return actions


def _value(values, init_mode, position, direction_index, next_position, goal):
    """Lay V(s, a); neu chua co thi khoi tao theo init_mode roi luu lai."""
    key = (position, direction_index)
    if key not in values:
        if init_mode == "manhattan":
            values[key] = 1 + _manhattan(next_position, goal)
        else:
            values[key] = 0
    return values[key]


def choose_action(current, goal, known_map, memory):
    """
    Min-LRTA* (Koenig & Simmons, AAAI-96).

    memory:
        "V"            : dict {((row, col), direction_index): gia tri}
        "pending"      : (o_truoc, chi_so_huong) cho buoc 4 hoan lai
        "init_mode"    : "zero" hoac "manhattan"
        "last_decision": thong tin de ghi log (q_values, chosen, update)

    Quy tac chon: V(s, a) nho nhat; hoa -> thu tu UP, RIGHT, DOWN, LEFT.
    Tra ve (None, memory) khi da toi dich hoac khong co o ke FREE nao.
    """
    if memory is None:
        memory = {}

    values = memory.setdefault("V", {})
    init_mode = memory.setdefault("init_mode", INIT_MODE)
    memory.setdefault("pending", None)
    memory["last_decision"] = {"position": current, "update": None}

    options = _available_actions(current, known_map)

    # --- Buoc 4 (hoan lai): V(prev, a) := 1 + min_a' V(current, a') ---
    pending = memory["pending"]
    if pending is not None:
        previous_position, previous_index = pending
        memory["pending"] = None
        if current != previous_position:
            if current == goal:
                best_next = 0
            elif options:
                best_next = min(
                    _value(values, init_mode, current, idx, nxt, goal)
                    for idx, _, nxt in options
                )
            else:
                best_next = None
            if best_next is not None:
                old = values.get((previous_position, previous_index))
                values[(previous_position, previous_index)] = 1 + best_next
                memory["last_decision"]["update"] = (
                    previous_position,
                    DIRECTIONS[previous_index],
                    old,
                    1 + best_next,
                )

    # --- Buoc 2: dung neu da toi dich ---
    if current == goal or not options:
        memory["last_position"] = current
        return None, memory

    # --- Buoc 3: chon a trong argmin V(s, a'), hoa -> thu tu huong chung ---
    scored = []
    for idx, direction, nxt in options:
        q = _value(values, init_mode, current, idx, nxt, goal)
        scored.append((q, idx, direction))
    scored.sort(key=lambda item: (item[0], item[1]))
    best_q, best_index, best_direction = scored[0]

    memory["pending"] = (current, best_index)
    memory["last_position"] = current
    memory["last_action"] = best_direction
    memory["last_decision"]["q_values"] = {
        DIRECTIONS[idx]: q for q, idx, _ in scored
    }
    memory["last_decision"]["chosen"] = best_direction
    return best_direction, memory
