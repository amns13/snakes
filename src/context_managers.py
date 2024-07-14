import fcntl
import os
import sys
import termios
from contextlib import contextmanager


@contextmanager
def single_char_input_mode():
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

    try:
        yield
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
