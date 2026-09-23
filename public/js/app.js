/**
 * Main Web Application Controller for Day Trading Simulator.
 * Integrates simulation engine, canvas chart, Firebase PvP matchmaking, and reactive UI.
 */

// --- Web Audio Sound Synthesizer ---
class SoundFx {
    constructor() {
        this.ctx = null;
    }

    _init() {
        if (!this.ctx) {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (AudioCtx) this.ctx = new AudioCtx();
        }
    }

    playBuy() {
        try {
            this._init();
            if (!this.ctx) return;
            const now = this.ctx.currentTime;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = "sine";
            osc.frequency.setValueAtTime(587.33, now); // D5
            osc.frequency.exponentialRampToValueAtTime(880.00, now + 0.12); // A5
            gain.gain.setValueAtTime(0.12, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.start(now);
            osc.stop(now + 0.16);
        } catch (e) {}
    }

    playSell() {
        try {
            this._init();
            if (!this.ctx) return;
            const now = this.ctx.currentTime;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = "triangle";
            osc.frequency.setValueAtTime(880.00, now);
            osc.frequency.exponentialRampToValueAtTime(440.00, now + 0.14);
            gain.gain.setValueAtTime(0.12, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.start(now);
            osc.stop(now + 0.16);
        } catch (e) {}
    }

    playWin() {
        try {
            this._init();
            if (!this.ctx) return;
            const notes = [523.25, 659.25, 783.99, 1046.50]; // C, E, G, C
            notes.forEach((freq, i) => {
                const now = this.ctx.currentTime + (i * 0.12);
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();
                osc.type = "sine";
                osc.frequency.setValueAtTime(freq, now);
                gain.gain.setValueAtTime(0.15, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
                osc.connect(gain);
                gain.connect(this.ctx.destination);
                osc.start(now);
                osc.stop(now + 0.26);
            });
        } catch (e) {}
    }
}

// --- App State & Controller ---
class TradingApp {
    constructor() {
        this.sfx = new SoundFx();
        this.fb = new FirebaseMatchmaker();

        this.nickname = localStorage.getItem("trader_nickname") || `Trader_${Math.floor(100 + Math.random() * 900)}`;
        this.mode = "solo"; // "solo" or "online"
        this.activeTicker = "NVXP";
        this.selectedQty = 50;
        this.activeSector = "All";
        this.searchQuery = "";

        // Match state
        this.matchData = null;
        this.matchTimeLeft = 180;
        this.matchTimerInterval = null;
        this.syncMetricsInterval = null;
        this.searchAbortCtrl = null;

        // Init engine
        this.engine = new MarketEngine(25000.0);
        this.chart = null;
        this.loopTimer = null;

        this._bindDom();
        this._initChart();
        this._bindEvents();
        this._renderScanner();
        this._selectTicker("NVXP");

        // Start solo loop initially
        this._scheduleNextTick();

        // Prompt mode select on first arrival
        this.showModeModal();
    }

    _bindDom() {
        // Headers & HUD
        this.elTopHeader = document.getElementById("top-header");
        this.elBattleHud = document.getElementById("battle-hud");

        // Metrics in Header
        this.elBalance = document.getElementById("hdr-balance");
        this.elBuyingPower = document.getElementById("hdr-bp");
        this.elUnrealized = document.getElementById("hdr-unrealized");
        this.elRealized = document.getElementById("hdr-realized");
        this.elTotalPnl = document.getElementById("hdr-total-pnl");
        this.elSpeedSelect = document.getElementById("speed-select");
        this.elBtnPause = document.getElementById("btn-pause");

        // Battle HUD
        this.elHudMyName = document.getElementById("hud-my-name");
        this.elHudMyScore = document.getElementById("hud-my-score");
        this.elHudLeaderBadge = document.getElementById("hud-leader-badge");
        this.elHudTimer = document.getElementById("hud-timer");
        this.elHudOppName = document.getElementById("hud-opp-name");
        this.elHudOppScore = document.getElementById("hud-opp-score");

        // Scanner
        this.elSearchInput = document.getElementById("scanner-search");
        this.elSectorScroll = document.getElementById("sector-scroll");
        this.elStockList = document.getElementById("stock-list");

        // Chart Header
        this.elActiveTicker = document.getElementById("chart-active-ticker");
        this.elActiveName = document.getElementById("chart-active-name");
        this.elActiveSector = document.getElementById("chart-active-sector");
        this.elActivePrice = document.getElementById("chart-active-price");
        this.elActiveChg = document.getElementById("chart-active-chg");

        // Execution Desk
        this.elDeskPrice = document.getElementById("desk-price");
        this.elQtyInput = document.getElementById("qty-input");
        this.elEstCost = document.getElementById("order-est-cost");
        this.elPosShares = document.getElementById("pos-shares");
        this.elPosAvg = document.getElementById("pos-avg");
        this.elPosVal = document.getElementById("pos-val");
        this.elPosPnl = document.getElementById("pos-pnl");

        // Bottom Tabs
        this.elTablePositions = document.getElementById("table-positions-body");
        this.elTableTrades = document.getElementById("table-trades-body");
        this.elNewsList = document.getElementById("news-feed-list");

        // Modals
        this.elModalMode = document.getElementById("modal-mode");
        this.elNicknameInput = document.getElementById("nickname-input");
        this.elModalMatchmaking = document.getElementById("modal-matchmaking");
        this.elMatchStatusTxt = document.getElementById("match-status-txt");
        this.elModalMatchEnd = document.getElementById("modal-match-end");
        this.elEndOutcome = document.getElementById("end-outcome");
        this.elEndDetails = document.getElementById("end-details");
    }

    _initChart() {
        this.chart = new CandlestickChart("chart-canvas");
    }

    _bindEvents() {
        // Nickname
        this.elNicknameInput.value = this.nickname;
        this.elNicknameInput.addEventListener("change", (e) => {
            this.nickname = e.target.value.trim() || `Trader_${Math.floor(100 + Math.random() * 900)}`;
            localStorage.setItem("trader_nickname", this.nickname);
        });

        // Search & Sector filter
        this.elSearchInput.addEventListener("input", (e) => {
            this.searchQuery = e.target.value.toUpperCase();
            this._renderScanner();
        });

        // Speed select
        this.elSpeedSelect.addEventListener("change", (e) => {
            this.engine.currentDifficulty = e.target.value;
        });

        // Pause
        this.elBtnPause.addEventListener("click", () => {
            this.engine.isPaused = !this.engine.isPaused;
            this.elBtnPause.textContent = this.engine.isPaused ? "▶ Resume" : "⏸ Pause";
        });

        // Reset
        document.getElementById("btn-reset").addEventListener("click", () => {
            if (confirm("Reset account equity to $25,000.00 and wipe current positions?")) {
                this.engine.resetAccount();
                this._updateAllUi();
            }
        });

        // Switch to Duel from Solo header
        document.getElementById("btn-switch-duel").addEventListener("click", () => {
            this.showModeModal();
        });

        // Quantity presets
        document.querySelectorAll(".btn-qty").forEach(btn => {
            btn.addEventListener("click", () => {
                document.querySelectorAll(".btn-qty").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                const val = btn.getAttribute("data-qty");
                if (val === "MAX") {
                    const price = this.engine.stocks[this.activeTicker].price;
                    const maxShares = Math.floor(this.engine.cash / price);
                    this.selectedQty = Math.max(1, maxShares);
                } else {
                    this.selectedQty = parseInt(val, 10);
                }
                this.elQtyInput.value = this.selectedQty;
                this._updateDeskEstimate();
            });
        });

        // Quantity steppers
        document.getElementById("btn-qty-minus").addEventListener("click", () => {
            this.selectedQty = Math.max(1, this.selectedQty - 10);
            this.elQtyInput.value = this.selectedQty;
            this._updateDeskEstimate();
        });
        document.getElementById("btn-qty-plus").addEventListener("click", () => {
            this.selectedQty = this.selectedQty + 10;
            this.elQtyInput.value = this.selectedQty;
            this._updateDeskEstimate();
        });
        this.elQtyInput.addEventListener("input", (e) => {
            const v = parseInt(e.target.value, 10);
            this.selectedQty = isNaN(v) || v <= 0 ? 1 : v;
            this._updateDeskEstimate();
        });

        // Trade execution buttons
        document.getElementById("btn-buy").addEventListener("click", () => this._executeOrder("BUY"));
        document.getElementById("btn-sell").addEventListener("click", () => this._executeOrder("SELL"));
        document.getElementById("btn-short").addEventListener("click", () => this._executeOrder("SHORT"));
        document.getElementById("btn-cover").addEventListener("click", () => this._executeOrder("COVER"));
        document.getElementById("btn-flatten").addEventListener("click", () => {
            this.engine.closePosition(this.activeTicker);
            this.sfx.playSell();
            this._updateAllUi();
        });

        // Bottom tab navigation
        document.querySelectorAll(".tab-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
                document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
                btn.classList.add("active");
                const target = btn.getAttribute("data-tab");
                document.getElementById(`tab-${target}`).classList.add("active");
            });
        });

        // Global hotkeys
        window.addEventListener("keydown", (e) => {
            if (e.target.tagName === "INPUT" || e.target.tagName === "SELECT") return;

            const key = e.key.toUpperCase();
            if (key === "B") this._executeOrder("BUY");
            else if (key === "S") this._executeOrder("SELL");
            else if (key === "H") this._executeOrder("SHORT");
            else if (key === "C") this._executeOrder("COVER");
            else if (key === " ") {
                e.preventDefault();
                this.engine.closePosition(this.activeTicker);
                this.sfx.playSell();
                this._updateAllUi();
            } else if (key === "1") this._setPresetQty(10);
            else if (key === "2") this._setPresetQty(50);
            else if (key === "3") this._setPresetQty(100);
            else if (key === "4") this._setPresetQty(500);
            else if (key === "5") this._setPresetQty("MAX");
        });

        // Battle HUD Actions
        document.getElementById("btn-next-opp").addEventListener("click", () => this._handleNextOpponent());
        document.getElementById("btn-leave-duel").addEventListener("click", () => this._leaveDuel());

        // Modal triggers
        document.getElementById("mode-solo").addEventListener("click", () => this._startSoloMode());
        document.getElementById("mode-online").addEventListener("click", () => this._startOnlineMatchmaking());
        document.getElementById("btn-cancel-match").addEventListener("click", () => {
            if (this.searchAbortCtrl) this.searchAbortCtrl.abort();
            this.elModalMatchmaking.style.display = "none";
            this.showModeModal();
        });

        // Match end buttons
        document.getElementById("btn-end-next").addEventListener("click", () => {
            this.elModalMatchEnd.style.display = "none";
            this._startOnlineMatchmaking();
        });
        document.getElementById("btn-end-menu").addEventListener("click", () => {
            this.elModalMatchEnd.style.display = "none";
            this._startSoloMode();
            this.showModeModal();
        });
    }

