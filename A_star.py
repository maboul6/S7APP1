import heapq

class Cell:
    def __init__(self):
        self.parent_i = -1
        self.parent_j = -1
        self.f = float('inf')
        self.g = float('inf')
        self.h = 0.0

def is_valid(row, col, ROW, COL):
    return 0 <= row < ROW and 0 <= col < COL

def is_unblocked(grid, row, col):
    return grid[row][col] == 0

def is_destination(row, col, dest):
    return row == dest[0] and col == dest[1]

def calculate_h_value(row, col, dest):
    return abs(row - dest[0]) + abs(col - dest[1])

def find_symbol(maze, symbol):
    for y, row in enumerate(maze):
        for x, value in enumerate(row):
            if value == symbol:
                return [y, x]
    raise ValueError(f"Symbol '{symbol}' not found in maze")

def convert_maze(mazefile):
    free_cells = {'0', 'E', 'S', 'T', 'C'}

    maze = []
    for row in mazefile:
        maze.append([0 if cell in free_cells else 1 for cell in row])

    return maze

def trace_path(cell_details, dest):
    path = []
    row, col = dest

    while not (cell_details[row][col].parent_i == row and
               cell_details[row][col].parent_j == col):
        path.append((col, row))   # inversion ici
        row, col = cell_details[row][col].parent_i, cell_details[row][col].parent_j

    path.append((col, row))
    path.reverse()
    return path


def a_star_search(mazefile):
    src = find_symbol(mazefile,'S')
    dest = find_symbol(mazefile,'E')
    maze = convert_maze(mazefile)
    ROW = len(maze)
    COL = len(maze[0])
    if not is_valid(src[0], src[1],ROW,COL) or not is_valid(dest[0], dest[1],ROW,COL):
        print("Source or destination is invalid")
        return None

    if not is_unblocked(maze, src[0], src[1]) or not is_unblocked(maze, dest[0], dest[1]):
        print("Source or the destination is blocked")
        return None

    if is_destination(src[0], src[1], dest):
        return [tuple(src)]

    closed_list = [[False for _ in range(COL)] for _ in range(ROW)]
    cell_details = [[Cell() for _ in range(COL)] for _ in range(ROW)]

    si, sj = src
    cell_details[si][sj].f = 0.0
    cell_details[si][sj].g = 0.0
    cell_details[si][sj].h = 0.0
    cell_details[si][sj].parent_i = si
    cell_details[si][sj].parent_j = sj

    open_list = []
    heapq.heappush(open_list, (0.0, si, sj))

    # 4 directions seulement: RIGHT, LEFT, DOWN, UP
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while open_list:
        f, i, j = heapq.heappop(open_list)

        if f != cell_details[i][j].f:
            continue

        closed_list[i][j] = True

        for di, dj in directions:
            new_i = i + di
            new_j = j + dj

            if not is_valid(new_i, new_j, ROW, COL):
                continue
            if closed_list[new_i][new_j]:
                continue
            if not is_unblocked(maze, new_i, new_j):
                continue

            if is_destination(new_i, new_j, dest):
                cell_details[new_i][new_j].parent_i = i
                cell_details[new_i][new_j].parent_j = j
                return trace_path(cell_details, (new_i, new_j))

            step_cost = 1.0
            g_new = cell_details[i][j].g + step_cost
            h_new = calculate_h_value(new_i, new_j, dest)
            f_new = g_new + h_new

            if cell_details[new_i][new_j].f > f_new:
                cell_details[new_i][new_j].f = f_new
                cell_details[new_i][new_j].g = g_new
                cell_details[new_i][new_j].h = h_new
                cell_details[new_i][new_j].parent_i = i
                cell_details[new_i][new_j].parent_j = j
                heapq.heappush(open_list, (f_new, new_i, new_j))

    print("Failed to find the destination cell")
    return None
