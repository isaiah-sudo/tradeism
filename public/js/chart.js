/**
 * Professional HTML5 Canvas Candlestick Chart.
 * High-performance, Retina-crisp, interactive with crosshair and volume bars.
 */

// Polyfill for roundRect if not natively supported
if (!CanvasRenderingContext2D.prototype.roundRect) {
    CanvasRenderingContext2D.prototype.roundRect = function(x, y, w, h, radii) {
        let r = radii || 0;
        if (typeof r === 'number') r = [r, r, r, r];
        else if (Array.isArray(r) && r.length === 1) r = [r[0], r[0], r[0], r[0]];
        const [tl = 0, tr = 0, br = 0, bl = 0] = r;
        this.beginPath();
        this.moveTo(x + tl, y);
        this.lineTo(x + w - tr, y);
        this.quadraticCurveTo(x + w, y, x + w, y + tr);
        this.lineTo(x + w, y + h - br);
        this.quadraticCurveTo(x + w, y + h, x + w - br, y + h);
        this.lineTo(x + bl, y + h);
        this.quadraticCurveTo(x, y + h, x, y + h - bl);
        this.lineTo(x, y + tl);
        this.quadraticCurveTo(x, y, x + tl, y);
        this.closePath();
        return this;
    };
}

class CandlestickChart {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');

        this.mousePos = null;
        this.candles = [];
        this.currentPrice = 0;
        this.ticker = "";
        this.tradeMarkers = [];
        this.position = null;
        this.activeNotification = null;
        this.notificationTimer = null;

        this.colors = {
            bg: "#131722",
            grid: "#1e222d",
            text: "#848e9c",
            textActive: "#d1d4dc",
            up: "#089981",
            upWick: "#089981",
            down: "#f23645",
            downWick: "#f23645",
            crosshair: "#434651",
            priceLine: "#2962ff",
            volumeUp: "rgba(8, 153, 129, 0.25)",
            volumeDown: "rgba(242, 54, 69, 0.25)"
        };

