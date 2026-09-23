import tkinter as tk
from typing import List, Optional
from simulation.stock import Stock, Candle

class CandlestickChart(tk.Frame):
    """
    High-performance, modern dark-themed Candlestick Chart with:
    - OHLC candles & wicks
    - Real-time live updating candle
    - 20-period SMA line
    - Volume histogram
    - Current price dotted guide line + badge
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

        self.canvas = tk.Canvas(self, bg=self.BG_COLOR, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Mouse hover state for crosshair
        self.hover_x: Optional[float] = None
        self.hover_y: Optional[float] = None
        self._layout_cache = None

        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Leave>", self._on_mouse_leave)
        self.canvas.bind("<Configure>", lambda e: self.draw())

    def set_stock(self, stock: Stock):
        self.stock = stock
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

        # Floating HUD at top right of canvas
        hud_text = f"O: ${candle.open:.2f}  H: ${candle.high:.2f}  L: ${candle.low:.2f}  C: ${candle.close:.2f}  Vol: {candle.volume:,}"
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
