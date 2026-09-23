/**
 * Professional HTML5 Canvas Candlestick Chart.
 * High-performance, Retina-crisp, interactive with crosshair and volume bars.
 */

class CandlestickChart {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');

        this.mousePos = null;
        this.candles = [];
        this.currentPrice = 0;
        this.ticker = "";

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

        const list = [...stock.candles];
        if (stock.currentCandle) {
            list.push(stock.currentCandle);
        }
        this.candles = list;
        this.render();
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

        // Add 6% vertical padding
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

        for (let i = 0; i < n; i++) {
            const c = this.candles[i];
            const x = Math.round(i * candleSpacing + (candleSpacing / 2));
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
            }
        }
    }
}
