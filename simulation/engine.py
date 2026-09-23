import time
import random
from typing import Dict, List, Optional
from simulation.stock import Stock
from simulation.news import NewsGenerator, NewsItem
from simulation.stock_universe import STOCK_DEFINITIONS

class Position:
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.shares = 0         # Positive = Long, Negative = Short, 0 = Flat
        self.avg_price = 0.0

    @property
    def side(self) -> str:
        if self.shares > 0:
            return "LONG"
        elif self.shares < 0:
            return "SHORT"
        return "FLAT"

    def current_value(self, current_price: float) -> float:
        """Market value or margin exposure."""
        return abs(self.shares) * current_price

    def unrealized_pnl(self, current_price: float) -> float:
        if self.shares == 0:
            return 0.0
        if self.shares > 0:
            # Long: (current - avg) * shares
            return (current_price - self.avg_price) * self.shares
        else:
            # Short: (avg - current) * abs(shares)
            return (self.avg_price - current_price) * abs(self.shares)

    def unrealized_pnl_pct(self, current_price: float) -> float:
        if self.shares == 0 or self.avg_price == 0:
            return 0.0
        if self.shares > 0:
            return ((current_price - self.avg_price) / self.avg_price) * 100.0
        else:
            return ((self.avg_price - current_price) / self.avg_price) * 100.0

class TradeLog:
    def __init__(self, time_str: str, ticker: str, action: str, shares: int, price: float, pnl: Optional[float] = None):
        self.time_str = time_str
        self.ticker = ticker
        self.action = action     # BUY, SELL, SHORT, COVER
        self.shares = shares
        self.price = price
        self.pnl = pnl

