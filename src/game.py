"""This file renders the game screen

Each cell in the grid has following attributes:
    - value [" ", "0", "#"]
        - Blank means that cell is empty
        - 0 depicts the body parts of the snake
        - # is the head of the snake
    - next direction
"""

import os
import random
import sys
import threading
import time
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import Optional

from src.context_managers import single_char_input_mode


class Direction(int, Enum):
    LEFT = 0
    DOWN = 1
    RIGHT = 2
    UP = 3

    @cached_property
    def opposite(self):
        if self == Direction.LEFT:
            return Direction.RIGHT

        if self == Direction.RIGHT:
            return Direction.LEFT

        if self == Direction.UP:
            return Direction.DOWN

        return Direction.UP


grid_lock = threading.Lock()

EMPTY = " "
BODY = "0"
HEAD = "#"


@dataclass
class Cell:
    """Class representing each cell in the game grid

    Attributes:
        value: Cell content
        moving: Direction in which the current cell will move. None for empty cells.
    """

    value: str = EMPTY
    moving: Optional[Direction] = None

    def __str__(self) -> str:
        return self.value

    def is_empty(self) -> bool:
        return self.value == EMPTY

    def is_body(self) -> bool:
        return self.value == BODY

    def is_head(self) -> bool:
        return self.value == HEAD


Row = list[Cell]
Grid = list[Row]


class Game:
    """Game class that represents the global state of the game."""

    def __init__(self, row_count: int, col_count: int):
        self.row_count = row_count
        self.col_count = col_count
        self.score: int = 0
        self.__grid = self.__generate_screen()
        self.__head = self.__initiate_head(self.grid)
        self.sleep_time = 1.0

    def __generate_screen(self) -> Grid:
        return [[Cell() for _ in range(self.col_count)] for _ in range(self.row_count)]

    def __initiate_head(self, grid: Grid) -> Cell:
        x, y = (
            random.randint(0, self.row_count - 1),
            random.randint(0, self.col_count - 1),
        )
        head = grid[x][y]
        head.value = HEAD
        head.moving = random.choice([d for d in Direction])
        return head

    @property
    def grid(self):
        return self.__grid

    @grid.setter
    def grid(self, _):
        raise NotImplementedError

    @property
    def head(self):
        return self.__head

    @head.setter
    def head(self, _):
        raise NotImplementedError

    def update_grid_and_head(self, _grid: Grid, _head: Cell):
        self.__grid = _grid
        self.__head = _head

    def move_snake_and_render_screen(self):
        with grid_lock:
            self.move_snake()
        self.render_screen()

    def move_snake(self):
        grid = self.grid

        new_grid: Grid = [
            [Cell() for _ in range(self.col_count)] for _ in range(self.row_count)
        ]

        for i, row in enumerate(grid):
            for j, cell in enumerate(row):
                if cell.is_empty():
                    continue

                assert cell.moving is not None, f"({i}, {j}) -> {cell.value}"

                next_x, next_y = next_location(
                    self.row_count, self.col_count, i, j, cell.moving
                )
                new_grid[next_x][next_y].value = cell.value
                if cell.is_body():
                    new_grid[next_x][next_y].moving = grid[next_x][next_y].moving
                else:  # head
                    new_grid[next_x][next_y].moving = cell.moving
                    new_head = new_grid[next_x][next_y]

        self.update_grid_and_head(new_grid, new_head)

    def refresh_game_state(self):
        while True:
            time.sleep(self.sleep_time)
            self.move_snake_and_render_screen()

    def render_screen(self):
        """Render the screen"""
        clear_screen()
        # render borders.
        print("_" * (self.col_count + 2))
        # render each element
        for i, row in enumerate(self.grid):
            row_contents = "".join([cell.value for cell in row])
            if i == self.row_count - 1:
                row_contents = row_contents.replace(EMPTY, "_")
            print(f"|{row_contents}|")

    def take_input(self):
        # There is an issue, that `a` key is not being read.
        # direction_mapping = {
        #     "w": Direction.UP,
        #     "a": Direction.LEFT,
        #     "s": Direction.DOWN,
        #     "d": Direction.RIGHT,
        # }
        direction_mapping = {
            "k": Direction.UP,
            "h": Direction.LEFT,
            "j": Direction.DOWN,
            "l": Direction.RIGHT,
        }

        with single_char_input_mode():
            while True:
                try:
                    c = sys.stdin.read(1)
                    if c == "q":
                        sys.exit(0)
                    new_direction = direction_mapping[c]
                    head = self.head
                    assert head.moving is not None
                    if (
                        new_direction != head.moving
                        and new_direction != head.moving.opposite
                    ):
                        head.moving = new_direction
                        self.move_snake_and_render_screen()
                except (IOError, KeyError):
                    pass


def clear_screen():
    os.system("clear")


def next_location(
    row_count: int, col_count: int, x: int, y: int, direction: Direction
) -> tuple[int, int]:
    """ Find the next location of the cell as per the direction

    Args:
        row_count: Number of horizontal rows in the game
        col_count: Number of vertical rows in the game
        x: X-coordinate
        y: Y-coordinate
        direction: Current direction

    Returns:
        Next coordinate of the cell
    """
    next_x = x
    next_y = y
    match direction:
        case Direction.LEFT:
            next_y = (next_y - 1) % col_count
        case Direction.RIGHT:
            next_y = (next_y + 1) % col_count
        case Direction.DOWN:
            next_x = (next_x + 1) % row_count
        case Direction.UP:
            next_x = (next_x - 1) % row_count

    return (next_x, next_y)
