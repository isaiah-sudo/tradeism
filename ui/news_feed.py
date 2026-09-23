import tkinter as tk
from tkinter import ttk
from typing import List
from simulation.news import NewsItem

class NewsFeedPanel(tk.Frame):
    """
    Bottom news feed panel showing real-time breaking market catalysts,
    sentiment tags, and animated flash banner on new alerts.
    """
    BG_COLOR = "#181a20"
    ITEM_BG = "#222631"
    GREEN = "#089981"
    RED = "#f23645"
    CYAN = "#00bcd4"
    YELLOW = "#f5a623"
    MUTED = "#848e9c"

    def __init__(self, parent, news_list: List[NewsItem], **kwargs):
        super().__init__(parent, bg=self.BG_COLOR, **kwargs)
        self.news_list = news_list

        self._build_ui()

    def _build_ui(self):
        # Header banner
        self.header_frame = tk.Frame(self, bg="#272b38", height=28)
        self.header_frame.pack(fill=tk.X, padx=8, pady=(6, 2))

        self.lbl_flash = tk.Label(
            self.header_frame,
            text="⚡ BREAKING NEWS TICKER",
            bg="#272b38",
            fg=self.CYAN,
            font=("Segoe UI", 9, "bold")
        )
        self.lbl_flash.pack(side=tk.LEFT, padx=8)

        self.lbl_latest_headline = tk.Label(
            self.header_frame,
            text="Awaiting market catalysts...",
            bg="#272b38",
            fg="#eaecef",
            font=("Segoe UI", 9)
        )
        self.lbl_latest_headline.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        # Scrollable container for list of past news
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

    def trigger_flash(self, item: NewsItem):
        """Flash top bar when breaking news hits."""
        shock_pct = f"{item.shock_pct * 100:+.1f}%"
        self.lbl_latest_headline.config(
            text=f"[{item.time_str}] [{item.ticker}] {item.headline} (Impact: {shock_pct})"
        )

        flash_color = "#3d1417" if item.sentiment == "BEARISH" else "#0e3427"
        normal_color = "#272b38"

        def _flash_step(count):
            if count <= 0:
                self.header_frame.config(bg=normal_color)
                self.lbl_flash.config(bg=normal_color)
                self.lbl_latest_headline.config(bg=normal_color)
                return
            c = flash_color if count % 2 == 1 else normal_color
            self.header_frame.config(bg=c)
            self.lbl_flash.config(bg=c)
            self.lbl_latest_headline.config(bg=c)
            self.after(160, lambda: _flash_step(count - 1))

        _flash_step(6)

    def _create_news_row(self, item: NewsItem, pack_before=None) -> tk.Frame:
        row = tk.Frame(self.scrollable_inner, bg=self.ITEM_BG, bd=1, relief=tk.FLAT)
        if pack_before:
            row.pack(fill=tk.X, pady=2, padx=2, before=pack_before)
        else:
            row.pack(fill=tk.X, pady=2, padx=2)

        # Time tag
        tk.Label(row, text=item.time_str, font=("Segoe UI", 8), fg=self.MUTED, bg=self.ITEM_BG).pack(side=tk.LEFT, padx=(6, 4), pady=4)

        # Ticker tag
        tk.Label(row, text=f"[{item.ticker}]", font=("Segoe UI", 9, "bold"), fg="#ffffff", bg=self.ITEM_BG).pack(side=tk.LEFT, padx=(0, 6), pady=4)

        # Sentiment Pill Badge
        sent_color = self.GREEN if item.sentiment == "BULLISH" else (self.RED if item.sentiment == "BEARISH" else self.YELLOW)
        lbl_sent = tk.Label(
            row,
            text=item.sentiment,
            font=("Segoe UI", 7, "bold"),
            fg="#ffffff",
            bg=sent_color,
            padx=4, pady=1
        )
        lbl_sent.pack(side=tk.LEFT, padx=(0, 8), pady=4)

        # Headline text
        tk.Label(
            row,
            text=item.headline,
            font=("Segoe UI", 9),
            fg="#eaecef",
            bg=self.ITEM_BG,
            anchor="w",
            justify="left"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, pady=4)

        # Shock badge
        if item.shock_pct != 0:
            tk.Label(
                row,
                text=f"{item.shock_pct * 100:+.1f}%",
                font=("Segoe UI", 8, "bold"),
                fg=sent_color,
                bg=self.ITEM_BG
            ).pack(side=tk.RIGHT, padx=8, pady=4)

        return row

    def refresh_news(self, news_items: List[NewsItem]):
        if not news_items:
            return

        children = self.scrollable_inner.winfo_children()
        if not children:
            for item in news_items[:20]:
                self._create_news_row(item)
            self._last_rendered_id = news_items[0].id if news_items else None
            return

        latest_item = news_items[0]
        if getattr(self, "_last_rendered_id", None) == latest_item.id:
            return
        self._last_rendered_id = latest_item.id

        # Insert new item at top
        first_child = children[0] if children else None
        self._create_news_row(latest_item, pack_before=first_child)

        # Prune oldest items
        current_children = self.scrollable_inner.winfo_children()
        if len(current_children) > 25:
            current_children[-1].destroy()