    _setPresetQty(val) {
        if (val === "MAX") {
            const price = this.engine.stocks[this.activeTicker].price;
            const maxShares = Math.floor(this.engine.cash / price);
            this.selectedQty = Math.max(1, maxShares);
        } else {
            this.selectedQty = val;
        }
        this.elQtyInput.value = this.selectedQty;
        this._updateDeskEstimate();
    }

    _renderScanner() {
        // 1. Sector pills
        this.elSectorScroll.innerHTML = "";
        for (const sec of SECTORS) {
            const pill = document.createElement("div");
            pill.className = `sector-pill ${this.activeSector === sec ? 'active' : ''}`;
            pill.textContent = sec;
            pill.addEventListener("click", () => {
                this.activeSector = sec;
                this._renderScanner();
            });
            this.elSectorScroll.appendChild(pill);
        }

        // 2. Stock items
        this.elStockList.innerHTML = "";
        const stocks = Object.values(this.engine.stocks);

        for (const st of stocks) {
            if (this.activeSector !== "All" && st.sector !== this.activeSector) continue;
            if (this.searchQuery && !st.ticker.includes(this.searchQuery) && !st.name.toUpperCase().includes(this.searchQuery)) continue;

            const row = document.createElement("div");
            row.className = `stock-row ${this.activeTicker === st.ticker ? 'active' : ''}`;
            row.id = `row-${st.ticker}`;

            const chgSign = st.change >= 0 ? "+" : "";
            const chgClass = st.change >= 0 ? "up" : "down";

            row.innerHTML = `
                <div class="stock-info">
                    <span class="sym">${st.ticker}</span>
                    <span class="sub">${st.name}</span>
                </div>
                <div class="stock-prices">
                    <span class="cur-p" id="price-${st.ticker}">$${st.price.toFixed(2)}</span>
                    <span class="pct ${chgClass}" id="pct-${st.ticker}">${chgSign}${st.changePct.toFixed(2)}%</span>
                </div>
            `;

            row.addEventListener("click", () => this._selectTicker(st.ticker));
            this.elStockList.appendChild(row);
        }
    }

