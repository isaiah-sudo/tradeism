import tkinter as tk
from typing import List
from simulation.engine import TradeLog

class TradeLogPanel(tk.Frame):
    """
    Bottom trade execution log panel showing time, action, ticker, shares, price, and realized P&L.
    """
    BG_COLOR = "#181a20"
    ITEM_BG = "#222631"
    GREEN = "#089981"
    RED = "#f23645"
    MUTED = "#848e9c"

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=self.BG_COLOR, **kwargs)
        self._build_ui()

    def _build_ui(self):
        # Table Header
        header = tk.Frame(self, bg="#272b38", height=26)
        header.pack(fill=tk.X, padx=8, pady=(6, 2))

        headers = [("TIME", 8), ("ACTION", 8), ("TICKER", 8), ("SHARES", 10), ("PRICE", 10), ("P&L", 12)]
        for text, width in headers:
            tk.Label(
                header,
                text=text,
                font=("Segoe UI", 8, "bold"),
                fg="#929aa5",
                bg="#272b38",
                width=width,
                anchor="w"
            ).pack(side=tk.LEFT, padx=4)

        # Scrollable container
        content_frame = tk.Frame(self, bg=self.BG_COLOR)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        self.canvas = tk.Canvas(content_frame, bg=self.BG_COLOR, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=self.canvas.yview)
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

    def _create_trade_row(self, t: TradeLog, pack_before=None) -> tk.Frame:
        row = tk.Frame(self.scrollable_inner, bg=self.ITEM_BG, bd=1, relief=tk.FLAT)
        if pack_before:
            row.pack(fill=tk.X, pady=2, padx=2, before=pack_before)
        else:
            row.pack(fill=tk.X, pady=2, padx=2)

        # Time
        tk.Label(row, text=t.time_str, font=("Segoe UI", 8), fg=self.MUTED, bg=self.ITEM_BG, width=8, anchor="w").pack(side=tk.LEFT, padx=4, pady=3)

        # Action
        act_color = self.GREEN if t.action in ("BUY", "COVER") else self.RED
        tk.Label(row, text=t.action, font=("Segoe UI", 8, "bold"), fg=act_color, bg=self.ITEM_BG, width=8, anchor="w").pack(side=tk.LEFT, padx=4, pady=3)

        # Ticker
        tk.Label(row, text=t.ticker, font=("Segoe UI", 8, "bold"), fg="#ffffff", bg=self.ITEM_BG, width=8, anchor="w").pack(side=tk.LEFT, padx=4, pady=3)

        # Shares
        tk.Label(row, text=f"{t.shares:,}", font=("Segoe UI", 8), fg="#eaecef", bg=self.ITEM_BG, width=10, anchor="w").pack(side=tk.LEFT, padx=4, pady=3)

        # Price
        tk.Label(row, text=f"${t.price:.2f}", font=("Segoe UI", 8), fg="#eaecef", bg=self.ITEM_BG, width=10, anchor="w").pack(side=tk.LEFT, padx=4, pady=3)

        # P&L
        if t.pnl is not None:
            pnl_color = self.GREEN if t.pnl >= 0 else self.RED
            pnl_text = f"{'+' if t.pnl >= 0 else ''}${t.pnl:,.2f}"
        else:
            pnl_color = self.MUTED
            pnl_text = "-"
        tk.Label(row, text=pnl_text, font=("Segoe UI", 8, "bold"), fg=pnl_color, bg=self.ITEM_BG, width=12, anchor="w").pack(side=tk.LEFT, padx=4, pady=3)
        return row

    def refresh_trades(self, trades: List[TradeLog]):
        if not trades:
            for child in self.scrollable_inner.winfo_children():
                child.destroy()
            lbl = tk.Label(
                self.scrollable_inner,
                text="No executed orders yet. Use Buy/Sell/Short/Cover buttons to trade!",
                font=("Segoe UI", 9),
                fg=self.MUTED,
                bg=self.BG_COLOR
            )
            lbl.pack(pady=15)
            self._has_empty_placeholder = True
            return

        # Clear placeholder if present
        if getattr(self, "_has_empty_placeholder", False):
            for child in self.scrollable_inner.winfo_children():
                child.destroy()
            self._has_empty_placeholder = False

        children = self.scrollable_inner.winfo_children()
        if not children:
            for t in trades[:30]:
                self._create_trade_row(t)
            return

        # Prepend latest trade at top
        latest_trade = trades[0]
        self._create_trade_row(latest_trade, pack_before=children[0])

        current_children = self.scrollable_inner.winfo_children()
        if len(current_children) > 30:
            current_children[-1].destroy()
