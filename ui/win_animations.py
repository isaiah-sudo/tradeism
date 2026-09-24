"""
Next-Generation Ultra-Smooth Win Animation Engine for Day Trading Simulator (v1.7).
Renders 60 FPS delta-time physics-driven celebration overlays:
- Money Rain & Gold Confetti (3D fluttering banknotes, metallic tumbling ribbons & sparkle starbursts)
- To The Moon Rocket Blast (Perspective warp-speed starfield, multi-stage thruster plumes & lunar fireworks)
- Cyber Matrix Glitch Rain (Dual-layer code stream with white-hot head glow, CRT scanlines & cyber HUD)
- Diamond Hands Supernova (Gravitational singularity vortex, blinding shockwaves & faceted crystal blast)
- Golden Bull Stampede (Charging golden bull, motion-blur echoes, twin laser eyes & bouncing coin avalanche)
"""

import tkinter as tk
import random
import math
import time
import sys
import threading
from typing import Optional, Callable, List, Dict, Any


def play_audio_fanfare(animation_id: str):
    """Plays an asynchronous celebratory audio chime on Windows systems without blocking the UI."""
    if sys.platform != "win32":
        return

    def _worker():
        try:
            import winsound
            if animation_id == "money_rain":
                # Double cash register cha-ching
                winsound.Beep(1200, 75)
                time.sleep(0.03)
                winsound.Beep(1760, 160)
            elif animation_id == "rocket_moon":
                # Ascending cosmic warp chime
                for freq in [440, 554, 659, 880, 1175]:
                    winsound.Beep(freq, 55)
            elif animation_id == "matrix_glitch":
                # High-speed cyber terminal chirp
                for freq in [980, 1400, 780, 1650, 1200]:
                    winsound.Beep(freq, 40)
            elif animation_id == "diamond_hands":
                # Gravitational charge-up into high crystal sparkle
                winsound.Beep(330, 130)
                time.sleep(0.04)
                for freq in [1320, 1760, 2093]:
                    winsound.Beep(freq, 70)
            elif animation_id == "golden_bull":
                # Sovereign Wall Street brass fanfare
                for freq in [523, 659, 784, 1046]:
                    winsound.Beep(freq, 85)
            else:
                winsound.Beep(1000, 100)
        except Exception:
            pass

    threading.Thread(target=_worker, daemon=True).start()