        this._setupListeners();
        this.resize();
    }

    _setupListeners() {
        window.addEventListener('resize', () => this.resize());

        this.canvas.addEventListener('mousemove', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            this.mousePos = {
                x: e.clientX - rect.left,
                y: e.clientY - rect.top
            };
            this.render();
        });

        this.canvas.addEventListener('mouseleave', () => {
            this.mousePos = null;
            this.render();
        });
    }

    resize() {
        const rect = this.canvas.parentElement.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;

        this.width = rect.width;
        this.height = Math.max(300, rect.height);

        this.canvas.width = this.width * dpr;
        this.canvas.height = this.height * dpr;
        this.canvas.style.width = `${this.width}px`;
        this.canvas.style.height = `${this.height}px`;

        this.ctx.setTransform(1, 0, 0, 1, 0, 0);
        this.ctx.scale(dpr, dpr);

        this.render();
    }

    setData(stock) {
        if (!stock) return;
        this.ticker = stock.ticker;
        this.currentPrice = stock.price;
        this.tradeMarkers = stock.tradeMarkers || [];

        const list = [...stock.candles];
        if (stock.currentCandle) {
            list.push(stock.currentCandle);
        }
        this.candles = list;
        this.render();
    }

    setPosition(pos) {
        this.position = pos;
        this.render();
    }

    showTradeNotification(action, shares, price, ticker, pnl = null, duration = 3.5) {
        this.activeNotification = {
            action: (action || "BUY").toUpperCase(),
            shares,
            price,
            ticker: ticker || this.ticker,
            pnl,
            time: Date.now() / 1000,
            duration
        };
        this.render();

        if (this.notificationTimer) cancelAnimationFrame(this.notificationTimer);
        const start = Date.now();
        const anim = () => {
            const elapsed = (Date.now() - start) / 1000;
            if (elapsed < duration) {
                this.render();
                this.notificationTimer = requestAnimationFrame(anim);
            } else {
                this.activeNotification = null;
                this.render();
            }
        };
        this.notificationTimer = requestAnimationFrame(anim);
    }

    render() {
        const ctx = this.ctx;
        const w = this.width;
        const h = this.height;

        if (!w || !h) return;

        // Background
        ctx.fillStyle = this.colors.bg;
        ctx.fillRect(0, 0, w, h);

        if (this.candles.length === 0) return;

        const rightMargin = 68;
        const bottomMargin = 26;
        const chartW = w - rightMargin;
        const chartH = h - bottomMargin;
        const volumeH = chartH * 0.18;
        const priceChartH = chartH - volumeH;

        // Find min and max price
        let minP = Infinity;
        let maxP = -Infinity;
        let maxVol = 1;

        for (const c of this.candles) {
            if (c.low < minP) minP = c.low;
            if (c.high > maxP) maxP = c.high;
            if (c.volume > maxVol) maxVol = c.volume;
        }

        if (minP === Infinity || maxP === -Infinity) {
            minP = this.currentPrice * 0.95;
            maxP = this.currentPrice * 1.05;
        }

        // Add 8% vertical padding
        const pad = (maxP - minP) * 0.08 || 1.0;
        minP = Math.max(0.01, minP - pad);
        maxP = maxP + pad;

        const priceRange = maxP - minP;
        const getY = (price) => priceChartH - ((price - minP) / priceRange) * priceChartH;
        const getPrice = (y) => maxP - (y / priceChartH) * priceRange;

        // --- Grid lines & Price axis ---
        ctx.lineWidth = 1;
        ctx.strokeStyle = this.colors.grid;
        ctx.fillStyle = this.colors.text;
        ctx.font = "11px 'Segoe UI', sans-serif";
        ctx.textAlign = "left";
        ctx.textBaseline = "middle";

        const numGridLines = 6;
        const stepP = priceRange / numGridLines;
        for (let i = 0; i <= numGridLines; i++) {
            const p = minP + (i * stepP);
            const y = Math.round(getY(p));

            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(chartW, y);
            ctx.stroke();

            // Price label on right margin
            ctx.fillText(`$${p.toFixed(2)}`, chartW + 8, y);
        }

        // Volume separator line
        ctx.beginPath();
        ctx.moveTo(0, priceChartH);
        ctx.lineTo(chartW, priceChartH);
        ctx.stroke();

        // Right margin divider line
        ctx.beginPath();
        ctx.moveTo(chartW, 0);
        ctx.lineTo(chartW, h);
        ctx.stroke();

        // --- Render Candlesticks and Volume ---
        const n = this.candles.length;
        const candleSpacing = chartW / Math.max(n, 40);
        const candleWidth = Math.max(3, candleSpacing * 0.72);

        let hoveredCandle = null;
        let hoveredX = 0;
        const candleCenters = [];

        for (let i = 0; i < n; i++) {
            const c = this.candles[i];
            const x = Math.round(i * candleSpacing + (candleSpacing / 2));
            candleCenters.push(x);
            const isUp = c.close >= c.open;
            const candleColor = isUp ? this.colors.up : this.colors.down;

            // Check hover
            if (this.mousePos && Math.abs(this.mousePos.x - x) <= candleSpacing / 2 && this.mousePos.x < chartW) {
                hoveredCandle = c;
                hoveredX = x;
            }

            // Volume bar
            const volBarH = (c.volume / maxVol) * volumeH;
            const volY = chartH - volBarH;
            ctx.fillStyle = isUp ? this.colors.volumeUp : this.colors.volumeDown;
            ctx.fillRect(x - (candleWidth / 2), volY, candleWidth, volBarH);

            // Wick (High - Low)
            const yHigh = Math.round(getY(c.high));
            const yLow = Math.round(getY(c.low));
            ctx.strokeStyle = isUp ? this.colors.upWick : this.colors.downWick;
            ctx.beginPath();
            ctx.moveTo(x, yHigh);
            ctx.lineTo(x, yLow);
            ctx.stroke();

            // Body (Open - Close)
            const yOpen = Math.round(getY(c.open));
            const yClose = Math.round(getY(c.close));
            const bodyY = Math.min(yOpen, yClose);
            const bodyH = Math.max(2, Math.abs(yClose - yOpen));

            ctx.fillStyle = candleColor;
            ctx.fillRect(x - (candleWidth / 2), bodyY, candleWidth, bodyH);
        }

        // --- Render Trade Markers over Candles ---
        if (this.tradeMarkers && this.tradeMarkers.length > 0) {
            for (let i = 0; i < n; i++) {
                const c = this.candles[i];
                const cx = candleCenters[i];
                // Match markers for this candle
                const markers = this.tradeMarkers.filter(m => Math.abs(m.candleTimestamp - c.timestamp) < 0.001);
                if (!markers || markers.length === 0) continue;

                for (const m of markers) {
                    const act = (m.action || "").toUpperCase();
                    const shs = m.shares;
                    ctx.save();
                    if (act === "BUY" || act === "COVER") {
                        const col = act === "BUY" ? "#089981" : "#2962ff";
                        const yLow = Math.round(getY(c.low));
                        let baseY = yLow + 16;
                        baseY = Math.min(priceChartH - 12, Math.max(24, baseY));

                        // Upward pointer triangle
                        ctx.fillStyle = col;
                        ctx.beginPath();
                        ctx.moveTo(cx, yLow + 2);
                        ctx.lineTo(cx - 5, baseY - 2);
                        ctx.lineTo(cx + 5, baseY - 2);
                        ctx.closePath();
                        ctx.fill();

                        // Pill badge
                        const badgeTxt = act === "BUY" ? `+${shs}` : `COV ${shs}`;
                        ctx.font = "bold 9px 'Segoe UI', sans-serif";
                        const tw = ctx.measureText(badgeTxt).width;
                        const pw = Math.max(32, tw + 10);
                        const ph = 14;

                        ctx.fillStyle = col;
                        ctx.strokeStyle = "#ffffff";
                        ctx.lineWidth = 1;
                        ctx.beginPath();
                        ctx.roundRect(cx - pw / 2, baseY - 2, pw, ph, 3);
                        ctx.fill();
                        ctx.stroke();

                        ctx.fillStyle = "#ffffff";
                        ctx.textAlign = "center";
                        ctx.textBaseline = "middle";
                        ctx.fillText(badgeTxt, cx, baseY - 2 + ph / 2);
                    } else {
                        // SHORT or SELL
                        const col = act === "SHORT" ? "#f23645" : "#ff9800";
                        const yHigh = Math.round(getY(c.high));
                        let baseY = yHigh - 16;
                        baseY = Math.max(16, Math.min(priceChartH - 24, baseY));

                        // Downward pointer triangle
                        ctx.fillStyle = col;
                        ctx.beginPath();
                        ctx.moveTo(cx, yHigh - 2);
                        ctx.lineTo(cx - 5, baseY + 2);
                        ctx.lineTo(cx + 5, baseY + 2);
                        ctx.closePath();
                        ctx.fill();

                        // Pill badge
                        const badgeTxt = act === "SHORT" ? `-${shs}` : `SEL ${shs}`;
                        ctx.font = "bold 9px 'Segoe UI', sans-serif";
                        const tw = ctx.measureText(badgeTxt).width;
                        const pw = Math.max(32, tw + 10);
                        const ph = 14;

                        ctx.fillStyle = col;
                        ctx.strokeStyle = "#ffffff";
                        ctx.lineWidth = 1;
                        ctx.beginPath();
                        ctx.roundRect(cx - pw / 2, baseY - 14, pw, ph, 3);
                        ctx.fill();
                        ctx.stroke();

                        ctx.fillStyle = "#ffffff";
                        ctx.textAlign = "center";
                        ctx.textBaseline = "middle";
                        ctx.fillText(badgeTxt, cx, baseY - 14 + ph / 2);
                    }
                    ctx.restore();
                }
            }
        }

        // --- Active Position Entry Price Line ---
        if (this.position && this.position.shares !== 0 && this.position.avgPrice > 0) {
            const posY = Math.round(getY(this.position.avgPrice));
            if (posY >= 0 && posY <= priceChartH) {
                const isLong = this.position.shares > 0;
                const posCol = isLong ? "#00e676" : "#ff5252";

                ctx.save();
                ctx.setLineDash([4, 4]);
                ctx.strokeStyle = posCol;
                ctx.lineWidth = 1.5;
                ctx.beginPath();
                ctx.moveTo(0, posY);
                ctx.lineTo(chartW, posY);
                ctx.stroke();
                ctx.restore();

                // Position badge tag
                const pnl = this.position.unrealizedPnL ? this.position.unrealizedPnL(this.currentPrice) : 0;
                const pnlPct = this.position.unrealizedPnLPct ? this.position.unrealizedPnLPct(this.currentPrice) : 0;
                const sideLbl = isLong ? `LONG ${this.position.shares}` : `SHORT ${Math.abs(this.position.shares)}`;
                const pnlSign = pnl >= 0 ? "+" : "";
                const pctSign = pnlPct >= 0 ? "+" : "";
                const posText = `🎯 ${sideLbl} @ $${this.position.avgPrice.toFixed(2)} (${pnlSign}$${pnl.toFixed(2)} | ${pctSign}${pnlPct.toFixed(1)}%)`;

                ctx.save();
                ctx.font = "bold 9px 'Segoe UI', sans-serif";
                const badgeW = ctx.measureText(posText).width + 16;
                const badgeH = 18;

                ctx.fillStyle = "#161a25";
                ctx.strokeStyle = posCol;
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.roundRect(8, posY - badgeH / 2, badgeW, badgeH, 3);
                ctx.fill();
                ctx.stroke();

                ctx.fillStyle = posCol;
                ctx.textAlign = "left";
                ctx.textBaseline = "middle";
                ctx.fillText(posText, 14, posY);
                ctx.restore();
            }
        }

        // --- Floating Trade Notification Toast ---
        if (this.activeNotification) {
            const notif = this.activeNotification;
            const elapsed = (Date.now() / 1000) - notif.time;
            if (elapsed < notif.duration) {
                let alpha = 1.0;
                if (elapsed > notif.duration - 0.8) {
                    alpha = Math.max(0, (notif.duration - elapsed) / 0.8);
                }

                ctx.save();
                ctx.globalAlpha = alpha;

                let icon = "🛒";
                let badgeCol = "#089981";
                let title = `BOUGHT ${notif.shares.toLocaleString()} ${notif.ticker} @ $${notif.price.toFixed(2)}`;
                let sub = `Cost: $${(notif.shares * notif.price).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

                if (notif.action === "SHORT") {
                    icon = "⚡";
                    badgeCol = "#f23645";
                    title = `SHORTED ${notif.shares.toLocaleString()} ${notif.ticker} @ $${notif.price.toFixed(2)}`;
                    sub = `Margin: $${(notif.shares * notif.price * 0.5).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
                } else if (notif.action === "COVER") {
                    icon = "🛡️";
                    badgeCol = "#2962ff";
                    title = `COVERED ${notif.shares.toLocaleString()} ${notif.ticker} @ $${notif.price.toFixed(2)}`;
                    if (notif.pnl !== null) {
                        const s = notif.pnl >= 0 ? "+" : "";
                        sub = `Realized: ${s}$${notif.pnl.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
                    }
                } else if (notif.action === "SELL") {
                    icon = "💰";
                    badgeCol = "#ff9800";
                    title = `SOLD ${notif.shares.toLocaleString()} ${notif.ticker} @ $${notif.price.toFixed(2)}`;
                    if (notif.pnl !== null) {
                        const s = notif.pnl >= 0 ? "+" : "";
                        sub = `Realized: ${s}$${notif.pnl.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
                    }
                } else if (notif.action === "REVERSE") {
                    icon = "🔄";
                    badgeCol = "#8e24aa";
                    title = `REVERSED POSITION: ${notif.shares.toLocaleString()} ${notif.ticker} @ $${notif.price.toFixed(2)}`;
                    if (notif.pnl !== null) {
                        const s = notif.pnl >= 0 ? "+" : "";
                        sub = `Realized P&L: ${s}$${notif.pnl.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
                    }
                }

                ctx.font = "bold 11px 'Segoe UI', sans-serif";
                const titleW = ctx.measureText(title).width;
                ctx.font = "10px 'Segoe UI', sans-serif";
                const subW = ctx.measureText(sub).width;
                const toastW = Math.max(240, Math.max(titleW, subW) + 54);
                const toastH = 40;
                const toastX = Math.round((chartW - toastW) / 2);
                const toastY = 12;

                // Box
                ctx.fillStyle = "#1e222d";
                ctx.strokeStyle = badgeCol;
                ctx.lineWidth = 1.5;
                ctx.beginPath();
                ctx.roundRect(toastX, toastY, toastW, toastH, 6);
                ctx.fill();
                ctx.stroke();

                // Icon / Left Accent strip
                ctx.fillStyle = badgeCol;
                ctx.beginPath();
                ctx.roundRect(toastX, toastY, 5, toastH, [6, 0, 0, 6]);
                ctx.fill();

                // Texts
                ctx.font = "16px 'Segoe UI', sans-serif";
                ctx.fillText(icon, toastX + 12, toastY + 25);

                ctx.font = "bold 11px 'Segoe UI', sans-serif";
                ctx.fillStyle = "#ffffff";
                ctx.textAlign = "left";
                ctx.fillText(title, toastX + 36, toastY + 17);

                ctx.font = "10px 'Segoe UI', sans-serif";
                ctx.fillStyle = badgeCol;
                ctx.fillText(sub, toastX + 36, toastY + 31);

                ctx.restore();
            }
        }

        // --- Current Price Line ---
        const curY = Math.round(getY(this.currentPrice));
        if (curY >= 0 && curY <= chartH) {
            ctx.save();
            ctx.setLineDash([4, 4]);
            ctx.strokeStyle = this.colors.priceLine;
            ctx.beginPath();
            ctx.moveTo(0, curY);
            ctx.lineTo(chartW, curY);
            ctx.stroke();
            ctx.restore();

            // Badge
            ctx.fillStyle = this.colors.priceLine;
            ctx.fillRect(chartW + 2, curY - 10, rightMargin - 4, 20);
            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 11px 'Segoe UI', sans-serif";
            ctx.fillText(`$${this.currentPrice.toFixed(2)}`, chartW + 6, curY);
        }

        // --- Crosshairs & Tooltip ---
        if (this.mousePos && this.mousePos.x < chartW && this.mousePos.y < chartH) {
            const mx = hoveredCandle ? hoveredX : this.mousePos.x;
            const my = this.mousePos.y;

            ctx.save();
            ctx.setLineDash([2, 2]);
            ctx.strokeStyle = this.colors.crosshair;

            // Vertical line
            ctx.beginPath();
            ctx.moveTo(mx, 0);
            ctx.lineTo(mx, chartH);
            ctx.stroke();

            // Horizontal line
            ctx.beginPath();
            ctx.moveTo(0, my);
            ctx.lineTo(chartW, my);
            ctx.stroke();
            ctx.restore();

            // Price badge at cursor Y
            const cursorPrice = getPrice(my);
            ctx.fillStyle = "#2a2e39";
            ctx.fillRect(chartW + 2, my - 9, rightMargin - 4, 18);
            ctx.fillStyle = "#ffffff";
            ctx.font = "11px 'Segoe UI', sans-serif";
            ctx.fillText(`$${cursorPrice.toFixed(2)}`, chartW + 6, my);

            // Candle Tooltip header
            if (hoveredCandle) {
                const isGreen = hoveredCandle.close >= hoveredCandle.open;
                const col = isGreen ? this.colors.up : this.colors.down;

                ctx.font = "12px Consolas, monospace";
                ctx.textAlign = "left";
                ctx.fillStyle = this.colors.text;

                let tx = 16;
                ctx.fillText(`O: `, tx, 20);
                ctx.fillStyle = col;
                ctx.fillText(`$${hoveredCandle.open.toFixed(2)}`, tx + 20, 20);

                tx += 85;
                ctx.fillStyle = this.colors.text;
                ctx.fillText(`H: `, tx, 20);
                ctx.fillStyle = col;
                ctx.fillText(`$${hoveredCandle.high.toFixed(2)}`, tx + 20, 20);

                tx += 85;
                ctx.fillStyle = this.colors.text;
                ctx.fillText(`L: `, tx, 20);
                ctx.fillStyle = col;
                ctx.fillText(`$${hoveredCandle.low.toFixed(2)}`, tx + 20, 20);

                tx += 85;
                ctx.fillStyle = this.colors.text;
                ctx.fillText(`C: `, tx, 20);
                ctx.fillStyle = col;
                ctx.fillText(`$${hoveredCandle.close.toFixed(2)}`, tx + 20, 20);

                tx += 85;
                ctx.fillStyle = this.colors.text;
                ctx.fillText(`Vol: `, tx, 20);
                ctx.fillStyle = this.colors.textActive;
                ctx.fillText(`${hoveredCandle.volume.toLocaleString()}`, tx + 35, 20);

                // Show trade marker info if on this candle
                const cMarkers = this.tradeMarkers.filter(m => Math.abs(m.candleTimestamp - hoveredCandle.timestamp) < 0.001);
                if (cMarkers.length > 0) {
                    const lastM = cMarkers[cMarkers.length - 1];
                    tx += 85;
                    const mCol = lastM.action === "BUY" || lastM.action === "COVER" ? this.colors.up : this.colors.down;
                    ctx.fillStyle = mCol;
                    ctx.font = "bold 12px Consolas, monospace";
                    ctx.fillText(`⚡ ${lastM.action} ${lastM.shares} @ $${lastM.price.toFixed(2)}`, tx, 20);
                }
            }
        }
    }
}
