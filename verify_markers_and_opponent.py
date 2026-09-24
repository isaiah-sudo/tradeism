import time
from ui.app import DayTradeSimApp
from network.firebase_manager import FirebaseManager

def verify_all_features():
    print("--- 1. Testing Trade Markers & Floating Notifications ---")
    app = DayTradeSimApp(mode="solo")
    app.update()

    # Select stock
    stock = app.engine.stocks["NVXP"]
    initial_markers_count = len(stock.trade_markers)
    print(f"Initial NVXP markers: {initial_markers_count}")

    # Buy 50 shares
    app.trading_panel._set_qty(50)
    app.trading_panel.do_buy()
    app.update()

    # Verify marker recorded
    assert len(stock.trade_markers) == initial_markers_count + 1, "Trade marker should be added on Buy"
    latest_marker = stock.trade_markers[-1]
    assert latest_marker.action == "BUY"
    assert latest_marker.shares == 50
    print(f"Marker Verified: {latest_marker.action} +{latest_marker.shares} @ ${latest_marker.price:.2f}")

    # Verify chart notification active
    assert app.chart.active_notification is not None, "Chart should have active notification"
    assert app.chart.active_notification["action"] == "BUY"
    assert app.chart.active_notification["shares"] == 50
    print("Floating on-chart notification verified:", app.chart.active_notification)

    # Verify position line on chart
    assert app.chart.position is not None, "Chart should track active position"
    assert app.chart.position.shares == 50, f"Expected 50 shares, got {app.chart.position.shares}"
    print(f"Active Position Guide Line Verified: {app.chart.position.side} {app.chart.position.shares} shs @ ${app.chart.position.avg_price:.2f}")

    # --- 2. Testing Percentage Presets & Nudges ---
    print("\n--- 2. Testing Quantity Presets & Nudges ---")
    app.trading_panel._set_pct_cash(0.50)  # 50%
    qty_50pct = app.trading_panel._get_qty()
    assert qty_50pct > 0, "50% cash should yield > 0 shares"
    print(f"50% cash preset verified: {qty_50pct} shares")

    app.trading_panel._nudge_qty(10)
    assert app.trading_panel._get_qty() == qty_50pct + 10, "Nudge +10 should add 10 shares"
    print(f"Nudge +10 verified: {app.trading_panel._get_qty()} shares")

    app.trading_panel._nudge_qty(-100)
    assert app.trading_panel._get_qty() >= 0, "Nudge -100 should clamp to >= 0"
    print(f"Nudge -100 verified: {app.trading_panel._get_qty()} shares")

    # --- 3. Testing Position Reversal & Short Logic ---
    print("\n--- 3. Testing Position Reversal & Short Logic ---")
    # We are currently LONG 50 shares
    pos = app.engine.positions["NVXP"]
    assert pos.shares == 50
    print(f"Current position before reverse: {pos.side} {pos.shares}")

    app.trading_panel.do_reverse()
    app.update()
    pos = app.engine.positions["NVXP"]
    assert pos.shares == -50, f"Expected SHORT 50 (-50), got {pos.shares}"
    assert pos.side == "SHORT"
    print(f"Reversed Position Verified: {pos.side} {pos.shares} shs")

    # Verify short marker added
    assert stock.trade_markers[-1].action == "SHORT"
    print(f"Short marker verified: {stock.trade_markers[-1]}")

    app.destroy()

    # --- 4. Testing Opponent Accuracy in Online Mode ---
    print("\n--- 4. Testing Opponent Accuracy in 1v1 Online Mode ---")
    fb = FirebaseManager()
    fb.sign_in_anonymous("OnlineTester")
    match_id = f"test_verif_{int(time.time())}"
    fb.active_match_id = match_id
    fb.player_slot = "player1"

    # Seed room with opponent initial data
    fb._firestore_set(f"matches/{match_id}", {
        "match_id": match_id,
        "seed": 777123,
        "player1": {"name": "OnlineTester", "equity": 25000.0, "pnl": 0.0, "pnl_pct": 0.0},
        "player2": {"name": "RivalPlayer_99", "equity": 26450.50, "pnl": 1450.50, "pnl_pct": 5.80}
    }, merge=False)

    match_data = {
        "match_id": match_id,
        "seed": 777123,
        "duration_seconds": 180,
        "start_time": time.time(),
        "opponent": {
            "name": "RivalPlayer_99",
            "equity": 26450.50,
            "pnl": 1450.50,
            "pnl_pct": 5.80
        }
    }
    app_online = DayTradeSimApp(mode="online", match_data=match_data, fb_manager=fb)
    app_online.update()

    # Simulate metric sync: I update my equity to 27,000, and receive opponent's 26,450.50
    opp_metrics = fb.update_player_metrics(27000.0, 2000.0, 8.0)
    assert opp_metrics is not None, "Failed to get opponent metrics"
    print(f"Opponent metrics returned from sync: {opp_metrics}")
    assert opp_metrics["equity"] == 26450.50, f"Expected 26450.50, got {opp_metrics['equity']}"

    # Verify latest opponent metrics method returns accurate fresh score
    latest_opp = fb.get_latest_opponent_metrics()
    assert latest_opp is not None, "get_latest_opponent_metrics returned None"
    print(f"Freshest Opponent Final Metrics: {latest_opp}")
    assert latest_opp["equity"] == 26450.50

    # Also test SimulatedOpponentBot accuracy
    bot_fb = FirebaseManager()
    from network.firebase_manager import SimulatedOpponentBot
    bot_fb.opponent_bot = SimulatedOpponentBot(name="WallSt_Titan")
    bot_metrics = bot_fb.update_player_metrics(25000.0, 0.0, 0.0)
    print(f"Bot opponent metrics: {bot_metrics}")
    assert bot_metrics["name"] == "WallSt_Titan"
    assert "equity" in bot_metrics

    app_online.destroy()
    print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    verify_all_features()
