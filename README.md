# ⚡ Day Trading Simulator

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter%2060%20FPS-00E676?style=for-the-badge)](https://docs.python.org/3/library/tkinter.html)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero%20External-FF9800?style=for-the-badge)](requirements.txt)
[![Stocks](https://img.shields.io/badge/Universe-100%20Volatile%20Stocks-2962FF?style=for-the-badge)](#-100-volatile-stocks-across-10-sectors)
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](LICENSE)

**An adrenaline-fueled, hyper-realistic intraday stock trading simulator.**  
Experience the chaos of Wall Street with **100 ultra-volatile stocks**, breaking news catalysts, high-performance candlestick charts, smart execution hotkeys, and 4 difficulty speed modes.

[Features](#-key-features) • [Stock Universe](#-100-volatile-stocks-across-10-sectors) • [Hotkeys](#-universal-keyboard-hotkeys) • [Quick Start](#-quick-start)

</div>

---

## 🎯 What is Day Trading Simulator?

**Day Trading Simulator** is a standalone Python application that drops you right into the trader's seat with **$25,000 in trading capital**. 

Prices move continuously using stochastic jump-diffusion and momentum dynamics. Breaking news flashes across the terminal, sending stocks rocketing +40% or plunging -45% in seconds. Execute Longs, Shorts, Covers, and Scalps with lightning-fast universal hotkeys, professional dual-mode MAX order sizing, and real-time P&L tracking.

---

## ⚡ Key Features

- **📊 High-Performance Candlestick & Volume Charts**:
  - Pure Tkinter Canvas rendering at 60+ FPS with zero lag.
  - Live candle formation: watch wicks expand, body colors pulse, and volume accumulate in real-time.
  - 15-period Moving Average (SMA) trendline.
  - Sub-millisecond crosshair cursor with floating OHLCV metrics HUD.
  - Dotted current price indicator with dynamic right-axis pill badge.

- **🔥 Dynamic Breaking News Engine**:
  - Over 50+ sector-specific headlines and market catalysts.
  - Instant price shocks (-48% to +45%) and lingering momentum drift.
  - Flashing breaking news alert banner and live color-coded ticker feed (`BULLISH`, `BEARISH`, `RUMOR`).

- **🔍 Pro Market Scanner & Watchlist**:
  - Live monitoring of all **100 stocks**.
  - **Instant Search**: Type any ticker or company name to filter the market in real-time.
  - **Dynamic Sorting**: Rank by **▲ Gainers** (top % spikes), **▼ Losers** (dip buys/shorts), or **A-Z**.
  - **Sector Quick-Filters**: Instant tabs for `ALL`, `MEME`, `BIO`, `CRYPTO`, and `PENNY`.

- **🕹️ 4 Simulation Speed Difficulties**:
  - **1x Relaxed** (1 tick / sec) – Learn candlestick patterns and plan swing trades.
  - **3x Day Trader** (3 ticks / sec) – Fast-paced intraday day trading.
  - **8x High Frequency (HFT)** (8 ticks / sec) – Rapid scalping with high news frequency.
  - **20x TURBO INSANE** (20 ticks / sec) – Pure chaos for maximum adrenaline.

- **💼 Professional Order Execution & Sizing**:
  - **Buy / Long**, **Sell / Close**, **Short Sell**, **Cover Short**, and **Flatten Position**.
  - **`⚡ MAX CASH` (F12)**: Automatically calculates the maximum affordable shares (`cash // price`) with zero overshoot.
  - **`💼 ALL POS` (M)**: Instantly sizes order to 100% of your open position (`abs(shares)`) for one-click exits.
  - **Smart MAX**: Toggles between closing your entire position and max cash allocation.
  - Live Net Equity, Available Cash, Unrealized P&L, Realized P&L, and Total Return tracking.

---

## 📈 100 Volatile Stocks Across 10 Sectors

Explore a diverse market universe designed for high intraday action:

| Sector | Stocks | Sample Tickers |
|---|---|---|
| **AI & Tech** | 10 | `NVXP`, `AIPL`, `QLAB`, `DATX`, `CYBR`, `ROBO`, `CHIP`, `NEUR`, `SaaS`, `OPTC` |
| **Meme & Retail Squeezes** | 10 | `MOON`, `APES`, `STON`, `YOLO`, `DIAM`, `HODL`, `TEND`, `MEME`, `WEN`, `DOGE` |
| **Biotech & Oncology** | 10 | `BIOX`, `DRUG`, `GENE`, `CRSP`, `VACC`, `CURE`, `PHRM`, `CLIN`, `TMRX`, `HEAL` |
| **Crypto & Web3** | 10 | `CRPT`, `BCON`, `ETHX`, `BLOK`, `DEFI`, `COIN`, `HASH`, `SATX`, `LEDG`, `MINT` |
| **Clean Energy & EV** | 10 | `APEX`, `VOLT`, `SOLR`, `WIND`, `NEXU`, `BATT`, `HYDR`, `ATOM`, `LITH`, `ELEC` |
| **Defense & Aerospace** | 10 | `ROCK`, `ORBT`, `SPAC`, `AERO`, `LOCK`, `DRON`, `DEFN`, `STAR`, `MISL`, `SATL` |
| **Finance & Commodities** | 10 | `GOLD`, `SILV`, `BANK`, `PAYX`, `LOAN`, `COMM`, `PRME`, `CAPX`, `FINT`, `URAN` |
| **Consumer & Media** | 10 | `PLAY`, `VRXX`, `GAME`, `STRM`, `BEVG`, `FOOD`, `FASH`, `CHEF`, `CASN`, `TOYS` |
| **Logistics & Transport** | 10 | `SHIP`, `RAIL`, `FLYX`, `CARG`, `TANK`, `LOGX`, `PORT`, `TRUK`, `DELV`, `RAXX` |
| **Penny Wildcard Scalpers** | 10 | `PUMP`, `PENY`, `RISK`, `WILD`, `SPEC`, `ZERO`, `LEAP`, `BOOM`, `DUMP`, `LOTO` |

---

## ⌨️ Universal Keyboard Hotkeys

Hotkeys work **everywhere** — including while searching stocks or typing share quantities:

| Action | Primary Key | Universal Shortcut |
|---|---|---|
| **BUY / LONG** | `B` | `F1` or `Alt+B` / `Ctrl+B` |
| **SELL / CLOSE** | `S` | `F2` or `Alt+S` / `Ctrl+S` |
| **SHORT SELL** | `X` | `F3` or `Alt+X` / `Ctrl+X` |
| **COVER SHORT** | `C` | `F4` or `Alt+C` / `Ctrl+C` |
| **FLATTEN POSITION** | `Esc` | `F8` or `Alt+F` |
| **PAUSE / RESUME** | `Space` | `F9` or `Pause` / `Alt+Space` |
| **MAX CASH SHARES** | `F12` | `Alt+M` |
| **ALL POSITION SHARES** | `M` | `Shift+M` |
| **NAVIGATE STOCKS** | `↑` / `↓` | Arrow keys (works inside search box too) |
| **CONFIRM / DEFOCUS** | `Enter` | Selects top search match and restores focus |

---

## 🚀 Quick Start

### 1. Requirements
- Python 3.9 or higher
- **Zero external dependencies!** Standard Python library only (`tkinter`, `random`, `math`, `time`, `collections`).

### 2. Launch
Clone the repository and run:

```bash
python main.py
```

---

## 🧪 Testing

Run the automated test suites:

```bash
# Unit tests for stock engine, orders, and portfolio math
python test_sim.py

# Headless GUI and event verification
python verify_gui.py

# Hotkeys and smart MAX validation
python verify_hotkeys_and_max.py
```

---

## 📄 License

This project is licensed under the MIT License.
