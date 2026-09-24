import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from typing import Optional, Callable, Dict, Any
from simulation.engine import MarketEngine
from simulation.news import NewsItem
from ui.chart import CandlestickChart
from ui.watchlist import WatchlistPanel
from ui.trading_panel import TradingPanel
from ui.news_feed import NewsFeedPanel
from ui.trade_log_panel import TradeLogPanel
from ui.battle_panel import BattleHUD, MatchEndDialog
from profile_manager import get_profile
from ui.shop_dialog import ShopDialog
from ui.win_animations import play_win_animation

class DayTradeSimApp(tk.Tk):
    """
    Main Application Window for the Day Trading Simulator.
    Supports Solo Sandbox and 1v1 Online PvP Battle modes.
    """
    THEME_BG = "#0e1117"
    BAR_BG = "#161a25"
    TEXT_WHITE = "#ffffff"
    TEXT_MUTED = "#848e9c"
    GREEN = "#089981"
    RED = "#f23645"

    def __init__(
        self,
        mode: str = "solo",
        match_data: Optional[Dict[str, Any]] = None,
        fb_manager: Optional[Any] = None,
        on_return_to_menu: Optional[Callable[[], None]] = None
    ):
        super().__init__()
        self.mode = mode
        self.match_data = match_data or {}
        self.fb_manager = fb_manager
        self.on_return_to_menu = on_return_to_menu
        self.battle_hud: Optional[BattleHUD] = None
        self._is_syncing_metrics = False
        self._match_dialog_open = False
        self.profile = get_profile()
        self.btn_bank_profit: Optional[tk.Button] = None

        seed = self.match_data.get("seed") if self.mode == "online" else None
        opp_name = self.match_data.get("opponent", {}).get("name", "Opponent") if self.mode == "online" else ""

        if self.mode == "online":
            self.title(f"⚡ DAY TRADE SIMULATOR • 1v1 DUEL vs {opp_name}")
        else:
            self.title("⚡ DAY TRADE SIMULATOR • PRO TRADER TERMINAL")

        self.geometry("1280x850")
        self.minsize(1050, 720)
        self.configure(bg=self.THEME_BG)

        # Set window icon if available
        import os, sys
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(base_dir, "assets", "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        # Initialize Simulation Engine (Deterministic seed if online)
        self.engine = MarketEngine(initial_cash=25000.0, seed=seed)
        if self.mode == "online":
            self.engine.current_difficulty = "Day Trader (3x)"

        self.active_ticker = "NVXP"
        self._loop_job: Optional[str] = None

        self._init_styles()
        self._build_header()
        if self.mode == "online":
            self._build_battle_hud()
        self._build_main_layout()
        self._build_bottom_panel()
        self._bind_hotkeys()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # Start simulation loop
        self._schedule_next_tick()

    def _init_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        # Configure Notebook styling for bottom tab bar
        style.configure("TNotebook", background=self.THEME_BG, borderwidth=0)
        style.configure("TNotebook.Tab", background="#1e222d", foreground="#848e9c", font=("Segoe UI", 9, "bold"), padding=[12, 4])
        style.map("TNotebook.Tab",
            background=[("selected", "#2a2e39")],
            foreground=[("selected", "#ffffff")]
        )

    def _build_header(self):
        """Top bar displaying account stats, speed difficulty buttons, pause & reset."""
        top_bar = tk.Frame(self, bg=self.BAR_BG, height=60, bd=1, relief=tk.FLAT)
        top_bar.pack(fill=tk.X, side=tk.TOP)

        # Left: App Brand & Account Metrics
        brand_f = tk.Frame(top_bar, bg=self.BAR_BG)
        brand_f.pack(side=tk.LEFT, padx=(15, 20), pady=6)

        tk.Label(brand_f, text="DAYTRADE", font=("Segoe UI", 12, "bold"), fg="#00e676", bg=self.BAR_BG).pack(anchor="w")
        tk.Label(brand_f, text="SIMULATOR PRO", font=("Segoe UI", 8), fg="#787b86", bg=self.BAR_BG).pack(anchor="w")

        # Metrics cluster
        metrics_f = tk.Frame(top_bar, bg=self.BAR_BG)
        metrics_f.pack(side=tk.LEFT, padx=10, pady=6)

        def make_stat_box(parent, label: str):
            f = tk.Frame(parent, bg=self.BAR_BG)
            f.pack(side=tk.LEFT, padx=12)
            lbl_title = tk.Label(f, text=label, font=("Segoe UI", 8, "bold"), fg=self.TEXT_MUTED, bg=self.BAR_BG)
            lbl_title.pack(anchor="w")
            lbl_val = tk.Label(f, text="$0.00", font=("Segoe UI", 11, "bold"), fg=self.TEXT_WHITE, bg=self.BAR_BG)
            lbl_val.pack(anchor="w")
            return lbl_val

        self.lbl_equity = make_stat_box(metrics_f, "NET EQUITY")
        self.lbl_cash = make_stat_box(metrics_f, "AVAILABLE CASH")
        self.lbl_unrealized = make_stat_box(metrics_f, "OPEN P&L")
        self.lbl_realized = make_stat_box(metrics_f, "REALIZED P&L")
        self.lbl_total_pnl = make_stat_box(metrics_f, "TOTAL RETURN")

        # Right: Speed Difficulty & Control Buttons (or Online Duel Badge)
        ctrl_f = tk.Frame(top_bar, bg=self.BAR_BG)
        ctrl_f.pack(side=tk.RIGHT, padx=15, pady=8)

        if self.mode == "online":
            tk.Label(
                ctrl_f,
                text="⚔️ 1v1 COMPETITIVE (3x Speed)",
                font=("Segoe UI", 9, "bold"),
                fg="#00e676",
                bg="#1a2e22",
                padx=8,
                pady=4
            ).pack(side=tk.LEFT, padx=4)

            btn_online_shop = tk.Button(
                ctrl_f,
                text="🛒 Shop",
                font=("Segoe UI", 8, "bold"),
                bg="#1e222d",
                fg="#ffd700",
                activebackground="#2a2e39",
                activeforeground="#ffffff",
                relief=tk.FLAT,
                padx=8, pady=3,
                cursor="hand2",
                command=self._open_shop
            )
            btn_online_shop.pack(side=tk.LEFT, padx=4)

            btn_leave = tk.Button(
                ctrl_f,
                text="🚪 Exit Duel",
                font=("Segoe UI", 8, "bold"),
                bg="#3d1b22",
                fg="#ff5252",
                relief=tk.FLAT,
                padx=8, pady=3,
                cursor="hand2",
                command=self._handle_leave_battle
            )
            btn_leave.pack(side=tk.LEFT, padx=4)
        else:
            # Difficulty Selector
            tk.Label(ctrl_f, text="SPEED:", font=("Segoe UI", 8, "bold"), fg=self.TEXT_MUTED, bg=self.BAR_BG).pack(side=tk.LEFT, padx=(0, 5))

            self.diff_buttons = {}
            for diff_name, short_label in [
                ("Relaxed (1x)", "1x Relaxed"),
                ("Day Trader (3x)", "3x Trader"),
                ("High Frequency (8x)", "8x HFT"),
                ("TURBO INSANE (20x)", "20x TURBO")
            ]:
                is_active = (diff_name == self.engine.current_difficulty)
                btn = tk.Button(
                    ctrl_f,
                    text=short_label,
                    font=("Segoe UI", 8, "bold"),
                    bg="#2962ff" if is_active else "#222631",
                    fg="#ffffff" if is_active else self.TEXT_MUTED,
                    activebackground="#3d72ff",
                    activeforeground="#ffffff",
                    relief=tk.FLAT,
                    padx=6, pady=2,
                    cursor="hand2",
                    command=lambda d=diff_name: self._set_difficulty(d)
                )
                btn.pack(side=tk.LEFT, padx=2)
                self.diff_buttons[diff_name] = btn

            # Pause / Resume Button
            self.btn_pause = tk.Button(
                ctrl_f,
                text="⏸ Pause",
                font=("Segoe UI", 8, "bold"),
                bg="#2a2e39",
                fg=self.TEXT_WHITE,
                activebackground="#363c4e",
                activeforeground=self.TEXT_WHITE,
                relief=tk.FLAT,
                padx=8, pady=2,
                cursor="hand2",
                command=self._toggle_pause
            )
            self.btn_pause.pack(side=tk.LEFT, padx=(10, 4))

            # Bank Profit to Menu Button
            self.btn_bank_profit = tk.Button(
                ctrl_f,
                text="💰 Bank Profit",
                font=("Segoe UI", 8, "bold"),
                bg="#1e222d",
                fg="#50535e",
                activebackground="#00e676",
                activeforeground="#000000",
                relief=tk.FLAT,
                padx=8, pady=2,
                cursor="hand2",
                state=tk.DISABLED,
                command=self._handle_bank_profit
            )
            self.btn_bank_profit.pack(side=tk.LEFT, padx=2)

            # Reset Game Button
            btn_reset = tk.Button(
                ctrl_f,
                text="🔄 Reset",
                font=("Segoe UI", 8, "bold"),
                bg="#3d1b22",
                fg="#ff5252",
                activebackground="#54242e",
                activeforeground="#ff5252",
                relief=tk.FLAT,
                padx=8, pady=2,
                cursor="hand2",
                command=self._reset_sim
            )
            btn_reset.pack(side=tk.LEFT, padx=2)

            # Trader Shop Button
            btn_shop = tk.Button(
                ctrl_f,
                text="🛒 Shop",
                font=("Segoe UI", 8, "bold"),
                bg="#1e222d",
                fg="#ffd700",
                activebackground="#2a2e39",
                activeforeground="#ffffff",
                relief=tk.FLAT,
                padx=8, pady=2,
                cursor="hand2",
                command=self._open_shop
            )
            btn_shop.pack(side=tk.LEFT, padx=2)

            # Return to Menu Button
            btn_menu = tk.Button(
                ctrl_f,
                text="🏠 Menu",
                font=("Segoe UI", 8, "bold"),
                bg="#1e222d",
                fg="#848e9c",
                activebackground="#2a2e39",
                activeforeground="#ffffff",
                relief=tk.FLAT,
                padx=8, pady=2,
                cursor="hand2",
                command=self._handle_return_to_menu
            )
            btn_menu.pack(side=tk.LEFT, padx=(6, 2))



    def _build_battle_hud(self):
        """Constructs 1v1 battle HUD panel at top of workspace."""
        my_name = getattr(self.fb_manager, "display_name", "You") or "You"
        opp = self.match_data.get("opponent", {})
        opp_name = opp.get("name", "Opponent")
        duration = self.match_data.get("duration_seconds", 180)
        start_time = self.match_data.get("start_time", time.time())

        self.battle_hud = BattleHUD(
            self,
            my_name=my_name,
            opponent_name=opp_name,
            round_duration=duration,
            start_time=start_time,
            on_next_opponent=self._handle_next_opponent,
            on_leave_battle=self._handle_leave_battle
        )
        if hasattr(self, "main_f") and self.main_f.winfo_exists():
            self.battle_hud.pack(fill=tk.X, side=tk.TOP, padx=8, pady=(4, 0), before=self.main_f)
        else:
            self.battle_hud.pack(fill=tk.X, side=tk.TOP, padx=8, pady=(4, 0))

    def _build_main_layout(self):
        """Center layout with Watchlist on left, Candlestick Chart in center, Trading Panel on right."""
        main_f = tk.Frame(self, bg=self.THEME_BG)
        self.main_f = main_f
        main_f.pack(fill=tk.BOTH, expand=True, padx=8, pady=(6, 0))


        # 1. Left Watchlist
        self.watchlist = WatchlistPanel(
            main_f,
            stocks=self.engine.stocks,
            on_select_stock=self._on_stock_selected
        )
        self.watchlist.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

        # 3. Right Trading Panel (packed to right first to ensure consistent space)
        self.trading_panel = TradingPanel(
            main_f,
            engine=self.engine,
            on_trade_executed=self._on_trade_executed
        )
        self.trading_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(6, 0))

        # 2. Center Candlestick Chart (fills remaining width)
        self.chart = CandlestickChart(
            main_f,
            stock=self.engine.stocks[self.active_ticker]
        )
        self.chart.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _build_bottom_panel(self):
        """Bottom notebook with Breaking News and Trade History."""
        bottom_f = tk.Frame(self, bg=self.THEME_BG, height=190)
        bottom_f.pack(fill=tk.X, side=tk.BOTTOM, padx=8, pady=(4, 8))
        bottom_f.pack_propagate(False)

        notebook = ttk.Notebook(bottom_f)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Breaking News Feed
        self.news_feed_panel = NewsFeedPanel(notebook, news_list=self.engine.news_feed)
        notebook.add(self.news_feed_panel, text="  ⚡ LIVE BREAKING NEWS FEED  ")

        # Tab 2: Trade Execution Log
        self.trade_log_panel = TradeLogPanel(notebook)
        notebook.add(self.trade_log_panel, text="  📋 ORDER & TRADE LOG  ")

        # Seed news display
        self.news_feed_panel.refresh_news(self.engine.news_feed)

    def _bind_hotkeys(self):
        """Universal keyboard trading hotkeys (Function keys, Alt combinations, and standard keys)."""
        # 1. Universal Function Keys & Alt Combinations (work anywhere, even in search or entries)
        for key in ["<F1>", "<Alt-b>", "<Alt-B>", "<Control-b>", "<Control-B>"]:
            self.bind_all(key, lambda e: self.trading_panel.do_buy())

        for key in ["<F2>", "<Alt-s>", "<Alt-S>", "<Control-s>", "<Control-S>"]:
            self.bind_all(key, lambda e: self.trading_panel.do_sell())

        for key in ["<F3>", "<Alt-x>", "<Alt-X>", "<Control-x>", "<Control-X>"]:
            self.bind_all(key, lambda e: self.trading_panel.do_short())

        for key in ["<F4>", "<Alt-c>", "<Alt-C>", "<Control-c>", "<Control-C>"]:
            self.bind_all(key, lambda e: self.trading_panel.do_cover())

        for key in ["<F8>", "<Alt-f>", "<Alt-F>"]:
            self.bind_all(key, lambda e: self.trading_panel.do_flatten())

        for key in ["<F9>", "<Pause>", "<Alt-space>"]:
            self.bind_all(key, lambda e: self._toggle_pause())

        for key in ["<F12>", "<Alt-m>", "<Alt-M>"]:
            self.bind_all(key, lambda e: self.trading_panel._set_max_cash())

        # 2. Standard single-key shortcuts when focus is not trapped in text search
        def make_safe_handler(action):
            def handler(e):
                focused = self.focus_get()
                # If user is actively typing in search entry, preserve text typing for letters
                if focused == self.watchlist.ent_search:
                    return
                action()
            return handler

        self.bind("<Key-b>", make_safe_handler(self.trading_panel.do_buy))
        self.bind("<Key-B>", make_safe_handler(self.trading_panel.do_buy))
        self.bind("<Key-s>", make_safe_handler(self.trading_panel.do_sell))
        self.bind("<Key-S>", make_safe_handler(self.trading_panel.do_sell))
        self.bind("<Key-x>", make_safe_handler(self.trading_panel.do_short))
        self.bind("<Key-X>", make_safe_handler(self.trading_panel.do_short))
        self.bind("<Key-c>", make_safe_handler(self.trading_panel.do_cover))
        self.bind("<Key-C>", make_safe_handler(self.trading_panel.do_cover))
        self.bind("<Key-r>", make_safe_handler(self.trading_panel.do_reverse))
        self.bind("<Key-R>", make_safe_handler(self.trading_panel.do_reverse))
        self.bind("<Key-m>", make_safe_handler(self.trading_panel._set_all_pos))
        self.bind("<Key-M>", make_safe_handler(self.trading_panel._set_all_pos))
        self.bind("<Escape>", lambda e: self.trading_panel.do_flatten())
        self.bind("<space>", make_safe_handler(self._toggle_pause))

        # Up/Down arrow to cycle active stock
        tickers = list(self.engine.stocks.keys())
        def _prev_stock(e):
            if self.focus_get() == self.watchlist.ent_search:
                return
            idx = tickers.index(self.active_ticker)
            new_ticker = tickers[(idx - 1) % len(tickers)]
            self.watchlist.select_stock(new_ticker)

        def _next_stock(e):
            if self.focus_get() == self.watchlist.ent_search:
                return
            idx = tickers.index(self.active_ticker)
            new_ticker = tickers[(idx + 1) % len(tickers)]
            self.watchlist.select_stock(new_ticker)

        self.bind("<Up>", _prev_stock)
        self.bind("<Down>", _next_stock)

    def _on_stock_selected(self, ticker: str):
        self.active_ticker = ticker
        pos = self.engine.positions.get(ticker)
        self.chart.set_stock(self.engine.stocks[ticker], position=pos)
        self.trading_panel.set_active_ticker(ticker)

    def _on_trade_executed(self):
        self.trade_log_panel.refresh_trades(self.engine.trades)
        self._update_header_metrics()
        pos = self.engine.positions.get(self.active_ticker)
        self.chart.set_position(pos)
        if self.engine.trades:
            latest = self.engine.trades[0]
            self.chart.show_trade_notification(latest.action, latest.shares, latest.price, latest.ticker)

    def _set_difficulty(self, diff_name: str):
        self.engine.current_difficulty = diff_name
        for d, btn in self.diff_buttons.items():
            if d == diff_name:
                btn.config(bg="#2962ff", fg="#ffffff")
            else:
                btn.config(bg="#222631", fg=self.TEXT_MUTED)

    def _toggle_pause(self):
        if self.mode == "online":
            return  # Pausing disabled in competitive online matches
        self.engine.is_paused = not self.engine.is_paused
        if self.engine.is_paused:
            self.btn_pause.config(text="▶ Resume", bg="#089981")
        else:
            self.btn_pause.config(text="⏸ Pause", bg="#2a2e39")

    def _reset_sim(self):
        if self.mode == "online":
            return  # Reset disabled during competitive online matches
        confirm = messagebox.askyesno("Reset Account", "Reset your balance to $25,000 and restart simulation?")
        if confirm:
            self.engine.reset_account()
            self.watchlist.update_prices()
            self.chart.set_stock(self.engine.stocks[self.active_ticker])
            self.trading_panel.update_display()
            self.trade_log_panel.refresh_trades([])
            self._update_header_metrics()

    def _update_header_metrics(self):
        eq = self.engine.total_equity
        cash = self.engine.cash
        unreal = self.engine.total_unrealized_pnl
        real = self.engine.realized_pnl
        tot_pnl = self.engine.total_pnl
        tot_pnl_pct = self.engine.total_pnl_pct

        curr_state = (round(eq, 2), round(cash, 2), round(unreal, 2), round(real, 2))
        if getattr(self, "_last_header_state", None) == curr_state:
            return
        self._last_header_state = curr_state

        self.lbl_equity.config(text=f"${eq:,.2f}")
        self.lbl_cash.config(text=f"${cash:,.2f}")

        # Unrealized
        c_unreal = self.GREEN if unreal >= 0 else self.RED
        self.lbl_unrealized.config(text=f"{'+' if unreal >= 0 else ''}${unreal:,.2f}", fg=c_unreal)

        # Realized
        c_real = self.GREEN if real >= 0 else self.RED
        self.lbl_realized.config(text=f"{'+' if real >= 0 else ''}${real:,.2f}", fg=c_real)

        # Total Return
        c_tot = self.GREEN if tot_pnl >= 0 else self.RED
        self.lbl_total_pnl.config(
            text=f"{'+' if tot_pnl >= 0 else ''}${tot_pnl:,.2f} ({'+' if tot_pnl_pct >= 0 else ''}{tot_pnl_pct:.2f}%)",
            fg=c_tot
        )

        # Update Bank Profit Button if equity is above starting $25,000
        if hasattr(self, "btn_bank_profit") and self.btn_bank_profit:
            profit_above_25k = max(0.0, eq - 25000.0)
            if profit_above_25k > 0:
                self.btn_bank_profit.config(
                    text=f"💰 Bank +${profit_above_25k:,.2f}",
                    state=tk.NORMAL,
                    bg="#00c853",
                    fg="#ffffff"
                )
            else:
                self.btn_bank_profit.config(
                    text="💰 Bank Profit",
                    state=tk.DISABLED,
                    bg="#1e222d",
                    fg="#50535e"
                )

    def _open_shop(self):
        ShopDialog(self)

    def _handle_bank_profit(self):
        profit = self.engine.bank_profit()
        if profit > 0:
            new_bal = self.profile.bank_profit(profit)
            play_win_animation(self)
            self.watchlist.update_prices()
            pos = self.engine.positions.get(self.active_ticker)
            self.chart.set_position(pos)
            self.chart.draw()
            self.trading_panel.update_display()
            self.trade_log_panel.refresh_trades(self.engine.trades)
            self._update_header_metrics()
            messagebox.showinfo(
                "💰 Profit Banked to Menu!",
                f"🎉 Profit locked in!\n\n"
                f"+${profit:,.2f} has been transferred to your Menu Vault.\n"
                f"Total Saved Menu Balance: ${new_bal:,.2f}\n\n"
                f"Round complete! Returning to main menu."
            )
            self._handle_return_to_menu()

    def _simulation_loop(self):
        """Heartbeat simulation step with throttled scanner rendering and online synchronization."""
        try:
            import time as _t
            news = self.engine.step()
            if news:
                self.news_feed_panel.trigger_flash(news)
                self.news_feed_panel.refresh_news(self.engine.news_feed)

            # Redraw active chart with position line & trading panel at full tick rate
            pos = self.engine.positions.get(self.active_ticker)
            self.chart.set_position(pos)
            self.chart.draw()
            self.trading_panel.update_display()
            self._update_header_metrics()

            # Handle Online 1v1 battle ticks & timer
            if self.mode == "online" and self.battle_hud:
                time_ok = self.battle_hud.tick_timer()
                if not time_ok and not self._match_dialog_open:
                    self._match_dialog_open = True
                    self.engine.is_paused = True

                    # Fetch the absolute latest fresh opponent metrics
                    final_opp_metrics = None
                    if self.fb_manager:
                        try:
                            final_opp_metrics = self.fb_manager.get_latest_opponent_metrics()
                        except Exception:
                            pass

                    opp_eq = self.battle_hud.opp_equity
                    if final_opp_metrics and "equity" in final_opp_metrics:
                        opp_eq = final_opp_metrics["equity"]
                        self.battle_hud.opp_equity = opp_eq

                    # If against simulated bot and still at initial 25000, advance tick for realistic score
                    if opp_eq == 25000.0 and self.fb_manager and self.fb_manager.opponent_bot:
                        self.fb_manager.opponent_bot.tick()
                        opp_eq = self.fb_manager.opponent_bot.equity
                        self.battle_hud.opp_equity = opp_eq

                    my_eq = self.engine.total_equity
                    diff = my_eq - opp_eq
                    if diff > 0.0:
                        self.profile.duels_won += 1
                        self.profile.save()
                        play_win_animation(self)

                    # Auto-bank profit above 25000
                    if my_eq > 25000.0:
                        profit = my_eq - 25000.0
                        self.profile.bank_profit(profit)

                    MatchEndDialog(
                        self,
                        my_equity=self.engine.total_equity,
                        opp_equity=opp_eq,
                        my_name=self.battle_hud.my_name,
                        opp_name=self.battle_hud.opponent_name,
                        on_next=self._handle_next_opponent,
                        on_menu=self._handle_leave_battle
                    )

                # Sync metrics with Firebase / Bot in background thread
                now = _t.time()
                if not hasattr(self, "_last_fb_sync") or (now - self._last_fb_sync) >= 1.0:
                    self._last_fb_sync = now
                    if not self._is_syncing_metrics and self.fb_manager:
                        self._sync_online_metrics()

            # Throttle 100-stock watchlist DOM updates to ~8 FPS for maximum GUI smoothness
            now = _t.time()
            if not hasattr(self, "_last_watchlist_tick") or (now - self._last_watchlist_tick) >= 0.12:
                self.watchlist.update_prices()
                self._last_watchlist_tick = now

        except Exception as e:
            print(f"Error in simulation loop: {e}")

        self._schedule_next_tick()

    def _schedule_next_tick(self):
        diff_cfg = self.engine.DIFFICULTIES.get(self.engine.current_difficulty, self.engine.DIFFICULTIES["Day Trader (3x)"])
        tick_ms = diff_cfg["tick_ms"]
        self._loop_job = self.after(tick_ms, self._simulation_loop)

    def _sync_online_metrics(self):
        """Asynchronously syncs current trading equity to Firebase and pulls opponent metrics."""
        self._is_syncing_metrics = True
        eq = self.engine.total_equity
        pnl = self.engine.total_pnl
        pnl_pct = self.engine.total_pnl_pct

        def worker():
            try:
                opp_data = self.fb_manager.update_player_metrics(eq, pnl, pnl_pct)
                if self.winfo_exists() and self.battle_hud and not self._match_dialog_open:
                    self.after(0, lambda: self.battle_hud.update_scores(eq, pnl, pnl_pct, opp_data) if (self.winfo_exists() and self.battle_hud) else None)
            except Exception:
                pass
            finally:
                self._is_syncing_metrics = False

        threading.Thread(target=worker, daemon=True).start()

    def _handle_next_opponent(self):
        """Omegle-style skip to find and pair with another opponent."""
        if self.fb_manager:
            self.fb_manager.forfeit_or_leave()

        # Pause simulation while searching
        self.engine.is_paused = True

        # Create quick search popup
        dialog = tk.Toplevel(self)
        dialog.title("Finding Next Opponent")
        dialog.geometry("420x220")
        dialog.resizable(False, False)
        dialog.configure(bg="#0e1117")
        dialog.transient(self)
        dialog.grab_set()

        # Center on parent
        self.update_idletasks()
        pw, ph = self.winfo_width(), self.winfo_height()
        px, py = self.winfo_rootx(), self.winfo_rooty()
        dialog.geometry(f"+{px + (pw - 420)//2}+{py + (ph - 220)//2}")

        tk.Label(dialog, text="🔍 Omegle Matchmaking", font=("Segoe UI", 14, "bold"), fg="#00e676", bg="#0e1117").pack(pady=(25, 6))
        lbl_status = tk.Label(dialog, text="Searching for next live opponent...", font=("Segoe UI", 10), fg="#c5c8d1", bg="#0e1117")
        lbl_status.pack(pady=4)

        cancel_ev = threading.Event()

        def do_cancel():
            cancel_ev.set()
            dialog.destroy()
            self._handle_leave_battle()

        btn_cancel = tk.Button(
            dialog,
            text="Cancel Search",
            font=("Segoe UI", 9),
            bg="#2a2e39",
            fg="#ff5252",
            relief=tk.FLAT,
            padx=12, pady=4,
            cursor="hand2",
            command=do_cancel
        )
        btn_cancel.pack(pady=15)

        def search_worker():
            new_match = self.fb_manager.find_match(cancel_ev)
            if cancel_ev.is_set():
                return
            if new_match:
                dialog.after(0, lambda: self._apply_new_match(dialog, new_match))
            else:
                dialog.after(0, lambda: self._on_requeue_timeout(dialog))

        threading.Thread(target=search_worker, daemon=True).start()

    def _apply_new_match(self, dialog, new_match: Dict[str, Any]):
        dialog.destroy()
        self._match_dialog_open = False
        self.match_data = new_match
        opp_name = new_match.get("opponent", {}).get("name", "Opponent")
        my_name = getattr(self.fb_manager, "display_name", "You") or "You"
        duration = new_match.get("duration_seconds", 180)

        now = time.time()
        start_time = new_match.get("start_time", now)
        if (now - start_time) > 10.0 or start_time > (now + 5.0):
            start_time = now
            new_match["start_time"] = now

        self.title(f"⚡ DAY TRADE SIMULATOR • 1v1 DUEL vs {opp_name}")

        # Reset account with synchronized seed
        self.engine.reset_account(seed=new_match.get("seed"))
        self.engine.is_paused = False

        if self.battle_hud and self.battle_hud.winfo_exists():
            self.battle_hud.reset_round(
                opponent_name=opp_name,
                round_duration=duration,
                start_time=start_time,
                my_name=my_name
            )
        else:
            self._build_battle_hud()

        self.watchlist.update_prices()
        self.chart.set_stock(self.engine.stocks[self.active_ticker])
        self.trading_panel.update_display()
        self.trade_log_panel.refresh_trades([])
        self._update_header_metrics()


    def _on_requeue_timeout(self, dialog):
        dialog.destroy()
        messagebox.showinfo("Matchmaking Timeout", "Could not find an opponent right now. Returning to main menu.")
        self._handle_leave_battle()

    def _handle_return_to_menu(self):
        """Cleans up active timers/processes and returns to the mode selection menu."""
        if hasattr(self, "engine") and self.engine.total_equity > 25000.0:
            profit = self.engine.bank_profit()
            if profit > 0:
                self.profile.bank_profit(profit)
        if self._loop_job:
            try:
                self.after_cancel(self._loop_job)
            except Exception:
                pass
            self._loop_job = None
        if self.mode == "online" and self.fb_manager:
            try:
                self.fb_manager.forfeit_or_leave()
            except Exception:
                pass
        self.destroy()
        if self.on_return_to_menu:
            self.on_return_to_menu()

    def _handle_leave_battle(self):
        if hasattr(self, "engine") and self.engine.total_equity > 25000.0:
            profit = self.engine.total_equity - 25000.0
            self.profile.bank_profit(profit)
        self._handle_return_to_menu()

    def destroy(self):
        if getattr(self, "_loop_job", None):
            try:
                self.after_cancel(self._loop_job)
            except Exception:
                pass
            self._loop_job = None
        super().destroy()

    def _on_window_close(self):
        if self.mode == "online" and self.fb_manager:
            self.fb_manager.forfeit_or_leave()
        self.destroy()
