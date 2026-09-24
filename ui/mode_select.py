import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import random
from typing import Callable, Optional, Dict, Any
from network.firebase_manager import FirebaseManager
from version import __version__
from network.updater import check_for_update, UpdateDialog
from profile_manager import get_profile
from ui.shop_dialog import ShopDialog

class FirebaseConfigDialog(tk.Toplevel):
    """Dialog allowing user to view and paste Firebase API Key and Project ID."""
    def __init__(self, parent, manager: FirebaseManager, on_saved: Optional[Callable[[], None]] = None):
        super().__init__(parent)
        self.title("Firebase Configuration")
        self.geometry("540x380")
        self.resizable(False, False)
        self.configure(bg="#0e1117")
        self.transient(parent)
        self.grab_set()

        self.manager = manager
        self.on_saved = on_saved

        # Center on parent
        self.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        self.geometry(f"+{px + (pw - 540)//2}+{py + (ph - 380)//2}")

        self._build_ui()

    def _build_ui(self):
        tk.Label(
            self,
            text="🔥 Firebase Cloud Configuration",
            font=("Segoe UI", 14, "bold"),
            fg="#ffffff",
            bg="#0e1117"
        ).pack(pady=(20, 4))

        tk.Label(
            self,
            text="Paste your Web API Key & Project ID from the Firebase Console.\nIf left as default, simulated matchmaking bots are used.",
            font=("Segoe UI", 9),
            fg="#848e9c",
            bg="#0e1117",
            justify=tk.CENTER
        ).pack(pady=(0, 15))

        f = tk.Frame(self, bg="#161a25", padx=20, pady=15, bd=1, relief=tk.SOLID)
        f.pack(fill=tk.X, padx=25)

        # API Key
        tk.Label(f, text="Web API Key (apiKey):", font=("Segoe UI", 9, "bold"), fg="#c5c8d1", bg="#161a25").pack(anchor="w")
        self.ent_key = tk.Entry(f, font=("Segoe UI", 9), bg="#0e1117", fg="#ffffff", insertbackground="#ffffff", relief=tk.FLAT)
        self.ent_key.pack(fill=tk.X, pady=(2, 10), ipady=3)
        self.ent_key.insert(0, self.manager.api_key)

        # Project ID
        tk.Label(f, text="Project ID (projectId):", font=("Segoe UI", 9, "bold"), fg="#c5c8d1", bg="#161a25").pack(anchor="w")
        self.ent_pid = tk.Entry(f, font=("Segoe UI", 9), bg="#0e1117", fg="#ffffff", insertbackground="#ffffff", relief=tk.FLAT)
        self.ent_pid.pack(fill=tk.X, pady=(2, 10), ipady=3)
        self.ent_pid.insert(0, self.manager.project_id)

        # Status indicator
        cfg_status = "✅ Configured for Firebase Online" if self.manager.is_configured else "ℹ️ Currently using offline bot matchmaker"
        cfg_color = "#00e676" if self.manager.is_configured else "#f5c518"
        self.lbl_status = tk.Label(self, text=cfg_status, font=("Segoe UI", 9, "bold"), fg=cfg_color, bg="#0e1117")
        self.lbl_status.pack(pady=10)

        # Buttons
        btn_f = tk.Frame(self, bg="#0e1117")
        btn_f.pack(pady=10)

        btn_save = tk.Button(
            btn_f,
            text="Save Settings",
            font=("Segoe UI", 9, "bold"),
            bg="#2962ff",
            fg="#ffffff",
            activebackground="#3d72ff",
            relief=tk.FLAT,
            padx=14, pady=5,
            cursor="hand2",
            command=self._save
        )
        btn_save.pack(side=tk.LEFT, padx=6)

        btn_close = tk.Button(
            btn_f,
            text="Cancel",
            font=("Segoe UI", 9),
            bg="#222631",
            fg="#848e9c",
            relief=tk.FLAT,
            padx=10, pady=5,
            cursor="hand2",
            command=self.destroy
        )
        btn_close.pack(side=tk.LEFT, padx=6)

    def _save(self):
        k = self.ent_key.get().strip()
        p = self.ent_pid.get().strip()
        self.manager.save_config(k, p)
        messagebox.showinfo("Saved", "Firebase settings saved successfully!")
        if self.on_saved:
            self.on_saved()
        self.destroy()


