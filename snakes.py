import threading

from src.screen import Game


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