    _selectTicker(ticker) {
        if (!this.engine.stocks[ticker]) return;
        this.activeTicker = ticker;

        document.querySelectorAll(".stock-row").forEach(r => r.classList.remove("active"));
        const activeRow = document.getElementById(`row-${ticker}`);
        if (activeRow) activeRow.classList.add("active");

        const st = this.engine.stocks[ticker];
        this.elActiveTicker.textContent = st.ticker;
        this.elActiveName.textContent = st.name;
        this.elActiveSector.textContent = st.sector;

        this.chart.setData(st);
        this._updateDeskEstimate();
        this._updateDeskPosition();
    }

    _executeOrder(action) {
        let ok = false;
        if (action === "BUY") {
            ok = this.engine.buy(this.activeTicker, this.selectedQty);
            if (ok) this.sfx.playBuy();
        } else if (action === "SELL") {
            ok = this.engine.sell(this.activeTicker, this.selectedQty);
            if (ok) this.sfx.playSell();
        } else if (action === "SHORT") {
            ok = this.engine.short(this.activeTicker, this.selectedQty);
            if (ok) this.sfx.playSell();
        } else if (action === "COVER") {
            ok = this.engine.cover(this.activeTicker, this.selectedQty);
            if (ok) this.sfx.playBuy();
        }

        if (ok) {
            this._updateAllUi();
        } else {
            // Flash red on order reject
            this.elEstCost.style.color = "var(--red)";
            setTimeout(() => this.elEstCost.style.color = "var(--text-muted)", 300);
        }
    }

