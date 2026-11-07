import random
from time import monotonic
import unittest

from ai_engine import DIFFICULTIES, candidate_moves, choose_move
from game_logic import AI, DIRECTIONS, HUMAN, SIZE, Game, create_board, is_valid_move, legal_moves
from test_game_logic import draw_board


class AITests(unittest.TestCase):
    def test_custom_sizes_center_block_and_win(self):
        for size in (5, 15, 20):
            for difficulty in DIFFICULTIES:
                with self.subTest(size=size, difficulty=difficulty):
                    self.assertEqual(choose_move(create_board(size), difficulty, time_limit=0), (size // 2, size // 2))
                    board = create_board(size)
                    board[size - 1][size - 1] = HUMAN
                    self.assertTrue(is_valid_move(board, *choose_move(board, difficulty, time_limit=0.02)))
                    self.assertIsNone(choose_move(draw_board(size), difficulty))
                    if difficulty != "Dễ":
                        for player in (HUMAN, AI):
                            board = create_board(size)
                            board[size - 1][size - 4:] = [player] * 4
                            self.assertEqual(choose_move(board, difficulty), (size - 1, size - 5))

    def test_empty_center_and_full_board(self):
        for difficulty in DIFFICULTIES:
            with self.subTest(difficulty=difficulty):
                self.assertEqual(choose_move(create_board(), difficulty, time_limit=0.01), (5, 5))
                self.assertIsNone(choose_move(draw_board(), difficulty))

    def test_medium_hard_win_and_block_in_all_directions(self):
        for difficulty in ("Vừa", "Khó"):
            for player in (AI, HUMAN):
                for dr, dc in DIRECTIONS:
                    with self.subTest(difficulty=difficulty, player=player, direction=(dr, dc)):
                        board = create_board()
                        start = (0, 9) if dc < 0 else (0, 0)
                        for i in range(4):
                            board[start[0] + i * dr][start[1] + i * dc] = player
                        before = [row[:] for row in board]
                        self.assertEqual(choose_move(board, difficulty), (start[0] + 4 * dr, start[1] + 4 * dc))
                        self.assertEqual(board, before)

    def test_win_has_priority_over_block(self):
        for difficulty in ("Vừa", "Khó"):
            board = create_board()
            board[0][:4] = [AI] * 4
            board[9][:4] = [HUMAN] * 4
            self.assertEqual(choose_move(board, difficulty), (0, 4))

    def test_easy_only_uses_adjacent_empty_cells(self):
        board = create_board()
        board[0][0] = HUMAN
        self.assertEqual(set(candidate_moves(board)), {(0, 1), (1, 0), (1, 1)})
        for _ in range(20):
            self.assertIn(choose_move(board, "Dễ"), candidate_moves(board))

    def test_one_remaining_square(self):
        board = draw_board()
        board[9][9] = ""
        for difficulty in DIFFICULTIES:
            self.assertEqual(choose_move(board, difficulty), (9, 9))

    def test_timeout_keeps_board_and_returns_legal_fallback(self):
        board = create_board()
        for r, c, p in ((5, 5, HUMAN), (5, 6, AI), (4, 6, HUMAN), (6, 6, AI)):
            board[r][c] = p
        before = [row[:] for row in board]
        for budget in (0, 0.01, 0.08):
            start = monotonic()
            self.assertTrue(is_valid_move(board, *choose_move(board, "Khó", time_limit=budget)))
            self.assertLess(monotonic() - start, budget + 0.5)
            self.assertEqual(board, before)

    def test_hard_finds_open_four(self):
        board = create_board()
        board[5][3:6] = [AI] * 3
        board[0][0] = HUMAN
        self.assertIn(choose_move(board, "Khó"), ((5, 2), (5, 6)))

    def test_complete_games_never_overwrite_or_continue_after_finish(self):
        rng = random.Random(810)
        for difficulty in DIFFICULTIES:
            game = Game(difficulty=difficulty)
            while not game.finished:
                player = game.turn
                move = rng.choice(legal_moves(game.board)) if player == HUMAN else choose_move(game.board, difficulty, time_limit=0.02)
                self.assertIsNotNone(move)
                self.assertTrue(game.play(*move, player))
                self.assertLessEqual(len(game.history), SIZE * SIZE)
                self.assertEqual(len({(r, c) for r, c, _ in game.history}), len(game.history))
            self.assertFalse(game.play(0, 0, game.turn))


if __name__ == "__main__":
    unittest.main()
