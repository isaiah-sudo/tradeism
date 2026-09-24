/**
 * Core Trading Simulation Engine.
 * JavaScript port identical in mechanics and math to the Python desktop engine.
 */

// --- Deterministic Pseudo-Random Number Generator ---
class SeededRandom {
    constructor(seed = null) {
        this.seed = seed;
        this.s = seed !== null ? (seed >>> 0) : Math.floor(Math.random() * 0xFFFFFFFF);
    }

    setSeed(seed) {
        this.seed = seed;
        this.s = seed !== null ? (seed >>> 0) : Math.floor(Math.random() * 0xFFFFFFFF);
    }

    // Mulberry32 32-bit generator
    random() {
        let t = (this.s += 0x6D2B79F5);
        t = Math.imul(t ^ (t >>> 15), t | 1);
        t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    }

    // Box-Muller transform for Gaussian distribution
    gauss(mean = 0, stdDev = 1) {
        let u1 = this.random();
        let u2 = this.random();
        while (u1 <= 1e-15) u1 = this.random(); // avoid log(0)
        const z0 = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
        return mean + z0 * stdDev;
    }

    uniform(min, max) {
        return min + (max - min) * this.random();
    }

    choice(arr) {
        if (!arr || arr.length === 0) return null;
        return arr[Math.floor(this.random() * arr.length)];
    }
}

// --- Candlestick Model ---
class Candle {
    constructor(timestamp, open, high, low, close, volume) {
        this.timestamp = timestamp;
        this.open = Number(open.toFixed(2));
        this.high = Number(high.toFixed(2));
        this.low = Number(low.toFixed(2));
        this.close = Number(close.toFixed(2));
        this.volume = Math.round(volume);
    }
}

// --- Stock Model ---
class Stock {
    constructor(ticker, name, sector, initialPrice, volatility, prng, tickPerCandle = 5) {
        this.ticker = ticker;
        this.name = name;
        this.sector = sector;
        this.initialPrice = initialPrice;
        this.prevClose = initialPrice;
        this.price = initialPrice;
        this.baseVolatility = volatility;
        this.volatility = volatility;
        this.drift = 0.0;
        this.driftDecay = 0.92;
        this.tickPerCandle = tickPerCandle;
        this.prng = prng || new SeededRandom();

        this.maxCandles = 80;
        this.candles = [];
        this.currentTickCount = 0;
        this.currentCandle = null;
        this.tradeMarkers = [];

        this._seedHistory(50);
    }

    addTradeMarker(action, shares, price, timeStr) {
        const ts = this.currentCandle ? this.currentCandle.timestamp : (this.candles.length ? this.candles[this.candles.length - 1].timestamp : Date.now() / 1000);
        const marker = {
            candleTimestamp: ts,
            action: action,
            shares: shares,
            price: Number(price.toFixed(2)),
            timeStr: timeStr
        };
        this.tradeMarkers.push(marker);
        if (this.tradeMarkers.length > 100) this.tradeMarkers.shift();
        return marker;
    }

    _seedHistory(numCandles) {
        let price = this.initialPrice * this.prng.uniform(0.85, 1.15);
        const now = (Date.now() / 1000) - (numCandles * 5);

        for (let i = 0; i < numCandles; i++) {
            const openP = price;
            const ret = this.prng.gauss(0, this.baseVolatility * 2.5);
            const closeP = Math.max(0.5, openP * (1.0 + ret));
            const highP = Math.max(openP, closeP) * (1.0 + Math.abs(this.prng.gauss(0, this.baseVolatility * 1.5)));
            let lowP = Math.min(openP, closeP) * (1.0 - Math.abs(this.prng.gauss(0, this.baseVolatility * 1.5)));
            lowP = Math.max(0.2, lowP);
            const vol = Math.floor(this.prng.uniform(5000, 80000));

            this.candles.push(new Candle(
                now + (i * 5),
                openP,
                highP,
                lowP,
                closeP,
                vol
            ));
            price = closeP;
        }

        this.price = Number(price.toFixed(2));
        this.prevClose = this.candles[0].open;
        this._startNewCandle(Date.now() / 1000);
    }

    _startNewCandle(timestamp) {
        this.currentCandle = new Candle(
            timestamp,
            this.price,
            this.price,
            this.price,
            this.price,
            0
        );
        this.currentTickCount = 0;
    }

    applyShock(priceMultiplier, extraDrift, extraVolatility = 0.02) {
        this.price = Math.max(0.10, Number((this.price * priceMultiplier).toFixed(2)));
        this.drift += extraDrift;
        this.volatility = Math.min(0.08, this.volatility + extraVolatility);

        if (this.currentCandle) {
            this.currentCandle.high = Math.max(this.currentCandle.high, this.price);
            this.currentCandle.low = Math.min(this.currentCandle.low, this.price);
            this.currentCandle.close = this.price;
            this.currentCandle.volume += Math.floor(Math.abs(extraDrift) * 150000) + 10000;
        }
    }

