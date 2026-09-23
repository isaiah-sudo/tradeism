import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable, List
from simulation.stock import Stock

class WatchlistPanel(tk.Frame):
    """
    Pro Day-Trader Watchlist & Market Scanner for 100 stocks.
    Features:
    - Real-time search filter by Ticker / Name
    - Sorting by: Gainers (highest %), Losers (lowest %), Ticker (A-Z)
    - Sector filter tabs: All, Tech, Meme, Bio, Crypto, Energy, Penny
    - High-performance scrollable list with mouse-wheel support
    - Visual pill badges for % change and selected stock indicator
    """
    BG_COLOR = "#181a20"
    ITEM_BG = "#222631"
    ITEM_SELECTED = "#2d3446"
    TEXT_COLOR = "#eaecef"
    MUTED_COLOR = "#848e9c"
    GREEN = "#089981"
    RED = "#f23645"

    def __init__(self, parent, stocks: Dict[str, Stock], on_select_stock: Callable[[str], None], **kwargs):
        super().__init__(parent, bg=self.BG_COLOR, width=270, **kwargs)
        self.stocks = stocks
        self.on_select_stock = on_select_stock
        self.selected_ticker = "NVXP"

        # Search, sector and sort state
        self.search_query = ""
        self.current_sector = "ALL"
        self.current_sort = "GAINERS"  # "GAINERS", "LOSERS", "TICKER"

        self.row_widgets: Dict[str, dict] = {}
        self.rendered_tickers: List[str] = []

        self.pack_propagate(False)
        self._build_ui()

    def _build_ui(self):
        # 1. Header Bar
        header = tk.Frame(self, bg=self.BG_COLOR, height=30)
        header.pack(fill=tk.X, padx=10, pady=(8, 4))

        tk.Label(
            header,
            text="MARKET SCANNER",
            bg=self.BG_COLOR,
            fg="#929aa5",
            font=("Segoe UI", 9, "bold")
        ).pack(side=tk.LEFT)

        self.lbl_count = tk.Label(
            header,
            text=f"{len(self.stocks)} STOCKS",
            bg=self.BG_COLOR,
            fg="#00e676",
            font=("Segoe UI", 8, "bold")
        )
        self.lbl_count.pack(side=tk.RIGHT)

        # 2. Search Box
        search_f = tk.Frame(self, bg="#222631", bd=1, relief=tk.FLAT)
        search_f.pack(fill=tk.X, padx=8, pady=(0, 5))

        tk.Label(search_f, text="🔍", font=("Segoe UI", 9), fg=self.MUTED_COLOR, bg="#222631").pack(side=tk.LEFT, padx=(6, 2))

        self.ent_search = tk.Entry(
            search_f,
            bg="#222631",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief=tk.FLAT,
            font=("Segoe UI", 9)
        )
        self.ent_search.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3, padx=(0, 6))
        self.ent_search.bind("<KeyRelease>", self._on_search_change)
        self.ent_search.bind("<Return>", self._on_search_return)
        self.ent_search.bind("<Escape>", self._on_search_escape)
        self.ent_search.bind("<Up>", self._on_search_up)
        self.ent_search.bind("<Down>", self._on_search_down)

        # 3. Quick Sort & Filter Tabs
        filter_f = tk.Frame(self, bg=self.BG_COLOR)
        filter_f.pack(fill=tk.X, padx=8, pady=(0, 4))

        self.sort_buttons = {}
        for mode, label in [("GAINERS", "▲ Gainers"), ("LOSERS", "▼ Losers"), ("TICKER", "A-Z")]:
            btn = tk.Button(
                filter_f,
                text=label,
                font=("Segoe UI", 7, "bold"),
                bg="#2962ff" if mode == self.current_sort else "#222631",
                fg="#ffffff" if mode == self.current_sort else self.MUTED_COLOR,
                activebackground="#3d72ff",
                activeforeground="#ffffff",
                relief=tk.FLAT,
                padx=4, pady=1,
                cursor="hand2",
                command=lambda m=mode: self._set_sort(m)
            )
            btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
            self.sort_buttons[mode] = btn

        # Sector quick buttons
        sec_f = tk.Frame(self, bg=self.BG_COLOR)
        sec_f.pack(fill=tk.X, padx=8, pady=(0, 6))

        self.sec_buttons = {}
        for s_code, s_name in [("ALL", "ALL"), ("Meme", "MEME"), ("Bio", "BIO"), ("Crypto", "CRYPTO"), ("Penny", "PENNY")]:
            btn = tk.Button(
                sec_f,
                text=s_name,
                font=("Segoe UI", 7, "bold"),
                bg="#3d4454" if s_code == self.current_sector else "#1e222d",
                fg="#ffffff" if s_code == self.current_sector else self.MUTED_COLOR,
                relief=tk.FLAT,
                padx=3, pady=1,
                cursor="hand2",
                command=lambda s=s_code: self._set_sector(s)
            )
            btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
            self.sec_buttons[s_code] = btn

        # 4. Scrollable Stock List
        list_container = tk.Frame(self, bg=self.BG_COLOR)
        list_container.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))

        self.canvas = tk.Canvas(list_container, bg=self.BG_COLOR, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(list_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_inner = tk.Frame(self.canvas, bg=self.BG_COLOR)

        self.scrollable_inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

        # Mouse wheel binding for smooth scrolling
        self._bind_mousewheel(self)

        self.refresh_list()

    def _bind_mousewheel(self, widget):
        widget.bind("<MouseWheel>", self._on_mousewheel)
        for child in widget.winfo_children():
            self._bind_mousewheel(child)

    def _on_mousewheel(self, event):
        if event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_search_change(self, event):
        self.search_query = self.ent_search.get().strip().upper()
        self.refresh_list()

    def _on_search_return(self, event):
        """Enter in search box selects top matching stock and returns focus to root."""
        if self.rendered_tickers:
            self.select_stock(self.rendered_tickers[0])
        self.master.focus_set()
        return "break"

    def _on_search_escape(self, event):
        """Escape clears search and removes focus to root."""
        self.ent_search.delete(0, tk.END)
        self._on_search_change(None)
        self.master.focus_set()
        return "break"

    def _on_search_up(self, event):
        """Up arrow navigates filtered stock list while in search."""
        if self.rendered_tickers:
            if self.selected_ticker in self.rendered_tickers:
                idx = self.rendered_tickers.index(self.selected_ticker)
                next_t = self.rendered_tickers[(idx - 1) % len(self.rendered_tickers)]
            else:
                next_t = self.rendered_tickers[-1]
            self.select_stock(next_t)
        return "break"

    def _on_search_down(self, event):
        """Down arrow navigates filtered stock list while in search."""
        if self.rendered_tickers:
            if self.selected_ticker in self.rendered_tickers:
                idx = self.rendered_tickers.index(self.selected_ticker)
                next_t = self.rendered_tickers[(idx + 1) % len(self.rendered_tickers)]
            else:
                next_t = self.rendered_tickers[0]
            self.select_stock(next_t)
        return "break"

    def _set_sort(self, sort_mode: str):
        self.current_sort = sort_mode
        for m, btn in self.sort_buttons.items():
            if m == sort_mode:
                btn.config(bg="#2962ff", fg="#ffffff")
            else:
                btn.config(bg="#222631", fg=self.MUTED_COLOR)
        self.refresh_list()

    def _set_sector(self, sector_code: str):
        self.current_sector = sector_code
        for s, btn in self.sec_buttons.items():
            if s == sector_code:
                btn.config(bg="#3d4454", fg="#ffffff")
            else:
                btn.config(bg="#1e222d", fg=self.MUTED_COLOR)
        self.refresh_list()

    def get_filtered_stocks(self) -> List[Stock]:
        stocks = list(self.stocks.values())

        # Sector filter
        if self.current_sector != "ALL":
            stocks = [s for s in stocks if self.current_sector.lower() in s.sector.lower()]

        # Search filter
        if self.search_query:
            stocks = [
                s for s in stocks
                if self.search_query in s.ticker.upper() or self.search_query in s.name.upper()
            ]

        # Sorting
        if self.current_sort == "GAINERS":
            stocks.sort(key=lambda s: s.change_pct, reverse=True)
        elif self.current_sort == "LOSERS":
            stocks.sort(key=lambda s: s.change_pct, reverse=False)
        elif self.current_sort == "TICKER":
            stocks.sort(key=lambda s: s.ticker)

        return stocks

    def refresh_list(self):
        """Rebuilds the row widgets based on current search and filters."""
        # Clear previous rows
        for child in self.scrollable_inner.winfo_children():
            child.destroy()
        self.row_widgets.clear()

        filtered = self.get_filtered_stocks()
        self.rendered_tickers = [s.ticker for s in filtered]
        self.lbl_count.config(text=f"{len(filtered)} / {len(self.stocks)}")

        for stock in filtered:
            ticker = stock.ticker
            is_sel = (ticker == self.selected_ticker)
            bg_color = self.ITEM_SELECTED if is_sel else self.ITEM_BG

            row = tk.Frame(self.scrollable_inner, bg=bg_color, bd=1, relief=tk.FLAT, cursor="hand2")
            row.pack(fill=tk.X, pady=2, padx=2)

            # Left block: Ticker & Sector / Name
            left_f = tk.Frame(row, bg=bg_color)
            left_f.pack(side=tk.LEFT, padx=6, pady=4)

            lbl_t = tk.Label(left_f, text=ticker, font=("Segoe UI", 10, "bold"), fg=self.TEXT_COLOR, bg=bg_color)
            lbl_t.pack(anchor="w")

            lbl_n = tk.Label(left_f, text=f"{stock.name[:13]}", font=("Segoe UI", 7), fg=self.MUTED_COLOR, bg=bg_color)
            lbl_n.pack(anchor="w")

            # Right block: Price & % pill
            right_f = tk.Frame(row, bg=bg_color)
            right_f.pack(side=tk.RIGHT, padx=6, pady=4)

            lbl_p = tk.Label(right_f, text=f"${stock.price:.2f}", font=("Segoe UI", 9, "bold"), fg=self.TEXT_COLOR, bg=bg_color)
            lbl_p.pack(anchor="e")

            pct = stock.change_pct
            lbl_chg = tk.Label(
                right_f,
                text=f"{'+' if pct >= 0 else ''}{pct:.2f}%",
                font=("Segoe UI", 7, "bold"),
                fg="#ffffff",
                bg=self.GREEN if pct >= 0 else self.RED,
                padx=4, pady=0
            )
            lbl_chg.pack(anchor="e", pady=(1, 0))

            # Bind click
            def make_click_handler(t=ticker):
                return lambda e: self.select_stock(t)

            handler = make_click_handler(ticker)
            row.bind("<Button-1>", handler)
            for child in (left_f, lbl_t, lbl_n, right_f, lbl_p, lbl_chg):
                child.bind("<Button-1>", handler)

            # Bind mousewheel to each child
            self._bind_mousewheel(row)

            self.row_widgets[ticker] = {
                "frame": row,
                "left_f": left_f,
                "right_f": right_f,
                "ticker": lbl_t,
                "name": lbl_n,
                "price": lbl_p,
                "pct": lbl_chg
            }

    def select_stock(self, ticker: str):
        self.selected_ticker = ticker
        self._update_highlight()
        if self.on_select_stock:
            self.on_select_stock(ticker)

    def _update_highlight(self):
        for t, widgets in self.row_widgets.items():
            is_sel = (t == self.selected_ticker)
            bg = self.ITEM_SELECTED if is_sel else self.ITEM_BG
            widgets["frame"].config(bg=bg)
            widgets["left_f"].config(bg=bg)
            widgets["right_f"].config(bg=bg)
            widgets["ticker"].config(bg=bg)
            widgets["name"].config(bg=bg)
            widgets["price"].config(bg=bg)

    def update_prices(self):
        """Fast tick refresh with text caching to eliminate redundant widget config calls."""
        for ticker in self.rendered_tickers:
            stock = self.stocks.get(ticker)
            widgets = self.row_widgets.get(ticker)
            if not stock or not widgets:
                continue

            p_str = f"${stock.price:.2f}"
            if widgets.get("last_p") != p_str:
                widgets["price"].config(text=p_str)
                widgets["last_p"] = p_str

            pct = stock.change_pct
            color = self.GREEN if pct >= 0 else self.RED
            sign = "+" if pct >= 0 else ""
            pct_str = f"{sign}{pct:.2f}%"

            if widgets.get("last_pct") != pct_str or widgets.get("last_color") != color:
                widgets["pct"].config(text=pct_str, bg=color)
                widgets["last_pct"] = pct_str
                widgets["last_color"] = color
