import pytest
from A_star import a_star_search

#Tests avec MazeMedium0
Maze_path = [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7),
        (2, 7), (3, 7), (4, 7), (4, 8), (4, 9), (5, 9), (6, 9), (7, 9),
        (8, 9), (9, 9), (9, 10), (9, 11), (10, 11), (11, 11), (12, 11),
        (13, 11), (13, 12), (13, 13), (14, 13), (15, 13), (16, 13),
        (17, 13), (17, 14), (18, 14), (19, 14), (20, 14), (21, 14),
        (22, 14), (22, 15)]

import csv
import A_star
import time

file = r"C:\Users\pofor\S7\APP1\S7APP1\assets\Mazes\mazeMedium_0"

def load_maze(path: str):
    maze = []
    with open(path, newline="") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            maze.append(row)
    return maze


def test_astar():
    mazefile = load_maze(file)

    path = A_star.a_star_search(mazefile)

    # 1) Il doit trouver un chemin
    assert path is not None
    assert len(path) > 0
    #2) Entrée et sortie sont corrects
    src_rc = A_star.find_symbol(mazefile, "S")
    dest_rc = A_star.find_symbol(mazefile, "E")
    src_xy = (src_rc[1], src_rc[0])
    dest_xy = (dest_rc[1], dest_rc[0])

    assert path[0] == src_xy
    assert path[-1] == dest_xy

    # 3) Le chemin ne doit pas passer dans un mur
    grid01 = A_star.convert_maze(mazefile)
    for (x, y) in path:
        assert grid01[y][x] == 0

def test_astar_planning_time():
    mazefile = load_maze(
        r"C:\Users\pofor\S7\APP1\S7APP1\assets\Mazes\mazeMedium_0"
    )

    start = time.perf_counter()
    A_star.a_star_search(mazefile)
    end = time.perf_counter()

    elapsed_ms = (end - start) * 1000
    print(elapsed_ms)