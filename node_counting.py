UNKNOWN = -1
WALL = 1
FREE = 0

UP = (-1, 0)
RIGHT = (0, 1)
DOWN = (1, 0)
LEFT = (0, -1)
DIRECTIONS = [UP, RIGHT, DOWN, LEFT]


def _in_bounds(position, known_map):
    """Kiem tra toa do nam trong pham vi known_map."""
    row, col = position
    return (
        0 <= row < len(known_map)
        and len(known_map) > 0
        and 0 <= col < len(known_map[row])
    )


def _manhattan(position, goal):
    return abs(position[0] - goal[0]) + abs(position[1] - goal[1])


"""
    Quy tắc chọn:
        1. Ưu tiên ô có visit_count nhỏ nhất.
        2. Nếu hoà, ưu tiên khoảng cách Manhattan đến goal nhỏ nhất.
        3. Nếu vẫn hoà, dùng thứ tự UP, RIGHT, DOWN, LEFT.
"""
def choose_action(current, goal, known_map, memory):

    if memory is None:
        memory = {}

    visit_count = memory.setdefault("visit_count", {})
    path_stack = memory.setdefault("path_stack", [])
    last_counted_position = memory.get("last_counted_position")
    if last_counted_position != current:
        visit_count[current] = visit_count.get(current, 0) + 1
        memory["last_counted_position"] = current

        if not path_stack:
            path_stack.append(current)
        elif len(path_stack) >= 2 and path_stack[-2] == current:
            path_stack.pop()
        elif path_stack[-1] != current:
            path_stack.append(current)

    if current == goal:
        memory["last_position"] = current
        return None, memory


    candidates = []
    for direction_index, direction in enumerate(DIRECTIONS):
        next_position = (
            current[0] + direction[0],
            current[1] + direction[1],
        )

        if not _in_bounds(next_position, known_map):
            continue

        if known_map[next_position[0]][next_position[1]] != FREE:
            continue

        candidates.append(
            (
                visit_count.get(next_position, 0),
                _manhattan(next_position, goal),
                direction_index,
                direction,
                next_position,
            )
        )

    if not candidates:
        memory["last_position"] = current
        return None, memory

    all_visited = all(item[0] > 0 for item in candidates)
    if all_visited and len(path_stack) >= 2:
        previous_position = path_stack[-2]
        for item in candidates:
            if item[4] == previous_position:
                memory["last_position"] = current
                memory["last_action"] = item[3]
                return item[3], memory

    candidates.sort(key=lambda item: (item[0], item[1], item[2]))
    action = candidates[0][3]

    memory["last_position"] = current
    memory["last_action"] = action
    return action, memory
