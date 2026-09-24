import tkinter as tk
import time
from typing import List, Optional, Dict, Any
from simulation.stock import Stock, Candle

class CandlestickChart(tk.Frame):
    """
    High-performance, modern dark-themed Candlestick Chart with:
    - OHLC candles & wicks
    - Real-time live updating candle
    - 20-period SMA line
    - Volume histogram
    - Current price dotted guide line + badge
    - Trade execution markers over candles
    - Average entry price position guide line
    - Floating trade notifications / toast banner
    - Crosshair & HUD tooltip on mouse hover
    """
    BG_COLOR = "#131722"
    GRID_COLOR = "#1f2430"
    AXIS_TEXT = "#787b86"
    GREEN_CANDLE = "#089981"
    RED_CANDLE = "#f23645"
    SMA_COLOR = "#f5a623"
    VOL_GREEN = "#089981"
    VOL_RED = "#f23645"
    CROSSHAIR_COLOR = "#505668"

    def __init__(self, parent, stock: Optional[Stock] = None, **kwargs):
        super().__init__(parent, bg=self.BG_COLOR, **kwargs)
        self.stock = stock
        self.position: Optional[Any] = None
        self.active_notification: Optional[Dict[str, Any]] = None

        self.canvas = tk.Canvas(self, bg=self.BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Mouse hover state for crosshair
        self.hover_x: Optional[float] = None
        self.hover_y: Optional[float] = None
        self._layout_cache = None

        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Leave>", self._on_mouse_leave)
        self.canvas.bind("<Configure>", lambda e: self.draw())

    def set_stock(self, stock: Stock, position: Optional[Any] = None):
        self.stock = stock
        if position is not None:
            self.position = position
        self.draw()

    def set_position(self, position: Optional[Any]):
        self.position = position

    def show_trade_notification(self, action: str, shares: int, price: float, ticker: str):
        """Displays a prominent on-chart floating toast notification for executed trade."""
        self.active_notification = {
            "action": action,
            "shares": shares,
            "price": price,
            "ticker": ticker,
            "time": time.time()
        }
        self.draw()

    def _on_mouse_move(self, event):
        self.hover_x = event.x
        self.hover_y = event.y
        self._render_crosshair()

    def _on_mouse_leave(self, event):
        self.hover_x = None
        self.hover_y = None
        self.canvas.delete("crosshair")

    def draw(self):
        self.canvas.delete("all")
        if not self.stock:
            return

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        if width <= 50 or height <= 50:
            return

        candles = self.stock.get_all_candles()
        if not candles:
            return

        # Layout boundaries
        right_margin = 75
        bottom_margin = 25
        top_margin = 35
        left_margin = 15

        chart_w = width - left_margin - right_margin
        chart_h = height - top_margin - bottom_margin

        # We allocate top 75% for candles and bottom 25% for volume
        vol_h = chart_h * 0.22
        price_h = chart_h * 0.74
        vol_top = top_margin + price_h + (chart_h * 0.04)

        # Limit number of visible candles to fit comfortably
        candle_slot_w = 12
        max_visible = max(10, int(chart_w / candle_slot_w))
        visible_candles = candles[-max_visible:]
        num_candles = len(visible_candles)

        if num_candles == 0:
            return

        candle_spacing = chart_w / max_visible
        body_width = max(3, candle_spacing * 0.7)

        # Calculate Price min/max
        min_p = min(c.low for c in visible_candles)
        max_p = max(c.high for c in visible_candles)
        if max_p == min_p:
            max_p += 1.0
            min_p -= 1.0

        # Add 5% padding to price bounds
        p_padding = (max_p - min_p) * 0.06
        min_p = max(0.01, min_p - p_padding)
        max_p = max_p + p_padding
        p_range = max_p - min_p

        # Calculate Volume max
        max_vol = max((c.volume for c in visible_candles), default=1)
        if max_vol == 0:
            max_vol = 1

        # Helper coordinate converter
        def p_to_y(price: float) -> float:
            return top_margin + price_h - ((price - min_p) / p_range * price_h)

        def vol_to_y(vol: int) -> float:
            h = (vol / max_vol) * vol_h
            return (vol_top + vol_h) - h

        # --- DRAW HORIZONTAL PRICE GRID & LABELS ---
        num_grid_lines = 6
        for i in range(num_grid_lines):
            grid_price = min_p + (p_range / (num_grid_lines - 1)) * i
            gy = p_to_y(grid_price)
            # Grid line
            self.canvas.create_line(left_margin, gy, width - right_margin, gy, fill=self.GRID_COLOR, dash=(2, 4))
            # Right axis price label
            self.canvas.create_text(
                width - right_margin + 6, gy,
                text=f"${grid_price:.2f}",
                fill=self.AXIS_TEXT,
                anchor="w",
                font=("Segoe UI", 9)
            )

        # --- DRAW VOLUME SEPARATOR ---
        self.canvas.create_line(left_margin, vol_top - 2, width - right_margin, vol_top - 2, fill=self.GRID_COLOR)
        self.canvas.create_text(
            width - right_margin + 6, vol_top + 10,
            text=f"Vol: {max_vol:,}",
            fill=self.AXIS_TEXT,
            anchor="w",
            font=("Segoe UI", 8)
        )

        # --- COMPUTE 20 SMA ---
        all_closes = [c.close for c in candles]
        sma_points = []
        sma_period = 15

        # Precompute SMA map
        candle_indices = range(len(candles) - num_candles, len(candles))
        for idx in candle_indices:
            if idx >= sma_period - 1:
                window = all_closes[idx - sma_period + 1 : idx + 1]
                avg = sum(window) / len(window)
            else:
                avg = sum(all_closes[:idx+1]) / (idx + 1)
            sma_points.append(avg)

        # --- DRAW CANDLES & VOLUME ---
        candle_centers = []
        for i, c in enumerate(visible_candles):
            cx = left_margin + (i * candle_spacing) + (candle_spacing / 2)
            candle_centers.append(cx)

            is_bull = c.close >= c.open
            color = self.GREEN_CANDLE if is_bull else self.RED_CANDLE

            # Volume Bar
            vy = vol_to_y(c.volume)
            v_bottom = vol_top + vol_h
            self.canvas.create_rectangle(
                cx - (body_width / 2), vy,
                cx + (body_width / 2), v_bottom,
                fill=color,
                outline=color
            )

            # Candle Wick
            hy = p_to_y(c.high)
            ly = p_to_y(c.low)
            self.canvas.create_line(cx, hy, cx, ly, fill=color, width=1.5)

            # Candle Body
            oy = p_to_y(c.open)
            cy = p_to_y(c.close)
            top_y = min(oy, cy)
            bot_y = max(oy, cy)
            if bot_y - top_y < 1.5:
                bot_y = top_y + 1.5

            self.canvas.create_rectangle(
                cx - (body_width / 2), top_y,
                cx + (body_width / 2), bot_y,
                fill=color,
                outline=color
            )

        # --- DRAW SMA LINE ---
        if len(sma_points) > 1:
            line_coords = []
            for i, sma_val in enumerate(sma_points):
                cx = candle_centers[i]
                cy = p_to_y(sma_val)
                line_coords.extend([cx, cy])
            self.canvas.create_line(line_coords, fill=self.SMA_COLOR, width=1.5, smooth=True)

        # --- DRAW CURRENT PRICE LEVEL (DASHED LINE + BADGE) ---
        curr_y = p_to_y(self.stock.price)
        is_up = self.stock.change_pct >= 0
        tag_color = self.GREEN_CANDLE if is_up else self.RED_CANDLE

        self.canvas.create_line(left_margin, curr_y, width - right_margin, curr_y, fill=tag_color, dash=(3, 3), width=1)
        # Price pill badge on right axis
        badge_h = 16
        self.canvas.create_rectangle(
            width - right_margin, curr_y - badge_h/2,
            width - 5, curr_y + badge_h/2,
            fill=tag_color,
            outline=tag_color
        )
        self.canvas.create_text(
            width - right_margin + 3, curr_y,
            text=f"${self.stock.price:.2f}",
            fill="#ffffff",
            anchor="w",
            font=("Segoe UI", 9, "bold")
        )

        # --- DRAW TRADE MARKERS OVER CANDLES ---
        if self.stock and self.stock.trade_markers:
            for i, c in enumerate(visible_candles):
                cx = candle_centers[i]
                # Match markers for this candle
                markers = [m for m in self.stock.trade_markers if abs(m.candle_timestamp - c.timestamp) < 0.001]
                if not markers:
                    continue

                for marker in markers:
                    act = marker.action.upper()
                    shs = marker.shares
                    if act in ("BUY", "COVER"):
                        # Render BELOW candle low pointing up
                        color = self.GREEN_CANDLE if act == "BUY" else "#2962ff"
                        base_y = p_to_y(c.low) + 16
                        base_y = min(vol_top - 18, max(top_margin + 24, base_y))
                        # Upward pointer
                        self.canvas.create_polygon(
                            cx, p_to_y(c.low) + 3,
                            cx - 5, base_y - 2,
                            cx + 5, base_y - 2,
                            fill=color, outline=""
                        )
                        # Pill badge
                        badge_txt = f"+{shs}" if act == "BUY" else f"COV {shs}"
                        pw = max(38, len(badge_txt) * 7 + 10)
                        self.canvas.create_rectangle(
                            cx - pw/2, base_y - 2,
                            cx + pw/2, base_y + 14,
                            fill=color, outline="#ffffff", width=1
                        )
                        self.canvas.create_text(
                            cx, base_y + 6,
                            text=badge_txt,
                            fill="#ffffff",
                            font=("Segoe UI", 8, "bold")
                        )
                    else:
                        # Render ABOVE candle high pointing down
                        color = self.RED_CANDLE if act == "SHORT" else "#ff9800"
                        base_y = p_to_y(c.high) - 16
                        base_y = max(top_margin + 12, min(vol_top - 24, base_y))
                        # Downward pointer
                        self.canvas.create_polygon(
                            cx, p_to_y(c.high) - 3,
                            cx - 5, base_y + 2,
                            cx + 5, base_y + 2,
                            fill=color, outline=""
                        )
                        # Pill badge
                        badge_txt = f"-{shs}" if act == "SHORT" else f"SEL {shs}"
                        pw = max(38, len(badge_txt) * 7 + 10)
                        self.canvas.create_rectangle(
                            cx - pw/2, base_y - 14,
                            cx + pw/2, base_y + 2,
                            fill=color, outline="#ffffff", width=1
                        )
                        self.canvas.create_text(
                            cx, base_y - 6,
                            text=badge_txt,
                            fill="#ffffff",
                            font=("Segoe UI", 8, "bold")
                        )

        # --- DRAW ACTIVE POSITION ENTRY PRICE GUIDE LINE ---
        if self.position and self.position.shares != 0 and self.position.avg_price > 0:
            pos_y = p_to_y(self.position.avg_price)
            if top_margin <= pos_y <= vol_top:
                is_long = self.position.shares > 0
                pos_col = "#00e676" if is_long else "#ff5252"
                self.canvas.create_line(left_margin, pos_y, width - right_margin, pos_y, fill=pos_col, dash=(4, 4), width=1.5)

                pnl = self.position.unrealized_pnl(self.stock.price)
                pct = self.position.unrealized_pnl_pct(self.stock.price)
                side_lbl = f"LONG {self.position.shares}" if is_long else f"SHORT {abs(self.position.shares)}"
                pos_text = f"🎯 {side_lbl} @ ${self.position.avg_price:.2f} ({'+' if pnl >= 0 else ''}${pnl:,.2f} | {'+' if pct >= 0 else ''}{pct:.1f}%)"

                badge_w = len(pos_text) * 6.5 + 14
                self.canvas.create_rectangle(
                    left_margin + 6, pos_y - 9,
                    left_margin + 6 + badge_w, pos_y + 9,
                    fill="#161a25", outline=pos_col, width=1
                )
                self.canvas.create_text(
                    left_margin + 12, pos_y,
                    text=pos_text,
                    fill=pos_col,
                    anchor="w",
                    font=("Segoe UI", 8, "bold")
                )

        # --- DRAW FLOATING TRADE NOTIFICATION TOAST ---
        if self.active_notification:
            elapsed = time.time() - self.active_notification["time"]
            if elapsed < 3.5:
                n = self.active_notification
                act = n["action"].upper()
                if act == "BUY":
                    badge_col = "#089981"
                    icon = "🛒"
                    title = f"BOUGHT {n['shares']:,} {n['ticker']} @ ${n['price']:.2f}"
                    sub = f"Cost: ${n['shares'] * n['price']:,.2f}"
                elif act == "SHORT":
                    badge_col = "#f23645"
                    icon = "⚡"
                    title = f"SHORTED {n['shares']:,} {n['ticker']} @ ${n['price']:.2f}"
                    sub = f"Margin: ${n['shares'] * n['price'] * 0.5:,.2f}"
                elif act == "SELL":
                    badge_col = "#ff9800"
                    icon = "💰"
                    title = f"SOLD {n['shares']:,} {n['ticker']} @ ${n['price']:.2f}"
                    sub = "Closed / Reduced Long"
                else:
                    badge_col = "#2962ff"
                    icon = "🛡️"
                    title = f"COVERED {n['shares']:,} {n['ticker']} @ ${n['price']:.2f}"
                    sub = "Closed / Reduced Short"

                toast_text = f"{icon} {title}  •  {sub}"
                card_w = max(320, len(toast_text) * 7.5 + 24)
                card_h = 30
                center_x = (width - right_margin + left_margin) / 2
                top_y = top_margin + 4

                self.canvas.create_rectangle(
                    center_x - card_w/2, top_y,
                    center_x + card_w/2, top_y + card_h,
                    fill="#161a25", outline=badge_col, width=1.5
                )
                self.canvas.create_text(
                    center_x, top_y + card_h/2,
                    text=toast_text,
                    fill="#ffffff",
                    font=("Segoe UI", 9, "bold")
                )
            else:
                self.active_notification = None

        # --- DRAW HEADER INFO ---
        self._draw_header(left_margin)

        # Cache layout parameters for fast crosshair rendering on mouse motion
        self._layout_cache = {
            "candle_centers": candle_centers,
            "visible_candles": visible_candles,
            "width": width,
            "height": height,
            "right_margin": right_margin,
            "bottom_margin": bottom_margin,
            "p_to_y": p_to_y,
            "min_p": min_p,
            "p_range": p_range,
            "price_h": price_h,
            "top_margin": top_margin,
            "left_margin": left_margin
        }

        # --- DRAW CROSSHAIR & TOOLTIP IF HOVERING ---
        if self.hover_x is not None and self.hover_y is not None:
            self._render_crosshair()

    def _render_crosshair(self):
        """Ultra-fast crosshair rendering without redrawing the entire chart."""
        self.canvas.delete("crosshair")
        if not self._layout_cache or self.hover_x is None or self.hover_y is None:
            return

        c = self._layout_cache
        hx, hy = self.hover_x, self.hover_y
        left_m = c["left_margin"]
        right_m = c["right_margin"]
        top_m = c["top_margin"]
        bottom_m = c["bottom_margin"]
        w = c["width"]
        h = c["height"]

        if not (left_m <= hx <= w - right_m and top_m <= hy <= h - bottom_m):
            return

        candle_centers = c["candle_centers"]
        visible_candles = c["visible_candles"]
        if not candle_centers:
            return

        # Find closest candle to hover_x
        best_idx = 0
        min_dist = float('inf')
        for i, cx in enumerate(candle_centers):
            dist = abs(cx - hx)
            if dist < min_dist:
                min_dist = dist
                best_idx = i

        snap_x = candle_centers[best_idx]
        candle = visible_candles[best_idx]

        # Vertical line
        self.canvas.create_line(snap_x, 30, snap_x, h - bottom_m, fill=self.CROSSHAIR_COLOR, dash=(2, 2), tags="crosshair")
        # Horizontal line
        self.canvas.create_line(15, hy, w - right_m, hy, fill=self.CROSSHAIR_COLOR, dash=(2, 2), tags="crosshair")

        # Y-axis hover price
        hover_price = c["min_p"] + ((top_m + c["price_h"] - hy) / c["price_h"]) * c["p_range"]
        self.canvas.create_rectangle(
            w - right_m, hy - 9,
            w - 5, hy + 9,
            fill="#363c4e",
            outline="#505668",
            tags="crosshair"
        )
        self.canvas.create_text(
            w - right_m + 3, hy,
            text=f"${hover_price:.2f}",
            fill="#ffffff",
            anchor="w",
            font=("Segoe UI", 8),
            tags="crosshair"
        )

        # Check if hovered candle has trade markers
        markers = [m for m in self.stock.trade_markers if abs(m.candle_timestamp - candle.timestamp) < 0.001] if self.stock else []
        marker_str = ""
        if markers:
            m_parts = [f"{m.action} {m.shares} @ ${m.price:.2f}" for m in markers]
            marker_str = " | ★ " + ", ".join(m_parts)

        # Floating HUD at top right of canvas
        hud_text = f"O: ${candle.open:.2f}  H: ${candle.high:.2f}  L: ${candle.low:.2f}  C: ${candle.close:.2f}  Vol: {candle.volume:,}{marker_str}"
        self.canvas.create_text(
            w - right_m - 10, 18,
            text=hud_text,
            fill="#d1d4dc",
            anchor="e",
            font=("Segoe UI", 9, "bold"),
            tags="crosshair"
        )

    def _draw_header(self, left_x: float):
        """Top banner inside canvas showing ticker, price, change, and indicator legend."""
        ticker = self.stock.ticker
        name = self.stock.name
        price = f"${self.stock.price:.2f}"
        pct = self.stock.change_pct
        pct_str = f"{'+' if pct >= 0 else ''}{pct:.2f}% (${self.stock.change_amount:+.2f})"
        color = self.GREEN_CANDLE if pct >= 0 else self.RED_CANDLE

        self.canvas.create_text(
            left_x, 18,
            text=f"{ticker}",
            fill="#ffffff",
            anchor="w",
            font=("Segoe UI", 14, "bold")
        )
        self.canvas.create_text(
            left_x + 65, 18,
            text=f"{name} • {self.stock.sector}",
            fill=self.AXIS_TEXT,
            anchor="w",
            font=("Segoe UI", 9)
        )
        self.canvas.create_text(
            left_x + 310, 18,
            text=price,
            fill="#ffffff",
            anchor="w",
            font=("Segoe UI", 13, "bold")
        )
        self.canvas.create_text(
            left_x + 395, 18,
            text=pct_str,
            fill=color,
            anchor="w",
            font=("Segoe UI", 11, "bold")
        )

        # Legend: 15 SMA
        self.canvas.create_line(left_x + 550, 18, left_x + 565, 18, fill=self.SMA_COLOR, width=2)
        self.canvas.create_text(
            left_x + 570, 18,
            text="15 SMA",
            fill=self.SMA_COLOR,
            anchor="w",
            font=("Segoe UI", 9, "bold")
        )
