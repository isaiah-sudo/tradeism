import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from simulation.engine import MarketEngine
from simulation.news import NewsItem
from ui.chart import CandlestickChart
from ui.watchlist import WatchlistPanel
from ui.trading_panel import TradingPanel
from ui.news_feed import NewsFeedPanel
from ui.trade_log_panel import TradeLogPanel

class DayTradeSimApp(tk.Tk):
    """
    Main Application Window for the Day Trading Simulator.
    """
    THEME_BG = "#0e1117"
    BAR_BG = "#161a25"
    TEXT_WHITE = "#ffffff"
    TEXT_MUTED = "#848e9c"
    GREEN = "#089981"
    RED = "#f23645"

    def __init__(self):
        super().__init__()
        self.title("⚡ DAY TRADE SIMULATOR • PRO TRADER TERMINAL")
        self.geometry("1280x820")
        self.minsize(1050, 700)
        self.configure(bg=self.THEME_BG)

        # Initialize Simulation Engine
        self.engine = MarketEngine(initial_cash=25000.0)
        self.active_ticker = "NVXP"
        self._loop_job: Optional[str] = None

        self._init_styles()
        self._build_header()
        self._build_main_layout()
        self._build_bottom_panel()
        self._bind_hotkeys()

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

        # Right: Speed Difficulty & Control Buttons
        ctrl_f = tk.Frame(top_bar, bg=self.BAR_BG)
        ctrl_f.pack(side=tk.RIGHT, padx=15, pady=8)

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

    def _build_main_layout(self):
        """Center layout with Watchlist on left, Candlestick Chart in center, Trading Panel on right."""
        main_f = tk.Frame(self, bg=self.THEME_BG)
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
        self.chart.set_stock(self.engine.stocks[ticker])
        self.trading_panel.set_active_ticker(ticker)

    def _on_trade_executed(self):
        self.trade_log_panel.refresh_trades(self.engine.trades)
        self._update_header_metrics()

    def _set_difficulty(self, diff_name: str):
        self.engine.current_difficulty = diff_name
        for d, btn in self.diff_buttons.items():
            if d == diff_name:
                btn.config(bg="#2962ff", fg="#ffffff")
            else:
                btn.config(bg="#222631", fg=self.TEXT_MUTED)

    def _toggle_pause(self):
        self.engine.is_paused = not self.engine.is_paused
        if self.engine.is_paused:
            self.btn_pause.config(text="▶ Resume", bg="#089981")
        else:
            self.btn_pause.config(text="⏸ Pause", bg="#2a2e39")

    def _reset_sim(self):
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

    def _simulation_loop(self):
        """Heartbeat simulation step with throttled scanner rendering."""
        try:
            import time as _t
            news = self.engine.step()
            if news:
                self.news_feed_panel.trigger_flash(news)
                self.news_feed_panel.refresh_news(self.engine.news_feed)

            # Redraw active chart & trading panel at full tick rate
            self.chart.draw()
            self.trading_panel.update_display()
            self._update_header_metrics()

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
