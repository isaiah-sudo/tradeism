import sys
from ui.app import DayTradeSimApp

def test_hotkeys_and_max():
    print("Initializing DayTradeSimApp...", flush=True)
    app = DayTradeSimApp()
    app.update()

    # 1. Test MAX CASH
    stock = app.engine.stocks["NVXP"]
    price = stock.price
    cash = app.engine.cash
    expected_max = int(cash // price)
    print(f"Testing MAX CASH for NVXP @ ${price:.2f} with cash ${cash:,.2f}...", flush=True)
    app.trading_panel._set_max_cash()
    app.update()
    actual_qty = app.trading_panel._get_qty()
    assert actual_qty == expected_max, f"Expected {expected_max}, got {actual_qty}"
    print(f"MAX CASH correctly calculated: {actual_qty} shares.", flush=True)

    # 2. Buy a specific amount to test ALL POS
    app.trading_panel._set_qty(75)
    app.trading_panel.do_buy()
    app.update()
    pos = app.engine.positions["NVXP"]
    assert pos.shares == 75, f"Expected 75 shares, got {pos.shares}"
    print("Bought 75 shares of NVXP.", flush=True)

    # Change quantity to something else, then test ALL POS
    app.trading_panel._set_qty(10)
    app.trading_panel._set_all_pos()
    app.update()
    assert app.trading_panel._get_qty() == 75, f"Expected 75 from ALL POS, got {app.trading_panel._get_qty()}"
    print("ALL POS correctly set quantity to 75.", flush=True)

    # 3. Test Smart MAX toggle
    app.trading_panel._set_qty(10)
    app.trading_panel._set_max_qty()  # Should set to 75 (position size)
    assert app.trading_panel._get_qty() == 75
    app.trading_panel._set_max_qty()  # Clicked again -> should set to max cash
    assert app.trading_panel._get_qty() == int(app.engine.cash // stock.price)
    print("Smart MAX toggle verified.", flush=True)

    # 4. Test hotkey while focused in Shares Entry
    print("Testing B/S hotkeys while focused inside ent_shares...", flush=True)
    app.trading_panel.ent_shares.focus_set()
    app.update()
    # Trigger Buy via ent_shares event
    app.trading_panel._set_qty(15)
    app.trading_panel.ent_shares.event_generate("<Key-b>")
    app.update()
    assert app.engine.positions["NVXP"].shares == 90, f"Expected 90 shares, got {app.engine.positions['NVXP'].shares}"
    print("Hotkeys inside shares entry verified (bought 15 shares using 'b').", flush=True)

    # Trigger Sell via ent_shares event
    app.trading_panel._set_qty(40)
    app.trading_panel.ent_shares.event_generate("<Key-s>")
    app.update()
    assert app.engine.positions["NVXP"].shares == 50, f"Expected 50 shares, got {app.engine.positions['NVXP'].shares}"
    print("Hotkeys inside shares entry verified (sold 40 shares using 's').", flush=True)

    # 5. Test Function Keys & Alt hotkeys while focused inside Search Entry
    print("Testing F1 / F2 / Alt hotkeys while focused in Search Entry...", flush=True)
    app.watchlist.ent_search.focus_set()
    app.watchlist.ent_search.insert(0, "searching...")
    app.update()

    # Trigger F1 (Buy)
    app.trading_panel._set_qty(10)
    app.event_generate("<F1>")
    app.update()
    assert app.engine.positions["NVXP"].shares == 60, f"Expected 60 shares after F1, got {app.engine.positions['NVXP'].shares}"
    print("F1 Buy while in search box verified (shares now 60).", flush=True)

    # Trigger F2 (Sell)
    app.trading_panel._set_qty(20)
    app.event_generate("<F2>")
    app.update()
    assert app.engine.positions["NVXP"].shares == 40, f"Expected 40 shares after F2, got {app.engine.positions['NVXP'].shares}"
    print("F2 Sell while in search box verified (shares now 40).", flush=True)

    # Clean up and exit
    if app._loop_job:
        app.after_cancel(app._loop_job)
    app.destroy()
    print("ALL TESTS PASSED SUCCESSFULLY!", flush=True)

if __name__ == "__main__":
    test_hotkeys_and_max()
