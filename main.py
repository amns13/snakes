import threading

from snakes.game import Game


def start_game(rows: int, cols: int):
    game = Game(row_count=rows, col_count=cols)

    game.render_screen()
    game_loop = threading.Thread(target=game.refresh_game_state)
    user_input_loop = threading.Thread(target=game.take_input)
    game_loop.start()
    user_input_loop.start()

    game_loop.join()
    user_input_loop.join()

    game.display_score()


def main():
    start_game(10, 10)


if __name__ == "__main__":
    main()
