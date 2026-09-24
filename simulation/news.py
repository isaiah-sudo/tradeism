import random
import time
from dataclasses import dataclass
from typing import List, Optional, Dict

@dataclass
class NewsItem:
    id: int
    timestamp: float
    time_str: str
    ticker: str
    headline: str
    sentiment: str       # 'BULLISH', 'BEARISH', 'NEUTRAL'
    shock_pct: float     # Direct instantaneous price impact (-0.35 to +0.40)
    momentum_drift: float# Persistent momentum drift added to stock (+0.02, -0.02)
    importance: str      # 'BREAKING', 'MAJOR', 'RUMOR'

class NewsGenerator:
    def __init__(self):
        self._next_id = 1

        # Sector-specific dynamic templates {name}, {ticker}
        self.sector_templates = {
            "AI & Tech": [
                {"headline": "{name} ({ticker}) reveals next-gen Quantum AI architecture crushing industry benchmarks!", "sentiment": "BULLISH", "shock": 0.14, "drift": 0.020, "importance": "BREAKING"},
                {"headline": "Whistleblower leaks internal memos claiming {name} ({ticker}) software capabilities are fabricated.", "sentiment": "BEARISH", "shock": -0.15, "drift": -0.022, "importance": "BREAKING"},
                {"headline": "Cloud hyper-scaler signs massive $10B exclusive infrastructure contract with {name} ({ticker})!", "sentiment": "BULLISH", "shock": 0.12, "drift": 0.016, "importance": "MAJOR"},
                {"headline": "Cybersecurity emergency: Critical zero-day vulnerability detected in {name} ({ticker}) core stack.", "sentiment": "BEARISH", "shock": -0.11, "drift": -0.015, "importance": "MAJOR"},
                {"headline": "Silicon Valley venture giant initiates aggressive accumulation of {name} ({ticker}) stock.", "sentiment": "BULLISH", "shock": 0.08, "drift": 0.010, "importance": "RUMOR"},
            ],
            "Meme & Retail": [
                {"headline": "r/WallStreetBets coordinates massive gamma squeeze on {ticker}! Short sellers scrambling!", "sentiment": "BULLISH", "shock": 0.18, "drift": 0.028, "importance": "BREAKING"},
                {"headline": "{name} ({ticker}) management announces 20-million share secondary offering directly into rally!", "sentiment": "BEARISH", "shock": -0.16, "drift": -0.022, "importance": "BREAKING"},
                {"headline": "Celebrity billionaire tweets cryptic rocket emoji pointing to {ticker}!", "sentiment": "BULLISH", "shock": 0.12, "drift": 0.018, "importance": "RUMOR"},
                {"headline": "Retail brokers throttle trading volume and leverage on {ticker} citing volatility.", "sentiment": "BEARISH", "shock": -0.10, "drift": -0.014, "importance": "MAJOR"},
                {"headline": "Viral social media movement pledges to 'never sell' {ticker} shares until astronomical targets!", "sentiment": "BULLISH", "shock": 0.10, "drift": 0.015, "importance": "RUMOR"},
            ],
            "Biotech": [
                {"headline": "FDA grants Breakthrough Therapy Designation for {name}'s ({ticker}) flagship clinical pipeline!", "sentiment": "BULLISH", "shock": 0.20, "drift": 0.030, "importance": "BREAKING"},
                {"headline": "Phase 3 clinical trial for {name} ({ticker}) suspended abruptly after patient complications!", "sentiment": "BEARISH", "shock": -0.22, "drift": -0.032, "importance": "BREAKING"},
                {"headline": "Global pharmaceutical giant approaches {name} ({ticker}) with unsolicited takeover proposal.", "sentiment": "BULLISH", "shock": 0.14, "drift": 0.020, "importance": "MAJOR"},
                {"headline": "Notorious short-seller fund releases devastating investigative exposé on {ticker} efficacy data.", "sentiment": "BEARISH", "shock": -0.12, "drift": -0.018, "importance": "RUMOR"},
                {"headline": "New England Journal of Medicine publishes peer-reviewed accolades for {ticker} therapeutic results.", "sentiment": "BULLISH", "shock": 0.11, "drift": 0.015, "importance": "MAJOR"},
            ],
            "Crypto & Web3": [
                {"headline": "Major banking consortium deploys settlement network on {name} ({ticker}) blockchain!", "sentiment": "BULLISH", "shock": 0.16, "drift": 0.022, "importance": "BREAKING"},
                {"headline": "Regulators issue emergency cease-and-desist against {name} ({ticker}) crypto protocol!", "sentiment": "BEARISH", "shock": -0.18, "drift": -0.025, "importance": "BREAKING"},
                {"headline": "Sovereign wealth fund confirms strategic digital asset allocation with {ticker}.", "sentiment": "BULLISH", "shock": 0.12, "drift": 0.018, "importance": "MAJOR"},
                {"headline": "Multi-million dollar bridge hack drains liquidity pools linked to {ticker}.", "sentiment": "BEARISH", "shock": -0.12, "drift": -0.018, "importance": "MAJOR"},
                {"headline": "Speculation mounts regarding imminent tier-1 exchange listing and derivatives for {ticker}.", "sentiment": "BULLISH", "shock": 0.09, "drift": 0.012, "importance": "RUMOR"},
            ],
            "Clean Energy": [
                {"headline": "{name} ({ticker}) awarded landmark multi-billion dollar clean federal energy grant!", "sentiment": "BULLISH", "shock": 0.15, "drift": 0.020, "importance": "BREAKING"},
                {"headline": "Key supply chain bottlenecks force {name} ({ticker}) to slash full-year production guidance in half!", "sentiment": "BEARISH", "shock": -0.14, "drift": -0.020, "importance": "BREAKING"},
                {"headline": "Breakthrough in energy efficiency patent puts {name} ({ticker}) years ahead of rivals.", "sentiment": "BULLISH", "shock": 0.12, "drift": 0.016, "importance": "MAJOR"},
                {"headline": "Tariff dispute threatens raw material supplies essential for {ticker} facilities.", "sentiment": "BEARISH", "shock": -0.10, "drift": -0.014, "importance": "MAJOR"},
            ],
            "Aerospace & Defense": [
                {"headline": "Pentagon awards {name} ({ticker}) classified next-gen defense contract!", "sentiment": "BULLISH", "shock": 0.15, "drift": 0.018, "importance": "BREAKING"},
                {"headline": "Rocket launch vehicle from {name} ({ticker}) suffers catastrophic pad anomaly during test.", "sentiment": "BEARISH", "shock": -0.15, "drift": -0.020, "importance": "BREAKING"},
                {"headline": "Allied nations place massive export orders for {ticker} autonomous defense systems.", "sentiment": "BULLISH", "shock": 0.11, "drift": 0.014, "importance": "MAJOR"},
                {"headline": "Congressional oversight committee probes cost overruns at {ticker} aerospace division.", "sentiment": "BEARISH", "shock": -0.08, "drift": -0.010, "importance": "RUMOR"},
            ],
            "Finance & Commodities": [
                {"headline": "Record gold & commodity price surges drive monster earnings for {name} ({ticker})!", "sentiment": "BULLISH", "shock": 0.13, "drift": 0.016, "importance": "BREAKING"},
                {"headline": "Severe regulatory audit reveals reserve shortfalls at {name} ({ticker})!", "sentiment": "BEARISH", "shock": -0.15, "drift": -0.022, "importance": "BREAKING"},
                {"headline": "Global central bank liquidity expansion triggers massive rally in {ticker}.", "sentiment": "BULLISH", "shock": 0.10, "drift": 0.013, "importance": "MAJOR"},
                {"headline": "Credit rating agency downgrades {name} ({ticker}) to junk status on debt concerns.", "sentiment": "BEARISH", "shock": -0.11, "drift": -0.015, "importance": "MAJOR"},
            ],
            "Consumer & Media": [
                {"headline": "{name}'s ({ticker}) new interactive release sets all-time viral engagement records!", "sentiment": "BULLISH", "shock": 0.13, "drift": 0.016, "importance": "BREAKING"},
                {"headline": "Mass consumer boycott erupts against {name} ({ticker}) following public relations debacle.", "sentiment": "BEARISH", "shock": -0.13, "drift": -0.018, "importance": "BREAKING"},
                {"headline": "Subscription numbers beat Wall Street estimates by 400% for {ticker}.", "sentiment": "BULLISH", "shock": 0.09, "drift": 0.013, "importance": "MAJOR"},
                {"headline": "Streaming piracy and copyright disputes cloud revenue outlook for {ticker}.", "sentiment": "BEARISH", "shock": -0.08, "drift": -0.010, "importance": "RUMOR"},
            ],
            "Logistics & Transport": [
                {"headline": "Freight rates skyrocket 250% following canal blockage; {name} ({ticker}) profits explode!", "sentiment": "BULLISH", "shock": 0.15, "drift": 0.018, "importance": "BREAKING"},
                {"headline": "Dockworkers strike shuts down all operations for {name} ({ticker}) indefinitely!", "sentiment": "BEARISH", "shock": -0.15, "drift": -0.020, "importance": "BREAKING"},
                {"headline": "Major e-commerce giant signs 5-year priority logistics agreement with {ticker}.", "sentiment": "BULLISH", "shock": 0.11, "drift": 0.014, "importance": "MAJOR"},
                {"headline": "Fuel surcharge spike eats deeply into {ticker} operating margins.", "sentiment": "BEARISH", "shock": -0.08, "drift": -0.012, "importance": "MAJOR"},
            ],
            "Penny Wildcard": [
                {"headline": "MICRO-CAP MANIA: Penny stock {name} ({ticker}) explodes +45% on astronomical buying volume!", "sentiment": "BULLISH", "shock": 0.22, "drift": 0.032, "importance": "BREAKING"},
                {"headline": "SEC halts trading on {ticker} pending investigation into unlawful pump-and-dump promotion!", "sentiment": "BEARISH", "shock": -0.24, "drift": -0.035, "importance": "BREAKING"},
                {"headline": "Subreddit trading army discovers low-float penny stock {ticker}! Rocket initiated!", "sentiment": "BULLISH", "shock": 0.18, "drift": 0.026, "importance": "RUMOR"},
                {"headline": "Dilution alert: {name} ({ticker}) files toxic convertible debt financing.", "sentiment": "BEARISH", "shock": -0.16, "drift": -0.022, "importance": "MAJOR"},
            ]
        }

        # Broad Market Macro News
        self.market_templates = [
            {"headline": "Federal Reserve unexpectedly slashes interest rates by 50 bps! Equity markets explode higher!", "sentiment": "BULLISH", "shock": 0.05, "drift": 0.012, "importance": "BREAKING"},
            {"headline": "Inflation print comes in blistering hot! Fed hints at emergency rate hikes; broad sell-off!", "sentiment": "BEARISH", "shock": -0.06, "drift": -0.014, "importance": "BREAKING"},
            {"headline": "Global geopolitical tension eases; international trade flows resume normalized pace.", "sentiment": "BULLISH", "shock": 0.04, "drift": 0.010, "importance": "MAJOR"},
            {"headline": "Sudden oil supply disruption triggers inflation fears across all financial sectors.", "sentiment": "BEARISH", "shock": -0.05, "drift": -0.011, "importance": "MAJOR"},
            {"headline": "Treasury yields tumble as central banks inject liquidity back into interbank lending.", "sentiment": "BULLISH", "shock": 0.05, "drift": 0.010, "importance": "MAJOR"},
        ]

    def generate_random_news(self, available_stocks: List[dict]) -> NewsItem:
        """
        available_stocks: List of dicts or objects with ticker, name, and sector.
        """
        # 15% chance of general market news, 85% chance of specific stock catalyst
        if random.random() < 0.15 or not available_stocks:
            template = random.choice(self.market_templates)
            ticker = "MARKET"
            headline = template["headline"]
            sentiment = template["sentiment"]
            base_shock = template["shock"]
            base_drift = template["drift"]
            importance = template["importance"]
        else:
            stock = random.choice(available_stocks)
            ticker = stock.ticker
            name = stock.name
            sector = stock.sector

            # Find matching sector templates or default to tech
            templates = self.sector_templates.get(sector, self.sector_templates["AI & Tech"])
            template = random.choice(templates)

            headline = template["headline"].format(name=name, ticker=ticker)
            sentiment = template["sentiment"]
            base_shock = template["shock"]
            base_drift = template["drift"]
            importance = template["importance"]

        # Random multiplier variance
        variance = random.uniform(0.90, 1.15)
        shock = round(base_shock * variance, 3)
        drift = round(base_drift * variance, 4)

        now = time.time()
        time_str = time.strftime("%H:%M:%S", time.localtime(now))

        item = NewsItem(
            id=self._next_id,
            timestamp=now,
            time_str=time_str,
            ticker=ticker,
            headline=headline,
            sentiment=sentiment,
            shock_pct=shock,
            momentum_drift=drift,
            importance=importance
        )
        self._next_id += 1
        return item