    _scheduleNextTick() {
        const diffCfg = MarketEngine.DIFFICULTIES[this.engine.currentDifficulty] || MarketEngine.DIFFICULTIES["Day Trader (3x)"];
        const tickMs = diffCfg.tickMs;

        this.loopTimer = setTimeout(() => {
            this._tick();
            this._scheduleNextTick();
        }, tickMs);
    }

    _tick() {
        const triggeredNews = this.engine.step();

        // Update active chart
        const activeStock = this.engine.stocks[this.activeTicker];
        if (activeStock) {
            this.chart.setData(activeStock);

            const chgSign = activeStock.change >= 0 ? "+" : "";
            const chgClass = activeStock.change >= 0 ? "up" : "down";

            this.elActivePrice.textContent = `$${activeStock.price.toFixed(2)}`;
            this.elActiveChg.className = `active-chg ${chgClass}`;
            this.elActiveChg.textContent = `${chgSign}$${activeStock.change.toFixed(2)} (${chgSign}${activeStock.changePct.toFixed(2)}%)`;

            this.elDeskPrice.textContent = `$${activeStock.price.toFixed(2)}`;
        }

        // Update row prices in scanner
        for (const st of Object.values(this.engine.stocks)) {
            const pEl = document.getElementById(`price-${st.ticker}`);
            const pctEl = document.getElementById(`pct-${st.ticker}`);
            if (pEl && pctEl) {
                pEl.textContent = `$${st.price.toFixed(2)}`;
                const sign = st.change >= 0 ? "+" : "";
                pctEl.className = `pct ${st.change >= 0 ? 'up' : 'down'}`;
                pctEl.textContent = `${sign}${st.changePct.toFixed(2)}%`;
            }
        }

        // If news triggered, update news tab
        if (triggeredNews) {
            this._renderNewsTab();
        }

        this._updateAllUi();
    }

