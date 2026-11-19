# shared_api.py - Quy ước dùng chung (khớp mục 2 và 3 của file phân công)
UNKNOWN = -1
WALL = 1
FREE = 0

UP = (-1, 0)
RIGHT = (0, 1)
DOWN = (1, 0)
LEFT = (0, -1)
DIRECTIONS = [UP, RIGHT, DOWN, LEFT]   # cũng là thứ tự phá hòa chung

# Mỗi thuật toán cài đúng một hàm:
#   choose_action(current, goal, known_map, memory) -> (action, memory)
# action là một hướng trong DIRECTIONS, hoặc None nếu không có hướng khả dụng.
