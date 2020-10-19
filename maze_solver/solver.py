import csv
from collections import namedtuple
from typing import List

from maze_solver import get_asset_path
from maze_solver.maze import Maze, MazeTile, Point

MazeExample = namedtuple('MazeExample', 'image entry_x entry_y exit_x exit_y')


def load_example(id: int) -> Maze:
    path = get_asset_path('examples.csv')
    with open(path) as csv_file:
        reader = csv.reader(csv_file)
        headers = next(reader, None)
        examples = [MazeExample(*row) for row in reader]
    ex = examples[id - 1]
    image_path = get_asset_path(ex.image)
    entry = Point(int(ex.entry_x), int(ex.entry_y))
    exit = Point(int(ex.exit_x), int(ex.exit_y))
    maze = Maze(image_path, entry, exit)
    return maze


def solve_maze(example_id: int):
    maze = load_example(example_id)
    maze.show()
    path = find_shortest_path(maze)
    maze.show_path(path)
    maze.show()


def bubble_up(queue, index):
    if index <= 0:
        return queue
    p_index = (index - 1) // 2
    if queue[index].d < queue[p_index].d:
        queue[index], queue[p_index] = queue[p_index], queue[index]
        queue[index].index_in_queue = index
        queue[p_index].index_in_queue = p_index
        queue = bubble_up(queue, p_index)
    return queue


def bubble_down(queue, index):
    length = len(queue)
    lc_index = 2 * index + 1
    rc_index = lc_index + 1
    if lc_index >= length:
        return queue
    if lc_index < length <= rc_index:  # just left child
        if queue[index].d > queue[lc_index].d:
            queue[index], queue[lc_index] = queue[lc_index], queue[index]
            queue[index].index_in_queue = index
            queue[lc_index].index_in_queue = lc_index
            queue = bubble_down(queue, lc_index)
    else:
        small = lc_index
        if queue[lc_index].d > queue[rc_index].d:
            small = rc_index
        if queue[small].d < queue[index].d:
            queue[index], queue[small] = queue[small], queue[index]
            queue[index].index_in_queue = index
            queue[small].index_in_queue = small
            queue = bubble_down(queue, small)
    return queue


def find_shortest_path(maze: Maze):
    pq = []  # type: List[MazeTile] # min-heap priority queue
    for x in range(maze.width):
        for y in range(maze.height):
            tile = maze.map[x][y]
            tile.index_in_queue = len(pq)
            pq.append(tile)
    start = maze.get_entry()
    start.d = 0
    pq = bubble_up(pq, start.index_in_queue)

    while len(pq) > 0:
        u = pq[0]
        u.processed = True
        pq[0] = pq[-1]
        pq[0].index_in_queue = 0
        pq.pop()
        pq = bubble_down(pq, 0)
        neighbors = maze.get_neighbors(u)
        for v in neighbors:
            dist = u.distance(v)
            if u.d + dist < v.d:
                v.d = u.d + dist
                v.parent = u
                idx = v.index_in_queue
                pq = bubble_down(pq, idx)
                pq = bubble_up(pq, idx)

    path = []  # type: List[MazeTile]
    end = maze.get_exit()
    path.append(end)
    iter_v = end
    while iter_v != start:
        path.append(iter_v)
        iter_v = iter_v.parent
    path.append(start)
    return path
