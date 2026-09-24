# ⚡ Day Trading Simulator

<div align="center">

[![Download Windows Installer](https://img.shields.io/badge/Installer-DayTradeSim--Setup--v1.6.0.exe-00E676?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/isaiah-sudo/tradeism/releases/latest/download/DayTradeSim-Setup-v1.6.0.exe)
[![Download Portable EXE](https://img.shields.io/badge/Portable-DayTradeSim.exe-00B0FF?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/isaiah-sudo/tradeism/releases/latest/download/DayTradeSim.exe)
[![GitHub Release](https://img.shields.io/github/v/release/isaiah-sudo/tradeism?style=for-the-badge&color=2962FF)](https://github.com/isaiah-sudo/tradeism/releases/latest)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero%20External-FF9800?style=for-the-badge)](requirements.txt)
[![Stocks](https://img.shields.io/badge/Universe-100%20Volatile%20Stocks-purple?style=for-the-badge)](#-100-volatile-stocks-across-10-sectors)
[![Multiplayer](https://img.shields.io/badge/Multiplayer-1v1%20Online%20Duel-ff007f?style=for-the-badge)](#-game-modes)
[![Shop & Perks](https://img.shields.io/badge/Shop-Win%20Animations%20%26%20Perks-ffd700?style=for-the-badge)](#-trader-shop--customizations)
[![License](https://img.shields.io/badge/License-MIT-gray?style=for-the-badge)](LICENSE)

**An adrenaline-fueled, hyper-realistic intraday stock trading simulator.**  
Experience the chaos of Wall Street with **100 ultra-volatile stocks**, breaking news catalysts, high-performance candlestick charts, smart execution hotkeys, 4 difficulty speed modes, **1v1 Omegle-style Online Duels**, and the brand new **Persistent Menu Vault & Trader Shop**!

[Download Installer](#-download--play-windows) • [Game Modes](#-game-modes) • [Trader Shop](#-trader-shop--customizations) • [Features](#-key-features) • [Stock Universe](#-100-volatile-stocks-across-10-sectors) • [Hotkeys](#-universal-keyboard-hotkeys) • [Source Run](#-running-from-source)

</div>

---

## 🎯 What is Day Trading Simulator?

**Day Trading Simulator** is a standalone Python application that drops you right into the trader's seat with **$25,000 in trading capital**. 

Prices move continuously using stochastic jump-diffusion and momentum dynamics. Breaking news flashes across the terminal, sending stocks rocketing +40% or plunging -45% in seconds. Execute Longs, Shorts, Covers, and Scalps with lightning-fast universal hotkeys, professional dual-mode MAX order sizing, and real-time P&L tracking.

---

## 🕹️ Game Modes

### 🎯 Solo Sandbox
Classic single-player trading terminal designed for mastery:
- **Adjustable Speeds**: Seamlessly switch between **1x Relaxed**, **3x Day Trader**, **8x HFT**, and **20x Turbo Insane**.
- **Pause & Resume**: Stop the market at any moment (`Space`) to analyze setups.
- **Unlimited Resets**: Reset your portfolio and market dynamics back to $25k at will.
- **100 Volatile Stocks**: Trade across 10 sectors with real-time candlestick charts and order executions.
- **Breaking News Engine**: Experience rapid catalyst price jumps and drops.

### ⚔️ 1v1 Online Duel (Omegle-Style Matchmaking)
High-octane competitive head-to-head trading battles:
- **Quick Pairing**: Enter your nickname (or keep your auto-generated handle) and click **Find 1v1 Opponent (Pair Now)**.
- **Live Real-Time Battle HUD**: The top HUD tracks your net equity vs your opponent's net equity in real time, featuring an active indicator displaying who is in the lead (`YOU LEAD` / `OPPONENT LEADS`).
- **Synchronized Match Seed**: Both traders trade against the exact same market movements, candlestick charts, and breaking news catalysts simultaneously.
- **3-Minute High-Stakes Blitz**: Out-trade, out-scale, and out-earn your rival before the 180-second duel clock expires!
- **⏭️ Next Opponent Instant Re-Pair**: Skip or forfeit at any time with the Next button to immediately pair with a fresh trader.

---

## 🛒 Trader Shop & Customizations (Upgraded in v1.7)

Lock in your hard-earned trading profits and build a persistent empire:
- **💰 Real-Time Profit Banking**: Whenever your net equity exceeds your starting $25,000 capital, the header's **💰 Bank Profit** button lights up green. One click takes your profit, saves it to your persistent **Menu Vault**, triggers your equipped high-octane 60 FPS celebration animation with vault stats, and transitions back to the menu!
- **💾 Local Machine Persistence**: All banked savings, unlocked items, and equipped cosmetic presets are persisted locally (`~/.daytradesim/user_profile.json` on Desktop, `localStorage` on Web).
- **🎆 Ultra-Smooth 60 FPS Win Animations (v1.7 Overhaul)**:
  - **💸 Money Rain & Gold Confetti** (Free default) — 3D fluttering banknotes with realistic polygon perspective flip physics, metallic tumbling foil confetti, and sparkling starbursts.
  - **🚀 To The Moon Rocket Blast** ($25,000) — Perspective warp-speed radial starfield, dynamic multi-tier thruster plumes (white core, plasma jet, smoke puffs & sparks), supersonic shockwaves, and lunar fireworks splashdown.
  - **⚡ Cyber Matrix Glitch Rain** ($75,000) — Dual-layer streaming digital code with brilliant white/mint leading head glow, authentic character scrambling/morphing, sweeping CRT scanlines, and cyber glitch slices.
  - **💎 Diamond Hands Supernova** ($200,000) — Gravitational singularity phase with inward-collapsing energy rings and motes, followed by a blinding cosmic supernova blast with 90+ faceted prismatic crystal shards.
  - **👑 Golden Bull Stampede** ($500,000) — Charging golden mechanical bull with motion-blur trailing echoes, twin piercing laser eyes, hoof ground shockwaves, and an avalanche of bouncing bullion and coins.
  - **🔊 Victory Fanfare Audio**: Asynchronous non-blocking victory chimes, fanfare chords, and cash register sounds synthesizer.
- **🎨 Custom UI Themes, SFX & Titles**: Unlock the **Cyberpunk Neon Theme** ($50,000), **Golden Bull VIP Theme** ($150,000), **DJ Airhorn SFX** ($15,000), and the prestigious **Wall Street Whale Title** ($100,000).

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

## 🎮 Download & Play (Windows)

Anyone on Windows can download and play immediately—**no Python installation or setup required!**

### Option 1: Official Windows Installer (Recommended)
👉 [**Download DayTradeSim-Setup-v1.6.0.exe**](https://github.com/isaiah-sudo/tradeism/releases/latest/download/DayTradeSim-Setup-v1.6.0.exe)
- 🚀 Official setup wizard
- 🖥️ Creates a **Desktop shortcut** with custom trading icon
- 📌 Adds a **Start Menu shortcut** for instant access
- ⚙️ Clean install & clean uninstaller in Windows *Settings > Apps*
- 🛡️ Installs safely per-user (no admin / UAC prompt required!)

### Option 2: Portable Standalone Executable
👉 [**Download DayTradeSim.exe**](https://github.com/isaiah-sudo/daytradesim/releases/latest/download/DayTradeSim.exe)
- 📁 Single 16 MB standalone file
- ⚡ Run directly from your Downloads folder or USB drive—zero installation required!

---

## 🐍 Running from Source

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
