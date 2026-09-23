import time
from network.firebase_manager import FirebaseManager
from ui.mode_select import ModeSelectWindow
from ui.battle_panel import BattleHUD, MatchEndDialog
from ui.app import DayTradeSimApp

def verify_multiplayer():
    print("--- 1. Testing FirebaseManager & Bot Fallback ---")
    fb = FirebaseManager()
    print(f"Is configured with credentials: {fb.is_configured} (Mock/Bot mode: {fb.is_mock_mode})")

    # Test Anonymous Sign In
    ok, msg = fb.sign_in_anonymous("DiamondTester")
    assert ok, f"Sign in failed: {msg}"
    print(f"Auth Success: user_id={fb.user_id}, name={fb.display_name}")

    # Test Matchmaking
    import threading
    cancel_ev = threading.Event()
    match_data = fb.find_match(cancel_ev)
    assert match_data is not None, "Matchmaking failed to produce match data"
    assert "seed" in match_data, "Missing seed in match data"
    assert "opponent" in match_data, "Missing opponent in match data"
    print(f"Match found! Opponent: {match_data['opponent']['name']}, Seed: {match_data['seed']}")

    # Test Metric Updates
    metrics = fb.update_player_metrics(26500.0, 1500.0, 6.0)
    assert metrics is not None, "Failed to get opponent metrics"
    print(f"Opponent live metrics: {metrics}")

    print("\n--- 2. Testing ModeSelectWindow Layout ---")
    launcher = ModeSelectWindow(
        on_start_solo=lambda: None,
        on_start_online=lambda m, f: None
    )
    launcher.update()
    assert launcher.ent_nickname.get() != "", "Nickname entry should be prefilled"
    print("ModeSelectWindow rendered successfully.")
    launcher.destroy()

    print("\n--- 3. Testing 1v1 Online App & BattleHUD ---")
    app = DayTradeSimApp(
        mode="online",
        match_data=match_data,
        fb_manager=fb
    )
    app.update()
    assert app.battle_hud is not None, "BattleHUD should be active in online mode"
    print("Online Duel window rendered with BattleHUD.")

    # Test initial HUD display
    app.battle_hud.update_scores(25000.0, 0.0, 0.0, metrics)
    app.update()
    leader_txt = app.battle_hud.lbl_leader.cget('text').encode('ascii', errors='replace').decode('ascii')
    print(f"HUD Leader text: {leader_txt}")

    # Execute a trade in online mode and verify HUD reflection
    print("Executing BUY in 1v1 duel...")
    app.trading_panel._set_qty(50)
    app.trading_panel.do_buy()
    app.update()

    # Step simulation
    for _ in range(5):
        app.engine.step()
        app.chart.draw()
        app.update()

    eq = app.engine.total_equity
    pnl = app.engine.total_pnl
    pnl_pct = app.engine.total_pnl_pct
    print(f"Trader Equity after tick: ${eq:,.2f} ({pnl_pct:+.2f}%)")

    # Update HUD with higher equity -> verify lead badge
    app.battle_hud.update_scores(28000.0, 3000.0, 12.0, {"equity": 24000.0, "pnl": -1000.0, "pnl_pct": -4.0, "name": "Opponent"})
    app.update()
    assert "YOU LEAD" in app.battle_hud.lbl_leader.cget("text"), f"Expected YOU LEAD, got: {app.battle_hud.lbl_leader.cget('text')}"
    leader_badge = app.battle_hud.lbl_leader.cget('text').encode('ascii', errors='replace').decode('ascii')
    print(f"Verified Leader Badge: {leader_badge}")

    # Test Omegle Re-Pairing
    print("Testing Omegle Re-Pairing to next opponent...")
    new_match_data = {
        "match_id": "test_m2",
        "seed": 999123,
        "duration_seconds": 180,
        "start_time": time.time(),
        "opponent": {"name": "NextOpponent_42", "equity": 25000.0, "pnl": 0.0, "pnl_pct": 0.0}
    }
    dummy_top = type("Dummy", (), {"destroy": lambda s: None})()
    app._apply_new_match(dummy_top, new_match_data)
    app.update()
    assert app.battle_hud.opponent_name == "NextOpponent_42", f"Opponent name not updated: {app.battle_hud.opponent_name}"
    print(f"Re-paired successfully with: {app.battle_hud.opponent_name}!")

    # Test MatchEndDialog
    print("Testing MatchEndDialog...")
    dialog = MatchEndDialog(
        app,
        my_equity=27500.0,
        opp_equity=24000.0,
        my_name="Tester",
        opp_name="NextOpponent_42",
        on_next=lambda: None,
        on_menu=lambda: None
    )
    dialog.update()
    dialog.destroy()
    print("MatchEndDialog verified.")

    # Clean shutdown
    if app._loop_job:
        app.after_cancel(app._loop_job)
    app.destroy()
    print("\n>>> ALL MULTIPLAYER & ONLINE TESTS PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    verify_multiplayer()