_HAS_PROMPTED_UPDATE_SESSION = False


class ModeSelectWindow(tk.Tk):
    """
    Startup Launcher window where user selects between Solo Sandbox and 1v1 Online PvP Duel.
    """
    THEME_BG = "#0e1117"
    CARD_BG = "#161a25"
    BORDER_COLOR = "#2a2e39"
    GREEN = "#00e676"
    BLUE = "#2962ff"
    TEXT_MUTED = "#848e9c"

    def __init__(self, on_start_solo: Callable[[], None], on_start_online: Callable[[Dict[str, Any], FirebaseManager], None]):
        super().__init__()
        self.title("⚡ DAY TRADE SIMULATOR • SELECT GAME MODE")
        self.geometry("860x580")
        self.resizable(False, False)
        self.configure(bg=self.THEME_BG)

        self.on_start_solo = on_start_solo
        self.on_start_online = on_start_online

        self.profile = get_profile()
        self.fb_manager = FirebaseManager()
        self._cancel_search = threading.Event()
        self._search_thread: Optional[threading.Thread] = None
        self._latest_update_info: Optional[Dict[str, Any]] = None
        self._update_dialog: Optional[UpdateDialog] = None

        self._center_window()
        self._build_ui()

        # Automatically look for updates when the app is launched
        self._update_job = self.after(800, self._check_updates_on_launch)

    def destroy(self):
        if getattr(self, "_update_job", None):
            try:
                self.after_cancel(self._update_job)
            except Exception:
                pass
            self._update_job = None
        super().destroy()

    def _center_window(self):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - 860) // 2
        y = (sh - 580) // 2
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        # 1. Header Banner
        header_f = tk.Frame(self, bg=self.THEME_BG)
        header_f.pack(fill=tk.X, pady=(20, 8))

        tk.Label(
            header_f,
            text="⚡ DAY TRADE SIMULATOR",
            font=("Segoe UI", 22, "bold"),
            fg=self.GREEN,
            bg=self.THEME_BG
        ).pack()

        tk.Label(
            header_f,
            text=f"CHOOSE YOUR SIMULATION MODE  •  v{__version__}",
            font=("Segoe UI", 10, "bold"),
            fg=self.TEXT_MUTED,
            bg=self.THEME_BG
        ).pack(pady=(2, 0))

        # Vault Balance & Shop Bar in Menu
        vault_f = tk.Frame(header_f, bg=self.CARD_BG, bd=1, relief=tk.SOLID, padx=16, pady=6)
        vault_f.pack(pady=(10, 0))

        tk.Label(
            vault_f,
            text="💰 MENU VAULT BALANCE:",
            font=("Segoe UI", 9, "bold"),
            fg=self.TEXT_MUTED,
            bg=self.CARD_BG
        ).pack(side=tk.LEFT, padx=(0, 6))

        self.lbl_vault_balance = tk.Label(
            vault_f,
            text=f"${self.profile.menu_balance:,.2f}",
            font=("Segoe UI", 12, "bold"),
            fg=self.GREEN,
            bg=self.CARD_BG
        )
        self.lbl_vault_balance.pack(side=tk.LEFT, padx=(0, 15))

        self.btn_open_shop = tk.Button(
            vault_f,
            text="🛒 Trader Shop",
            font=("Segoe UI", 9, "bold"),
            bg="#2962ff",
            fg="#ffffff",
            activebackground="#3d72ff",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=10, pady=2,
            cursor="hand2",
            command=self._open_shop
        )
        self.btn_open_shop.pack(side=tk.LEFT)

        # Top-Right Control Bar (Check for Updates & Firebase Config)
        top_ctrls = tk.Frame(self, bg=self.THEME_BG)
        top_ctrls.place(relx=1.0, y=18, anchor="ne", x=-25)

        self.btn_top_shop = tk.Button(
            top_ctrls,
            text="🛒 Shop",
            font=("Segoe UI", 8, "bold"),
            bg="#1e222d",
            fg="#ffd700",
            activebackground="#2a2e39",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=8, pady=3,
            cursor="hand2",
            command=self._open_shop
        )
        self.btn_top_shop.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_update = tk.Button(
            top_ctrls,
            text="🔄 Check for Updates",
            font=("Segoe UI", 8),
            bg="#1e222d",
            fg=self.TEXT_MUTED,
            activebackground="#2a2e39",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=8, pady=3,
            cursor="hand2",
            command=self._on_check_updates_click
        )
        self.btn_update.pack(side=tk.LEFT, padx=(0, 6))

        btn_cfg = tk.Button(
            top_ctrls,
            text="⚙️ Firebase Config",
            font=("Segoe UI", 8),
            bg="#1e222d",
            fg=self.TEXT_MUTED,
            activebackground="#2a2e39",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=8, pady=3,
            cursor="hand2",
            command=self._open_config_dialog
        )
        btn_cfg.pack(side=tk.LEFT)

        # 2. Dual Selection Cards Container
        cards_f = tk.Frame(self, bg=self.THEME_BG)
        cards_f.pack(fill=tk.BOTH, expand=True, padx=40, pady=15)

        # --- LEFT CARD: SOLO MODE ---
        solo_card = tk.Frame(cards_f, bg=self.CARD_BG, bd=1, relief=tk.SOLID, padx=22, pady=20)
        solo_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))

        tk.Label(
            solo_card,
            text="🎯 SOLO SANDBOX",
            font=("Segoe UI", 15, "bold"),
            fg="#ffffff",
            bg=self.CARD_BG
        ).pack(anchor="w", pady=(0, 5))

        tk.Label(
            solo_card,
            text="Practice trading high-volatility equities with zero pressure. Test custom hotkeys and master candlestick patterns.",
            font=("Segoe UI", 9),
            fg=self.TEXT_MUTED,
            bg=self.CARD_BG,
            wraplength=320,
            justify=tk.LEFT
        ).pack(anchor="w", pady=(0, 15))

        # Bullet points
        bullets = [
            "✔ Multi-speed difficulty (1x to 20x Turbo)",
            "✔ Pause and resume simulation anytime",
            "✔ 100 volatile stocks & breaking news feed",
            "✔ Instant account reset & unlimited practice"
        ]
        for b in bullets:
            tk.Label(solo_card, text=b, font=("Segoe UI", 9), fg="#c5c8d1", bg=self.CARD_BG).pack(anchor="w", pady=2)

        # Solo launch button
        btn_solo = tk.Button(
            solo_card,
            text="▶ Play Solo Sandbox",
            font=("Segoe UI", 11, "bold"),
            bg="#1e88e5",
            fg="#ffffff",
            activebackground="#2196f3",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=18, pady=10,
            cursor="hand2",
            command=self._launch_solo
        )
        btn_solo.pack(side=tk.BOTTOM, fill=tk.X, pady=(15, 0))

        # --- RIGHT CARD: 1V1 ONLINE DUEL (OMEGLE-STYLE) ---
        online_card = tk.Frame(cards_f, bg=self.CARD_BG, bd=1, relief=tk.SOLID, padx=22, pady=20)
        online_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(15, 0))

        tk.Label(
            online_card,
            text="⚔️ 1v1 ONLINE DUEL",
            font=("Segoe UI", 15, "bold"),
            fg="#ff5252",
            bg=self.CARD_BG
        ).pack(anchor="w", pady=(0, 5))

        tk.Label(
            online_card,
            text="Omegle-style pairing with live traders! Both compete on identical charts in a 3-minute blitz. Out-earn your rival!",
            font=("Segoe UI", 9),
            fg=self.TEXT_MUTED,
            bg=self.CARD_BG,
            wraplength=320,
            justify=tk.LEFT
        ).pack(anchor="w", pady=(0, 15))

        # Online bullets
        bullets_online = [
            "✔ Synchronized live market & breaking news",
            "✔ Real-time Opponent Equity HUD & lead tracker",
            "✔ 3-Minute High-Stakes Blitz Duels",
            "✔ Omegle 'Next' skip to instant re-pair"
        ]
        for b in bullets_online:
            tk.Label(online_card, text=b, font=("Segoe UI", 9), fg="#c5c8d1", bg=self.CARD_BG).pack(anchor="w", pady=2)

        # Trader Name Entry
        name_f = tk.Frame(online_card, bg=self.CARD_BG)
        name_f.pack(fill=tk.X, pady=(12, 5))

        tk.Label(name_f, text="Trader Nickname:", font=("Segoe UI", 9, "bold"), fg=self.TEXT_MUTED, bg=self.CARD_BG).pack(anchor="w")
        self.ent_nickname = tk.Entry(name_f, font=("Segoe UI", 10), bg="#0e1117", fg="#00e676", insertbackground="#ffffff", relief=tk.FLAT)
        self.ent_nickname.pack(fill=tk.X, pady=(3, 0), ipady=3)
        self.ent_nickname.insert(0, f"Trader_{random.randint(100, 999)}")

        # Search / Matchmaking Status Area
        self.status_f = tk.Frame(online_card, bg=self.CARD_BG)
        self.status_f.pack(fill=tk.X, pady=(10, 0))

        self.lbl_queue_status = tk.Label(
            self.status_f,
            text="Ready to queue.",
            font=("Segoe UI", 9),
            fg=self.TEXT_MUTED,
            bg=self.CARD_BG
        )
        self.lbl_queue_status.pack()

        # Online launch button
        self.btn_online = tk.Button(
            online_card,
            text="🔍 Find 1v1 Opponent (Pair Now)",
            font=("Segoe UI", 11, "bold"),
            bg="#00c853",
            fg="#ffffff",
            activebackground="#00e676",
            activeforeground="#000000",
            relief=tk.FLAT,
            padx=18, pady=10,
            cursor="hand2",
            command=self._start_matchmaking
        )
        self.btn_online.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        self.btn_cancel = tk.Button(
            online_card,
            text="Cancel Search",
            font=("Segoe UI", 9),
            bg="#2a2e39",
            fg="#ff5252",
            relief=tk.FLAT,
            padx=10, pady=4,
            cursor="hand2",
            command=self._cancel_matchmaking
        )

        # 3. Footer indicator
        self._update_footer_status()

    def _update_footer_status(self):
        backend_str = "🔥 Firebase Cloud Connected" if self.fb_manager.is_configured else "🤖 Offline Bot Mode (Add Firebase in config to enable global online)"
        backend_color = "#00e676" if self.fb_manager.is_configured else "#f5c518"
        if not hasattr(self, "lbl_footer"):
            self.lbl_footer = tk.Label(self, text=backend_str, font=("Segoe UI", 8), fg=backend_color, bg=self.THEME_BG)
            self.lbl_footer.pack(side=tk.BOTTOM, pady=8)
        else:
            self.lbl_footer.config(text=backend_str, fg=backend_color)

    def _open_config_dialog(self):
        FirebaseConfigDialog(self, self.fb_manager, on_saved=self._update_footer_status)

    def _open_shop(self):
        ShopDialog(self, on_profile_updated=self._update_vault_display)

    def _update_vault_display(self):
        self.lbl_vault_balance.config(text=f"${self.profile.menu_balance:,.2f}")

    def _launch_solo(self):
        self.destroy()
        self.on_start_solo()

    def _start_matchmaking(self):
        nickname = self.ent_nickname.get().strip() or f"Trader_{random.randint(100, 999)}"
        self.btn_online.pack_forget()
        self.btn_cancel.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        self.lbl_queue_status.config(text="📡 Authenticating trader session...", fg="#2962ff")
        self._cancel_search.clear()

        def worker():
            ok, msg = self.fb_manager.sign_in_anonymous(nickname)
            if not ok:
                self.after(0, lambda: self._on_match_error(msg))
                return

            self.after(0, lambda: self.lbl_queue_status.config(text="🔍 Searching for live opponent (Omegle queue)...", fg="#00e676"))
            match_data = self.fb_manager.find_match(self._cancel_search, display_name=nickname)

            if self._cancel_search.is_set():
                return

            if match_data:
                self.after(0, lambda: self._on_match_found(match_data))
            else:
                self.after(0, lambda: self._on_match_timeout())

        self._search_thread = threading.Thread(target=worker, daemon=True)
        self._search_thread.start()

    def _cancel_matchmaking(self):
        self._cancel_search.set()
        self.btn_cancel.pack_forget()
        self.btn_online.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        self.lbl_queue_status.config(text="Search cancelled.", fg=self.TEXT_MUTED)

    def _on_match_error(self, err_msg: str):
        self._cancel_matchmaking()
        messagebox.showerror("Connection Error", f"Unable to authenticate:\n{err_msg}")

    def _on_match_timeout(self):
        self._cancel_matchmaking()
        messagebox.showinfo("Queue Timeout", "No opponent was found in the queue. You can retry or play in Solo mode!")

    def _on_match_found(self, match_data: Dict[str, Any]):
        opp_name = match_data.get("opponent", {}).get("name", "Opponent")
        self.lbl_queue_status.config(text=f"🎯 MATCHED WITH {opp_name}! Launching...", fg="#00e676")
        self.after(600, lambda: self._launch_online(match_data))

    def _launch_online(self, match_data: Dict[str, Any]):
        self.destroy()
        self.on_start_online(match_data, self.fb_manager)

    def _on_check_updates_click(self):
        """User clicked 'Check for Updates' button."""
        if self._latest_update_info and self._latest_update_info.get("update_available"):
            if not (self._update_dialog and self._update_dialog.winfo_exists()):
                self._update_dialog = UpdateDialog(self, self._latest_update_info)
            return

        self.btn_update.config(text="⏳ Checking...", state=tk.DISABLED)

        def worker():
            res = check_for_update(current_version=__version__)
            try:
                self.after(0, lambda: self._handle_update_check_result(res, user_initiated=True))
            except Exception:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def _check_updates_on_launch(self):
        """
        Automatically looks for updates when the app is launched.
        Runs asynchronously in the background. If an update is available,
        automatically prompts the user with the UpdateDialog.
        """
        global _HAS_PROMPTED_UPDATE_SESSION
        try:
            if not self.winfo_exists():
                return
        except Exception:
            return

        try:
            self.btn_update.config(text="🔄 Checking updates...")
        except Exception:
            pass

        def worker():
            try:
                res = check_for_update(current_version=__version__)
                should_prompt = not _HAS_PROMPTED_UPDATE_SESSION
                self.after(0, lambda: self._handle_update_check_result(
                    res, user_initiated=False, auto_prompt=should_prompt
                ))
            except Exception:
                try:
                    self.after(0, lambda: self.btn_update.config(
                        text="🔄 Check for Updates", bg="#1e222d", fg=self.TEXT_MUTED
                    ))
                except Exception:
                    pass

        threading.Thread(target=worker, daemon=True).start()

    def _handle_update_check_result(self, res: Dict[str, Any], user_initiated: bool = False, auto_prompt: bool = False):
        global _HAS_PROMPTED_UPDATE_SESSION
        if not self.winfo_exists():
            return

        self.btn_update.config(state=tk.NORMAL)
        if res.get("update_available"):
            self._latest_update_info = res
            v_latest = res.get("latest_version", "")
            self.btn_update.config(
                text=f"🚀 Update Ready (v{v_latest})",
                bg="#00c853",
                fg="#ffffff",
                activebackground="#00e676",
                activeforeground="#000000"
            )

            is_queueing = bool(self._search_thread and self._search_thread.is_alive())
            already_open = bool(self._update_dialog is not None and self._update_dialog.winfo_exists())

            if (user_initiated or auto_prompt) and not is_queueing and not already_open:
                _HAS_PROMPTED_UPDATE_SESSION = True
                self._update_dialog = UpdateDialog(self, res)
        else:
            self.btn_update.config(text="🔄 Check for Updates", bg="#1e222d", fg=self.TEXT_MUTED)
            if user_initiated:
                if "error" in res:
                    messagebox.showerror(
                        "Update Check",
                        f"Could not check for updates:\n{res['error']}\n\nPlease check your internet connection."
                    )
                else:
                    messagebox.showinfo(
                        "You're Up to Date!",
                        f"Day Trading Simulator v{__version__} is currently the newest version available."
                    )
