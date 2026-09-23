import tkinter as tk
from tkinter import ttk, messagebox
import time
from typing import Optional, Callable, Dict, Any

class BattleHUD(tk.Frame):
    """
    Top-of-screen competitive HUD for 1v1 online matches.
    Displays synchronized round timer, live leader indicator, opponent equity,
    and Omegle-style 'Next Opponent' skip button.
    """
    THEME_BG = "#131722"
    ACCENT_BLUE = "#2962ff"
    GREEN = "#089981"
    RED = "#f23645"
    GOLD = "#f5c518"
    TEXT_MUTED = "#848e9c"

    def __init__(
        self,
        parent,
        my_name: str,
        opponent_name: str,
        round_duration: int = 180,
        start_time: Optional[float] = None,
        on_next_opponent: Optional[Callable[[], None]] = None,
        on_leave_battle: Optional[Callable[[], None]] = None
    ):
        super().__init__(parent, bg=self.THEME_BG, bd=1, relief=tk.SOLID, height=68)
        self.pack_propagate(False)

        self.my_name = my_name
        self.opponent_name = opponent_name
        self.round_duration = round_duration
        self.start_time = start_time or time.time()
        self.on_next_opponent = on_next_opponent
        self.on_leave_battle = on_leave_battle

        self.my_equity = 25000.0
        self.my_pnl = 0.0
        self.my_pnl_pct = 0.0

        self.opp_equity = 25000.0
        self.opp_pnl = 0.0
        self.opp_pnl_pct = 0.0
        self.opp_status = "Trading"

        self.is_match_ended = False

        self._build_ui()

    def _build_ui(self):
        # 1. Left: YOU Box
        left_f = tk.Frame(self, bg=self.THEME_BG)
        left_f.pack(side=tk.LEFT, padx=(18, 10), pady=6)

        lbl_you_tag = tk.Label(left_f, text=f"YOU ({self.my_name})", font=("Segoe UI", 8, "bold"), fg=self.ACCENT_BLUE, bg=self.THEME_BG)
        lbl_you_tag.pack(anchor="w")

        self.lbl_my_score = tk.Label(left_f, text="$25,000.00 (+0.00%)", font=("Segoe UI", 12, "bold"), fg="#ffffff", bg=self.THEME_BG)
        self.lbl_my_score.pack(anchor="w")

        # 2. Center: VS, LEADER BADGE, and COUNTDOWN TIMER
        center_f = tk.Frame(self, bg=self.THEME_BG)
        center_f.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, pady=4)

        # Leader badge
        self.lbl_leader = tk.Label(
            center_f,
            text="⚔️ 1v1 MATCH STARTED • EVEN",
            font=("Segoe UI", 10, "bold"),
            fg=self.GOLD,
            bg=self.THEME_BG
        )
        self.lbl_leader.pack(anchor="center", pady=(2, 0))

        # Timer cluster
        time_f = tk.Frame(center_f, bg=self.THEME_BG)
        time_f.pack(anchor="center")

        tk.Label(time_f, text="TIME REMAINING: ", font=("Segoe UI", 8, "bold"), fg=self.TEXT_MUTED, bg=self.THEME_BG).pack(side=tk.LEFT)
        self.lbl_timer = tk.Label(time_f, text="03:00", font=("Consolas", 12, "bold"), fg="#ffffff", bg=self.THEME_BG)
        self.lbl_timer.pack(side=tk.LEFT)

        # 3. Right: OPPONENT Box & Omegle Controls
        right_f = tk.Frame(self, bg=self.THEME_BG)
        right_f.pack(side=tk.RIGHT, padx=(10, 18), pady=6)

        # Control buttons
        btn_f = tk.Frame(right_f, bg=self.THEME_BG)
        btn_f.pack(side=tk.RIGHT, padx=(15, 0))

        # Omegle Next button
        self.btn_next = tk.Button(
            btn_f,
            text="⏭ Next Opponent",
            font=("Segoe UI", 9, "bold"),
            bg="#d83a56",
            fg="#ffffff",
            activebackground="#ff4d6d",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=10,
            pady=3,
            cursor="hand2",
            command=self._confirm_next_opponent
        )
        self.btn_next.pack(side=tk.TOP, pady=1)

        btn_leave = tk.Button(
            btn_f,
            text="Leave Battle",
            font=("Segoe UI", 7),
            bg="#222631",
            fg=self.TEXT_MUTED,
            activebackground="#323846",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=6,
            pady=1,
            cursor="hand2",
            command=self._confirm_leave
        )
        btn_leave.pack(side=tk.TOP, pady=1)

        # Opponent score
        opp_score_f = tk.Frame(right_f, bg=self.THEME_BG)
        opp_score_f.pack(side=tk.RIGHT, padx=5)

        self.lbl_opp_tag = tk.Label(
            opp_score_f,
            text=f"OPPONENT ({self.opponent_name})",
            font=("Segoe UI", 8, "bold"),
            fg="#ff5252",
            bg=self.THEME_BG
        )
        self.lbl_opp_tag.pack(anchor="e")

        self.lbl_opp_score = tk.Label(
            opp_score_f,
            text="$25,000.00 (+0.00%)",
            font=("Segoe UI", 12, "bold"),
            fg="#ffffff",
            bg=self.THEME_BG
        )
        self.lbl_opp_score.pack(anchor="e")

    def update_scores(self, my_equity: float, my_pnl: float, my_pnl_pct: float, opp_data: Optional[Dict[str, Any]] = None):
        """Update live scores and leader status."""
        self.my_equity = my_equity
        self.my_pnl = my_pnl
        self.my_pnl_pct = my_pnl_pct

        # My score display
        c_my = self.GREEN if my_pnl >= 0 else self.RED
        self.lbl_my_score.config(
            text=f"${my_equity:,.2f} ({'+' if my_pnl_pct >= 0 else ''}{my_pnl_pct:.2f}%)",
            fg=c_my
        )

        if opp_data:
            self.opp_equity = opp_data.get("equity", self.opp_equity)
            self.opp_pnl = opp_data.get("pnl", self.opp_pnl)
            self.opp_pnl_pct = opp_data.get("pnl_pct", self.opp_pnl_pct)
            status = opp_data.get("status", "playing")
            if "name" in opp_data and opp_data["name"]:
                self.opponent_name = opp_data["name"]
                self.lbl_opp_tag.config(text=f"OPPONENT ({self.opponent_name})")

            c_opp = self.GREEN if self.opp_pnl >= 0 else self.RED
            status_text = " [FORFEITED]" if status == "forfeited" else ""
            self.lbl_opp_score.config(
                text=f"${self.opp_equity:,.2f} ({'+' if self.opp_pnl_pct >= 0 else ''}{self.opp_pnl_pct:.2f}%){status_text}",
                fg=c_opp
            )

        # Leader badge calculation
        diff = self.my_equity - self.opp_equity
        if abs(diff) < 1.0:
            self.lbl_leader.config(text="⚔️ 1v1 MATCH • EVEN TIE ($0.00)", fg=self.GOLD)
        elif diff > 0:
            self.lbl_leader.config(text=f"👑 YOU LEAD BY +${diff:,.2f}!", fg=self.GREEN)
        else:
            self.lbl_leader.config(text=f"⚠️ OPPONENT LEADS BY -${abs(diff):,.2f}!", fg=self.RED)

    def tick_timer(self) -> bool:
        """
        Updates remaining time. Returns True if time is still remaining, False if expired.
        """
        if self.is_match_ended:
            return False

        elapsed = time.time() - self.start_time
        remaining = max(0, int(self.round_duration - elapsed))

        mins = remaining // 60
        secs = remaining % 60
        self.lbl_timer.config(text=f"{mins:02d}:{secs:02d}")

        if remaining <= 10:
            self.lbl_timer.config(fg="#ff5252")
        else:
            self.lbl_timer.config(fg="#ffffff")

        if remaining <= 0:
            self.is_match_ended = True
            return False

        return True

    def _confirm_next_opponent(self):
        confirm = messagebox.askyesno(
            "Skip to Next Opponent",
            f"Skip current match against {self.opponent_name} and find a new opponent?\n(This will forfeit your current round)"
        )
        if confirm and self.on_next_opponent:
            self.on_next_opponent()

    def _confirm_leave(self):
        confirm = messagebox.askyesno(
            "Leave Battle",
            "Leave online duel and return to menu?"
        )
        if confirm and self.on_leave_battle:
            self.on_leave_battle()