class WinAnimationOverlay:
    """
    Renders 60 FPS hardware-accelerated celebration animations over any Tkinter window.
    Features delta-time physics, dynamic resizing, 3D polygon banknote tumbling,
    shockwave rings, and non-blocking victory flow.
    """
    def __init__(
        self,
        parent: tk.Widget,
        animation_id: str = "money_rain",
        on_finished: Optional[Callable[[], None]] = None,
        profit_info: Optional[Dict[str, Any]] = None
    ):
        self.parent = parent
        self.animation_id = animation_id
        self.on_finished = on_finished
        self.profit_info = profit_info

        self.particles: List[Dict[str, Any]] = []
        self.frame_count = 0
        self.elapsed_time = 0.0
        self.max_duration = 4.2  # ~4.2 seconds
        self._anim_job: Optional[str] = None
        self._stopped = False
        self._last_time = time.perf_counter()

        self.w = max(parent.winfo_width(), 950)
        self.h = max(parent.winfo_height(), 620)

        # Screen shake offsets
        self.shake_x = 0.0
        self.shake_y = 0.0

        # Create overlay canvas
        self.canvas = tk.Canvas(
            parent,
            bg="#06090f",
            highlightthickness=0,
            bd=0
        )
        self.canvas.place(x=0, y=0, relwidth=1.0, relheight=1.0)
        tk.Misc.lift(self.canvas)

        # Dynamic resize listener
        self.canvas.bind("<Configure>", self._on_resize)

        # Interactive dismiss listeners
        self.canvas.bind("<Button-1>", lambda e: self.stop())
        self._esc_bind = self.parent.bind("<Escape>", lambda e: self.stop(), add="+")

        # Top-Right Skip / Close Button
        self.btn_skip = tk.Button(
            self.canvas,
            text="✕ Close [Esc]",
            font=("Segoe UI", 9, "bold"),
            bg="#181d29",
            fg="#94a3b8",
            activebackground="#ef4444",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=12, pady=5,
            cursor="hand2",
            bd=0,
            command=self.stop
        )
        self.btn_skip.bind("<Enter>", lambda e: self.btn_skip.config(bg="#ef4444", fg="#ffffff"))
        self.btn_skip.bind("<Leave>", lambda e: self.btn_skip.config(bg="#181d29", fg="#94a3b8"))
        self.btn_skip_win = self.canvas.create_window(self.w - 75, 32, window=self.btn_skip)

        # Static HUD Elements
        self.banner_card = None
        self.banner_id = None
        self.sub_id = None
        self.profit_badge_rect = None
        self.profit_badge_text = None

        # Play victory audio in background
        play_audio_fanfare(self.animation_id)

        # Initialize specific animation scene
        self._init_animation()
        self._create_hud_elements()

        # Kickoff 60 FPS tick
        self._tick()

    def _on_resize(self, event):
        if event.widget == self.canvas and event.width > 50 and event.height > 50:
            self.w = event.width
            self.h = event.height
            self._reposition_hud()

    def _create_hud_elements(self):
        cx = self.w // 2
        cy = 90 if self.profit_info else 105

        # Glowing banner container card
        theme_colors = {
            "money_rain": ("#00e676", "#042614"),
            "rocket_moon": ("#00e5ff", "#041a2e"),
            "matrix_glitch": ("#39ff14", "#02240b"),
            "diamond_hands": ("#b388ff", "#180a2e"),
            "golden_bull": ("#ffd700", "#2b1c03")
        }
        border_col, bg_col = theme_colors.get(self.animation_id, ("#00e676", "#071724"))

        # Main Title Banner
        titles = {
            "money_rain": "💸 CASH TSUNAMI! PROFIT LOCKED! 💸",
            "rocket_moon": "🚀 TO THE MOON! 100x GAINS! 🚀",
            "matrix_glitch": "⚡ SYSTEM OVERRIDE: VICTORY PROTOCOL ⚡",
            "diamond_hands": "💎 DIAMOND HANDS: COSMIC SUPERNOVA! 💎",
            "golden_bull": "👑 WALL STREET WHALE: BULL STAMPEDE! 👑"
        }
        subtitles = {
            "money_rain": "VAULT BOOSTED • HIGH ROLLER STATUS UNLOCKED",
            "rocket_moon": "INTERPLANETARY APEX • ORBITAL BREAKOUT CONFIRMED",
            "matrix_glitch": "WALL STREET TERMINAL COMPROMISED • ALPHA EXTRACTED",
            "diamond_hands": "UNSHAKEABLE CONVICTION • COSMIC WEALTH CREATED",
            "golden_bull": "MARKET APEX PREDATOR • UNSTOPPABLE RUNNING BULL"
        }

        # Card Background
        card_w, card_h = 360, 48
        if self.profit_info:
            card_h = 68
        self.banner_card = self.canvas.create_rectangle(
            cx - card_w, cy - card_h, cx + card_w, cy + card_h,
            fill=bg_col,
            outline=border_col,
            width=2
        )

        font_family = "Consolas" if self.animation_id == "matrix_glitch" else "Segoe UI"
        self.banner_id = self.canvas.create_text(
            cx, cy - (14 if self.profit_info else 8),
            text=titles.get(self.animation_id, "VICTORY!"),
            font=(font_family, 24, "bold"),
            fill=border_col
        )
        self.sub_id = self.canvas.create_text(
            cx, cy + (12 if not self.profit_info else 10),
            text=subtitles.get(self.animation_id, "PROFIT SECURED"),
            font=(font_family, 11, "bold"),
            fill="#e2e8f0"
        )

        # Banked Profit Pill if available
        if self.profit_info:
            p_text = ""
            if "profit" in self.profit_info and self.profit_info["profit"] > 0:
                p_text = f"💰 +${self.profit_info['profit']:,.2f} TRANSFERRED TO VAULT"
                if "new_balance" in self.profit_info:
                    p_text += f" • TOTAL VAULT: ${self.profit_info['new_balance']:,.2f}"
            elif "duel_win" in self.profit_info and "diff" in self.profit_info:
                p_text = f"🏆 DUEL VICTORY! +${self.profit_info['diff']:,.2f} LEAD OVER OPPONENT!"

            if p_text:
                self.profit_badge_rect = self.canvas.create_rectangle(
                    cx - 280, cy + 34, cx + 280, cy + 58,
                    fill="#102e1b", outline="#00e676", width=1
                )
                self.profit_badge_text = self.canvas.create_text(
                    cx, cy + 46,
                    text=p_text,
                    font=("Segoe UI", 10, "bold"),
                    fill="#00e676"
                )

    def _reposition_hud(self):
        cx = self.w // 2
        cy = 90 if self.profit_info else 105
        card_w, card_h = 360, (68 if self.profit_info else 48)

        if self.banner_card:
            self.canvas.coords(self.banner_card, cx - card_w, cy - card_h, cx + card_w, cy + card_h)
        if self.banner_id:
            self.canvas.coords(self.banner_id, cx, cy - (14 if self.profit_info else 8))
        if self.sub_id:
            self.canvas.coords(self.sub_id, cx, cy + (12 if not self.profit_info else 10))
        if self.profit_badge_rect:
            self.canvas.coords(self.profit_badge_rect, cx - 280, cy + 34, cx + 280, cy + 58)
        if self.profit_badge_text:
            self.canvas.coords(self.profit_badge_text, cx, cy + 46)
        if hasattr(self, "btn_skip_win"):
            self.canvas.coords(self.btn_skip_win, self.w - 75, 32)

    def _init_animation(self):
        w, h = self.w, self.h
        if self.animation_id == "rocket_moon":
            self._init_rocket(w, h)
        elif self.animation_id == "matrix_glitch":
            self._init_matrix(w, h)
        elif self.animation_id == "diamond_hands":
            self._init_diamond_hands(w, h)
        elif self.animation_id == "golden_bull":
            self._init_golden_bull(w, h)
        else:
            self._init_money_rain(w, h)

    # =========================================================================
    # 1. MONEY RAIN & GOLD CONFETTI (3D BANKNOTES & TUMBLING METALLIC FOIL)
    # =========================================================================
    def _init_money_rain(self, w, h):
        self.canvas.configure(bg="#040b08")

        # 30 Realistic 3D Fluttering Banknotes
        for _ in range(32):
            self.particles.append({
                "type": "banknote",
                "x": random.uniform(30, w - 30),
                "y": random.uniform(-h * 0.9, -20),
                "vx": random.uniform(-1.0, 1.0),
                "vy": random.uniform(4.0, 8.5),
                "bw": random.uniform(40, 52),
                "bh": random.uniform(22, 28),
                "rot": random.uniform(0, math.pi * 2),
                "v_rot": random.uniform(-0.04, 0.04),
                "flip": random.uniform(0, math.pi * 2),
                "v_flip": random.uniform(0.08, 0.18),
                "wobble": random.uniform(0, math.pi * 2),
                "poly_tag": None,
                "text_tag": None
            })

        # 60 Shimmering Metallic Foil Confetti Ribbons
        confetti_colors = ["#ffd700", "#ffecb3", "#00e676", "#00e5ff", "#ff1744", "#ff4081", "#ffffff"]
        for _ in range(65):
            self.particles.append({
                "type": "confetti",
                "x": random.uniform(20, w - 20),
                "y": random.uniform(-h * 0.8, -10),
                "vx": random.uniform(-1.8, 1.8),
                "vy": random.uniform(4.5, 9.5),
                "w": random.uniform(10, 18),
                "h": random.uniform(6, 12),
                "color": random.choice(confetti_colors),
                "flip": random.uniform(0, math.pi * 2),
                "v_flip": random.uniform(0.12, 0.28),
                "rot": random.uniform(0, math.pi * 2),
                "v_rot": random.uniform(-0.08, 0.08),
                "tag": None
            })

        # 25 Shimmering Star Sparkles & Currency Icons
        sparkles = ["✨", "✦", "⭐", "💰", "🤑", "🌟"]
        for _ in range(25):
            self.particles.append({
                "type": "sparkle",
                "x": random.uniform(30, w - 30),
                "y": random.uniform(-h * 0.6, -10),
                "vx": random.uniform(-0.8, 0.8),
                "vy": random.uniform(3.0, 6.0),
                "char": random.choice(sparkles),
                "size": random.randint(14, 26),
                "color": random.choice(["#ffd700", "#ffffff", "#00e676", "#76ff03"]),
                "wobble": random.uniform(0, math.pi * 2),
                "tag": None
            })

    def _tick_money_rain(self, w, h, dt_scale: float):
        # Pulse banner border glow
        if self.banner_card:
            glow = "#00e676" if (int(self.elapsed_time * 8)) % 2 == 0 else "#ffd700"
            self.canvas.itemconfig(self.banner_card, outline=glow)

        for p in self.particles:
            p_type = p["type"]
            p["x"] += p["vx"] * dt_scale
            p["y"] += p["vy"] * dt_scale

            # Respawn at top
            if p["y"] > h + 30:
                p["y"] = random.uniform(-70, -15)
                p["x"] = random.uniform(20, w - 20)

            if p_type == "banknote":
                p["rot"] += p["v_rot"] * dt_scale
                p["flip"] += p["v_flip"] * dt_scale
                p["wobble"] += 0.05 * dt_scale
                p["x"] += math.sin(p["wobble"]) * 1.2 * dt_scale

                # Calculate 3D perspective foreshortening
                cos_r = math.cos(p["rot"])
                sin_r = math.sin(p["rot"])
                cos_f = math.cos(p["flip"])
                hw = p["bw"] * 0.5
                hh = p["bh"] * 0.5 * cos_f

                x1 = p["x"] - hw * cos_r + hh * sin_r
                y1 = p["y"] - hw * sin_r - hh * cos_r
                x2 = p["x"] + hw * cos_r + hh * sin_r
                y2 = p["y"] + hw * sin_r - hh * cos_r
                x3 = p["x"] + hw * cos_r - hh * sin_r
                y3 = p["y"] + hw * sin_r + hh * cos_r
                x4 = p["x"] - hw * cos_r - hh * sin_r
                y4 = p["y"] - hw * sin_r + hh * cos_r

                # Front/Back 3D shading
                front = (cos_f >= 0)
                body_col = "#00e676" if front else "#093318"
                out_col = "#00c853" if front else "#00e676"
                txt_col = "#ffffff" if front else "#00e676"

                if p["poly_tag"] is None:
                    p["poly_tag"] = self.canvas.create_polygon(
                        x1, y1, x2, y2, x3, y3, x4, y4,
                        fill=body_col, outline=out_col, width=1.5
                    )
                    p["text_tag"] = self.canvas.create_text(
                        p["x"], p["y"], text="$100", font=("Segoe UI", 8, "bold"), fill=txt_col
                    )
                else:
                    self.canvas.coords(p["poly_tag"], x1, y1, x2, y2, x3, y3, x4, y4)
                    self.canvas.coords(p["text_tag"], p["x"], p["y"])
                    self.canvas.itemconfig(p["poly_tag"], fill=body_col, outline=out_col)
                    self.canvas.itemconfig(p["text_tag"], fill=txt_col)

            elif p_type == "confetti":
                p["rot"] += p["v_rot"] * dt_scale
                p["flip"] += p["v_flip"] * dt_scale
                cos_f = abs(math.cos(p["flip"]))
                cw = max(2.0, p["w"] * cos_f)
                ch = p["h"]

                cos_r = math.cos(p["rot"])
                sin_r = math.sin(p["rot"])
                x1 = p["x"] - cw * cos_r + ch * sin_r
                y1 = p["y"] - cw * sin_r - ch * cos_r
                x2 = p["x"] + cw * cos_r + ch * sin_r
                y2 = p["y"] + cw * sin_r - ch * cos_r
                x3 = p["x"] + cw * cos_r - ch * sin_r
                y3 = p["y"] + cw * sin_r + ch * cos_r
                x4 = p["x"] - cw * cos_r - ch * sin_r
                y4 = p["y"] - cw * sin_r + ch * cos_r

                if p["tag"] is None:
                    p["tag"] = self.canvas.create_polygon(x1, y1, x2, y2, x3, y3, x4, y4, fill=p["color"], outline="")
                else:
                    self.canvas.coords(p["tag"], x1, y1, x2, y2, x3, y3, x4, y4)

            elif p_type == "sparkle":
                p["wobble"] += 0.08 * dt_scale
                p["x"] += math.sin(p["wobble"]) * 1.5 * dt_scale
                if p["tag"] is None:
                    p["tag"] = self.canvas.create_text(
                        p["x"], p["y"], text=p["char"], font=("Segoe UI", p["size"]), fill=p["color"]
                    )
                else:
                    self.canvas.coords(p["tag"], p["x"], p["y"])

    # =========================================================================
    # 2. TO THE MOON ROCKET BLAST (WARP SPEED, THRUSTER PLUMES & FIREWORKS)
    # =========================================================================
    def _init_rocket(self, w, h):
        self.canvas.configure(bg="#030612")
        self.moon_x = w // 2
        self.moon_y = 120

        # Lunar Glow Halo Rings
        self.moon_halo1 = self.canvas.create_oval(
            self.moon_x - 70, self.moon_y - 70, self.moon_x + 70, self.moon_y + 70,
            outline="#00e5ff", width=2
        )
        self.moon_halo2 = self.canvas.create_oval(
            self.moon_x - 90, self.moon_y - 90, self.moon_x + 90, self.moon_y + 90,
            outline="#ffd700", width=1, dash=(4, 4)
        )
        self.moon_id = self.canvas.create_text(
            self.moon_x, self.moon_y, text="🌕", font=("Segoe UI", 68)
        )

        # 75 Perspective Warp Stars streaming outward from celestial apex (moon)
        for _ in range(75):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(30, max(w, h))
            self.particles.append({
                "type": "warp_star",
                "angle": angle,
                "dist": dist,
                "spd": random.uniform(10, 26),
                "color": random.choice(["#ffffff", "#00e5ff", "#80d8ff", "#ffd700"]),
                "line_tag": None
            })

        # Rocket State
        self.rocket = {
            "x": self.moon_x,
            "y": h + 100,
            "vy": -7.0,
            "accel": -0.15,
            "max_vy": -22.0
        }
        self.rocket_tag = self.canvas.create_text(self.rocket["x"], self.rocket["y"], text="🚀", font=("Segoe UI", 56))

        # Dynamic Exhaust Plume Fire Polygon
        self.flame_poly = self.canvas.create_polygon(0, 0, 0, 0, 0, 0, fill="#ff6d00", outline="#ffff00", width=1.5)
        self.plasma_core = self.canvas.create_oval(0, 0, 0, 0, fill="#ffffff", outline="")

        # Exhaust particles pool (smoke and flame sparks)
        self.exhaust_particles: List[Dict[str, Any]] = []

        # Supersonic Shockwave Rings
        self.shockwaves: List[Dict[str, Any]] = []

        # Lunar Fireworks Pool
        self.lunar_fireworks: List[Dict[str, Any]] = []

    def _tick_rocket(self, w, h, dt_scale: float):
        rx = self.rocket["x"]
        ry = self.rocket["y"]

        # Accelerate rocket upwards
        self.rocket["vy"] = max(self.rocket["max_vy"], self.rocket["vy"] + self.rocket["accel"] * dt_scale)
        self.rocket["y"] += self.rocket["vy"] * dt_scale
        ry = self.rocket["y"]

        # Screen shake during liftoff phase
        if ry > self.moon_y + 100:
            shake_amp = min(5.0, abs(self.rocket["vy"]) * 0.25)
            self.shake_x = random.uniform(-shake_amp, shake_amp)
            self.shake_y = random.uniform(-shake_amp, shake_amp)
        else:
            self.shake_x = 0.0
            self.shake_y = 0.0

        # Update rocket position
        self.canvas.coords(self.rocket_tag, rx + self.shake_x, ry + self.shake_y)

        # Update multi-tier thruster flame
        flame_len = min(65.0, 30.0 + abs(self.rocket["vy"]) * 2.0 + random.uniform(-6, 6))
        flame_w = random.uniform(10, 16)
        fx1, fy1 = rx - flame_w, ry + 28
        fx2, fy2 = rx + flame_w, ry + 28
        fx3, fy3 = rx, ry + 28 + flame_len
        self.canvas.coords(self.flame_poly, fx1, fy1, fx2, fy2, fx3, fy3)
        self.canvas.itemconfig(self.flame_poly, fill=random.choice(["#ff3d00", "#ff6d00", "#ffea00"]))

        # Plasma core oval
        self.canvas.coords(self.plasma_core, rx - 7, ry + 25, rx + 7, ry + 42)

        # Spawn exhaust smoke & flame sparks
        if len(self.exhaust_particles) < 35 and ry > self.moon_y - 20:
            for _ in range(2):
                self.exhaust_particles.append({
                    "x": rx + random.uniform(-8, 8),
                    "y": ry + 36,
                    "vx": random.uniform(-2.5, 2.5),
                    "vy": random.uniform(6.0, 14.0),
                    "size": random.randint(8, 16),
                    "life": 1.0,
                    "decay": random.uniform(0.04, 0.08),
                    "char": random.choice(["🔥", "💥", "💨", "✨"]),
                    "tag": None
                })

        # Update exhaust particles
        for ep in list(self.exhaust_particles):
            ep["x"] += ep["vx"] * dt_scale
            ep["y"] += ep["vy"] * dt_scale
            ep["life"] -= ep["decay"] * dt_scale
            if ep["life"] <= 0:
                if ep["tag"]:
                    self.canvas.delete(ep["tag"])
                self.exhaust_particles.remove(ep)
            else:
                if ep["tag"] is None:
                    ep["tag"] = self.canvas.create_text(ep["x"], ep["y"], text=ep["char"], font=("Segoe UI", ep["size"]))
                else:
                    self.canvas.coords(ep["tag"], ep["x"], ep["y"])

        # Supersonic Shockwave Trigger
        if self.frame_count in (25, 45):
            self.shockwaves.append({
                "x": rx,
                "y": ry + 30,
                "r": 10.0,
                "max_r": 160.0,
                "spd": 8.0,
                "color": "#00e5ff",
                "tag": None
            })

        for sw in list(self.shockwaves):
            sw["r"] += sw["spd"] * dt_scale
            if sw["r"] >= sw["max_r"]:
                if sw["tag"]:
                    self.canvas.delete(sw["tag"])
                self.shockwaves.remove(sw)
            else:
                x1, y1 = sw["x"] - sw["r"], sw["y"] - sw["r"]
                x2, y2 = sw["x"] + sw["r"], sw["y"] + sw["r"]
                if sw["tag"] is None:
                    sw["tag"] = self.canvas.create_oval(x1, y1, x2, y2, outline=sw["color"], width=2)
                else:
                    self.canvas.coords(sw["tag"], x1, y1, x2, y2)

        # Warp Stars Stream
        max_dist = math.hypot(w, h)
        for p in self.particles:
            p["dist"] += p["spd"] * dt_scale
            if p["dist"] > max_dist:
                p["dist"] = random.uniform(25, 80)
                p["angle"] = random.uniform(0, math.pi * 2)

            cos_a = math.cos(p["angle"])
            sin_a = math.sin(p["angle"])
            tail_len = min(50.0, p["dist"] * 0.18)
            x1 = self.moon_x + cos_a * p["dist"]
            y1 = self.moon_y + sin_a * p["dist"]
            x2 = self.moon_x + cos_a * (p["dist"] + tail_len)
            y2 = self.moon_y + sin_a * (p["dist"] + tail_len)

            if p["line_tag"] is None:
                p["line_tag"] = self.canvas.create_line(x1, y1, x2, y2, fill=p["color"], width=1.5)
            else:
                self.canvas.coords(p["line_tag"], x1, y1, x2, y2)

        # Lunar Fireworks Finale (When rocket reaches moon)
        if ry <= self.moon_y + 40 and len(self.lunar_fireworks) == 0:
            for _ in range(45):
                angle = random.uniform(0, math.pi * 2)
                spd = random.uniform(3.0, 14.0)
                self.lunar_fireworks.append({
                    "x": self.moon_x,
                    "y": self.moon_y,
                    "vx": math.cos(angle) * spd,
                    "vy": math.sin(angle) * spd,
                    "char": random.choice(["✨", "⭐", "💥", "🔷"]),
                    "tag": None
                })

        for fw in self.lunar_fireworks:
            fw["x"] += fw["vx"] * dt_scale
            fw["y"] += fw["vy"] * dt_scale
            fw["vy"] += 0.15 * dt_scale  # gentle gravity
            if fw["tag"] is None:
                fw["tag"] = self.canvas.create_text(fw["x"], fw["y"], text=fw["char"], font=("Segoe UI", 14))
            else:
                self.canvas.coords(fw["tag"], fw["x"], fw["y"])

    # =========================================================================
    # 3. CYBER MATRIX GLITCH RAIN (AUTHENTIC HEAD GLOW, SCANLINES & MORPHING)
    # =========================================================================
    def _init_matrix(self, w, h):
        self.canvas.configure(bg="#010a04")

        # Code Stream Columns (32 columns)
        cols = max(18, min(42, w // 32))
        pool = ["$", "¥", "€", "₿", "BUY", "WIN", "BULL", "GAIN", "CALL", "7F", "A4", "0", "1", "ALPHA", "EXE", "SEC", "+999%"]
        self.matrix_cols: List[Dict[str, Any]] = []

        for c in range(cols):
            x = c * 32 + 16
            chars = [random.choice(pool) for _ in range(14)]
            self.matrix_cols.append({
                "x": x,
                "y": random.uniform(-350, 0),
                "spd": random.uniform(12.0, 24.0),
                "chars": chars,
                "head_char": random.choice(pool),
                "head_tag": None,
                "trail_tag": None
            })

        # CRT Scanline
        self.scanline_y = 0.0
        self.scanline = self.canvas.create_line(0, 0, w, 0, fill="#39ff14", width=2)

        # Dynamic Glitch Bands
        self.glitch_rect1 = self.canvas.create_rectangle(0, -50, w, -50, fill="#00ff66", outline="")
        self.glitch_rect2 = self.canvas.create_rectangle(0, -50, w, -50, fill="#00e5ff", outline="")

    def _tick_matrix(self, w, h, dt_scale: float):
        pool = ["$", "¥", "€", "₿", "BUY", "WIN", "BULL", "GAIN", "CALL", "7F", "A4", "0", "1", "ALPHA", "EXE", "SEC", "+999%"]

        # CRT Scanline Sweep
        self.scanline_y = (self.scanline_y + 4.5 * dt_scale) % h
        self.canvas.coords(self.scanline, 0, self.scanline_y, w, self.scanline_y)

        # Glitch Slice Bands
        if random.random() < 0.25:
            gy1 = random.uniform(40, h - 40)
            gh1 = random.uniform(4, 18)
            self.canvas.coords(self.glitch_rect1, 0, gy1, w, gy1 + gh1)
            self.canvas.itemconfig(self.glitch_rect1, fill=random.choice(["#00e676", "#00e5ff", "#ff007f"]))
        else:
            self.canvas.coords(self.glitch_rect1, 0, -50, w, -50)

        for col in self.matrix_cols:
            col["y"] += col["spd"] * dt_scale
            if col["y"] > h + 250:
                col["y"] = random.uniform(-250, -40)
                col["spd"] = random.uniform(12.0, 24.0)

            # Random character morphing (authentically scrambles code like the movie!)
            if random.random() < 0.20:
                idx = random.randint(0, len(col["chars"]) - 1)
                col["chars"][idx] = random.choice(pool)
                col["head_char"] = random.choice(pool)

            # Trailing body text (Matrix emerald green)
            trail_text = "\n".join(col["chars"])
            if col["trail_tag"] is None:
                col["trail_tag"] = self.canvas.create_text(
                    col["x"], col["y"],
                    text=trail_text,
                    font=("Consolas", 10, "bold"),
                    fill="#00e676",
                    anchor="n"
                )
                col["head_tag"] = self.canvas.create_text(
                    col["x"], col["y"] + (len(col["chars"]) * 14),
                    text=col["head_char"],
                    font=("Consolas", 12, "bold"),
                    fill="#ffffff",
                    anchor="n"
                )
            else:
                self.canvas.coords(col["trail_tag"], col["x"], col["y"])
                self.canvas.itemconfig(col["trail_tag"], text=trail_text)
                self.canvas.coords(col["head_tag"], col["x"], col["y"] + (len(col["chars"]) * 14))
                self.canvas.itemconfig(col["head_tag"], text=col["head_char"])

        # Cyber Terminal prompt cursor blink on subtitle
        if self.sub_id:
            cursor = "_" if (int(self.elapsed_time * 4)) % 2 == 0 else " "
            base_txt = "WALL STREET TERMINAL COMPROMISED • ALPHA EXTRACTED"
            self.canvas.itemconfig(self.sub_id, text=f"{base_txt} {cursor}")

    # =========================================================================
    # 4. DIAMOND HANDS SUPERNOVA (SINGULARITY, EXPANDING SHOCKWAVES & GEMS)
    # =========================================================================
    def _init_diamond_hands(self, w, h):
        self.canvas.configure(bg="#050314")
        self.cx = w // 2
        self.cy = h // 2 + 10
        self.detonated = False

        # Central Diamond Hands Badge
        self.dh_text_id = self.canvas.create_text(
            self.cx, self.cy, text="💎🙌💎", font=("Segoe UI", 42)
        )

        # Gravitational Singularity Inward Contracting Rings (Phase 1)
        self.gravity_rings = [
            {"r": 350.0, "tag": self.canvas.create_oval(0, 0, 0, 0, outline="#00e5ff", width=2)},
            {"r": 250.0, "tag": self.canvas.create_oval(0, 0, 0, 0, outline="#b388ff", width=2)},
            {"r": 150.0, "tag": self.canvas.create_oval(0, 0, 0, 0, outline="#ffffff", width=1.5)}
        ]

        # Inward Gravity Particle Motes
        for _ in range(40):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(180, 420)
            self.particles.append({
                "type": "inward_mote",
                "angle": angle,
                "dist": dist,
                "spd": random.uniform(6.0, 14.0),
                "char": random.choice(["✨", "✦", "🔹", "⚡"]),
                "tag": None
            })

        # Outward Cosmic Shockwaves (Phase 2)
        self.cosmic_shockwaves: List[Dict[str, Any]] = []

    def _tick_diamond_hands(self, w, h, dt_scale: float):
        self.cx = w // 2
        self.cy = h // 2 + 10

        # Phase 1: Singularity Compression (0.0s to 1.1s)
        if self.elapsed_time < 1.1:
            progress = self.elapsed_time / 1.1
            scale_sz = int(42 + progress * 24)
            vib_x = random.uniform(-progress * 4, progress * 4)
            vib_y = random.uniform(-progress * 4, progress * 4)
            self.canvas.coords(self.dh_text_id, self.cx + vib_x, self.cy + vib_y)
            self.canvas.itemconfig(self.dh_text_id, font=("Segoe UI", scale_sz))

            # Contract gravity rings inward
            for gr in self.gravity_rings:
                gr["r"] -= 12.0 * dt_scale
                if gr["r"] <= 10.0:
                    gr["r"] = 350.0
                r = gr["r"]
                self.canvas.coords(gr["tag"], self.cx - r, self.cy - r, self.cx + r, self.cy + r)

            # Inward motes
            for mote in self.particles:
                mote["dist"] -= mote["spd"] * dt_scale
                if mote["dist"] < 15.0:
                    mote["dist"] = random.uniform(220, 450)
                mx = self.cx + math.cos(mote["angle"]) * mote["dist"]
                my = self.cy + math.sin(mote["angle"]) * mote["dist"]
                if mote["tag"] is None:
                    mote["tag"] = self.canvas.create_text(mx, my, text=mote["char"], font=("Segoe UI", 12))
                else:
                    self.canvas.coords(mote["tag"], mx, my)

        # Phase 2: THE SUPERNOVA BURST DETONATION!
        else:
            if not self.detonated:
                self.detonated = True
                # Clean up singularity rings and motes
                for gr in self.gravity_rings:
                    self.canvas.delete(gr["tag"])
                for mote in self.particles:
                    if mote.get("tag"):
                        self.canvas.delete(mote["tag"])
                self.particles.clear()

                # Change central text to burst icon
                self.canvas.itemconfig(self.dh_text_id, text="💥 SUPERNOVA! 💥", font=("Segoe UI", 48, "bold"))

                # Trigger 3 Blinding Shockwave Rings
                for sw_color, spd in [("#ffffff", 18.0), ("#00e5ff", 12.0), ("#d500f9", 8.0)]:
                    self.cosmic_shockwaves.append({
                        "r": 15.0,
                        "spd": spd,
                        "max_r": max(w, h) * 0.9,
                        "color": sw_color,
                        "tag": self.canvas.create_oval(0, 0, 0, 0, outline=sw_color, width=3)
                    })

                # Explode 90 Faceted Prismatic Gem Shards
                gem_icons = ["💎", "💠", "🔷", "✨", "⭐", "⚡", "🪙"]
                colors = ["#00e5ff", "#2979ff", "#e040fb", "#ffd700", "#ffffff"]
                for _ in range(90):
                    angle = random.uniform(0, math.pi * 2)
                    spd = random.uniform(6.0, 24.0)
                    self.particles.append({
                        "type": "gem_shard",
                        "x": self.cx,
                        "y": self.cy,
                        "vx": math.cos(angle) * spd,
                        "vy": math.sin(angle) * spd,
                        "char": random.choice(gem_icons),
                        "size": random.randint(14, 28),
                        "color": random.choice(colors),
                        "drag": random.uniform(0.97, 0.99),
                        "tag": None
                    })

            # Update Expanding Shockwave Rings
            for sw in list(self.cosmic_shockwaves):
                sw["r"] += sw["spd"] * dt_scale
                r = sw["r"]
                if r >= sw["max_r"]:
                    self.canvas.delete(sw["tag"])
                    self.cosmic_shockwaves.remove(sw)
                else:
                    self.canvas.coords(sw["tag"], self.cx - r, self.cy - r, self.cx + r, self.cy + r)

            # Update Exploding Gem Shards
            for shard in self.particles:
                shard["vx"] *= shard["drag"] ** dt_scale
                shard["vy"] = (shard["vy"] + 0.22 * dt_scale) * (shard["drag"] ** dt_scale)
                shard["x"] += shard["vx"] * dt_scale
                shard["y"] += shard["vy"] * dt_scale

                if shard["tag"] is None:
                    shard["tag"] = self.canvas.create_text(
                        shard["x"], shard["y"], text=shard["char"], font=("Segoe UI", shard["size"])
                    )
                else:
                    self.canvas.coords(shard["tag"], shard["x"], shard["y"])

    # =========================================================================
    # 5. GOLDEN BULL STAMPEDE (MOTION BLUR, LASER EYES & BOUNCING BULLION)
    # =========================================================================
    def _init_golden_bull(self, w, h):
        self.canvas.configure(bg="#0c0903")
        self.bull_x = -180.0
        self.bull_y = h // 2 + 20
        self.bull_vx = 17.5

        # Motion Blur Echoes (3 trailing silhouettes)
        self.bull_echoes = [
            self.canvas.create_text(-200, 0, text="👑🐂", font=("Segoe UI", 52), fill="#614800"),
            self.canvas.create_text(-200, 0, text="👑🐂", font=("Segoe UI", 54), fill="#a87d00"),
            self.canvas.create_text(-200, 0, text="👑🐂", font=("Segoe UI", 56), fill="#ffd700")
        ]
        self.bull_id = self.bull_echoes[2]

        # Twin Piercing Crimson/Gold Laser Eyes
        self.laser_line1 = self.canvas.create_line(0, 0, 0, 0, fill="#ff1744", width=3)
        self.laser_line2 = self.canvas.create_line(0, 0, 0, 0, fill="#ffd700", width=2)

        # Hoof Ground Stomp Rings
        self.hoof_rings: List[Dict[str, Any]] = []

        # 70 Golden Coins & Bullion Bars
        gold_tokens = ["🪙", "🧱", "👑", "🏆", "💰", "✨"]
        for _ in range(70):
            self.particles.append({
                "type": "gold_coin",
                "x": random.uniform(40, w - 40),
                "y": random.uniform(-150, 0),
                "vx": random.uniform(-4.0, 4.0),
                "vy": random.uniform(6.0, 15.0),
                "char": random.choice(gold_tokens),
                "size": random.randint(18, 28),
                "bounce_floor": h - random.uniform(20, 60),
                "tag": None
            })

    def _tick_golden_bull(self, w, h, dt_scale: float):
        self.bull_x += self.bull_vx * dt_scale
        if self.bull_x > w + 220:
            self.bull_x = -180.0

        # Gallop stride physics
        gallop_phase = self.frame_count * 0.45
        gallop_y = self.bull_y + math.sin(gallop_phase) * 16.0

        # Ground camera rumble synced with hoof impact
        if math.sin(gallop_phase) > 0.85:
            self.shake_y = random.uniform(-4.0, 4.0)
            # Spawn hoof shockwave
            if len(self.hoof_rings) < 4:
                self.hoof_rings.append({
                    "x": self.bull_x - 30,
                    "y": gallop_y + 35,
                    "r": 5.0,
                    "max_r": 90.0,
                    "spd": 7.0,
                    "tag": self.canvas.create_oval(0, 0, 0, 0, outline="#ffd700", width=2)
                })
        else:
            self.shake_y = 0.0

        # Update hoof stomp rings
        for hr in list(self.hoof_rings):
            hr["r"] += hr["spd"] * dt_scale
            r = hr["r"]
            if r >= hr["max_r"]:
                self.canvas.delete(hr["tag"])
                self.hoof_rings.remove(hr)
            else:
                self.canvas.coords(hr["tag"], hr["x"] - r, hr["y"] - r * 0.5, hr["x"] + r, hr["y"] + r * 0.5)

        # Update Motion Blur Trailing Echoes
        self.canvas.coords(self.bull_echoes[0], self.bull_x - 70, gallop_y + self.shake_y)
        self.canvas.coords(self.bull_echoes[1], self.bull_x - 35, gallop_y + self.shake_y)
        self.canvas.coords(self.bull_echoes[2], self.bull_x, gallop_y + self.shake_y)

        # Update Twin Laser Eyes
        eye_x = self.bull_x + 42
        eye_y = gallop_y - 12 + self.shake_y
        laser_target_y = gallop_y + random.uniform(-60, 60)
        self.canvas.coords(self.laser_line1, eye_x, eye_y, w, laser_target_y)
        self.canvas.coords(self.laser_line2, eye_x, eye_y - 3, w, laser_target_y - 3)

        # Update Bouncing Coin & Bullion Cascade
        for p in self.particles:
            p["x"] += p["vx"] * dt_scale
            p["y"] += p["vy"] * dt_scale
            p["vy"] += 0.35 * dt_scale  # gravity

            # Floor Bounce Physics
            if p["y"] > p["bounce_floor"]:
                p["y"] = p["bounce_floor"]
                p["vy"] = -abs(p["vy"]) * 0.65
                p["vx"] *= 0.85
                # Respawn if coin lost all velocity
                if abs(p["vy"]) < 1.5:
                    p["y"] = random.uniform(-100, -20)
                    p["x"] = random.uniform(30, w - 30)
                    p["vy"] = random.uniform(6.0, 14.0)
                    p["vx"] = random.uniform(-3.5, 3.5)

            if p["tag"] is None:
                p["tag"] = self.canvas.create_text(p["x"], p["y"], text=p["char"], font=("Segoe UI", p["size"]))
            else:
                self.canvas.coords(p["tag"], p["x"], p["y"])

    # =========================================================================
    # MAIN 60 FPS DELTA-TIME TICK LOOP
    # =========================================================================
    def _tick(self):
        if self._stopped:
            return

        now = time.perf_counter()
        dt = min(now - self._last_time, 0.05)
        self._last_time = now
        self.elapsed_time += dt
        self.frame_count += 1
        dt_scale = dt * 60.0  # normalized to 1.0 at 60 FPS

        w, h = self.w, self.h

        try:
            if self.animation_id == "rocket_moon":
                self._tick_rocket(w, h, dt_scale)
            elif self.animation_id == "matrix_glitch":
                self._tick_matrix(w, h, dt_scale)
            elif self.animation_id == "diamond_hands":
                self._tick_diamond_hands(w, h, dt_scale)
            elif self.animation_id == "golden_bull":
                self._tick_golden_bull(w, h, dt_scale)
            else:
                self._tick_money_rain(w, h, dt_scale)
        except Exception:
            # Shield tick from canvas errors if widget destroyed mid-render
            self.stop()
            return

        # Check duration
        if self.elapsed_time >= self.max_duration:
            self.stop()
        else:
            # Target 60 FPS (~16.6ms) with processing compensation
            proc_time = time.perf_counter() - now
            interval = max(1, int((0.0166 - proc_time) * 1000))
            self._anim_job = self.canvas.after(interval, self._tick)

    def stop(self):
        """Safely terminates animation, destroys overlay canvas, and executes on_finished callback."""
        if self._stopped:
            return
        self._stopped = True

        if self._anim_job:
            try:
                self.canvas.after_cancel(self._anim_job)
            except Exception:
                pass
            self._anim_job = None

        try:
            if hasattr(self, "_esc_bind"):
                self.parent.unbind("<Escape>", self._esc_bind)
        except Exception:
            pass

        try:
            self.canvas.destroy()
        except Exception:
            pass

        if self.on_finished:
            cb = self.on_finished
            self.on_finished = None
            try:
                cb()
            except Exception:
                pass


def play_win_animation(
    parent: tk.Widget,
    animation_id: Optional[str] = None,
    on_finished: Optional[Callable[[], None]] = None,
    profit_info: Optional[Dict[str, Any]] = None
) -> WinAnimationOverlay:
    """Helper function to play currently equipped or specified crazy win animation."""
    from profile_manager import get_profile
    if not animation_id:
        animation_id = get_profile().equipped_animation
    return WinAnimationOverlay(
        parent,
        animation_id=animation_id,
        on_finished=on_finished,
        profit_info=profit_info
    )
