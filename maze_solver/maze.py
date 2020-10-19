from collections import namedtuple
from dataclasses import InitVar, dataclass, field
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np
from tensorflow.python.ops.gen_array_ops import Tile

ENTRY_COLOR = (255, 0, 0)
EXIT_COLOR = (0, 255, 0)
PATH_COLOR = (170, 0, 170)

Point = namedtuple('Point', 'x y')


@dataclass
class MazeTile:
    x: int
    y: int
    wall: int = field(compare=False)
    d: float = field(init=False, default=float('inf'), compare=False)
    parent: Tile = field(init=False, default=None, compare=False)
    processed: bool = field(init=False, default=False, compare=False)
    index_in_queue: Optional[int] = field(init=False, default=None, compare=False)

    def distance(self, other: 'Tile') -> float:
        return 0.1 + abs(self.wall - other.wall)

    def as_point(self):
        return Point(self.x, self.y)


@dataclass
class Maze:
    """Represents a maze with one entry and one exit point. The maze is loaded from a black & white image, where
    white represents empty space and black represents walls
    """
    image_path: InitVar[Path]
    entry: Point
    exit: Point
    map: np.ndarray = field(init=False)
    image: np.ndarray = field(init=False)
    width: int = field(init=False)
    height: int = field(init=False)

    def __post_init__(self, image_path: Path):
        assert image_path.exists()
        self.image = cv2.imread(str(image_path))
        self.height, self.width = self.image.shape[:2]
        gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        thresh, bw_image = cv2.threshold(gray_image, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        self.map = np.full((self.width, self.height), None)
        for x in range(self.width):
            for y in range(self.height):
                self.map[x][y] = MazeTile(x, y, bw_image[y][x])

        # Draw entry and exit points, then save image
        cv2.circle(self.image, self.entry, 3, ENTRY_COLOR, -1)
        cv2.circle(self.image, self.exit, 3, EXIT_COLOR, -1)
        temp_folder = Path('temp')
        if not temp_folder.exists:
            temp_folder.mkdir()
        cv2.imwrite('temp/initial_maze.png', self.image)

    def get_tile(self, point: Point) -> MazeTile:
        return self.map[point.x][point.y]

    def get_entry(self) -> MazeTile:
        return self.get_tile(self.entry)

    def get_exit(self) -> MazeTile:
        return self.get_tile(self.exit)

    def get_neighbors(self, tile: MazeTile):
        """Get neighbor directly above, below, right, and left"""
        neighbors = []
        x, y = tile.x, tile.y
        if x > 0 and not self.map[x - 1][y].processed:
            neighbors.append(self.map[x - 1][y])
        if x < self.width - 1 and not self.map[x + 1][y].processed:
            neighbors.append(self.map[x + 1][y])
        if y > 0 and not self.map[x][y - 1].processed:
            neighbors.append(self.map[x][y - 1])
        if y < self.height - 1 and not self.map[x][y + 1].processed:
            neighbors.append(self.map[x][y + 1])
        return neighbors

    def show(self, size=(7, 7)):
        cv2.namedWindow('Maze Solver', cv2.WINDOW_NORMAL)
        cv2.imshow('Maze Solver', self.image)
        cv2.waitKey(0)

    def show_path(self, path: List[MazeTile], thickness=2):
        start = path[0].as_point()
        for tile in path[1:]:
            end = tile.as_point()
            cv2.line(self.image, start, end, PATH_COLOR, thickness)
            start = tile.as_point()
        # cv2.imshow('Maze Solver', self.image)
        cv2.imwrite('temp/solved_maze.png', self.image)
        cv2.waitKey(100)
        cv2.destroyAllWindows()