class MarketEngine:
    DIFFICULTIES = {
        "Relaxed (1x)": {"tick_ms": 1000, "news_prob": 0.03, "label": "Casual Trader (1 tick/sec)"},
        "Day Trader (3x)": {"tick_ms": 330, "news_prob": 0.05, "label": "Active Day Trader (3 ticks/sec)"},
        "High Frequency (8x)": {"tick_ms": 125, "news_prob": 0.08, "label": "HFT Scalper (8 ticks/sec)"},
        "TURBO INSANE (20x)": {"tick_ms": 50, "news_prob": 0.12, "label": "Adrenaline Junkie (20 ticks/sec)"},
    }

    def __init__(self, initial_cash: float = 25000.0):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.realized_pnl = 0.0
        self.positions: Dict[str, Position] = {}
        self.trades: List[TradeLog] = []

        # News engine
        self.news_gen = NewsGenerator()
        self.news_feed: List[NewsItem] = []
        self.latest_news: Optional[NewsItem] = None
        self.ticks_since_news = 0

        # Market trend (macro drift)
        self.macro_trend = 0.0

        # Difficulty / Speed
        self.current_difficulty = "Day Trader (3x)"
        self.is_paused = False

        # Initialize 100 volatile stocks across all sectors
        self.stocks: Dict[str, Stock] = {}
        for ticker, name, sector, init_p, vol in STOCK_DEFINITIONS:
            self.stocks[ticker] = Stock(ticker, name, sector, initial_price=init_p, volatility=vol)

        for ticker in self.stocks:
            self.positions[ticker] = Position(ticker)

        # Seed with initial market welcome news
        welcome_news = NewsItem(
            id=0,
            timestamp=time.time(),
            time_str=time.strftime("%H:%M:%S"),
            ticker="MARKET",
            headline="Wall Street bell rings! High volatility expected across tech, meme, and biotech sectors.",
            sentiment="NEUTRAL",
            shock_pct=0.0,
            momentum_drift=0.0,
            importance="BREAKING"
        )
        self.news_feed.append(welcome_news)
        self.latest_news = welcome_news

    @property
    def total_equity(self) -> float:
        equity = self.cash
        for ticker, pos in self.positions.items():
            if pos.shares != 0:
                current_p = self.stocks[ticker].price
                equity += pos.unrealized_pnl(current_p)
        return equity

    @property
    def total_unrealized_pnl(self) -> float:
        unrealized = 0.0
        for ticker, pos in self.positions.items():
            if pos.shares != 0:
                current_p = self.stocks[ticker].price
                unrealized += pos.unrealized_pnl(current_p)
        return unrealized

    @property
    def total_pnl(self) -> float:
        return self.total_equity - self.initial_cash

    @property
    def total_pnl_pct(self) -> float:
        return (self.total_pnl / self.initial_cash) * 100.0

    def step(self) -> Optional[NewsItem]:
        """Perform one market tick across all stocks."""
        if self.is_paused:
            return None

        # Macro trend fluctuation
        self.macro_trend += random.gauss(0, 0.003)
        self.macro_trend *= 0.96

        # News event check
        diff_cfg = self.DIFFICULTIES.get(self.current_difficulty, self.DIFFICULTIES["Day Trader (3x)"])
        self.ticks_since_news += 1

        triggered_news: Optional[NewsItem] = None
        # Guarantee minimum 10 ticks between news so it's not a complete spam
        if self.ticks_since_news >= 15 and random.random() < diff_cfg["news_prob"]:
            triggered_news = self.news_gen.generate_random_news(list(self.stocks.values()))
            self.news_feed.insert(0, triggered_news)
            if len(self.news_feed) > 50:
                self.news_feed.pop()
            self.latest_news = triggered_news
            self.ticks_since_news = 0

            # Apply news impact
            if triggered_news.ticker == "MARKET":
                for st in self.stocks.values():
                    mult = 1.0 + (triggered_news.shock_pct * random.uniform(0.6, 1.2))
                    st.apply_shock(mult, triggered_news.momentum_drift * 0.5)
            elif triggered_news.ticker in self.stocks:
                st = self.stocks[triggered_news.ticker]
                mult = 1.0 + triggered_news.shock_pct
                st.apply_shock(mult, triggered_news.momentum_drift)

        # Advance each stock
        for stock in self.stocks.values():
            stock.step(self.macro_trend)

        return triggered_news

    # --- ORDER EXECUTION ---

    def buy(self, ticker: str, shares: int) -> bool:
        """Buy shares (enter or add to Long position, or cover Short)."""
        if shares <= 0 or ticker not in self.stocks:
            return False
        stock = self.stocks[ticker]
        pos = self.positions[ticker]
        price = stock.price
        cost = shares * price

        if pos.shares < 0:
            # We are shorting, so buying here is covering!
            return self.cover(ticker, shares)

        if self.cash < cost:
            return False

        self.cash -= cost
        new_shares = pos.shares + shares
        pos.avg_price = ((pos.shares * pos.avg_price) + cost) / new_shares
        pos.shares = new_shares

        time_str = time.strftime("%H:%M:%S")
        self.trades.insert(0, TradeLog(time_str, ticker, "BUY", shares, price))
        if len(self.trades) > 100:
            self.trades.pop()
        return True

    def sell(self, ticker: str, shares: int) -> bool:
        """Sell shares to close or reduce Long position."""
        if shares <= 0 or ticker not in self.stocks:
            return False
        pos = self.positions[ticker]
        if pos.shares <= 0:
            return False

        stock = self.stocks[ticker]
        price = stock.price
        shares_to_sell = min(shares, pos.shares)
        proceeds = shares_to_sell * price
        cost_basis = shares_to_sell * pos.avg_price
        pnl = proceeds - cost_basis

        self.cash += proceeds
        self.realized_pnl += pnl
        pos.shares -= shares_to_sell
        if pos.shares == 0:
            pos.avg_price = 0.0

        time_str = time.strftime("%H:%M:%S")
        self.trades.insert(0, TradeLog(time_str, ticker, "SELL", shares_to_sell, price, pnl))
        if len(self.trades) > 100:
            self.trades.pop()
        return True

    def short(self, ticker: str, shares: int) -> bool:
        """Short sell shares (borrow and sell at current price)."""
        if shares <= 0 or ticker not in self.stocks:
            return False
        pos = self.positions[ticker]
        stock = self.stocks[ticker]
        price = stock.price
        proceeds = shares * price

        # If already long, close long first or reject
        if pos.shares > 0:
            return False

        # Margin check: require at least 50% margin cash
        required_margin = proceeds * 0.5
        if self.cash < required_margin:
            return False

        # When shorting, cash increases by proceeds, but equity depends on liability
        self.cash += proceeds
        abs_shares = abs(pos.shares)
        new_shares = abs_shares + shares
        pos.avg_price = ((abs_shares * pos.avg_price) + proceeds) / new_shares
        pos.shares = -new_shares

        time_str = time.strftime("%H:%M:%S")
        self.trades.insert(0, TradeLog(time_str, ticker, "SHORT", shares, price))
        if len(self.trades) > 100:
            self.trades.pop()
        return True

    def cover(self, ticker: str, shares: int) -> bool:
        """Buy back shorted shares to close/reduce Short position."""
        if shares <= 0 or ticker not in self.stocks:
            return False
        pos = self.positions[ticker]
        if pos.shares >= 0:
            return False

        stock = self.stocks[ticker]
        price = stock.price
        abs_shares = abs(pos.shares)
        shares_to_cover = min(shares, abs_shares)
        cost = shares_to_cover * price

        # Short PnL = (avg_price - cover_price) * shares
        pnl = (pos.avg_price - price) * shares_to_cover

        if self.cash < cost:
            # Emergency liquidating if cash is short
            pass

        self.cash -= cost
        self.realized_pnl += pnl
        pos.shares += shares_to_cover
        if pos.shares == 0:
            pos.avg_price = 0.0

        time_str = time.strftime("%H:%M:%S")
        self.trades.insert(0, TradeLog(time_str, ticker, "COVER", shares_to_cover, price, pnl))
        if len(self.trades) > 100:
            self.trades.pop()
        return True

    def close_position(self, ticker: str) -> bool:
        """Quickly flatten position in ticker."""
        pos = self.positions.get(ticker)
        if not pos or pos.shares == 0:
            return False
        if pos.shares > 0:
            return self.sell(ticker, pos.shares)
        else:
            return self.cover(ticker, abs(pos.shares))

    def reset_account(self):
        """Reset game state."""
        self.cash = self.initial_cash
        self.realized_pnl = 0.0
        self.trades.clear()
        for ticker in self.stocks:
            self.positions[ticker] = Position(ticker)
            # Re-seed stock
            st = self.stocks[ticker]
            st.price = st.initial_price
            st.drift = 0.0
            st.volatility = st.base_volatility
            st.candles.clear()
            st._seed_history(50)
