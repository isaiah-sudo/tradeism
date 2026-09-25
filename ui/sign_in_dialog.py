"""
Sign In Dialog for Day Trading Simulator.
Supports Google Sign-In via browser OAuth and direct Email/Password sign-in/registration.
Synchronizes user progress (name, menu balance, shop items, animations) with Firebase Cloud.
"""

import sys
import webbrowser
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, Dict, Any

from profile_manager import get_profile, UserProfile
from network.firebase_manager import FirebaseManager
from network.auth_server import AuthCallbackServer


def is_web_environment() -> bool:
    """Detects whether running in a web assembly / browser Python runtime."""
    if sys.platform.startswith("emscripten") or sys.platform == "wasi":
        return True
    if "pyodide" in sys.modules:
        return True
    return False


class SignInDialog(tk.Toplevel):
    THEME_BG = "#0e1117"
    CARD_BG = "#161a25"
    BORDER_COLOR = "#2a2e39"
    TEXT_MUTED = "#848e9c"
    GREEN = "#00e676"
    BLUE = "#2962ff"
    RED = "#ff5252"

    def __init__(self, parent, fb_manager: FirebaseManager,
                 on_auth_changed: Optional[Callable[[], None]] = None):
        super().__init__(parent)
        self.fb_manager = fb_manager
        self.profile = get_profile()
        self.on_auth_changed = on_auth_changed

        self.title("⚡ DAY TRADE SIMULATOR • ACCOUNT SIGN IN")
        self.geometry("520x580")
        self.resizable(False, False)
        self.configure(bg=self.THEME_BG)
        self.transient(parent)
        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.auth_server: Optional[AuthCallbackServer] = None
        self.mode = "signin"  # "signin" or "signup"

        self._center_window(parent)
        self._build_ui()

        # If on desktop and not already signed in, start local server and open browser
        if not is_web_environment() and not self.profile.is_authenticated():
            self._start_browser_auth()

    def _center_window(self, parent):
        self.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        w, h = 520, 580
        x = px + max(0, (pw - w) // 2)
        y = py + max(0, (ph - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _on_close(self):
        if self.auth_server:
            try:
                self.auth_server.stop()
            except Exception:
                pass
            self.auth_server = None
        self.destroy()

    def _build_ui(self):
        # Clear any existing widgets
        for w in self.winfo_children():
            w.destroy()

        if self.profile.is_authenticated():
            self._build_authenticated_ui()
        else:
            self._build_unauthenticated_ui()

    def _build_authenticated_ui(self):
        """View displayed when the user is currently signed in."""
        hdr = tk.Frame(self, bg=self.THEME_BG, padx=25, pady=20)
        hdr.pack(fill=tk.X)

        tk.Label(
            hdr,
            text="👤 TRADER ACCOUNT",
            font=("Segoe UI", 18, "bold"),
            fg="#ffffff",
            bg=self.THEME_BG
        ).pack(anchor="w")

        tk.Label(
            hdr,
            text="Your progress is saved and automatically backed up to Firebase Cloud.",
            font=("Segoe UI", 9),
            fg=self.TEXT_MUTED,
            bg=self.THEME_BG
        ).pack(anchor="w", pady=(2, 0))

        # Profile Details Card
        card = tk.Frame(self, bg=self.CARD_BG, bd=1, relief=tk.SOLID, padx=20, pady=18)
        card.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 15))

        # Avatar & Nickname
        top_row = tk.Frame(card, bg=self.CARD_BG)
        top_row.pack(fill=tk.X, pady=(0, 15))

        tk.Label(top_row, text="👑", font=("Segoe UI", 28), bg=self.CARD_BG).pack(side=tk.LEFT, padx=(0, 12))
        info_sub = tk.Frame(top_row, bg=self.CARD_BG)
        info_sub.pack(side=tk.LEFT, fill=tk.Y)

        display_name = self.profile.player_name or self.profile.auth_display_name or "Trader"
        tk.Label(
            info_sub,
            text=display_name,
            font=("Segoe UI", 15, "bold"),
            fg=self.GREEN,
            bg=self.CARD_BG
        ).pack(anchor="w")

        email_str = self.profile.auth_email or "Signed in with Google"
        tk.Label(
            info_sub,
            text=email_str,
            font=("Segoe UI", 9),
            fg=self.TEXT_MUTED,
            bg=self.CARD_BG
        ).pack(anchor="w")

        # Status badge
        tk.Label(
            card,
            text="☁️ CLOUD SYNC ACTIVE  •  PROGRESS SAVED",
            font=("Segoe UI", 8, "bold"),
            fg=self.GREEN,
            bg="#0c2317",
            padx=10, pady=4
        ).pack(anchor="w", pady=(0, 15))

        # Stats Grid
        stats_f = tk.Frame(card, bg=self.CARD_BG)
        stats_f.pack(fill=tk.X, pady=(0, 15))

        stats = [
            ("💰 Menu Vault Balance:", f"${self.profile.menu_balance:,.2f}"),
            ("📈 Total Profit Banked:", f"${self.profile.total_profit_banked:,.2f}"),
            ("🎒 Shop Items Owned:", f"{len(self.profile.inventory)} items"),
            ("🏆 PvP Duels Won:", f"{self.profile.duels_won} wins"),
            ("✨ Equipped Animation:", self.profile.equipped_animation)
        ]

        for label_text, val_text in stats:
            row = tk.Frame(stats_f, bg=self.CARD_BG)
            row.pack(fill=tk.X, pady=3)
            tk.Label(row, text=label_text, font=("Segoe UI", 9), fg=self.TEXT_MUTED, bg=self.CARD_BG).pack(side=tk.LEFT)
            tk.Label(row, text=val_text, font=("Segoe UI", 9, "bold"), fg="#ffffff", bg=self.CARD_BG).pack(side=tk.RIGHT)

        # Action Buttons
        btn_box = tk.Frame(self, bg=self.THEME_BG, padx=25, pady=10)
        btn_box.pack(fill=tk.X, side=tk.BOTTOM)

        btn_sync = tk.Button(
            btn_box,
            text="🔄 Sync Cloud Now",
            font=("Segoe UI", 9, "bold"),
            bg="#1e222d",
            fg="#ffffff",
            activebackground="#2a2e39",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=14, pady=8,
            cursor="hand2",
            command=self._manual_sync_cloud
        )
        btn_sync.pack(side=tk.LEFT, padx=(0, 8))

        btn_sign_out = tk.Button(
            btn_box,
            text="🚪 Sign Out",
            font=("Segoe UI", 9, "bold"),
            bg="#ff5252",
            fg="#ffffff",
            activebackground="#ff7070",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=14, pady=8,
            cursor="hand2",
            command=self._handle_sign_out
        )
        btn_sign_out.pack(side=tk.LEFT)

        btn_close = tk.Button(
            btn_box,
            text="Close",
            font=("Segoe UI", 9),
            bg="#161a25",
            fg=self.TEXT_MUTED,
            relief=tk.FLAT,
            padx=14, pady=8,
            cursor="hand2",
            command=self._on_close
        )
        btn_close.pack(side=tk.RIGHT)

    def _build_unauthenticated_ui(self):
        """View displayed when the user is not signed in."""
        hdr = tk.Frame(self, bg=self.THEME_BG, padx=24, pady=16)
        hdr.pack(fill=tk.X)

        tk.Label(
            hdr,
            text="⚡ SIGN IN TO DAY TRADE SIM",
            font=("Segoe UI", 16, "bold"),
            fg="#ffffff",
            bg=self.THEME_BG
        ).pack(anchor="w")

        tk.Label(
            hdr,
            text="Sign in to save your trader name, menu balance, and shop purchases to the cloud!",
            font=("Segoe UI", 9),
            fg=self.TEXT_MUTED,
            bg=self.THEME_BG
        ).pack(anchor="w", pady=(2, 0))

        content_f = tk.Frame(self, bg=self.THEME_BG, padx=24)
        content_f.pack(fill=tk.BOTH, expand=True)

        # 1. Desktop Browser Sign-In Area (if not web)
        if not is_web_environment():
            browser_card = tk.Frame(content_f, bg=self.CARD_BG, bd=1, relief=tk.SOLID, padx=16, pady=12)
            browser_card.pack(fill=tk.X, pady=(0, 12))

            tk.Label(
                browser_card,
                text="🌐 BROWSER SIGN IN VIA TRADEISM.MEN",
                font=("Segoe UI", 9, "bold"),
                fg=self.GREEN,
                bg=self.CARD_BG
            ).pack(anchor="w")

            self.lbl_browser_status = tk.Label(
                browser_card,
                text="Opening tradeism.men in your browser. Sign in with Google or Email there!",
                font=("Segoe UI", 8),
                fg=self.TEXT_MUTED,
                bg=self.CARD_BG,
                wraplength=420,
                justify=tk.LEFT
            )
            self.lbl_browser_status.pack(anchor="w", pady=(3, 8))

            btn_reopen = tk.Button(
                browser_card,
                text="🔗 Open tradeism.men Sign-In Page",
                font=("Segoe UI", 9, "bold"),
                bg="#2962ff",
                fg="#ffffff",
                activebackground="#3d72ff",
                activeforeground="#ffffff",
                relief=tk.FLAT,
                padx=12, pady=5,
                cursor="hand2",
                command=self._start_browser_auth
            )
            btn_reopen.pack(anchor="w")

            # Divider
            div = tk.Frame(content_f, bg=self.THEME_BG)
            div.pack(fill=tk.X, pady=6)
            tk.Label(div, text="─── OR SIGN IN DIRECTLY IN APP ───", font=("Segoe UI", 8, "bold"), fg="#4f5869", bg=self.THEME_BG).pack()

        # 2. In-App Direct Email / Password Form
        form_card = tk.Frame(content_f, bg=self.CARD_BG, bd=1, relief=tk.SOLID, padx=18, pady=14)
        form_card.pack(fill=tk.BOTH, expand=True)

        # Tabs: Sign In / Create Account
        tabs_f = tk.Frame(form_card, bg="#0e1117", bd=1, relief=tk.SOLID)
        tabs_f.pack(fill=tk.X, pady=(0, 12))

        self.btn_tab_in = tk.Button(
            tabs_f, text="Sign In", font=("Segoe UI", 9, "bold"),
            bg="#2962ff", fg="#ffffff", relief=tk.FLAT,
            padx=12, pady=4, cursor="hand2",
            command=lambda: self._set_mode("signin")
        )
        self.btn_tab_in.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.btn_tab_up = tk.Button(
            tabs_f, text="Create Account", font=("Segoe UI", 9, "bold"),
            bg="#0e1117", fg=self.TEXT_MUTED, relief=tk.FLAT,
            padx=12, pady=4, cursor="hand2",
            command=lambda: self._set_mode("signup")
        )
        self.btn_tab_up.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Input fields
        self.f_nickname = tk.Frame(form_card, bg=self.CARD_BG)
        tk.Label(self.f_nickname, text="Trader Nickname:", font=("Segoe UI", 8, "bold"), fg=self.TEXT_MUTED, bg=self.CARD_BG).pack(anchor="w")
        self.ent_nick = tk.Entry(self.f_nickname, font=("Segoe UI", 9), bg="#0e1117", fg="#00e676", insertbackground="#ffffff", relief=tk.FLAT)
        self.ent_nick.pack(fill=tk.X, pady=(2, 6), ipady=3)
        current_name = self.profile.player_name or "Trader"
        self.ent_nick.insert(0, current_name)

        tk.Label(form_card, text="Email Address:", font=("Segoe UI", 8, "bold"), fg=self.TEXT_MUTED, bg=self.CARD_BG).pack(anchor="w")
        self.ent_email = tk.Entry(form_card, font=("Segoe UI", 9), bg="#0e1117", fg="#ffffff", insertbackground="#ffffff", relief=tk.FLAT)
        self.ent_email.pack(fill=tk.X, pady=(2, 8), ipady=3)

        tk.Label(form_card, text="Password:", font=("Segoe UI", 8, "bold"), fg=self.TEXT_MUTED, bg=self.CARD_BG).pack(anchor="w")
        self.ent_pass = tk.Entry(form_card, font=("Segoe UI", 9), bg="#0e1117", fg="#ffffff", insertbackground="#ffffff", show="•", relief=tk.FLAT)
        self.ent_pass.pack(fill=tk.X, pady=(2, 8), ipady=3)

        # Submit Button
        self.btn_submit = tk.Button(
            form_card,
            text="Sign In",
            font=("Segoe UI", 10, "bold"),
            bg="#00c853",
            fg="#ffffff",
            activebackground="#00e676",
            activeforeground="#000000",
            relief=tk.FLAT,
            pady=6,
            cursor="hand2",
            command=self._handle_in_app_submit
        )
        self.btn_submit.pack(fill=tk.X, pady=(4, 6))

        # Status Label
        self.lbl_status = tk.Label(
            form_card,
            text="",
            font=("Segoe UI", 8),
            fg=self.RED,
            bg=self.CARD_BG,
            wraplength=400
        )
        self.lbl_status.pack()

    def _set_mode(self, mode: str):
        self.mode = mode
        if mode == "signin":
            self.btn_tab_in.config(bg="#2962ff", fg="#ffffff")
            self.btn_tab_up.config(bg="#0e1117", fg=self.TEXT_MUTED)
            self.f_nickname.pack_forget()
            self.btn_submit.config(text="Sign In")
        else:
            self.btn_tab_up.config(bg="#2962ff", fg="#ffffff")
            self.btn_tab_in.config(bg="#0e1117", fg=self.TEXT_MUTED)
            self.f_nickname.pack(fill=tk.X, pady=(0, 6), before=self.ent_email)
            self.btn_submit.config(text="Create Account")
        self.lbl_status.config(text="")

    def _start_browser_auth(self):
        """Starts the local HTTP server and opens user's browser."""
        if self.auth_server:
            try:
                self.auth_server.stop()
            except Exception:
                pass

        def on_browser_success(auth_data: Dict[str, Any]):
            # Deliver to main thread
            self.after(0, lambda: self._on_auth_complete(auth_data))

        try:
            self.auth_server = AuthCallbackServer(
                api_key=self.fb_manager.api_key,
                project_id=self.fb_manager.project_id,
                auth_domain=self.fb_manager.auth_domain,
                on_success=on_browser_success
            )
            self.auth_server.start()
            login_url = self.auth_server.get_web_url()
            webbrowser.open(login_url)
            if hasattr(self, "lbl_browser_status") and self.lbl_browser_status:
                self.lbl_browser_status.config(
                    text=f"🟢 Opened tradeism.men in browser!\nSign in with Google or Email on tradeism.men to sync your account.",
                    fg="#29b6f6"
                )
        except Exception as e:
            print(f"[SignInDialog] Error launching browser auth: {e}")
            if hasattr(self, "lbl_browser_status") and self.lbl_browser_status:
                self.lbl_browser_status.config(
                    text="Could not launch browser automatically. You can sign in below directly.",
                    fg=self.RED
                )

    def _handle_in_app_submit(self):
        email = self.ent_email.get().strip()
        pwd = self.ent_pass.get()
        nick = getattr(self, "ent_nick", None)
        nickname = nick.get().strip() if nick else ""

        if not email or not pwd:
            self.lbl_status.config(text="Please enter both email and password.", fg=self.RED)
            return

        self.btn_submit.config(state=tk.DISABLED, text="Authenticating...")
        self.lbl_status.config(text="Contacting Firebase...", fg="#29b6f6")

        def worker():
            if self.mode == "signup":
                ok, msg = self.fb_manager.sign_up_email(email, pwd, nickname)
            else:
                ok, msg = self.fb_manager.sign_in_email(email, pwd, nickname)

            if ok:
                auth_payload = {
                    "uid": self.fb_manager.user_id,
                    "email": email,
                    "displayName": nickname or self.fb_manager.display_name,
                    "idToken": self.fb_manager.id_token,
                    "refreshToken": getattr(self.fb_manager, "refresh_token_str", "")
                }
                self.after(0, lambda: self._on_auth_complete(auth_payload))
            else:
                self.after(0, lambda: self._on_auth_failed(msg))

        threading.Thread(target=worker, daemon=True).start()

    def _on_auth_failed(self, error_msg: str):
        self.btn_submit.config(state=tk.NORMAL, text="Sign In" if self.mode == "signin" else "Create Account")
        self.lbl_status.config(text=error_msg, fg=self.RED)

    def _on_auth_complete(self, auth_data: Dict[str, Any]):
        """Called when authentication succeeds either via browser or in-app."""
        uid = auth_data.get("uid", "")
        email = auth_data.get("email", "")
        disp_name = auth_data.get("displayName", "")
        id_token = auth_data.get("idToken", "")
        ref_token = auth_data.get("refreshToken", "")

        # Update FirebaseManager session
        self.fb_manager.set_authenticated_session(
            user_id=uid,
            email=email,
            display_name=disp_name,
            id_token=id_token,
            refresh_token=ref_token
        )

        # Update local profile with auth credentials
        self.profile.set_auth(
            uid=uid,
            email=email,
            display_name=disp_name,
            id_token=id_token,
            refresh_token=ref_token
        )

        # Pull existing cloud profile or push local progress
        cloud_data = self.fb_manager.load_user_profile(uid)
        if cloud_data:
            self.profile.apply_cloud_data(cloud_data)
        else:
            # Upload local profile progress
            self.fb_manager.save_user_profile(uid, self.profile.to_dict())

        # Cleanup server
        if self.auth_server:
            try:
                self.auth_server.stop()
            except Exception:
                pass
            self.auth_server = None

        if self.on_auth_changed:
            self.on_auth_changed()

        # Rebuild dialog UI to show authenticated view
        self._build_ui()
        messagebox.showinfo("Signed In", f"Welcome back, {self.profile.player_name}!\nAll your progress (name, balance, and shop items) is now saved to the cloud.")

    def _handle_sign_out(self):
        confirm = messagebox.askyesno("Sign Out", "Are you sure you want to sign out of your account?")
        if not confirm:
            return

        self.fb_manager.sign_out()
        self.profile.clear_auth()

        if self.on_auth_changed:
            self.on_auth_changed()

        self._build_ui()
        messagebox.showinfo("Signed Out", "You have signed out. Progress is now stored locally as guest.")

    def _manual_sync_cloud(self):
        """Forces a pull and push to ensure cloud profile is 100% updated."""
        if not self.profile.is_authenticated():
            return

        uid = self.profile.auth_uid
        cloud_data = self.fb_manager.load_user_profile(uid)
        if cloud_data:
            self.profile.apply_cloud_data(cloud_data)
        self.fb_manager.save_user_profile(uid, self.profile.to_dict())

        if self.on_auth_changed:
            self.on_auth_changed()

        self._build_ui()
        messagebox.showinfo("Cloud Synced", "All progress has been synchronized with the cloud!")
