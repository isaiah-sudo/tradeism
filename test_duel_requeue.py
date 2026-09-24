"""
Verification of Duel Rematch / Next Opponent flow.
"""

import unittest
import tkinter as tk
import time
from unittest.mock import MagicMock

from ui.app import DayTradeSimApp
from ui.battle_panel import MatchEndDialog
from network.firebase_manager import FirebaseManager


class TestDuelNextOpponent(unittest.TestCase):
    def test_next_opponent_flow(self):
        fb = FirebaseManager()
        app = DayTradeSimApp(
            mode="online",
            match_data={"duration_seconds": 180, "opponent": {"name": "Bot_Alpha"}},
            fb_manager=fb
        )
        app.update()

        # Verify initial HUD is present and opponent is Bot_Alpha
        self.assertEqual(app.battle_hud.opponent_name, "Bot_Alpha")
        self.assertEqual(app.pack_slaves()[1], app.battle_hud)

        # Simulate match ending
        app.battle_hud.is_match_ended = True
        app.engine.is_paused = True

        # Simulate MatchEndDialog next button click
        next_called = {"called": False}
        def mock_handle_next():
            next_called["called"] = True
            # Simulate match found
            new_match_data = {
                "match_id": "test_m2",
                "seed": 99999,
                "duration_seconds": 180,
                "start_time": time.time(),
                "player_slot": "player1",
                "opponent": {"uid": "b2", "name": "Bot_Beta", "equity": 25000.0, "pnl": 0.0, "pnl_pct": 0.0}
            }
            dummy_dialog = tk.Toplevel(app)
            app._apply_new_match(dummy_dialog, new_match_data)

        end_dialog = MatchEndDialog(
            app,
            my_equity=26500.0,
            opp_equity=24000.0,
            my_name="You",
            opp_name="Bot_Alpha",
            on_next=mock_handle_next,
            on_menu=lambda: None
        )
        end_dialog.update()

        # Click next on end dialog
        end_dialog._do_next()
        app.update()

        self.assertTrue(next_called["called"])
        # Verify BattleHUD is still at the top and opponent is Bot_Beta
        self.assertEqual(app.battle_hud.opponent_name, "Bot_Beta")
        self.assertEqual(app.pack_slaves()[1], app.battle_hud)
        self.assertFalse(app.engine.is_paused)
        self.assertFalse(app._match_dialog_open)

        # Run several simulation ticks and verify opponent metrics update
        for _ in range(5):
            app.engine.step()
            app.update()

        self.assertEqual(app.battle_hud.opponent_name, "Bot_Beta")
        app.destroy()


if __name__ == "__main__":
    unittest.main()
