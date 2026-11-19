# edge_counting.py

UP = (-1, 0)
RIGHT = (0, 1)
DOWN = (1, 0)
LEFT = (0, -1)
DIRECTIONS = [UP, RIGHT, DOWN, LEFT]

def choose_action(current, goal, known_map, memory):
    """
    Thuật toán Edge Counting (Đếm cạnh) cho tác tử điều hướng trong mê cung.
    - current: (row, col) tọa độ hiện tại
    - goal: (row, col) tọa độ đích (nếu biết)
    - known_map: lưới 2D (0: FREE, 1: WALL, -1: UNKNOWN)[cite: 2]
    - memory: dict lưu trạng thái riêng qua các bước[cite: 2]
    """
    # 1. Khởi tạo bộ nhớ cho edge_counts nếu chưa có
    if 'edge_counts' not in memory:
        memory['edge_counts'] = {}

    r, c = current
    rows = len(known_map)
    cols = len(known_map[0])

    valid_neighbors = []

    # 2. Xét 4 hướng lân cận
    for d in DIRECTIONS:
        nr, nc = r + d[0], c + d[1]
        # Kiểm tra ô lân cận nằm trong bản đồ và là FREE (0)[cite: 2]
        if 0 <= nr < rows and 0 <= nc < cols:
            if known_map[nr][nc] == 0:  # FREE[cite: 2]
                neighbor = (nr, nc)
                # Chuẩn hóa cạnh (A, B) và (B, A) là một bằng cách sắp xếp tọa độ[cite: 3]
                edge_key = tuple(sorted([current, neighbor]))
                # Lấy số lần đi qua cạnh này (mặc định là 0 nếu chưa đi)
                count = memory['edge_counts'].get(edge_key, 0)
                valid_neighbors.append((count, d, neighbor))

    # Nếu không tìm thấy ô trống xung quanh
    if not valid_neighbors:
        return DIRECTIONS[0], memory, #[cite: 2]

    # 3. Sắp xếp để chọn cạnh có số lần đi qua thấp nhất[cite: 3]
    valid_neighbors.sort(key=lambda x: x[0])
    min_count = valid_neighbors[0][0]
    best_options = [item for item in valid_neighbors if item[0] == min_count]

    # Lấy hướng đi tối ưu
    chosen_item = best_options[0]
    chosen_direction = chosen_item[1]
    chosen_neighbor = chosen_item[2]

    # 4. Tăng bộ đếm cho cạnh vừa chọn lên 1 và cập nhật vào memory[cite: 3]
    edge_key = tuple(sorted([current, chosen_neighbor]))
    memory['edge_counts'][edge_key] = memory['edge_counts'].get(edge_key, 0) + 1

    return chosen_direction, memory