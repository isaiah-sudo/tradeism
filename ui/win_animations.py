"""
Crazy Win Animation Overlay Engine for Day Trading Simulator.
Renders high-intensity visual celebration effects on a transparent/dark overlay Canvas:
- Money Rain & Gold Confetti
- Rocket Blastoff To The Moon
- Cyber Matrix Glitch Rain
- Diamond Hands Supernova
- Golden Bull Stampede
"""

import tkinter as tk
import random
import math
import time
from typing import Optional, Callable, List, Dict, Any

class WinAnimationOverlay:
    """
    Renders high-octane celebration animations over any Tkinter window.
    """
    def __init__(self, parent: tk.Widget, animation_id: str = "money_rain", on_finished: Optional[Callable[[], None]] = None):
        self.parent = parent
        self.animation_id = animation_id
        self.on_finished = on_finished
        self.particles: List[Dict[str, Any]] = []
        self.frame_count = 0
        self.max_frames = 120  # ~4 seconds at 30ms/frame
        self._anim_job: Optional[str] = None

        self.w = max(parent.winfo_width(), 900)
        self.h = max(parent.winfo_height(), 600)

        # Create overlay canvas over entire parent window
        self.canvas = tk.Canvas(
            parent,
            bg="#06090e",
            highlightthickness=0,
            bd=0
        )
        self.canvas.place(x=0, y=0, relwidth=1.0, relheight=1.0)
        tk.Misc.lift(self.canvas)

        # Click to dismiss early
        self.canvas.bind("<Button-1>", lambda e: self.stop())
        self.parent.bind("<Escape>", lambda e: self.stop())

        # Close button in top-right
        self.btn_skip = tk.Button(
            self.canvas,
            text="✕ Close",
            font=("Segoe UI", 9, "bold"),
            bg="#222631",
            fg="#848e9c",
            activebackground="#ff5252",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=8, pady=2,
            cursor="hand2",
            command=self.stop
        )
        self.canvas.create_window(self.w - 50, 30, window=self.btn_skip)

        self._init_animation()
        self._tick()

    def _init_animation(self):
        w = self.canvas.winfo_width() or self.w
        h = self.canvas.winfo_height() or self.h

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

    # 1. Money Rain
    def _init_money_rain(self, w, h):
        emojis = ["💵", "💸", "💰", "$100", "🤑", "✨", "⭐", "🎉"]
        for _ in range(75):
            self.particles.append({
                "type": "rain",
                "x": random.uniform(20, w - 20),
                "y": random.uniform(-h * 0.8, -10),
                "vx": random.uniform(-1.5, 1.5),
                "vy": random.uniform(5.0, 12.0),
                "text": random.choice(emojis),
                "size": random.randint(14, 26),
                "color": random.choice(["#00e676", "#ffd700", "#ffffff", "#00ffcc"]),
                "wobble": random.uniform(0, math.pi * 2),
                "wobble_spd": random.uniform(0.08, 0.18)
            })

        self.banner_id = self.canvas.create_text(
            w // 2, h // 2,
            text="💸 CASH TSUNAMI! PROFIT LOCKED! 💸",
            font=("Segoe UI", 28, "bold"),
            fill="#00e676"
        )
        self.sub_id = self.canvas.create_text(
            w // 2, h // 2 + 50,
            text="PROFIT TRANSFERRED TO MENU VAULT",
            font=("Segoe UI", 13, "bold"),
            fill="#ffd700"
        )

    # 2. Rocket Moon
    def _init_rocket(self, w, h):
        self.rocket = {
            "x": w // 2,
            "y": h + 50,
            "vy": -14.0,
            "shake": 0
        }
        # Star field
        for _ in range(60):
            self.particles.append({
                "type": "star",
                "x": random.uniform(0, w),
                "y": random.uniform(0, h),
                "len": random.uniform(5, 25),
                "spd": random.uniform(10, 25)
            })
        # Moon
        self.moon_id = self.canvas.create_text(
            w // 2, 90,
            text="🌕",
            font=("Segoe UI", 60)
        )
        self.banner_id = self.canvas.create_text(
            w // 2, h // 2,
            text="🚀 TO THE MOON! 100x GAINS! 🚀",
            font=("Segoe UI", 30, "bold"),
            fill="#00e6ff"
        )

    # 3. Matrix Glitch
    def _init_matrix(self, w, h):
        cols = max(15, w // 35)
        chars = ["0", "1", "$", "WIN", "PROFIT", "BUY", "7F", "9A", "CALL", "MOON", "100K", "BULL"]
        for c in range(cols):
            self.particles.append({
                "type": "matrix_col",
                "x": c * 35 + 15,
                "y": random.uniform(-300, 0),
                "spd": random.uniform(10, 22),
                "chars": [random.choice(chars) for _ in range(12)],
                "color": random.choice(["#00ff66", "#00e676", "#39ff14", "#00ffff"])
            })
        self.banner_id = self.canvas.create_text(
            w // 2, h // 2,
            text="⚡ SYSTEM OVERRIDE: VICTORY PROTOCOL ⚡",
            font=("Consolas", 24, "bold"),
            fill="#00ff66"
        )

    # 4. Diamond Hands Supernova
    def _init_diamond_hands(self, w, h):
        self.dh_phase = 0
        self.dh_scale = 10
        self.center_x = w // 2
        self.center_y = h // 2 - 20

        self.dh_text_id = self.canvas.create_text(
            self.center_x, self.center_y,
            text="💎🙌💎",
            font=("Segoe UI", 48)
        )
        self.banner_id = self.canvas.create_text(
            self.center_x, self.center_y + 90,
            text="💎 DIAMOND HANDS SUPERNOVA! 💎",
            font=("Segoe UI", 26, "bold"),
            fill="#00e5ff"
        )

    # 5. Golden Bull Stampede
    def _init_golden_bull(self, w, h):
        self.bull_x = -150
        self.bull_y = h // 2
        self.bull_vx = 18.0

        for _ in range(50):
            self.particles.append({
                "type": "gold_coin",
                "x": random.uniform(50, w - 50),
                "y": random.uniform(-100, 0),
                "vx": random.uniform(-3, 3),
                "vy": random.uniform(6, 14),
                "text": random.choice(["🪙", "👑", "🥇", "💰", "✨"]),
                "size": random.randint(18, 28)
            })

        self.bull_id = self.canvas.create_text(
            self.bull_x, self.bull_y,
            text="👑 🐂 ⚡",
            font=("Segoe UI", 56)
        )
        self.banner_id = self.canvas.create_text(
            w // 2, 80,
            text="👑 WALL STREET WHALE: BULL STAMPEDE! 👑",
            font=("Segoe UI", 26, "bold"),
            fill="#ffd700"
        )

    def _tick(self):
        self.frame_count += 1
        w = self.canvas.winfo_width() or self.w
        h = self.canvas.winfo_height() or self.h

        if self.animation_id == "rocket_moon":
            self._tick_rocket(w, h)
        elif self.animation_id == "matrix_glitch":
            self._tick_matrix(w, h)
        elif self.animation_id == "diamond_hands":
            self._tick_diamond_hands(w, h)
        elif self.animation_id == "golden_bull":
            self._tick_golden_bull(w, h)
        else:
            self._tick_money_rain(w, h)

        if self.frame_count >= self.max_frames:
            self.stop()
        else:
            self._anim_job = self.canvas.after(30, self._tick)

    def _tick_money_rain(self, w, h):
        # Pulse banner color
        c = "#00e676" if (self.frame_count // 4) % 2 == 0 else "#ffd700"
        self.canvas.itemconfig(self.banner_id, fill=c)

        for p in self.particles:
            p["wobble"] += p["wobble_spd"]
            p["x"] += p["vx"] + math.sin(p["wobble"]) * 1.5
            p["y"] += p["vy"]

            if p["y"] > h + 20:
                p["y"] = random.uniform(-80, -10)
                p["x"] = random.uniform(20, w - 20)

            if "tag" not in p:
                p["tag"] = self.canvas.create_text(
                    p["x"], p["y"],
                    text=p["text"],
                    font=("Segoe UI", p["size"]),
                    fill=p["color"]
                )
            else:
                self.canvas.coords(p["tag"], p["x"], p["y"])

    def _tick_rocket(self, w, h):
        # Spawn flame/exhaust particles
        rx = self.rocket["x"]
        ry = self.rocket["y"]
        self.rocket["y"] += self.rocket["vy"]

        # Thruster fire
        for _ in range(3):
            self.particles.append({
                "type": "fire",
                "x": rx + random.uniform(-10, 10),
                "y": ry + 40,
                "vy": random.uniform(6, 12),
                "vx": random.uniform(-2, 2),
                "text": random.choice(["🔥", "💥", "✨"]),
                "size": random.randint(12, 20),
                "life": 20
            })

        # Rocket text tag
        if not hasattr(self, "rocket_tag"):
            self.rocket_tag = self.canvas.create_text(
                rx, ry,
                text="🚀",
                font=("Segoe UI", 52)
            )
        else:
            self.canvas.coords(self.rocket_tag, rx, ry)

        # Stars warp lines
        for p in list(self.particles):
            if p["type"] == "star":
                p["y"] += p["spd"]
                if p["y"] > h:
                    p["y"] = -10
                    p["x"] = random.uniform(0, w)
                if "line_tag" not in p:
                    p["line_tag"] = self.canvas.create_line(p["x"], p["y"], p["x"], p["y"] + p["len"], fill="#00e5ff", width=2)
                else:
                    self.canvas.coords(p["line_tag"], p["x"], p["y"], p["x"], p["y"] + p["len"])
            elif p["type"] == "fire":
                p["y"] += p["vy"]
                p["x"] += p["vx"]
                p["life"] -= 1
                if "tag" not in p:
                    p["tag"] = self.canvas.create_text(p["x"], p["y"], text=p["text"], font=("Segoe UI", p["size"]))
                else:
                    self.canvas.coords(p["tag"], p["x"], p["y"])
                if p["life"] <= 0:
                    self.canvas.delete(p["tag"])
                    self.particles.remove(p)

    def _tick_matrix(self, w, h):
        for p in self.particles:
            p["y"] += p["spd"]
            if p["y"] > h:
                p["y"] = random.uniform(-200, -20)
                p["x"] = (p["x"] + 15) % w

            # Update string display
            txt = "\n".join(p["chars"])
            if "tag" not in p:
                p["tag"] = self.canvas.create_text(
                    p["x"], p["y"],
                    text=txt,
                    font=("Consolas", 10, "bold"),
                    fill=p["color"],
                    anchor="n"
                )
            else:
                self.canvas.coords(p["tag"], p["x"], p["y"])

        # Glitch lines
        if random.random() < 0.35:
            gy = random.uniform(50, h - 50)
            gh = random.uniform(3, 12)
            gline = self.canvas.create_rectangle(0, gy, w, gy + gh, fill=random.choice(["#00e676", "#00e5ff", "#ff007f"]), outline="")
            self.canvas.after(50, lambda l=gline: self.canvas.delete(l))

    def _tick_diamond_hands(self, w, h):
        if self.frame_count < 30:
            # Scale up diamond hands
            sz = int(24 + self.frame_count * 1.5)
            self.canvas.itemconfig(self.dh_text_id, font=("Segoe UI", sz))
        elif self.frame_count == 30:
            # EXPLOSION!
            self.canvas.itemconfig(self.dh_text_id, text="💥 SUPERNOVA 💥")
            for _ in range(80):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(4, 18)
                self.particles.append({
                    "type": "shard",
                    "x": self.center_x,
                    "y": self.center_y,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "text": random.choice(["💎", "✨", "🔷", "💠", "⚡"]),
                    "size": random.randint(14, 28)
                })
        else:
            for p in list(self.particles):
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                p["vy"] += 0.2  # subtle gravity
                if "tag" not in p:
                    p["tag"] = self.canvas.create_text(p["x"], p["y"], text=p["text"], font=("Segoe UI", p["size"]))
                else:
                    self.canvas.coords(p["tag"], p["x"], p["y"])

    def _tick_golden_bull(self, w, h):
        self.bull_x += self.bull_vx
        if self.bull_x > w + 150:
            self.bull_x = -150

        # Shake ground
        shake_y = self.bull_y + (math.sin(self.frame_count * 0.8) * 6)
        self.canvas.coords(self.bull_id, self.bull_x, shake_y)

        # Bull laser eyes
        lx1, ly1 = self.bull_x + 30, shake_y - 10
        laser = self.canvas.create_line(lx1, ly1, w, ly1 + random.uniform(-40, 40), fill="#ff1744", width=3)
        self.canvas.after(35, lambda l=laser: self.canvas.delete(l))

        # Gold rain
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["y"] > h + 20:
                p["y"] = -20
                p["x"] = random.uniform(30, w - 30)

            if "tag" not in p:
                p["tag"] = self.canvas.create_text(p["x"], p["y"], text=p["text"], font=("Segoe UI", p["size"]))
            else:
                self.canvas.coords(p["tag"], p["x"], p["y"])

    def stop(self):
        if self._anim_job:
            try:
                self.canvas.after_cancel(self._anim_job)
            except Exception:
                pass
            self._anim_job = None

        try:
            self.canvas.destroy()
        except Exception:
            pass

        if self.on_finished:
            try:
                self.on_finished()
            except Exception:
                pass


def play_win_animation(parent: tk.Widget, animation_id: Optional[str] = None, on_finished: Optional[Callable[[], None]] = None) -> WinAnimationOverlay:
    """Helper function to play currently equipped or specified crazy win animation."""
    from profile_manager import get_profile
    if not animation_id:
        animation_id = get_profile().equipped_animation
    return WinAnimationOverlay(parent, animation_id=animation_id, on_finished=on_finished)
