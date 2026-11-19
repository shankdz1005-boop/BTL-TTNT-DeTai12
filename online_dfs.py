# online_dfs.py

UNKNOWN = -1
WALL = 1
FREE = 0
UP = (-1, 0)
RIGHT = (0, 1)
DOWN = (1, 0)
LEFT = (0, -1)
DIRECTIONS = [UP, RIGHT, DOWN, LEFT]

def choose_action(current, goal, known_map, memory):
    """
    current: (row, col) vị trí hiện tại của robot
    goal: (row, col) tọa độ đích
    known_map: lưới 2D chứa các trạng thái UNKNOWN (-1), WALL (1), FREE (0) đã quan sát
    memory: dict riêng của thuật toán, được duy trì qua các bước
    Return:
        action: một tuple hướng trong DIRECTIONS (hoặc None nếu không còn đường đi)
        memory: bộ nhớ đã cập nhật
    """
    # 1. Khởi tạo bộ nhớ nếu chưa tồn tại
    if "path_stack" not in memory:
        memory["path_stack"] = []      # Ngăn xếp lưu đường đi từ gốc đến hiện tại
    if "visited" not in memory:
        memory["visited"] = set()      # Tập hợp các ô đã từng đặt chân tới
    if "tried_directions" not in memory:
        memory["tried_directions"] = {} # Lưu danh sách các hướng đã thử tại mỗi ô

    current_tuple = tuple(current)
    memory["visited"].add(current_tuple)

    # Đảm bảo đỉnh stack luôn là current
    if not memory["path_stack"] or memory["path_stack"][-1] != current_tuple:
        memory["path_stack"].append(current_tuple)

    # Khởi tạo tập hướng đã thử cho ô hiện tại nếu chưa có
    if current_tuple not in memory["tried_directions"]:
        memory["tried_directions"][current_tuple] = []

    # 2. Kiểm tra nếu đã đến đích
    if current_tuple == tuple(goal):
        return None, memory

    # 3. Tìm các hướng khả dĩ (chưa thử, nằm trong bản đồ, và là FREE)
    rows = len(known_map)
    cols = len(known_map[0])
    candidate_action = None

    for action in DIRECTIONS:
        if action in memory["tried_directions"][current_tuple]:
            continue
        
        next_row = current[0] + action[0]
        next_col = current[1] + action[1]
        
        # Kiểm tra giới hạn bản đồ và ô đó phải là FREE (đã quan sát và đi được)
        if 0 <= next_row < rows and 0 <= next_col < cols:
            if known_map[next_row][next_col] == FREE:
                candidate_action = action
                break  # Lấy hướng đầu tiên thỏa mãn theo thứ tự ưu tiên UP, RIGHT, DOWN, LEFT

    # 4. Nếu tìm được hướng đi mới tiến lên
    if candidate_action is not None:
        memory["tried_directions"][current_tuple].append(candidate_action)
        return candidate_action, memory

    # 5. XỬ LÝ NGÕ CỤT (Không còn hướng đi mới, tiến hành quay lui - backtracking)
    # Loại bỏ ô hiện tại ra khỏi stack
    if memory["path_stack"]:
        memory["path_stack"].pop()

    # Nếu stack rỗng nghĩa là đã vét cạn toàn bộ không gian khám phá mà không thấy đích
    if not memory["path_stack"]:
        return None, memory

    # Lấy ô phía trước trong stack để quay về
    parent_cell = memory["path_stack"][-1]
    backtrack_action = (parent_cell[0] - current[0], parent_cell[1] - current[1])

    return backtrack_action, memory


# ==========================================
# VÍ DỤ KIỂM THỬ NHỎ (TEST EXAMPLE)
# ==========================================
if __name__ == "__main__":
    # Mê cung mô phỏng có ngõ cụt để kiểm tra khả năng quay lui của Online DFS
    # 0: FREE, 1: WALL
    true_maze = [
        [0, 0, 1],
        [1, 0, 1], # Ô (1,1) là một ngã ba/ngõ cụt cụt cụt
        [0, 0, 0]
    ]
    
    start = (0, 0)
    goal = (2, 2)
    
    # known_map ban đầu toàn UNKNOWN (-1)
    known_map = [
        [-1, -1, -1],
        [-1, -1, -1],
        [-1, -1, -1]
    ]
    
    current = start
    memory = {}
    
    print("--- BẮT ĐẦU CHẠY KIỂM THỬ ONLINE DFS ---")
    print(f"Start: {start}, Goal: {goal}\n")
    
    step = 0
    max_steps = 20
    
    while current != goal and step < max_steps:
        step += 1
        # Mô phỏng môi trường cấp quan sát cục bộ xung quanh ô hiện tại
        r, c = current
        known_map[r][c] = true_maze[r][c]
        for d in DIRECTIONS:
            nr, nc = r + d[0], c + d[1]
            if 0 <= nr < len(true_maze) and 0 <= nc < len(true_maze[0]):
                known_map[nr][nc] = true_maze[nr][nc]
                
        # Gọi hàm thuật toán
        action, memory = choose_action(current, goal, known_map, memory)
        
        if action is None:
            print(f"Bước {step}: Không tìm thấy đường đi hoặc đã đạt đích.")
            break
            
        print(f"Bước {step}: Vị trí hiện tại {current} -> Chọn hành động {action}")
        
        # Môi trường thực hiện bước đi
        current = (current[0] + action[0], current[1] + action[1])

    if current == goal:
        print(f"\n[THÀNH CÔNG] Đã đến đích tại {current} sau {step} bước!")
    else:
        print(f"\n[KẾT THÚC] Dừng lại sau {step} bước.")