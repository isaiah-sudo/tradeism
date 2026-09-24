/**
 * Crazy Win Animations Engine for Day Trading Simulator (Web Edition).
 * Renders high-octane 60fps canvas celebration animations:
 * - Money Rain & Gold Confetti
 * - Rocket Blastoff To The Moon
 * - Cyber Matrix Glitch Rain
 * - Diamond Hands Supernova
 * - Golden Bull Stampede
 */

class WinAnimationEngine {
    constructor() {
        this.canvas = document.getElementById("anim-canvas");
        this.ctx = this.canvas ? this.canvas.getContext("2d") : null;
        this.ui = document.getElementById("anim-overlay-ui");
        this.btnSkip = document.getElementById("btn-skip-anim");

        this.active = false;
        this.animationId = "money_rain";
        this.animFrameId = null;
        this.particles = [];
        this.frameCount = 0;
        this.maxFrames = 260; // ~4.3 seconds at 60fps
        this.extraData = {};

        this._initEvents();
    }

    _initEvents() {
        if (this.btnSkip) {
            this.btnSkip.addEventListener("click", () => this.stop());
        }
        if (this.canvas) {
            this.canvas.addEventListener("click", () => this.stop());
        }
        window.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && this.active) {
                this.stop();
            }
        });
        window.addEventListener("resize", () => {
            if (this.active) this._resize();
        });
    }

    _resize() {
        if (!this.canvas) return;
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    play(animationId = "money_rain", titleOverride = null) {
        this.stop();
        if (!this.canvas || !this.ctx) {
            this.canvas = document.getElementById("anim-canvas");
            if (this.canvas) this.ctx = this.canvas.getContext("2d");
        }
        if (!this.canvas || !this.ctx) return;

        this.animationId = animationId || "money_rain";
        this.titleOverride = titleOverride;
        this.active = true;
        this.frameCount = 0;
        this.particles = [];
        this.extraData = {};

        this._resize();
        this.canvas.style.display = "block";
        if (this.ui) this.ui.style.display = "block";

        this._initParticles();
        this._loop();
    }

    stop() {
        this.active = false;
        if (this.animFrameId) {
            cancelAnimationFrame(this.animFrameId);
            this.animFrameId = null;
        }
        if (this.canvas) {
            this.canvas.style.display = "none";
            this.canvas.style.transform = "none";
            if (this.ctx) this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        }
        if (this.ui) this.ui.style.display = "none";
    }

    _initParticles() {
        const w = this.canvas.width;
        const h = this.canvas.height;

        if (this.animationId === "rocket_moon") {
            this.extraData.rocket = { x: w / 2, y: h + 100, vy: -12.0, size: 70 };
            this.extraData.moon = { x: w / 2, y: 110, radius: 45, visible: true };
            // Stars
            for (let i = 0; i < 90; i++) {
                this.particles.push({
                    type: "star",
                    x: Math.random() * w,
                    y: Math.random() * h,
                    len: 10 + Math.random() * 30,
                    spd: 12 + Math.random() * 25
                });
            }
        } else if (this.animationId === "matrix_glitch") {
            const cols = Math.floor(w / 30);
            const chars = ["0", "1", "$", "WIN", "PROFIT", "BUY", "7F", "9A", "CALL", "MOON", "100K", "BULL"];
            for (let c = 0; c < cols; c++) {
                this.particles.push({
                    type: "matrix_col",
                    x: c * 30 + 15,
                    y: -Math.random() * 500,
                    spd: 12 + Math.random() * 18,
                    chars: Array.from({ length: 14 }, () => chars[Math.floor(Math.random() * chars.length)]),
                    color: Math.random() > 0.3 ? "#00ff66" : "#00ffff"
                });
            }
        } else if (this.animationId === "diamond_hands") {
            this.extraData.dh = { x: w / 2, y: h / 2, scale: 0.1, maxScale: 1.0, exploded: false };
        } else if (this.animationId === "golden_bull") {
            this.extraData.bull = { x: -200, y: h / 2, vx: 18.0, size: 75 };
            for (let i = 0; i < 70; i++) {
                this.particles.push({
                    type: "gold_coin",
                    x: Math.random() * w,
                    y: -Math.random() * 300,
                    vx: (Math.random() - 0.5) * 5,
                    vy: 6 + Math.random() * 10,
                    text: ["🪙", "👑", "🥇", "💰", "✨"][Math.floor(Math.random() * 5)],
                    size: 22 + Math.random() * 16,
                    rot: Math.random() * 360,
                    vrot: (Math.random() - 0.5) * 8
                });
            }
        } else {
            // Money Rain (default)
            const emojis = ["💵", "💸", "💰", "$100", "🤑", "✨", "⭐", "🎉"];
            for (let i = 0; i < 90; i++) {
                this.particles.push({
                    type: "rain",
                    x: Math.random() * w,
                    y: -Math.random() * (h * 0.9) - 20,
                    vx: (Math.random() - 0.5) * 3,
                    vy: 5 + Math.random() * 9,
                    text: emojis[Math.floor(Math.random() * emojis.length)],
                    size: 20 + Math.random() * 20,
                    wobble: Math.random() * Math.PI * 2,
                    wobbleSpd: 0.05 + Math.random() * 0.1
                });
            }
        }
    }

    _loop() {
        if (!this.active) return;
        this.frameCount++;

        const w = this.canvas.width;
        const h = this.canvas.height;
        this.ctx.clearRect(0, 0, w, h);

        if (this.animationId === "rocket_moon") {
            this._drawRocket(w, h);
        } else if (this.animationId === "matrix_glitch") {
            this._drawMatrix(w, h);
        } else if (this.animationId === "diamond_hands") {
            this._drawDiamondHands(w, h);
        } else if (this.animationId === "golden_bull") {
            this._drawGoldenBull(w, h);
        } else {
            this._drawMoneyRain(w, h);
        }

        if (this.frameCount >= this.maxFrames) {
            this.stop();
        } else {
            this.animFrameId = requestAnimationFrame(() => this._loop());
        }
    }

    // 1. Money Rain
    _drawMoneyRain(w, h) {
        // Draw falling bills
        for (const p of this.particles) {
            p.wobble += p.wobbleSpd;
            p.x += p.vx + Math.sin(p.wobble) * 2;
            p.y += p.vy;

            if (p.y > h + 40) {
                p.y = -40;
                p.x = Math.random() * w;
            }

            this.ctx.font = `${p.size}px sans-serif`;
            this.ctx.textAlign = "center";
            this.ctx.textBaseline = "middle";
            this.ctx.fillText(p.text, p.x, p.y);
        }

        // Center Pulsing Banner
        const pulse = 1 + Math.sin(this.frameCount * 0.1) * 0.06;
        this.ctx.save();
        this.ctx.translate(w / 2, h / 2);
        this.ctx.scale(pulse, pulse);

        // Backdrop box
        this.ctx.fillStyle = "rgba(14, 17, 23, 0.85)";
        this.ctx.strokeStyle = "#00e676";
        this.ctx.lineWidth = 4;
        this.ctx.beginPath();
        this.ctx.roundRect(-340, -60, 680, 120, 16);
        this.ctx.fill();
        this.ctx.stroke();

        // Banner text
        this.ctx.font = "bold 32px 'Segoe UI', Roboto, sans-serif";
        this.ctx.textAlign = "center";
        this.ctx.textBaseline = "middle";
        this.ctx.fillStyle = (this.frameCount % 16 < 8) ? "#00e676" : "#ffd700";
        this.ctx.fillText(this.titleOverride || "💸 CASH TSUNAMI! PROFIT LOCKED! 💸", 0, -14);

        this.ctx.font = "bold 15px 'Segoe UI', Roboto, sans-serif";
        this.ctx.fillStyle = "#ffffff";
        this.ctx.fillText("PROFIT TRANSFERRED TO MENU VAULT BALANCE", 0, 24);

        this.ctx.restore();
    }

    // 2. Rocket Blastoff
    _drawRocket(w, h) {
        const rocket = this.extraData.rocket;

        // Screen shake during launch
        if (rocket.y > 0) {
            const shake = (Math.random() - 0.5) * 6;
            this.canvas.style.transform = `translate(${shake}px, ${shake}px)`;
        } else {
            this.canvas.style.transform = "none";
        }

        // Warp stars
        this.ctx.strokeStyle = "#00e5ff";
        this.ctx.lineWidth = 2;
        for (const s of this.particles) {
            if (s.type === "star") {
                s.y += s.spd;
                if (s.y > h) {
                    s.y = -10;
                    s.x = Math.random() * w;
                }
                this.ctx.beginPath();
                this.ctx.moveTo(s.x, s.y);
                this.ctx.lineTo(s.x, s.y + s.len);
                this.ctx.stroke();
            }
        }

        // Moon
        this.ctx.font = "80px sans-serif";
        this.ctx.textAlign = "center";
        this.ctx.fillText("🌕", w / 2, 110);

        // Rocket position update
        rocket.y += rocket.vy;

        // Thruster flame particles
        for (let i = 0; i < 4; i++) {
            this.particles.push({
                type: "flame",
                x: rocket.x + (Math.random() - 0.5) * 20,
                y: rocket.y + 40,
                vx: (Math.random() - 0.5) * 4,
                vy: 8 + Math.random() * 10,
                text: ["🔥", "💥", "✨"][Math.floor(Math.random() * 3)],
                size: 20 + Math.random() * 16,
                life: 25
            });
        }

        // Draw flames
        for (let i = this.particles.length - 1; i >= 0; i--) {
            const p = this.particles[i];
            if (p.type === "flame") {
                p.x += p.vx;
                p.y += p.vy;
                p.life--;
                this.ctx.font = `${p.size}px sans-serif`;
                this.ctx.fillText(p.text, p.x, p.y);
                if (p.life <= 0) this.particles.splice(i, 1);
            }
        }

        // Draw rocket
        this.ctx.font = `${rocket.size}px sans-serif`;
        this.ctx.fillText("🚀", rocket.x, rocket.y);

        // Banner
        this.ctx.fillStyle = "rgba(14, 17, 23, 0.85)";
        this.ctx.strokeStyle = "#00e5ff";
        this.ctx.lineWidth = 3;
        this.ctx.beginPath();
        this.ctx.roundRect(w / 2 - 320, h / 2 - 40, 640, 80, 14);
        this.ctx.fill();
        this.ctx.stroke();

        this.ctx.font = "bold 30px 'Segoe UI', Roboto, sans-serif";
        this.ctx.fillStyle = "#00e5ff";
        this.ctx.fillText(this.titleOverride || "🚀 TO THE MOON! 100x GAINS! 🚀", w / 2, h / 2 + 10);
    }

    // 3. Matrix Glitch Rain
    _drawMatrix(w, h) {
        // Digital rain columns
        this.ctx.font = "bold 13px Consolas, monospace";
        this.ctx.textAlign = "center";

        for (const col of this.particles) {
            col.y += col.spd;
            if (col.y > h + 200) col.y = -200;

            for (let i = 0; i < col.chars.length; i++) {
                const charY = col.y + i * 22;
                if (charY > -20 && charY < h + 20) {
                    this.ctx.fillStyle = (i === col.chars.length - 1) ? "#ffffff" : col.color;
                    this.ctx.fillText(col.chars[i], col.x, charY);
                }
            }
        }

        // Random horizontal glitch slice
        if (Math.random() < 0.4) {
            const gy = Math.random() * h;
            const gh = 6 + Math.random() * 18;
            this.ctx.fillStyle = Math.random() > 0.5 ? "rgba(0, 255, 102, 0.3)" : "rgba(255, 0, 128, 0.3)";
            this.ctx.fillRect(0, gy, w, gh);
        }

        // Banner box
        this.ctx.fillStyle = "rgba(6, 12, 8, 0.92)";
        this.ctx.strokeStyle = "#00ff66";
        this.ctx.lineWidth = 3;
        this.ctx.beginPath();
        this.ctx.roundRect(w / 2 - 340, h / 2 - 50, 680, 100, 12);
        this.ctx.fill();
        this.ctx.stroke();

        this.ctx.font = "bold 26px Consolas, monospace";
        this.ctx.fillStyle = "#00ff66";
        this.ctx.fillText(this.titleOverride || "⚡ SYSTEM OVERRIDE: VICTORY PROTOCOL ⚡", w / 2, h / 2 - 5);

        this.ctx.font = "bold 14px Consolas, monospace";
        this.ctx.fillStyle = "#00ffff";
        this.ctx.fillText("HIGH FREQUENCY ALPHA LOCKED • PROFITS TRANSFERRED", w / 2, h / 2 + 25);
    }

    // 4. Diamond Hands Supernova
    _drawDiamondHands(w, h) {
        const dh = this.extraData.dh;

        if (this.frameCount < 40) {
            // Expanding glowing hands
            dh.scale = Math.min(1.0, this.frameCount / 35);
            this.ctx.save();
            this.ctx.translate(dh.x, dh.y);
            this.ctx.scale(dh.scale * 1.5, dh.scale * 1.5);
            this.ctx.font = "64px sans-serif";
            this.ctx.textAlign = "center";
            this.ctx.textBaseline = "middle";
            this.ctx.fillText("💎🙌💎", 0, 0);
            this.ctx.restore();
        } else if (this.frameCount === 40) {
            // DETONATE SHARDS!
            for (let i = 0; i < 110; i++) {
                const angle = Math.random() * Math.PI * 2;
                const spd = 6 + Math.random() * 18;
                this.particles.push({
                    type: "shard",
                    x: dh.x,
                    y: dh.y,
                    vx: Math.cos(angle) * spd,
                    vy: Math.sin(angle) * spd,
                    text: ["💎", "✨", "🔷", "💠", "⚡"][Math.floor(Math.random() * 5)],
                    size: 18 + Math.random() * 20
                });
            }
        } else {
            // Shards exploding outwards
            for (const p of this.particles) {
                p.x += p.vx;
                p.y += p.vy;
                p.vy += 0.15; // subtle gravity
                this.ctx.font = `${p.size}px sans-serif`;
                this.ctx.textAlign = "center";
                this.ctx.fillText(p.text, p.x, p.y);
            }
        }

        // Banner
        this.ctx.fillStyle = "rgba(14, 17, 23, 0.88)";
        this.ctx.strokeStyle = "#00e5ff";
        this.ctx.lineWidth = 3;
        this.ctx.beginPath();
        this.ctx.roundRect(w / 2 - 320, h / 2 + 100, 640, 80, 14);
        this.ctx.fill();
        this.ctx.stroke();

        this.ctx.font = "bold 28px 'Segoe UI', Roboto, sans-serif";
        this.ctx.fillStyle = "#00e5ff";
        this.ctx.textAlign = "center";
        this.ctx.fillText(this.titleOverride || "💎 DIAMOND HANDS SUPERNOVA! 💎", w / 2, h / 2 + 148);
    }

    // 5. Golden Bull Stampede
    _drawGoldenBull(w, h) {
        const bull = this.extraData.bull;
        bull.x += bull.vx;
        if (bull.x > w + 200) bull.x = -200;

        const shakeY = bull.y + Math.sin(this.frameCount * 0.7) * 8;

        // Laser eyes
        const lx = bull.x + 40;
        const ly = shakeY - 12;
        this.ctx.strokeStyle = "#ff1744";
        this.ctx.lineWidth = 4;
        this.ctx.beginPath();
        this.ctx.moveTo(lx, ly);
        this.ctx.lineTo(w, ly + (Math.random() - 0.5) * 60);
        this.ctx.stroke();

        // Draw bull
        this.ctx.font = `${bull.size}px sans-serif`;
        this.ctx.textAlign = "center";
        this.ctx.fillText("👑 🐂 ⚡", bull.x, shakeY);

        // Falling gold
        for (const p of this.particles) {
            p.x += p.vx;
            p.y += p.vy;
            p.rot += p.vrot;
            if (p.y > h + 30) {
                p.y = -30;
                p.x = Math.random() * w;
            }
            this.ctx.save();
            this.ctx.translate(p.x, p.y);
            this.ctx.rotate(p.rot * Math.PI / 180);
            this.ctx.font = `${p.size}px sans-serif`;
            this.ctx.fillText(p.text, 0, 0);
            this.ctx.restore();
        }

        // Banner
        this.ctx.fillStyle = "rgba(14, 17, 23, 0.88)";
        this.ctx.strokeStyle = "#ffd700";
        this.ctx.lineWidth = 3;
        this.ctx.beginPath();
        this.ctx.roundRect(w / 2 - 340, 70, 680, 80, 14);
        this.ctx.fill();
        this.ctx.stroke();

        this.ctx.font = "bold 28px 'Segoe UI', Roboto, sans-serif";
        this.ctx.fillStyle = "#ffd700";
        this.ctx.textAlign = "center";
        this.ctx.fillText(this.titleOverride || "👑 WALL STREET WHALE: BULL STAMPEDE! 👑", w / 2, 118);
    }
}

// Global instance
window.winAnimations = new WinAnimationEngine();
