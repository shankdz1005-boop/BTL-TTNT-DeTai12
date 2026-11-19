# lrta_star.py
# Thành viên 2 - LRTA* (Learning Real-Time A*) cho môi trường quan sát một phần.
#
# Chỉ đọc known_map (UNKNOWN/FREE/WALL), current, goal và memory.
# Tuyệt đối không truy cập maze thật.

UNKNOWN = -1
WALL = 1
FREE = 0

UP = (-1, 0)
RIGHT = (0, 1)
DOWN = (1, 0)
LEFT = (0, -1)
DIRECTIONS = [UP, RIGHT, DOWN, LEFT]  # thứ tự phá hòa chung

STEP_COST = 1  # c(s, s') = 1 cho mọi bước di chuyển hợp lệ


def _manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _h(memory, cell, goal):
    """Giá trị H(cell).

    - Ô đã có trong bảng H (đã được học): dùng giá trị đã học.
    - Ô chưa có (kể cả ô UNKNOWN): khởi tạo bằng Manhattan đến goal.
      Manhattan chỉ phụ thuộc tọa độ nên không dùng bất kỳ thông tin
      nào về mê cung thật (giả định robot biết tọa độ goal).
    """
    H = memory["H"]
    if cell not in H:
        H[cell] = _manhattan(cell, goal)
    return H[cell]


def choose_action(current, goal, known_map, memory):
    """Chọn hành động theo LRTA*.

    Mỗi bước:
      1. Lập danh sách trạng thái kế tiếp s' mà known_map xác định là FREE
         (ô UNKNOWN, WALL hoặc ngoài lưới đều không được xét).
      2. Với mỗi s', tính f(s') = c(s, s') + H(s').
      3. Cập nhật  H(s) = min_{s'} f(s').
      4. Chọn s' có f nhỏ nhất; hòa thì theo thứ tự UP, RIGHT, DOWN, LEFT.

    Trả về (action, memory). Nếu không có ô kề FREE -> (None, memory).
    """
    if memory is None:
        memory = {}
    memory.setdefault("H", {})          # bảng H học được, giữ qua mọi bước
    memory.setdefault("steps", 0)       # số lần gọi (phục vụ log)
    memory.setdefault("last_update", None)

    rows = len(known_map)
    cols = len(known_map[0]) if rows else 0

    candidates = []  # (f, thứ_tự_hướng, hướng)
    for order, d in enumerate(DIRECTIONS):
        nr, nc = current[0] + d[0], current[1] + d[1]
        if not (0 <= nr < rows and 0 <= nc < cols):
            continue
        if known_map[nr][nc] != FREE:   # UNKNOWN và WALL đều bị loại
            continue
        f = STEP_COST + _h(memory, (nr, nc), goal)
        candidates.append((f, order, d))

    memory["steps"] += 1
    if not candidates:
        return None, memory

    best_f, _, best_dir = min(candidates)   # so sánh (f, thứ tự hướng)

    old_h = _h(memory, current, goal)
    memory["H"][current] = best_f           # H(s) = min [c + H(s')]
    memory["last_update"] = (current, old_h, best_f)

    return best_dir, memory
