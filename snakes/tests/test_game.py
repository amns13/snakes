from unittest import TestCase

from snakes.game import HEAD, Direction, Game, next_location


class NextLocationTestCase(TestCase):
    """Test cases for next location finding logic"""

    def test_next_location_when_direction_is_up(self):
        """Test next_location for direction up"""
        result = next_location(10, 10, 5, 5, Direction.UP)
        self.assertTupleEqual((4, 5), result)

    def test_next_location_when_direction_is_up_on_boundary(self):
        """Test next_location for direction up when on boundary"""
        result = next_location(10, 10, 0, 5, Direction.UP)
        self.assertTupleEqual((9, 5), result)

    def test_next_location_when_direction_is_down(self):
        """Test next_location for direction down"""
        result = next_location(10, 10, 5, 5, Direction.DOWN)
        self.assertTupleEqual((6, 5), result)

    def test_next_location_when_direction_is_down_on_boundary(self):
        """Test next_location for direction down when on boundary"""
        result = next_location(10, 10, 9, 5, Direction.DOWN)
        self.assertTupleEqual((0, 5), result)

    def test_next_location_when_direction_is_left(self):
        """Test next_location for direction left"""
        result = next_location(10, 10, 5, 5, Direction.LEFT)
        self.assertTupleEqual((5, 4), result)

    def test_next_location_when_direction_is_left_on_boundary(self):
        """Test next_location for direction left on boundary"""
        result = next_location(10, 10, 5, 0, Direction.LEFT)
        self.assertTupleEqual((5, 9), result)

    def test_next_location_when_direction_is_right(self):
        """Test next_location for direction right"""
        result = next_location(10, 10, 5, 5, Direction.RIGHT)
        self.assertTupleEqual((5, 6), result)

    def test_next_location_when_direction_is_right_on_boundary(self):
        """Test next_location for direction right on boundary"""
        result = next_location(10, 10, 5, 9, Direction.RIGHT)
        self.assertTupleEqual((5, 0), result)


class GameTest(TestCase):
    def test_game_initiated_grid_and_head_are_valid(self):
        game = Game(5, 5)
        self.assertEqual(5, len(game.grid))
        for row in game.grid:
            self.assertEqual(5, len(row))
        self.assertIsNotNone(game.head)
        self.assertEqual(HEAD, game.head.value)
        self.assertIsNotNone(game.head.moving)
