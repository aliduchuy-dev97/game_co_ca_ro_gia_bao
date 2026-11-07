"""Kiểm thử luật bằng thư viện unittest có sẵn trong Python."""

import unittest

from game_logic import AI, DIRECTIONS, HUMAN, SIZE, Game, check_win, create_board, is_draw, is_valid_move, legal_moves


def draw_board(size=SIZE):
    # Mỗi hướng chỉ có tối đa 2 quân cùng loại liên tiếp.
    return [[HUMAN if (r + 2 * c) % 4 < 2 else AI for c in range(size)] for r in range(size)]


class GameLogicTests(unittest.TestCase):
    def test_custom_sizes_edges_and_draws(self):
        for size in (5, 8, 15, 20):
            with self.subTest(size=size):
                board = create_board(size)
                self.assertEqual(len(board), size)
                self.assertTrue(all(len(row) == size for row in board))
                game = Game(board=board)
                self.assertTrue(game.play(size - 1, size - 1, HUMAN))
                self.assertFalse(game.play(size, 0, AI))
                for col in range(size - 5, size):
                    board[size - 1][col] = HUMAN
                self.assertEqual(len(check_win(board, size - 1, size - 1)), 5)
                self.assertTrue(is_draw(draw_board(size)))

    def test_invalid_sizes(self):
        for size in (0, 4, 21, -1, 10.5, True, "10"):
            with self.subTest(size=size), self.assertRaises(ValueError):
                create_board(size)

    def test_new_board_rows_are_independent(self):
        board = create_board()
        board[0][0] = HUMAN
        self.assertEqual(board[1][0], "")
        self.assertEqual(len(legal_moves(board)), 99)

    def test_all_five_in_a_row_positions_and_last_moves(self):
        for player in (HUMAN, AI):
            for dr, dc in DIRECTIONS:
                for r in range(SIZE):
                    for c in range(SIZE):
                        cells = [(r + k * dr, c + k * dc) for k in range(5)]
                        if not all(0 <= nr < SIZE and 0 <= nc < SIZE for nr, nc in cells):
                            continue
                        with self.subTest(player=player, cells=cells):
                            board = create_board()
                            for nr, nc in cells:
                                board[nr][nc] = player
                            for nr, nc in cells:
                                self.assertEqual(set(check_win(board, nr, nc)), set(cells))

    def test_overline_and_blocked_ends_still_win(self):
        board = create_board()
        board[0] = [AI] + [HUMAN] * 6 + [AI, "", ""]
        self.assertEqual(len(check_win(board, 0, 3)), 6)

    def test_gap_four_and_empty_are_not_wins(self):
        board = create_board()
        for c in (0, 1, 2, 3, 5):
            board[9][c] = HUMAN
        self.assertFalse(check_win(board, 9, 2))
        self.assertFalse(check_win(board, 9, 4))
        self.assertFalse(check_win(board, -1, 0))

    def test_invalid_moves_do_not_change_state(self):
        game = Game()
        for r, c, player in ((-1, 0, HUMAN), (10, 0, HUMAN), (0, 10, HUMAN), (0, 0, AI), (0, 0, "Q")):
            self.assertFalse(game.play(r, c, player))
        self.assertTrue(game.play(0, 0, HUMAN))
        self.assertFalse(game.play(0, 0, AI))
        self.assertFalse(game.play(0, 1, HUMAN))
        self.assertEqual(len(game.history), 1)
        self.assertEqual(game.turn, AI)
        self.assertFalse(is_valid_move(game.board, -1, -1))

    def test_finished_game_locks_and_win_checked_before_full_board(self):
        board = [[HUMAN] * SIZE for _ in range(SIZE)]
        board[9][9] = ""
        game = Game(board=board)
        self.assertTrue(game.play(9, 9, HUMAN))
        self.assertTrue(game.finished)
        self.assertEqual(game.winner, HUMAN)
        self.assertFalse(game.play(0, 0, AI))
        self.assertFalse(is_draw(game.board))

    def test_full_board_draw(self):
        board = draw_board()
        self.assertTrue(is_draw(board))
        self.assertFalse(any(check_win(board, r, c) for r in range(SIZE) for c in range(SIZE)))
        last_player = board[9][9]
        board[9][9] = ""
        self.assertFalse(is_draw(board))
        game = Game(board=board, turn=last_player)
        self.assertTrue(game.play(9, 9, last_player))
        self.assertTrue(game.finished)
        self.assertIsNone(game.winner)


if __name__ == "__main__":
    unittest.main()
