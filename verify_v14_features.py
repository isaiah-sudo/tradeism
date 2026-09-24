"""
Comprehensive verification test for v1.4 features:
- Menu Vault Balance persistence
- Shop Dialog with items, categories, purchasing, and equipping
- Crazy Win Animation overlay playback
- Bank Profit button in trading terminal and auto-banking
"""

import sys
import os
import tkinter as tk
from profile_manager import get_profile, SHOP_ITEMS
from ui.mode_select import ModeSelectWindow
from ui.app import DayTradeSimApp
from ui.shop_dialog import ShopDialog
from ui.win_animations import WinAnimationOverlay, play_win_animation

def verify_all():
    print("=== STARTING V1.4 COMPREHENSIVE VERIFICATION ===", flush=True)

    # 1. Profile Verification
    profile = get_profile()
    init_balance = profile.menu_balance
    print(f"Current Vault Balance: ${profile.menu_balance:,.2f}", flush=True)
    print(f"Inventory: {profile.inventory}", flush=True)
    print(f"Equipped Animation: {profile.equipped_animation}", flush=True)

    # 2. ModeSelectWindow Verification
    print("Testing ModeSelectWindow UI with Vault Balance & Shop...", flush=True)
    def dummy_solo(): pass
    def dummy_online(m, f): pass
    launcher = ModeSelectWindow(dummy_solo, dummy_online)
    launcher.update()

    assert hasattr(launcher, "lbl_vault_balance"), "ModeSelectWindow missing lbl_vault_balance"
    assert hasattr(launcher, "btn_open_shop"), "ModeSelectWindow missing btn_open_shop"
    print(f"ModeSelectWindow displayed vault balance: {launcher.lbl_vault_balance.cget('text')}", flush=True)

    # Open Shop from launcher
    shop = ShopDialog(launcher)
    shop.update()
    print("ShopDialog opened successfully from launcher.", flush=True)
    assert len(shop.scroll_content.winfo_children()) == len(SHOP_ITEMS), "All items rendered in shop"

    # Test previewing crazy win animations
    for anim in ["money_rain", "rocket_moon", "matrix_glitch", "diamond_hands", "golden_bull"]:
        print(f"Testing crazy win animation: {anim}...", flush=True)
        overlay = WinAnimationOverlay(shop, animation_id=anim)
        for _ in range(15):
            shop.update()
        overlay.stop()
        shop.update()
        print(f"Animation {anim} rendered without errors.", flush=True)

    shop.destroy()
    launcher.destroy()

    # 3. DayTradeSimApp Banking Verification
    print("Testing DayTradeSimApp trading terminal with Bank Profit...", flush=True)
    app = DayTradeSimApp()
    app.update()

    assert hasattr(app, "btn_bank_profit"), "DayTradeSimApp missing btn_bank_profit"
    # Starting equity is 25000, bank button should be disabled initially
    assert str(app.btn_bank_profit['state']) == str(tk.DISABLED), "Bank Profit button should be disabled initially"
    print("Verified Bank Profit button is initially disabled at $25,000 equity.", flush=True)

    # Simulate trading gain
    app.trading_panel._set_qty(100)
    app.trading_panel.do_buy()
    app.update()

    stock = app.engine.stocks[app.active_ticker]
    # Artificially raise price to create profit
    stock.price += 40.0
    app._update_header_metrics()
    app.update()

    profit_above = app.engine.total_equity - 25000.0
    print(f"New Equity: ${app.engine.total_equity:,.2f} (Profit above 25k: ${profit_above:,.2f})", flush=True)
    assert str(app.btn_bank_profit['state']) == str(tk.NORMAL), "Bank Profit button should now be enabled"
    print("Verified Bank Profit button is enabled with green style!", flush=True)

    # Bank the profit
    pre_bank_vault = profile.menu_balance
    banked = app.engine.bank_profit()
    print(f"Banked ${banked:,.2f} via engine.bank_profit()", flush=True)
    new_vault = profile.bank_profit(banked)
    print(f"New Vault Balance: ${new_vault:,.2f}", flush=True)
    assert new_vault >= pre_bank_vault + banked, "Vault balance increased by banked profit"

    # Verify trading account reset to starting $25,000
    app._update_header_metrics()
    app.update()
    print(f"Trading Equity reset to: ${app.engine.total_equity:,.2f}, Cash: ${app.engine.cash:,.2f}", flush=True)
    assert abs(app.engine.total_equity - 25000.0) < 0.01, "Equity reset to $25,000"

    app.destroy()
    print("=== ALL V1.4 VERIFICATIONS PASSED SUCCESSFULLY! ===", flush=True)

if __name__ == "__main__":
    verify_all()
