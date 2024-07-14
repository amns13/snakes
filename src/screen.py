"""This file renders the game screen

Each cell in the grid has following attributes:
    - value [" ", "0", "#"]
        - Blank means that cell is empty
        - 0 depicts the body parts of the snake
        - # is the head of the snake
    - next direction
"""

import fcntl
import random
import os
import sys
import termios
import threading
import time
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import Optional


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
        try:
            ##########    BOILERPLATE TO ENABLE READING SINGLE CHARACTER FROM INPUT AT A TIME ##########
            # TODO: See if this can be converted into a context manager

            # This code block is to make sure that we can read one character input at a time without the need to click enter.
            # Ref: https://docs.python.org/2/faq/library.html#how-do-i-get-a-single-keypress-at-a-time

            # Get the file descriptor of standard input.
            # Ref: https://stackoverflow.com/a/32199696/9152588
            # Ref: https://en.wikipedia.org/wiki/File_descriptor
            fd = sys.stdin.fileno()

            # `termios` module provides an interface to unix tty.
            # Ref: https://docs.python.org/3/library/termios.html
            # Ref: https://manpages.debian.org/bookworm/manpages-dev/termios.3.en.html

            # Store the existing state of the tty/terminal
            oldterm = termios.tcgetattr(fd)

            newattr = termios.tcgetattr(fd)
            # Disable canonical mode. In noncanonical mode input is available immediately
            # without the user having to type a line-delimiter character.
            # Also, disable echo to prevent printing the user input in terminal.
            # Refer the termios documentation linked above.
            newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
            # Update the tty properties. `TCSANOW` flag makes the changes immediately.
            termios.tcsetattr(fd, termios.TCSANOW, newattr)

            # `fcntl` module provides an interface to unix fcntl. This allows to manipulate the file descriptor.
            # Ref: https://docs.python.org/3/library/fcntl.html
            # Ref: https://manpages.debian.org/bookworm/manpages-dev/fcntl.2.en.html
            oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
            # Set the standard input to non-blocking mode.
            # Ref: https://www.geeksforgeeks.org/non-blocking-io-with-pipes-in-c/
            fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)
            #######################################################

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
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
            fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)


def clear_screen():
    os.system("clear")


def next_location(
    row_count: int, col_count: int, x: int, y: int, direction: Direction
) -> tuple[int, int]:
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


def start_game(rows: int, cols: int):
    game = Game(row_count=rows, col_count=cols)
    # TODO: Remove asserts after test cases are added
    assert game.head.is_head()
    assert game.head is not None

    game.render_screen()
    game_loop = threading.Thread(target=game.refresh_game_state)
    user_input_loop = threading.Thread(target=game.take_input)
    game_loop.start()
    user_input_loop.start()


def main():
    start_game(10, 10)


if __name__ == "__main__":
    main()
