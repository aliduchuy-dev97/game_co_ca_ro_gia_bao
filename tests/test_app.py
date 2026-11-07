"""Chạy giao diện Streamlit thật bằng AppTest, không cần trình duyệt."""

from pathlib import Path
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from game_logic import AI, HUMAN, MODE_AI, MODE_PVP, Game, create_board
from test_game_logic import draw_board

APP = str(Path(__file__).resolve().parents[1] / "app.py")


class AppTests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(APP, default_timeout=15).run()
        self.assertFalse(self.app.exception)

    def cell(self, row, col):
        game = self.app.session_state.game
        prefix = f"cell_{game.game_id}_{len(game.history)}_{row}_{col}_"
        return next(button for button in self.app.button if button.key.startswith(prefix))

    def test_player_ai_and_unrelated_reruns(self):
        self.cell(5, 5).click().run()
        self.assertFalse(self.app.exception)
        game = self.app.session_state.game
        self.assertEqual([p for _, _, p in game.history], [HUMAN, AI])
        self.assertTrue(self.cell(5, 5).disabled)
        self.app.run().run()
        self.assertEqual(len(self.app.session_state.game.history), 2)
        self.app.selectbox(key="next_difficulty").select("Khó").run()
        self.assertEqual(self.app.session_state.game.difficulty, "Vừa")
        self.assertEqual(len(self.app.session_state.game.history), 2)

    def test_replay_new_game_and_score_retention(self):
        self.cell(0, 0).click().run()
        self.app.session_state.stats = {"wins": 2, "losses": 1, "draws": 3}
        self.app.selectbox(key="next_difficulty").select("Khó").run()
        self.app.button(key="replay").click().run()
        self.assertEqual(self.app.session_state.game.difficulty, "Vừa")
        self.assertEqual(self.app.session_state.game.history, [])
        self.app.button(key="new_game").click().run()
        self.assertEqual(self.app.session_state.game.difficulty, "Khó")
        self.assertEqual(self.app.session_state.game.game_id, 2)
        self.assertEqual(self.app.session_state.stats, {"wins": 2, "losses": 1, "draws": 3})

    def test_human_win_locks_board_counts_once_and_skips_ai(self):
        game = Game()
        game.board[0][:4] = [HUMAN] * 4
        game.history = [(0, i, HUMAN) for i in range(4)]
        self.app.session_state.game = game
        self.app.run()
        self.cell(0, 4).click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.session_state.game.winner, HUMAN)
        self.assertEqual(len(self.app.session_state.game.history), 5)
        self.assertEqual(len(self.app.session_state.game.winning_cells), 5)
        self.assertTrue(all(button.disabled for button in self.app.button if button.key.startswith("cell_")))
        self.app.run().run()
        self.assertEqual(self.app.session_state.stats["wins"], 1)

    def test_ai_win_counts_once(self):
        board = create_board()
        board[9][:4] = [AI] * 4
        self.app.session_state.game = Game(board=board, turn=AI)
        self.app.run().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.session_state.game.winner, AI)
        self.assertEqual(self.app.session_state.stats["losses"], 1)

    def test_draw_counts_once(self):
        board = draw_board()
        turn = board[9][9]
        board[9][9] = ""
        self.app.session_state.game = Game(board=board, turn=turn)
        self.app.run()
        if turn == HUMAN:
            self.cell(9, 9).click().run()
        self.app.run()
        self.assertFalse(self.app.exception)
        self.assertTrue(self.app.session_state.game.finished)
        self.assertIsNone(self.app.session_state.game.winner)
        self.assertEqual(self.app.session_state.stats["draws"], 1)

    def test_fast_click_from_old_render_is_ignored(self):
        stale_button = self.cell(0, 1)
        self.cell(0, 0).click().run()
        stale_button.click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(len(self.app.session_state.game.history), 2)

    def test_custom_size_applies_on_new_game_and_replay_keeps_current_size(self):
        self.cell(0, 0).click().run()
        self.app.selectbox(key="next_board_size").select(15).run()
        self.assertEqual(len(self.app.session_state.game.board), 10)
        self.assertEqual(len(self.app.session_state.game.history), 2)
        self.app.button(key="new_game").click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(len(self.app.session_state.game.board), 15)
        self.assertEqual(sum(b.key.startswith("cell_") for b in self.app.button), 225)
        self.cell(14, 14).click().run()
        self.assertEqual(len(self.app.session_state.game.history), 2)
        self.app.selectbox(key="next_board_size").select(5).run()
        self.app.button(key="replay").click().run()
        self.assertEqual(len(self.app.session_state.game.board), 15)
        self.assertEqual(self.app.session_state.game.history, [])
        self.app.button(key="new_game").click().run()
        self.assertEqual(sum(b.key.startswith("cell_") for b in self.app.button), 25)
        self.assertEqual(len(self.app.session_state.game.board), 5)

    def test_largest_board_last_cell_and_rerun(self):
        self.app.selectbox(key="next_board_size").select(20).run()
        self.app.button(key="new_game").click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(sum(b.key.startswith("cell_") for b in self.app.button), 400)
        self.cell(19, 19).click().run()
        self.app.run()
        self.assertEqual(len(self.app.session_state.game.history), 2)
        self.assertEqual(self.app.session_state.game.board[19][19], HUMAN)

    def start_pvp(self):
        self.app.selectbox(key="next_mode").select(MODE_PVP).run()
        self.app.button(key="new_game").click().run()

    def test_pvp_alternates_one_move_per_click_without_ai(self):
        self.start_pvp()
        with patch("ai_engine.choose_move") as choose:
            for count, move in enumerate(((0, 0), (1, 0), (0, 1), (1, 1)), 1):
                self.cell(*move).click().run()
                self.assertFalse(self.app.exception)
                self.assertEqual(len(self.app.session_state.game.history), count)
                self.assertTrue(self.cell(*move).disabled)
            self.app.run().run()
            choose.assert_not_called()
        self.assertEqual([p for _, _, p in self.app.session_state.game.history], [HUMAN, AI, HUMAN, AI])
        self.assertEqual(self.app.session_state.game.turn, HUMAN)
        self.assertEqual(self.app.session_state.stats, {"wins": 0, "losses": 0, "draws": 0})

    def test_mode_changes_only_on_new_game_and_replay_keeps_mode(self):
        self.app.selectbox(key="next_mode").select(MODE_PVP).run()
        self.assertEqual(self.app.session_state.game.mode, MODE_AI)
        self.assertTrue(self.app.selectbox(key="next_difficulty").disabled)
        self.app.button(key="new_game").click().run()
        self.cell(0, 0).click().run()
        self.assertEqual(len(self.app.session_state.game.history), 1)
        self.app.selectbox(key="next_mode").select(MODE_AI).run()
        self.assertEqual(self.app.session_state.game.mode, MODE_PVP)
        self.assertEqual(len(self.app.session_state.game.history), 1)
        self.app.button(key="replay").click().run()
        self.assertEqual(self.app.session_state.game.mode, MODE_PVP)
        self.assertEqual(self.app.session_state.game.history, [])
        self.app.button(key="new_game").click().run()
        self.assertEqual(self.app.session_state.game.mode, MODE_AI)
        self.cell(0, 0).click().run()
        self.assertEqual(len(self.app.session_state.game.history), 2)

    def test_pvp_both_players_win_lock_board_and_count_once(self):
        for winner in (HUMAN, AI):
            with self.subTest(winner=winner):
                previous_id = self.app.session_state.game.game_id
                self.app.session_state.game = Game(board=create_board(5), mode=MODE_PVP, game_id=previous_id + 1)
                self.app.run()
                if winner == HUMAN:
                    sequence = [(r, c) for c in range(4) for r in (0, 1)] + [(0, 4)]
                else:
                    sequence = [(r, c) for c in range(4) for r in (1, 0)] + [(4, 4), (0, 4)]
                for move in sequence:
                    self.cell(*move).click().run()
                self.assertFalse(self.app.exception)
                self.assertEqual(self.app.session_state.game.winner, winner)
                self.assertEqual(len(self.app.session_state.game.winning_cells), 5)
                self.assertTrue(all(b.disabled for b in self.app.button if b.key.startswith("cell_")))
                self.app.run().run()
                self.assertEqual(self.app.session_state.pvp_stats[winner], 1)
                self.assertEqual(self.app.session_state.stats, {"wins": 0, "losses": 0, "draws": 0})

    def test_pvp_draw_on_os_click_counts_once(self):
        board = draw_board(5)
        self.assertEqual(board[4][3], AI)
        board[4][3] = ""
        self.app.session_state.game = Game(board=board, mode=MODE_PVP, turn=AI)
        self.app.run()
        self.assertFalse(self.cell(4, 3).disabled)
        self.cell(4, 3).click().run()
        self.app.run()
        self.assertTrue(self.app.session_state.game.finished)
        self.assertIsNone(self.app.session_state.game.winner)
        self.assertEqual(self.app.session_state.pvp_stats["draws"], 1)
        self.assertEqual(self.app.session_state.stats["draws"], 0)

    def test_pvp_stale_click_cannot_play_for_the_next_player(self):
        self.start_pvp()
        stale = self.cell(0, 1)
        self.cell(0, 0).click().run()
        stale.click().run()
        self.assertEqual(len(self.app.session_state.game.history), 1)
        self.assertEqual(self.app.session_state.game.turn, AI)
        self.cell(1, 0).click().run()
        self.assertEqual(self.app.session_state.game.history[-1], (1, 0, AI))

    def test_scoreboards_remain_separate_when_switching_modes(self):
        self.app.session_state.stats = {"wins": 2, "losses": 1, "draws": 3}
        self.app.session_state.pvp_stats = {HUMAN: 4, AI: 5, "draws": 6}
        self.start_pvp()
        self.assertEqual([m.value for m in self.app.metric], ["4", "5", "6", "0"])
        self.app.selectbox(key="next_mode").select(MODE_AI).run()
        self.app.button(key="new_game").click().run()
        self.assertEqual([m.value for m in self.app.metric], ["2", "1", "3", "0"])
        self.start_pvp()
        self.assertEqual([m.value for m in self.app.metric], ["4", "5", "6", "0"])


if __name__ == "__main__":
    unittest.main()