class MatchEndDialog(tk.Toplevel):
    """
    Shows final victory/defeat results when 3-minute round expires.
    Offers instant 'Find Next Opponent' (Omegle style) or 'Back to Menu'.
    """
    def __init__(
        self,
        parent,
        my_equity: float,
        opp_equity: float,
        my_name: str,
        opp_name: str,
        on_next: Callable[[], None],
        on_menu: Callable[[], None]
    ):
        super().__init__(parent)
        self.title("⚡ MATCH RESULTS")
        self.geometry("480x360")
        self.resizable(False, False)
        self.configure(bg="#0e1117")
        self.transient(parent)
        self.grab_set()

        self.on_next = on_next
        self.on_menu = on_menu

        # Center on parent
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        x = px + (pw - 480) // 2
        y = py + (ph - 360) // 2
        self.geometry(f"+{x}+{y}")

        diff = my_equity - opp_equity
        if diff > 0.0:
            result_title = "🏆 VICTORY!"
            result_sub = f"You crushed {opp_name} by +${diff:,.2f}!"
            color = "#00e676"
        elif diff < 0.0:
            result_title = "💀 DEFEAT!"
            result_sub = f"{opp_name} made +${abs(diff):,.2f} more than you!"
            color = "#ff5252"
        else:
            result_title = "🤝 DRAW!"
            result_sub = "Both traders ended with identical equity!"
            color = "#f5c518"

        # Content
        tk.Label(self, text=result_title, font=("Segoe UI", 24, "bold"), fg=color, bg="#0e1117").pack(pady=(25, 5))
        tk.Label(self, text=result_sub, font=("Segoe UI", 11), fg="#c5c8d1", bg="#0e1117").pack(pady=(0, 20))

        # Stats frame
        card = tk.Frame(self, bg="#161a25", bd=1, relief=tk.SOLID, padx=20, pady=15)
        card.pack(fill=tk.X, padx=30, pady=5)

        def make_row(parent, label, val_you, val_opp):
            r = tk.Frame(parent, bg="#161a25")
            r.pack(fill=tk.X, pady=3)
            tk.Label(r, text=label, font=("Segoe UI", 9, "bold"), fg="#848e9c", bg="#161a25", width=14, anchor="w").pack(side=tk.LEFT)
            tk.Label(r, text=val_you, font=("Segoe UI", 10, "bold"), fg="#00e676" if "+" in val_you else "#ffffff", bg="#161a25", width=14, anchor="center").pack(side=tk.LEFT)
            tk.Label(r, text=val_opp, font=("Segoe UI", 10, "bold"), fg="#848e9c", bg="#161a25", width=14, anchor="e").pack(side=tk.RIGHT)

        make_row(card, "TRADER", f"YOU ({my_name})", opp_name)
        make_row(card, "FINAL EQUITY", f"${my_equity:,.2f}", f"${opp_equity:,.2f}")
        my_pnl_str = f"{'+' if my_equity >= 25000 else ''}${my_equity - 25000:,.2f}"
        opp_pnl_str = f"{'+' if opp_equity >= 25000 else ''}${opp_equity - 25000:,.2f}"
        make_row(card, "NET PROFIT", my_pnl_str, opp_pnl_str)

        # Buttons
        btn_f = tk.Frame(self, bg="#0e1117")
        btn_f.pack(pady=25)

        btn_next = tk.Button(
            btn_f,
            text="⏭ Find Next Opponent (Omegle)",
            font=("Segoe UI", 11, "bold"),
            bg="#2962ff",
            fg="#ffffff",
            activebackground="#3d72ff",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=16,
            pady=8,
            cursor="hand2",
            command=self._do_next
        )
        btn_next.pack(side=tk.LEFT, padx=8)

        btn_menu = tk.Button(
            btn_f,
            text="Main Menu",
            font=("Segoe UI", 10),
            bg="#222631",
            fg="#848e9c",
            activebackground="#323846",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=14,
            pady=8,
            cursor="hand2",
            command=self._do_menu
        )
        btn_menu.pack(side=tk.LEFT, padx=8)

    def _do_next(self):
        self.destroy()
        self.on_next()

    def _do_menu(self):
        self.destroy()
        self.on_menu()