    step(marketTrend = 0.0) {
        // Drift decay
        this.drift *= this.driftDecay;
        this.volatility += (this.baseVolatility - this.volatility) * 0.05;

        let microSpike = 0.0;
        if (this.prng.random() < 0.04) {
            microSpike = this.prng.choice([-1, 1]) * this.prng.uniform(0.01, 0.04);
        }

        const shock = this.prng.gauss(0, this.volatility) + this.drift + (marketTrend * 0.5) + microSpike;
        let delta = this.price * shock;

        // Hard bound per-tick moves to avoid explosive overflows
        const maxDelta = this.price * 0.15;
        delta = Math.max(-maxDelta, Math.min(maxDelta, delta));

        this.price = Math.max(0.05, Number((this.price + delta).toFixed(2)));

        // Update live forming candle
        if (this.currentCandle) {
            this.currentCandle.high = Math.max(this.currentCandle.high, this.price);
            this.currentCandle.low = Math.min(this.currentCandle.low, this.price);
            this.currentCandle.close = this.price;

            const baseVol = Math.floor(this.prng.uniform(500, 4500));
            const volDelta = Math.floor(Math.abs(delta / this.price) * 45000) + baseVol;
            this.currentCandle.volume += volDelta;
            this.currentTickCount += 1;

            if (this.currentTickCount >= this.tickPerCandle) {
                this.candles.push(this.currentCandle);
                if (this.candles.length > this.maxCandles) {
                    this.candles.shift();
                }
                this._startNewCandle(Date.now() / 1000);
            }
        }

        return this.price;
    }

    get change() {
        return Number((this.price - this.prevClose).toFixed(2));
    }

    get changePct() {
        if (this.prevClose === 0) return 0;
        return Number((((this.price - this.prevClose) / this.prevClose) * 100).toFixed(2));
    }
}

// --- Position Model ---
class Position {
    constructor(ticker) {
        this.ticker = ticker;
        this.shares = 0; // > 0 Long, < 0 Short, == 0 Flat
        this.avgPrice = 0.0;
        this.lockedMargin = 0.0;
    }

    get side() {
        if (this.shares > 0) return "LONG";
        if (this.shares < 0) return "SHORT";
        return "FLAT";
    }

    currentValue(currentPrice) {
        return Math.abs(this.shares) * currentPrice;
    }

    unrealizedPnL(currentPrice) {
        if (this.shares === 0) return 0.0;
        if (this.shares > 0) {
            return (currentPrice - this.avgPrice) * this.shares;
        } else {
            return (this.avgPrice - currentPrice) * Math.abs(this.shares);
        }
    }

    unrealizedPnLPct(currentPrice) {
        if (this.shares === 0 || this.avgPrice === 0) return 0.0;
        if (this.shares > 0) {
            return ((currentPrice - this.avgPrice) / this.avgPrice) * 100.0;
        } else {
            return ((this.avgPrice - currentPrice) / this.avgPrice) * 100.0;
        }
    }
}

// --- Trade Log Model ---
class TradeLog {
    constructor(timeStr, ticker, action, shares, price, pnl = null) {
        this.timeStr = timeStr;
        this.ticker = ticker;
        this.action = action; // BUY, SELL, SHORT, COVER
        this.shares = shares;
        this.price = Number(price.toFixed(2));
        this.pnl = pnl !== null ? Number(pnl.toFixed(2)) : null;
    }
}

// --- Market Engine ---
class MarketEngine {
    static DIFFICULTIES = {
        "Relaxed (1x)": { tickMs: 1000, newsProb: 0.03, label: "Casual Trader (1 tick/sec)" },
        "Day Trader (3x)": { tickMs: 330, newsProb: 0.05, label: "Active Day Trader (3 ticks/sec)" },
        "High Frequency (8x)": { tickMs: 125, newsProb: 0.08, label: "HFT Scalper (8 ticks/sec)" },
        "TURBO INSANE (20x)": { tickMs: 50, newsProb: 0.12, label: "Adrenaline Junkie (20 ticks/sec)" }
    };

