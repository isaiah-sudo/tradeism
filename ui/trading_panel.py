import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
from simulation.engine import MarketEngine

class TradingPanel(tk.Frame):
    """
    Trade execution panel for Buy/Sell/Short/Cover orders and live position monitoring.
    """
    BG_COLOR = "#181a20"
    PANEL_BG = "#222631"
    TEXT_COLOR = "#eaecef"
    MUTED_COLOR = "#848e9c"
    GREEN = "#089981"
    GREEN_HOVER = "#0baf94"
    RED = "#f23645"
    RED_HOVER = "#f44d5a"
    BLUE = "#2962ff"
    ORANGE = "#e65100"

    def __init__(self, parent, engine: MarketEngine, on_trade_executed: Callable[[], None], **kwargs):
        super().__init__(parent, bg=self.BG_COLOR, width=280, **kwargs)
        self.engine = engine
        self.on_trade_executed = on_trade_executed
        self.active_ticker = "NVXP"

        self.pack_propagate(False)
        self._build_ui()

    def set_active_ticker(self, ticker: str):
        self.active_ticker = ticker
        self.lbl_active_stock.config(text=f"ORDER ENTRY • {ticker}")
        self.update_display()

    def _build_ui(self):
        # Section Header
        self.lbl_active_stock = tk.Label(
            self,
            text=f"ORDER ENTRY • {self.active_ticker}",
            bg=self.BG_COLOR,
            fg="#929aa5",
            font=("Segoe UI", 9, "bold")
        )
        self.lbl_active_stock.pack(anchor="w", padx=12, pady=(10, 8))

        # Position Card
        pos_card = tk.Frame(self, bg=self.PANEL_BG, bd=1, relief=tk.FLAT)
        pos_card.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Label(pos_card, text="CURRENT POSITION", font=("Segoe UI", 8, "bold"), fg=self.MUTED_COLOR, bg=self.PANEL_BG).pack(anchor="w", padx=10, pady=(8, 4))

        # Position Grid details
        grid_f = tk.Frame(pos_card, bg=self.PANEL_BG)
        grid_f.pack(fill=tk.X, padx=10, pady=(0, 8))

        tk.Label(grid_f, text="Side / Shares:", font=("Segoe UI", 9), fg=self.MUTED_COLOR, bg=self.PANEL_BG).grid(row=0, column=0, sticky="w", pady=2)
        self.lbl_pos_shares = tk.Label(grid_f, text="FLAT (0)", font=("Segoe UI", 9, "bold"), fg=self.TEXT_COLOR, bg=self.PANEL_BG)
        self.lbl_pos_shares.grid(row=0, column=1, sticky="e", pady=2)

        tk.Label(grid_f, text="Avg Price:", font=("Segoe UI", 9), fg=self.MUTED_COLOR, bg=self.PANEL_BG).grid(row=1, column=0, sticky="w", pady=2)
        self.lbl_pos_avg = tk.Label(grid_f, text="$0.00", font=("Segoe UI", 9), fg=self.TEXT_COLOR, bg=self.PANEL_BG)
        self.lbl_pos_avg.grid(row=1, column=1, sticky="e", pady=2)

        tk.Label(grid_f, text="Unrealized P&L:", font=("Segoe UI", 9), fg=self.MUTED_COLOR, bg=self.PANEL_BG).grid(row=2, column=0, sticky="w", pady=2)
        self.lbl_pos_pnl = tk.Label(grid_f, text="$0.00 (0.00%)", font=("Segoe UI", 9, "bold"), fg=self.MUTED_COLOR, bg=self.PANEL_BG)
        self.lbl_pos_pnl.grid(row=2, column=1, sticky="e", pady=2)

        grid_f.grid_columnconfigure(0, weight=1)
        grid_f.grid_columnconfigure(1, weight=1)

        # Quantity Entry Area
        qty_card = tk.Frame(self, bg=self.PANEL_BG, bd=1, relief=tk.FLAT)
        qty_card.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Label(qty_card, text="ORDER QUANTITY", font=("Segoe UI", 8, "bold"), fg=self.MUTED_COLOR, bg=self.PANEL_BG).pack(anchor="w", padx=10, pady=(8, 4))

        input_f = tk.Frame(qty_card, bg=self.PANEL_BG)
        input_f.pack(fill=tk.X, padx=10, pady=(0, 6))

        tk.Label(input_f, text="Shares:", font=("Segoe UI", 10), fg=self.TEXT_COLOR, bg=self.PANEL_BG).pack(side=tk.LEFT)
        self.ent_shares = tk.Entry(
            input_f,
            font=("Segoe UI", 11, "bold"),
            bg="#131722",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief=tk.FLAT,
            justify="right",
            width=10
        )
        self.ent_shares.insert(0, "100")
        self.ent_shares.pack(side=tk.RIGHT, ipady=3)

        # Allow trading hotkeys even while typing inside the shares entry!
        self.ent_shares.bind("<Key-b>", lambda e: self._shortcut_exec(self.do_buy))
        self.ent_shares.bind("<Key-B>", lambda e: self._shortcut_exec(self.do_buy))
        self.ent_shares.bind("<Key-s>", lambda e: self._shortcut_exec(self.do_sell))
        self.ent_shares.bind("<Key-S>", lambda e: self._shortcut_exec(self.do_sell))
        self.ent_shares.bind("<Key-x>", lambda e: self._shortcut_exec(self.do_short))
        self.ent_shares.bind("<Key-X>", lambda e: self._shortcut_exec(self.do_short))
        self.ent_shares.bind("<Key-c>", lambda e: self._shortcut_exec(self.do_cover))
        self.ent_shares.bind("<Key-C>", lambda e: self._shortcut_exec(self.do_cover))
        self.ent_shares.bind("<Return>", lambda e: self._defocus())
        self.ent_shares.bind("<Escape>", lambda e: self._defocus())

        # Quick preset buttons (Row 1: amounts)
        btn_preset_f = tk.Frame(qty_card, bg=self.PANEL_BG)
        btn_preset_f.pack(fill=tk.X, padx=10, pady=(0, 4))

        for q in [10, 50, 100, 500]:
            btn = tk.Button(
                btn_preset_f,
                text=str(q),
                bg="#2a2e39",
                fg=self.TEXT_COLOR,
                activebackground="#363c4e",
                activeforeground="#ffffff",
                relief=tk.FLAT,
                font=("Segoe UI", 8, "bold"),
                command=lambda val=q: self._set_qty(val),
                cursor="hand2",
                width=4
            )
            btn.pack(side=tk.LEFT, expand=True, padx=2)

        # Row 2: Smart Max Controls
        btn_max_f = tk.Frame(qty_card, bg=self.PANEL_BG)
        btn_max_f.pack(fill=tk.X, padx=10, pady=(0, 8))

        btn_max_cash = tk.Button(
            btn_max_f,
            text="⚡ MAX CASH (F12)",
            bg="#2a2e39",
            fg="#f5a623",
            activebackground="#363c4e",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            font=("Segoe UI", 8, "bold"),
            command=self._set_max_cash,
            cursor="hand2"
        )
        btn_max_cash.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))

        btn_all_pos = tk.Button(
            btn_max_f,
            text="💼 ALL POS (M)",
            bg="#2a2e39",
            fg="#00bcd4",
            activebackground="#363c4e",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            font=("Segoe UI", 8, "bold"),
            command=self._set_all_pos,
            cursor="hand2"
        )
        btn_all_pos.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(2, 0))

        # Action Buttons
        btn_f = tk.Frame(self, bg=self.BG_COLOR)
        btn_f.pack(fill=tk.X, padx=10, pady=4)

        # Buy Button
        self.btn_buy = tk.Button(
            btn_f,
            text="BUY / LONG  (B / F1)",
            bg=self.GREEN,
            fg="#ffffff",
            activebackground=self.GREEN_HOVER,
            activeforeground="#ffffff",
            relief=tk.FLAT,
            font=("Segoe UI", 11, "bold"),
            command=self.do_buy,
            cursor="hand2",
            pady=6
        )
        self.btn_buy.pack(fill=tk.X, pady=(0, 6))

        # Sell Button
        self.btn_sell = tk.Button(
            btn_f,
            text="SELL / CLOSE  (S / F2)",
            bg=self.RED,
            fg="#ffffff",
            activebackground=self.RED_HOVER,
            activeforeground="#ffffff",
            relief=tk.FLAT,
            font=("Segoe UI", 11, "bold"),
            command=self.do_sell,
            cursor="hand2",
            pady=6
        )
        self.btn_sell.pack(fill=tk.X, pady=(0, 6))

        # Short & Cover Split Row
        sub_btn_f = tk.Frame(btn_f, bg=self.BG_COLOR)
        sub_btn_f.pack(fill=tk.X, pady=(0, 6))

        self.btn_short = tk.Button(
            sub_btn_f,
            text="SHORT (X / F3)",
            bg="#d9534f",
            fg="#ffffff",
            relief=tk.FLAT,
            font=("Segoe UI", 9, "bold"),
            command=self.do_short,
            cursor="hand2",
            pady=4
        )
        self.btn_short.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 3))

        self.btn_cover = tk.Button(
            sub_btn_f,
            text="COVER (C / F4)",
            bg=self.BLUE,
            fg="#ffffff",
            relief=tk.FLAT,
            font=("Segoe UI", 9, "bold"),
            command=self.do_cover,
            cursor="hand2",
            pady=4
        )
        self.btn_cover.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(3, 0))

        # Close Position Quick Action
        self.btn_close = tk.Button(
            btn_f,
            text="FLATTEN POSITION (Esc / F8)",
            bg="#363c4e",
            fg=self.TEXT_COLOR,
            relief=tk.FLAT,
            font=("Segoe UI", 9, "bold"),
            command=self.do_flatten,
            cursor="hand2",
            pady=4
        )
        self.btn_close.pack(fill=tk.X, pady=(4, 0))

        # Status / Feedback toast
        self.lbl_status = tk.Label(
            self,
            text="",
            bg=self.BG_COLOR,
            fg="#ffcc00",
            font=("Segoe UI", 8),
            wraplength=250
        )
        self.lbl_status.pack(fill=tk.X, padx=10, pady=(6, 0))

    def _shortcut_exec(self, func):
        func()
        return "break"

    def _defocus(self):
        self.master.focus_set()
        return "break"

    def _get_qty(self) -> int:
        try:
            val = int(self.ent_shares.get().strip())
            return max(0, val)
        except ValueError:
            return 100

    def _set_qty(self, qty: int):
        self.ent_shares.delete(0, tk.END)
        self.ent_shares.insert(0, str(qty))

    def _set_max_cash(self):
        """Set shares to maximum affordable using available cash."""
        stock = self.engine.stocks.get(self.active_ticker)
        if not stock or stock.price <= 0:
            return
        max_shares = int(self.engine.cash // stock.price)
        if max_shares <= 0:
            self._set_qty(0)
            self._flash_status(f"Cash (${self.engine.cash:,.2f}) insufficient for 1 share of {self.active_ticker} (${stock.price:.2f})!", is_error=True)
        else:
            self._set_qty(max_shares)
            self._flash_status(f"MAX CASH: {max_shares:,} shares (${max_shares * stock.price:,.2f})")

    def _set_all_pos(self):
        """Set shares to current open position size."""
        pos = self.engine.positions.get(self.active_ticker)
        if not pos or pos.shares == 0:
            self._flash_status(f"No open position in {self.active_ticker}!", is_error=True)
            return
        abs_shs = abs(pos.shares)
        self._set_qty(abs_shs)
        self._flash_status(f"ALL POS: {abs_shs:,} shares ({pos.side})")

    def _set_max_qty(self):
        """Smart MAX: toggles to all position shares if open, otherwise max cash."""
        pos = self.engine.positions.get(self.active_ticker)
        current_qty = self._get_qty()
        if pos and pos.shares != 0 and current_qty != abs(pos.shares):
            self._set_all_pos()
        else:
            self._set_max_cash()

    def _flash_status(self, msg: str, is_error: bool = False):
        color = self.RED if is_error else "#00e676"
        self.lbl_status.config(text=msg, fg=color)
        self.after(2500, lambda: self.lbl_status.config(text=""))

    def do_buy(self):
        qty = self._get_qty()
        if qty <= 0:
            self._flash_status("Please enter a valid share quantity (> 0)!", is_error=True)
            return
        stock = self.engine.stocks.get(self.active_ticker)
        if not stock:
            return
        if self.engine.cash < qty * stock.price:
            self._flash_status(f"Insufficient cash! Need ${(qty * stock.price):,.2f}", is_error=True)
            return

        ok = self.engine.buy(self.active_ticker, qty)
        if ok:
            self._flash_status(f"Bought {qty} {self.active_ticker} @ ${stock.price:.2f}")
            if self.on_trade_executed:
                self.on_trade_executed()
            self.update_display()
        else:
            self._flash_status("Buy order rejected.", is_error=True)

    def do_sell(self):
        qty = self._get_qty()
        stock = self.engine.stocks.get(self.active_ticker)
        pos = self.engine.positions.get(self.active_ticker)
        if not pos or pos.shares <= 0:
            self._flash_status("No Long position to sell!", is_error=True)
            return

        ok = self.engine.sell(self.active_ticker, qty)
        if ok:
            self._flash_status(f"Sold {qty} {self.active_ticker} @ ${stock.price:.2f}")
            if self.on_trade_executed:
                self.on_trade_executed()
            self.update_display()
        else:
            self._flash_status("Sell order rejected.", is_error=True)

    def do_short(self):
        qty = self._get_qty()
        stock = self.engine.stocks.get(self.active_ticker)
        if not stock:
            return
        pos = self.engine.positions.get(self.active_ticker)
        if pos and pos.shares > 0:
            self._flash_status("Close Long position first!", is_error=True)
            return

        ok = self.engine.short(self.active_ticker, qty)
        if ok:
            self._flash_status(f"Shorted {qty} {self.active_ticker} @ ${stock.price:.2f}")
            if self.on_trade_executed:
                self.on_trade_executed()
            self.update_display()
        else:
            self._flash_status("Short order rejected (Insufficient margin).", is_error=True)

    def do_cover(self):
        qty = self._get_qty()
        stock = self.engine.stocks.get(self.active_ticker)
        pos = self.engine.positions.get(self.active_ticker)
        if not pos or pos.shares >= 0:
            self._flash_status("No Short position to cover!", is_error=True)
            return

        ok = self.engine.cover(self.active_ticker, qty)
        if ok:
            self._flash_status(f"Covered {qty} {self.active_ticker} @ ${stock.price:.2f}")
            if self.on_trade_executed:
                self.on_trade_executed()
            self.update_display()
        else:
            self._flash_status("Cover order rejected.", is_error=True)

    def do_flatten(self):
        pos = self.engine.positions.get(self.active_ticker)
        if not pos or pos.shares == 0:
            self._flash_status("Position is already flat.")
            return
        ok = self.engine.close_position(self.active_ticker)
        if ok:
            self._flash_status(f"Flattened {self.active_ticker} position.")
            if self.on_trade_executed:
                self.on_trade_executed()
            self.update_display()

    def update_display(self):
        pos = self.engine.positions.get(self.active_ticker)
        stock = self.engine.stocks.get(self.active_ticker)
        if not pos or not stock:
            return

        # Position info
        if pos.shares > 0:
            self.lbl_pos_shares.config(text=f"LONG {pos.shares} shs", fg=self.GREEN)
        elif pos.shares < 0:
            self.lbl_pos_shares.config(text=f"SHORT {abs(pos.shares)} shs", fg=self.RED)
        else:
            self.lbl_pos_shares.config(text="FLAT (0 shs)", fg=self.MUTED_COLOR)

        self.lbl_pos_avg.config(text=f"${pos.avg_price:.2f}")

        # P&L
        pnl = pos.unrealized_pnl(stock.price)
        pct = pos.unrealized_pnl_pct(stock.price)
        if pos.shares == 0:
            self.lbl_pos_pnl.config(text="$0.00 (0.00%)", fg=self.MUTED_COLOR)
        else:
            color = self.GREEN if pnl >= 0 else self.RED
            sign = "+" if pnl >= 0 else ""
            self.lbl_pos_pnl.config(
                text=f"{sign}${pnl:,.2f} ({sign}{pct:.2f}%)",
                fg=color
            )
