"""This file renders the game screen

Each cell in the grid has following attributes:
    - value [" ", "0", "#"]
        - Blank means that cell is empty
        - 0 depicts the body parts of the snake
        - # is the head of the snake
    - next direction
"""

import fcntl
from functools import cached_property
import os
import sys
import termios
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional

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

GRID_COLS = 10
GRID_ROWS = 10


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


@dataclass
class Cell:
    """Class representing each cell in the game grid

    Attributes:
        value: Cell content
        moving: Direction in which the current cell will move. None for empty cells.
    """

    value: str = " "
    moving: Optional[Direction] = None

    def __str__(self) -> str:
        return self.value

    def is_empty(self) -> bool:
        return self.value == " "

    def is_body(self) -> bool:
        return self.value == "0"

    def is_head(self) -> bool:
        return self.value == "#"


Row = list[Cell]
Grid = list[Row]


def clear_screen():
    os.system("clear")


def render_screen():
    """Render the screen"""
    global grid
    clear_screen()
    # render borders.
    print("-" * (GRID_COLS + 2))
    # render each element
    for row in grid:
        row_contents = "".join([cell.value for cell in row])
        print(f"|{row_contents}|")

    print("-" * (GRID_COLS + 2))


def update_head_direction(direction: Direction):
    global head
    with grid_lock:
        head.moving = direction


def next_location(x: int, y: int, direction: Direction) -> tuple[int, int]:
    next_x = x
    next_y = y
    match direction:
        case Direction.LEFT:
            next_y = (next_y - 1) % GRID_COLS
        case Direction.RIGHT:
            next_y = (next_y + 1) % GRID_COLS
        case Direction.DOWN:
            next_x = (next_x + 1) % GRID_ROWS
        case Direction.UP:
            next_x = (next_x - 1) % GRID_ROWS

    return (next_x, next_y)


def move_snake_and_render_screen():
    global grid
    with grid_lock:
        move_snake()
        render_screen()


def move_snake():
    global grid
    global head

    new_grid: Grid = [[Cell() for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            if cell.is_empty():
                continue

            assert cell.moving is not None, f"({i}, {j}) -> {cell.value}"

            next_x, next_y = next_location(i, j, cell.moving)
            new_grid[next_x][next_y].value = cell.value
            if cell.is_body():
                new_grid[next_x][next_y].moving = grid[next_x][next_y].moving
            else:  # head
                new_grid[next_x][next_y].moving = cell.moving
                head = new_grid[next_x][next_y]

    grid = new_grid


def refresh_game_state():
    sleep_time = 1.0
    while True:
        time.sleep(sleep_time)
        move_snake_and_render_screen()


def take_input():
    global head
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
        while True:
            try:
                c = sys.stdin.read(1)
                if c == "q":
                    sys.exit(0)
                new_direction = direction_mapping[c]
                if (
                    direction_mapping[c] != head.moving
                    and new_direction != head.moving.opposite
                ):
                    update_head_direction(new_direction)
                    move_snake_and_render_screen()
            except (IOError, KeyError):
                pass
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)


def main():
    global grid
    grid = [
        [Cell() for _ in range(10)],
        [
            Cell(),
            *[Cell("0", Direction.RIGHT) for _ in range(5)],
            Cell("0", Direction.DOWN),
            *[Cell() for _ in range(3)],
        ],
        [
            *[Cell() for _ in range(6)],
            Cell("0", Direction.DOWN),
            *[Cell() for _ in range(3)],
        ],
        [
            *[Cell() for _ in range(6)],
            Cell("0", Direction.DOWN),
            *[Cell() for _ in range(3)],
        ],
        [
            *[Cell() for _ in range(6)],
            Cell("#", Direction.DOWN),
            *[Cell() for _ in range(3)],
        ],
        [Cell() for _ in range(10)],
        [Cell() for _ in range(10)],
        [Cell() for _ in range(10)],
        [Cell() for _ in range(10)],
        [Cell() for _ in range(10)],
    ]

    global head
    head = grid[4][6]

    assert head.is_head()
    assert head.moving is not None

    render_screen()

    game_loop = threading.Thread(target=refresh_game_state)
    user_input_loop = threading.Thread(target=take_input)
    game_loop.start()
    user_input_loop.start()


if __name__ == "__main__":
    main()