    constructor(initialCash = 25000.0, seed = null) {
        this.seed = seed;
        this.prng = new SeededRandom(seed);
        this.initialCash = initialCash;
        this.cash = initialCash;
        this.realizedPnL = 0.0;
        this.positions = {};
        this.trades = [];

        this.newsGen = new NewsGenerator(() => this.prng.random());
        this.newsFeed = [];
        this.latestNews = null;
        this.ticksSinceNews = 0;

        this.macroTrend = 0.0;
        this.currentDifficulty = "Day Trader (3x)";
        this.isPaused = false;

        this.stocks = {};
        for (const item of STOCK_DEFINITIONS) {
            this.stocks[item.ticker] = new Stock(
                item.ticker,
                item.name,
                item.sector,
                item.price,
                item.volatility,
                this.prng
            );
            this.positions[item.ticker] = new Position(item.ticker);
        }

        // Welcome news
        const d = new Date();
        const timeStr = [
            String(d.getHours()).padStart(2, '0'),
            String(d.getMinutes()).padStart(2, '0'),
            String(d.getSeconds()).padStart(2, '0')
        ].join(':');

        const welcomeNews = {
            id: 0,
            timestamp: Date.now() / 1000,
            timeStr: timeStr,
            ticker: "MARKET",
            headline: "Wall Street bell rings! High volatility expected across tech, meme, and biotech sectors.",
            sentiment: "NEUTRAL",
            shockPct: 0.0,
            momentumDrift: 0.0,
            importance: "BREAKING"
        };
        this.newsFeed.push(welcomeNews);
        this.latestNews = welcomeNews;
    }

    get totalEquity() {
        return Number((this.initialCash + this.realizedPnL + this.totalUnrealizedPnL).toFixed(2));
    }

    get totalUnrealizedPnL() {
        let unrl = 0.0;
        for (const [ticker, pos] of Object.entries(this.positions)) {
            if (pos.shares !== 0) {
                const curPrice = this.stocks[ticker].price;
                unrl += pos.unrealizedPnL(curPrice);
            }
        }
        return Number(unrl.toFixed(2));
    }

    get totalPnL() {
        return Number((this.totalEquity - this.initialCash).toFixed(2));
    }

    get totalPnLPct() {
        return Number(((this.totalPnL / this.initialCash) * 100).toFixed(2));
    }

    get buyingPower() {
        // 4x intraday margin on cash
        return Number(Math.max(0, this.cash * 4).toFixed(2));
    }

    step() {
        if (this.isPaused) return null;

        // Macro trend drift
        this.macroTrend += this.prng.gauss(0, 0.003);
        this.macroTrend *= 0.96;

        const diffCfg = MarketEngine.DIFFICULTIES[this.currentDifficulty] || MarketEngine.DIFFICULTIES["Day Trader (3x)"];
        this.ticksSinceNews += 1;

        let triggeredNews = null;
        if (this.ticksSinceNews >= 15 && this.prng.random() < diffCfg.newsProb) {
            triggeredNews = this.newsGen.generateRandomNews(Object.values(this.stocks));
            this.newsFeed.unshift(triggeredNews);
            if (this.newsFeed.length > 50) this.newsFeed.pop();
            this.latestNews = triggeredNews;
            this.ticksSinceNews = 0;

            // Apply shock
            if (triggeredNews.ticker === "MARKET") {
                for (const st of Object.values(this.stocks)) {
                    const mult = 1.0 + (triggeredNews.shockPct * this.prng.uniform(0.6, 1.2));
                    st.applyShock(mult, triggeredNews.momentumDrift * 0.5);
                }
            } else if (this.stocks[triggeredNews.ticker]) {
                const st = this.stocks[triggeredNews.ticker];
                const mult = 1.0 + triggeredNews.shockPct;
                st.applyShock(mult, triggeredNews.momentumDrift);
            }
        }

        // Advance all stocks
        for (const st of Object.values(this.stocks)) {
            st.step(this.macroTrend);
        }

        return triggeredNews;
    }

    buy(ticker, shares) {
        if (shares <= 0 || !this.stocks[ticker]) return false;
        const pos = this.positions[ticker];
        const stock = this.stocks[ticker];
        const price = stock.price;

        if (pos.shares < 0) {
            const shortShs = Math.abs(pos.shares);
            if (shares <= shortShs) {
                return this.cover(ticker, shares);
            } else {
                if (!this.cover(ticker, shortShs)) return false;
                const remaining = shares - shortShs;
                return this.buy(ticker, remaining);
            }
        }

        const cost = shares * price;
        if (this.cash < cost) return false;

        this.cash -= cost;
        const newShares = pos.shares + shares;
        pos.avgPrice = ((pos.shares * pos.avgPrice) + cost) / newShares;
        pos.shares = newShares;

        const timeStr = new Date().toTimeString().split(' ')[0];
        this.trades.unshift(new TradeLog(timeStr, ticker, "BUY", shares, price));
        if (this.trades.length > 100) this.trades.pop();
        stock.addTradeMarker("BUY", shares, price, timeStr);
        return true;
    }

