import math
import random
import time
from collections import deque
from dataclasses import dataclass, field
from typing import List, Optional, Deque

@dataclass
class Candle:
    timestamp: float
    open: float
    high: float
    low: float
    close: float
    volume: int

@dataclass
class TradeMarker:
    candle_timestamp: float
    action: str          # BUY, SELL, SHORT, COVER
    shares: int
    price: float
    time_str: str

class Stock:
    def __init__(self, ticker: str, name: str, sector: str, initial_price: float, volatility: float, tick_per_candle: int = 5):
        self.ticker = ticker
        self.name = name
        self.sector = sector
        self.initial_price = initial_price
        self.prev_close = initial_price
        self.price = initial_price
        self.base_volatility = volatility  # Typical standard deviation per step (e.g. 0.015 = 1.5%)
        self.volatility = volatility
        self.drift = 0.0                   # Current momentum / directional pressure
        self.drift_decay = 0.958           # Drift decays smoothly over more time
        self.tick_per_candle = tick_per_candle

        # Candlestick management with bounded deque for O(1) appends
        self.max_candles = 80
        self.candles: Deque[Candle] = deque(maxlen=self.max_candles)
        self.current_tick_count = 0
        self.current_candle: Optional[Candle] = None
        self.trade_markers: List[TradeMarker] = []

        # Pre-seed historical candles so chart starts with rich data
        self._seed_history(50)

    def _seed_history(self, num_candles: int):
        import random
        price = self.initial_price * random.uniform(0.85, 1.15)
        now = time.time() - (num_candles * 5)
        for i in range(num_candles):
            open_p = price
            # Random walk for candle
            ret = random.gauss(0, self.base_volatility * 1.5)
            close_p = max(0.5, open_p * (1.0 + ret))
            high_p = max(open_p, close_p) * (1.0 + abs(random.gauss(0, self.base_volatility * 1.5)))
            low_p = min(open_p, close_p) * (1.0 - abs(random.gauss(0, self.base_volatility * 1.5)))
            low_p = max(0.2, low_p)
            vol = int(random.uniform(5000, 80000))
            self.candles.append(Candle(
                timestamp=now + (i * 5),
                open=round(open_p, 2),
                high=round(high_p, 2),
                low=round(low_p, 2),
                close=round(close_p, 2),
                volume=vol
            ))
            price = close_p
        
        self.price = round(price, 2)
        self.prev_close = self.candles[0].open
        self._start_new_candle(time.time())

    def _start_new_candle(self, timestamp: float):
        self.current_candle = Candle(
            timestamp=timestamp,
            open=self.price,
            high=self.price,
            low=self.price,
            close=self.price,
            volume=0
        )
        self.current_tick_count = 0

    def apply_shock(self, price_multiplier: float, extra_drift: float, extra_volatility: float = 0.015):
        """Called when news catalyst hits this stock."""
        self.price = max(0.10, round(self.price * price_multiplier, 2))
        self.drift = max(-0.045, min(0.045, self.drift + extra_drift))
        self.volatility = min(0.05, self.volatility + extra_volatility)
        if self.current_candle:
            self.current_candle.high = max(self.current_candle.high, self.price)
            self.current_candle.low = min(self.current_candle.low, self.price)
            self.current_candle.close = self.price
            self.current_candle.volume += int(abs(extra_drift) * 150000) + 10000

    def step(self, market_trend: float = 0.0) -> float:
        """Simulate one tick of price movement."""
        # Decay temporary news drift and volatility back toward baseline smoothly
        self.drift *= self.drift_decay
        self.volatility += (self.base_volatility - self.volatility) * 0.05

        # Price movement: drift + random shock + market trend
        micro_spike = 0.0
        if random.random() < 0.03:
            micro_spike = random.choice([-1, 1]) * random.uniform(0.005, 0.02)

        shock = random.gauss(0, self.volatility) + self.drift + (market_trend * 0.5) + micro_spike

        # Bound per-tick moves to avoid violent single-tick spikes
        max_tick_delta = 0.06
        shock = max(-max_tick_delta, min(max_tick_delta, shock))

        new_price = max(0.10, self.price * (1.0 + shock))
        self.price = round(new_price, 2)

        # Volume for this tick
        tick_vol = int(random.uniform(500, 15000) * (1.0 + abs(shock) * 20))

        # Update active candle
        if self.current_candle is None:
            self._start_new_candle(time.time())

        self.current_candle.high = max(self.current_candle.high, self.price)
        self.current_candle.low = min(self.current_candle.low, self.price)
        self.current_candle.close = self.price
        self.current_candle.volume += tick_vol
        self.current_tick_count += 1

        # Check if candle is complete (deque auto-evicts oldest item)
        if self.current_tick_count >= self.tick_per_candle:
            self.candles.append(self.current_candle)
            self._start_new_candle(time.time())

        return self.price

    @property
    def change_pct(self) -> float:
        if self.prev_close == 0:
            return 0.0
        return ((self.price - self.prev_close) / self.prev_close) * 100.0

    @property
    def change_amount(self) -> float:
        return self.price - self.prev_close

    def get_all_candles(self) -> List[Candle]:
        """Returns historical completed candles plus current live candle."""
        result = list(self.candles)
        if self.current_candle is not None:
            result.append(self.current_candle)
        return result

    def add_trade_marker(self, action: str, shares: int, price: float, time_str: str) -> TradeMarker:
        """Record trade execution marker for the active candle."""
        ts = self.current_candle.timestamp if self.current_candle else (self.candles[-1].timestamp if self.candles else time.time())
        marker = TradeMarker(
            candle_timestamp=ts,
            action=action,
            shares=shares,
            price=price,
            time_str=time_str
        )
        self.trade_markers.append(marker)
        if len(self.trade_markers) > 100:
            self.trade_markers.pop(0)
        return marker