    _updateAllUi() {
        // Header metrics
        this.elBalance.textContent = `$${this.engine.totalEquity.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        this.elBuyingPower.textContent = `$${this.engine.buyingPower.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

        const unrl = this.engine.totalUnrealizedPnL;
        const unrlSign = unrl >= 0 ? "+" : "";
        this.elUnrealized.textContent = `${unrlSign}$${unrl.toFixed(2)}`;
        this.elUnrealized.className = `value ${unrl >= 0 ? 'up' : 'down'}`;

        const rlz = this.engine.realizedPnL;
        const rlzSign = rlz >= 0 ? "+" : "";
        this.elRealized.textContent = `${rlzSign}$${rlz.toFixed(2)}`;
        this.elRealized.className = `value ${rlz >= 0 ? 'up' : 'down'}`;

        const pnl = this.engine.totalPnL;
        const pnlPct = this.engine.totalPnLPct;
        const pnlSign = pnl >= 0 ? "+" : "";
        this.elTotalPnl.textContent = `${pnlSign}$${pnl.toFixed(2)} (${pnlSign}${pnlPct.toFixed(2)}%)`;
        this.elTotalPnl.className = `value ${pnl >= 0 ? 'up' : 'down'}`;

        // Desk
        this._updateDeskEstimate();
        this._updateDeskPosition();

        // Tables
        this._renderPositionsTab();
        this._renderTradesTab();
    }

    _updateDeskEstimate() {
        const st = this.engine.stocks[this.activeTicker];
        if (!st) return;
        const est = this.selectedQty * st.price;
        this.elEstCost.textContent = `Est. Value: $${est.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }

    _updateDeskPosition() {
        const pos = this.engine.positions[this.activeTicker];
        const st = this.engine.stocks[this.activeTicker];
        if (!pos || !st) return;

        this.elPosShares.textContent = `${pos.shares} (${pos.side})`;
        this.elPosShares.className = `val ${pos.shares > 0 ? 'up' : pos.shares < 0 ? 'down' : ''}`;

        this.elPosAvg.textContent = pos.avgPrice > 0 ? `$${pos.avgPrice.toFixed(2)}` : "$0.00";
        this.elPosVal.textContent = `$${pos.currentValue(st.price).toFixed(2)}`;

        const uPnl = pos.unrealizedPnL(st.price);
        const uPct = pos.unrealizedPnLPct(st.price);
        const sign = uPnl >= 0 ? "+" : "";
        this.elPosPnl.textContent = `${sign}$${uPnl.toFixed(2)} (${sign}${uPct.toFixed(2)}%)`;
        this.elPosPnl.className = `val ${uPnl >= 0 ? 'up' : 'down'}`;
    }

    _renderPositionsTab() {
        let html = "";
        for (const [ticker, pos] of Object.entries(this.engine.positions)) {
            if (pos.shares === 0) continue;
            const st = this.engine.stocks[ticker];
            const uPnl = pos.unrealizedPnL(st.price);
            const uPct = pos.unrealizedPnLPct(st.price);
            const sign = uPnl >= 0 ? "+" : "";
            const cls = uPnl >= 0 ? "up" : "down";

            html += `
                <tr>
                    <td style="color:#fff;font-weight:700;">${ticker}</td>
                    <td>${st.sector}</td>
                    <td class="${pos.shares > 0 ? 'up' : 'down'}">${pos.side}</td>
                    <td>${pos.shares}</td>
                    <td>$${pos.avgPrice.toFixed(2)}</td>
                    <td>$${st.price.toFixed(2)}</td>
                    <td>$${pos.currentValue(st.price).toFixed(2)}</td>
                    <td class="${cls}">${sign}$${uPnl.toFixed(2)}</td>
                    <td class="${cls}">${sign}${uPct.toFixed(2)}%</td>
                    <td><button class="btn-ctrl" onclick="app.engine.closePosition('${ticker}'); app._updateAllUi();" style="padding:2px 8px;font-size:10px;">FLATTEN</button></td>
                </tr>
            `;
        }
        this.elTablePositions.innerHTML = html || `<tr><td colspan="10" style="text-align:center;color:var(--text-muted);padding:24px;">No open positions. Use Buy or Short to trade.</td></tr>`;
    }

    _renderTradesTab() {
        let html = "";
        for (const t of this.engine.trades) {
            const pnlStr = t.pnl !== null ? `${t.pnl >= 0 ? '+' : ''}$${t.pnl.toFixed(2)}` : "-";
            const pnlCls = t.pnl !== null ? (t.pnl >= 0 ? 'up' : 'down') : '';

            html += `
                <tr>
                    <td style="color:var(--text-muted);">${t.timeStr}</td>
                    <td style="color:#fff;font-weight:700;">${t.ticker}</td>
                    <td class="${t.action === 'BUY' || t.action === 'COVER' ? 'up' : 'down'}">${t.action}</td>
                    <td>${t.shares}</td>
                    <td>$${t.price.toFixed(2)}</td>
                    <td class="${pnlCls}">${pnlStr}</td>
                </tr>
            `;
        }
        this.elTableTrades.innerHTML = html || `<tr><td colspan="6" style="text-align:center;color:var(--text-muted);padding:24px;">No trades executed yet.</td></tr>`;
    }

    _renderNewsTab() {
        let html = "";
        for (const item of this.engine.newsFeed) {
            const badgeCls = item.importance.toLowerCase();
            const sentCls = item.sentiment === "BULLISH" ? "up" : item.sentiment === "BEARISH" ? "down" : "gold";

            html += `
                <div class="news-item">
                    <span class="news-time">${item.timeStr}</span>
                    <span class="news-badge ${badgeCls}">${item.importance}</span>
                    <span class="news-headline">${item.headline}</span>
                    <span class="${sentCls}" style="font-weight:700;font-size:11px;">${item.sentiment}</span>
                </div>
            `;
        }
        this.elNewsList.innerHTML = html;
    }

    // --- Mode Management ---
    showModeModal() {
        this.elModalMode.style.display = "flex";
    }

    _startSoloMode() {
        this.mode = "solo";
        this.elModalMode.style.display = "none";
        this.elTopHeader.style.display = "flex";
        this.elBattleHud.style.display = "none";

        if (this.matchTimerInterval) clearInterval(this.matchTimerInterval);
        if (this.syncMetricsInterval) clearInterval(this.syncMetricsInterval);
    }

    async _startOnlineMatchmaking() {
        this.elModalMode.style.display = "none";
        this.elModalMatchmaking.style.display = "flex";
        this.elMatchStatusTxt.textContent = "Connecting to Firebase PvP Matchmaker...";

        this.searchAbortCtrl = new AbortController();

        try {
            const matchData = await this.fb.findMatch(
                (status) => { this.elMatchStatusTxt.textContent = status; },
                this.searchAbortCtrl.signal
            );

            if (!matchData) return;

            this.elModalMatchmaking.style.display = "none";
            this._enterOnlineMatch(matchData);
        } catch (e) {
            console.error("Matchmaking error:", e);
            this.elMatchStatusTxt.textContent = "Error during matchmaking. Retrying...";
            setTimeout(() => this.showModeModal(), 1500);
        }
    }

    _enterOnlineMatch(matchData) {
        this.mode = "online";
        this.matchData = matchData;
        this.matchTimeLeft = matchData.durationSeconds || 180;

        // Reset account to initial $25,000 and seed engine
        this.engine.resetAccount(matchData.seed);
        this.engine.currentDifficulty = "Day Trader (3x)"; // 330ms

        // Switch headers
        this.elTopHeader.style.display = "none";
        this.elBattleHud.style.display = "flex";

        this.elHudMyName.textContent = `YOU (${this.nickname})`;
        this.elHudOppName.textContent = `OPPONENT (${matchData.opponent.name})`;

        this._updateHudDisplay(25000.0, 0.0, 0.0, matchData.opponent);

        // Timer interval
        if (this.matchTimerInterval) clearInterval(this.matchTimerInterval);
        this.matchTimerInterval = setInterval(() => {
            this.matchTimeLeft -= 1;
            const mins = Math.floor(Math.max(0, this.matchTimeLeft) / 60);
            const secs = Math.max(0, this.matchTimeLeft) % 60;
            this.elHudTimer.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;

            if (this.matchTimeLeft <= 0) {
                clearInterval(this.matchTimerInterval);
                this._finishMatch();
            }
        }, 1000);

        // Sync metrics interval (every 1.5s)
        if (this.syncMetricsInterval) clearInterval(this.syncMetricsInterval);
        this.syncMetricsInterval = setInterval(async () => {
            const eq = this.engine.totalEquity;
            const pnl = this.engine.totalPnL;
            const pnlPct = this.engine.totalPnLPct;

            const oppData = await this.fb.updatePlayerMetrics(eq, pnl, pnlPct);
            if (oppData) {
                this._updateHudDisplay(eq, pnl, pnlPct, oppData);

                if (oppData.status === "forfeited") {
                    clearInterval(this.syncMetricsInterval);
                    clearInterval(this.matchTimerInterval);
                    this._showMatchEndModal("VICTORY! Opponent Left the Match", eq, oppData.equity);
                }
            }
        }, 1500);

        this._updateAllUi();
    }

    _updateHudDisplay(myEq, myPnl, myPnlPct, opp) {
        const mySign = myPnl >= 0 ? "+" : "";
        this.elHudMyScore.textContent = `$${myEq.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} (${mySign}${myPnlPct.toFixed(2)}%)`;

        const oppEq = opp.equity || 25000.0;
        const oppPnl = opp.pnl || 0.0;
        const oppPnlPct = opp.pnl_pct || 0.0;
        const oppSign = oppPnl >= 0 ? "+" : "";
        this.elHudOppScore.textContent = `$${oppEq.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} (${oppSign}${oppPnlPct.toFixed(2)}%)`;

        // Leader badge
        const diff = Math.abs(myEq - oppEq);
        if (Math.abs(myEq - oppEq) < 5.0) {
            this.elHudLeaderBadge.textContent = "⚔️ 1v1 MATCH • TIED";
            this.elHudLeaderBadge.className = "hud-leader-badge gold";
        } else if (myEq > oppEq) {
            this.elHudLeaderBadge.textContent = `🔥 YOU LEAD BY $${diff.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            this.elHudLeaderBadge.className = "hud-leader-badge up";
        } else {
            this.elHudLeaderBadge.textContent = `⚠️ OPPONENT LEADS BY $${diff.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            this.elHudLeaderBadge.className = "hud-leader-badge down";
        }
    }

    _finishMatch() {
        if (this.syncMetricsInterval) clearInterval(this.syncMetricsInterval);
        const myEq = this.engine.totalEquity;
        const oppEq = this.matchData && this.matchData.opponent ? this.matchData.opponent.equity : 25000.0;

        let title = "MATCH COMPLETE: TIED!";
        if (myEq > oppEq) {
            title = "🏆 VICTORY! YOU CRUSHED YOUR OPPONENT!";
            this.sfx.playWin();
        } else if (myEq < oppEq) {
            title = "💀 DEFEAT! OPPONENT WON THIS ROUND!";
        }

        this._showMatchEndModal(title, myEq, oppEq);
    }

    _showMatchEndModal(title, myEq, oppEq) {
        this.elEndOutcome.textContent = title;
        this.elEndOutcome.className = `modal-title ${myEq > oppEq ? 'up' : myEq < oppEq ? 'down' : 'gold'}`;

        const myPnl = myEq - 25000.0;
        const oppPnl = oppEq - 25000.0;
        const mySign = myPnl >= 0 ? "+" : "";
        const oppSign = oppPnl >= 0 ? "+" : "";

        this.elEndDetails.innerHTML = `
            <div style="font-size:15px;margin-bottom:12px;color:var(--text-white);">
                <b>Your Final Balance:</b> $${myEq.toFixed(2)} (${mySign}$${myPnl.toFixed(2)})<br>
                <b>Opponent Final Balance:</b> $${oppEq.toFixed(2)} (${oppSign}$${oppPnl.toFixed(2)})
            </div>
            <p style="color:var(--text-muted);font-size:12px;">Click Next Opponent to jump directly into another live 1v1 showdown!</p>
        `;
        this.elModalMatchEnd.style.display = "flex";
    }

    async _handleNextOpponent() {
        await this.fb.forfeitOrLeave();
        if (this.matchTimerInterval) clearInterval(this.matchTimerInterval);
        if (this.syncMetricsInterval) clearInterval(this.syncMetricsInterval);
        this._startOnlineMatchmaking();
    }

    async _leaveDuel() {
        await this.fb.forfeitOrLeave();
        if (this.matchTimerInterval) clearInterval(this.matchTimerInterval);
        if (this.syncMetricsInterval) clearInterval(this.syncMetricsInterval);
        this._startSoloMode();
    }
}

// Global initialization
let app = null;
window.addEventListener("DOMContentLoaded", () => {
    app = new TradingApp();
});