    sell(ticker, shares) {
        if (shares <= 0 || !this.stocks[ticker]) return false;
        const pos = this.positions[ticker];
        if (pos.shares <= 0) return false;

        const stock = this.stocks[ticker];
        const price = stock.price;
        const sharesToSell = Math.min(shares, pos.shares);
        const proceeds = sharesToSell * price;
        const costBasis = sharesToSell * pos.avgPrice;
        const pnl = proceeds - costBasis;

        this.cash += proceeds;
        this.realizedPnL += pnl;
        pos.shares -= sharesToSell;
        if (pos.shares === 0) pos.avgPrice = 0.0;

        const timeStr = new Date().toTimeString().split(' ')[0];
        this.trades.unshift(new TradeLog(timeStr, ticker, "SELL", sharesToSell, price, pnl));
        if (this.trades.length > 100) this.trades.pop();
        stock.addTradeMarker("SELL", sharesToSell, price, timeStr);
        return true;
    }

    short(ticker, shares) {
        if (shares <= 0 || !this.stocks[ticker]) return false;
        const pos = this.positions[ticker];
        const stock = this.stocks[ticker];
        const price = stock.price;

        if (pos.shares > 0) {
            const longShs = pos.shares;
            if (shares <= longShs) {
                return this.sell(ticker, shares);
            } else {
                if (!this.sell(ticker, longShs)) return false;
                const remaining = shares - longShs;
                return this.short(ticker, remaining);
            }
        }

        const proceeds = shares * price;
        // Margin requirement: 50% cash collateral
        const reqMargin = proceeds * 0.5;
        if (this.cash < reqMargin) return false;

        this.cash -= reqMargin;
        pos.lockedMargin += reqMargin;
        const absShares = Math.abs(pos.shares);
        const newShares = absShares + shares;
        pos.avgPrice = ((absShares * pos.avgPrice) + proceeds) / newShares;
        pos.shares = -newShares;

        const timeStr = new Date().toTimeString().split(' ')[0];
        this.trades.unshift(new TradeLog(timeStr, ticker, "SHORT", shares, price));
        if (this.trades.length > 100) this.trades.pop();
        stock.addTradeMarker("SHORT", shares, price, timeStr);
        return true;
    }

    cover(ticker, shares) {
        if (shares <= 0 || !this.stocks[ticker]) return false;
        const pos = this.positions[ticker];
        if (pos.shares >= 0) return false;

        const stock = this.stocks[ticker];
        const price = stock.price;
        const absShares = Math.abs(pos.shares);
        const sharesToCover = Math.min(shares, absShares);
        const pnl = (pos.avgPrice - price) * sharesToCover;

        const marginFrac = sharesToCover / absShares;
        const marginRelease = pos.lockedMargin * marginFrac;
        pos.lockedMargin = Math.max(0, pos.lockedMargin - marginRelease);

        this.cash += marginRelease + pnl;
        this.realizedPnL += pnl;
        pos.shares += sharesToCover;
        if (pos.shares === 0) {
            pos.avgPrice = 0.0;
            pos.lockedMargin = 0.0;
        }

        const timeStr = new Date().toTimeString().split(' ')[0];
        this.trades.unshift(new TradeLog(timeStr, ticker, "COVER", sharesToCover, price, pnl));
        if (this.trades.length > 100) this.trades.pop();
        stock.addTradeMarker("COVER", sharesToCover, price, timeStr);
        return true;
    }

    reversePosition(ticker) {
        const pos = this.positions[ticker];
        if (!pos || pos.shares === 0) return false;
        const shs = Math.abs(pos.shares);
        if (pos.shares > 0) {
            return this.short(ticker, 2 * shs);
        } else {
            return this.buy(ticker, 2 * shs);
        }
    }

    closePosition(ticker) {
        const pos = this.positions[ticker];
        if (!pos || pos.shares === 0) return false;
        if (pos.shares > 0) {
            return this.sell(ticker, pos.shares);
        } else {
            return this.cover(ticker, Math.abs(pos.shares));
        }
    }

    resetAccount(seed = null) {
        if (seed !== null) {
            this.seed = seed;
            this.prng.setSeed(seed);
        }
        this.cash = this.initialCash;
        this.realizedPnL = 0.0;
        this.trades = [];
        for (const ticker in this.stocks) {
            this.positions[ticker] = new Position(ticker);
            const st = this.stocks[ticker];
            st.price = st.initialPrice;
            st.drift = 0.0;
            st.volatility = st.baseVolatility;
            st.tradeMarkers = [];
            st.candles = [];
            st._seedHistory(50);
        }
    }
}
