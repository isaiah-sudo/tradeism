"""
Shop Dialog for Day Trading Simulator.
Allows players to spend their banked profits on crazy win animations,
custom themes, sound packs, and trader titles.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
from profile_manager import get_profile, SHOP_ITEMS, SHOP_ITEM_MAP
from ui.win_animations import play_win_animation

class ShopDialog(tk.Toplevel):
    THEME_BG = "#0e1117"
    CARD_BG = "#161a25"
    BORDER_COLOR = "#2a2e39"
    TEXT_MUTED = "#848e9c"
    GREEN = "#00e676"
    GOLD = "#ffd700"
    BLUE = "#2962ff"

    def __init__(self, parent, on_profile_updated: Optional[Callable[[], None]] = None):
        super().__init__(parent)
        self.title("🛒 TRADER SHOP • CRAZY WIN ANIMATIONS & PERKS")
        self.geometry("780x640")
        self.minsize(680, 520)
        self.configure(bg=self.THEME_BG)
        self.transient(parent)
        self.grab_set()

        self.profile = get_profile()
        self.on_profile_updated = on_profile_updated
        self.active_category = "all"

        self._center_window(parent)
        self._build_ui()

    def _center_window(self, parent):
        self.update_idletasks()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        w, h = 780, 640
        x = px + max(0, (pw - w) // 2)
        y = py + max(0, (ph - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        # 1. Header with Vault Balance
        hdr_frame = tk.Frame(self, bg=self.THEME_BG, padx=24, pady=16)
        hdr_frame.pack(fill=tk.X)

        title_box = tk.Frame(hdr_frame, bg=self.THEME_BG)
        title_box.pack(side=tk.LEFT)

        tk.Label(
            title_box,
            text="🛒 TRADER SHOP & REWARDS",
            font=("Segoe UI", 18, "bold"),
            fg="#ffffff",
            bg=self.THEME_BG
        ).pack(anchor="w")

        tk.Label(
            title_box,
            text="Bank profits above $25k to unlock crazy victory celebrations & custom perks!",
            font=("Segoe UI", 9),
            fg=self.TEXT_MUTED,
            bg=self.THEME_BG
        ).pack(anchor="w", pady=(2, 0))

        # Balance pill on top right
        bal_box = tk.Frame(hdr_frame, bg="#1a2e22", bd=1, relief=tk.SOLID, padx=16, pady=8)
        bal_box.pack(side=tk.RIGHT)

        tk.Label(
            bal_box,
            text="MENU VAULT BALANCE",
            font=("Segoe UI", 8, "bold"),
            fg=self.TEXT_MUTED,
            bg="#1a2e22"
        ).pack(anchor="e")

        self.lbl_vault_balance = tk.Label(
            bal_box,
            text=f"${self.profile.menu_balance:,.2f}",
            font=("Segoe UI", 16, "bold"),
            fg=self.GREEN,
            bg="#1a2e22"
        )
        self.lbl_vault_balance.pack(anchor="e")

        # 2. Filter Category Tabs
        filter_f = tk.Frame(self, bg=self.THEME_BG, padx=24)
        filter_f.pack(fill=tk.X, pady=(0, 10))

        categories = [
            ("all", "🌟 All Items"),
            ("animation", "🎆 Crazy Win Animations"),
            ("theme", "🎨 Themes"),
            ("sfx", "🔊 Audio"),
            ("title", "🎖️ Titles")
        ]
        self.cat_buttons = {}
        for cat_id, cat_lbl in categories:
            btn = tk.Button(
                filter_f,
                text=cat_lbl,
                font=("Segoe UI", 9, "bold" if cat_id == self.active_category else "normal"),
                bg="#2962ff" if cat_id == self.active_category else "#161a25",
                fg="#ffffff" if cat_id == self.active_category else self.TEXT_MUTED,
                activebackground="#3d72ff",
                activeforeground="#ffffff",
                relief=tk.FLAT,
                padx=12, pady=5,
                cursor="hand2",
                command=lambda c=cat_id: self._select_category(c)
            )
            btn.pack(side=tk.LEFT, padx=(0, 8))
            self.cat_buttons[cat_id] = btn

        # 3. Scrollable Catalog Canvas
        catalog_container = tk.Frame(self, bg=self.THEME_BG, padx=24, pady=4)
        catalog_container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(catalog_container, bg=self.THEME_BG, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(catalog_container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scroll_content = tk.Frame(self.canvas, bg=self.THEME_BG)

        self.scroll_content.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_content, anchor="nw")
        self.canvas.configure(xscrollcommand=None, yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.bind_all("<MouseWheel>", self._on_mousewheel)

        self._render_items()

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        if self.winfo_exists():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _select_category(self, cat_id: str):
        self.active_category = cat_id
        for cid, btn in self.cat_buttons.items():
            is_sel = (cid == cat_id)
            btn.config(
                bg="#2962ff" if is_sel else "#161a25",
                fg="#ffffff" if is_sel else self.TEXT_MUTED,
                font=("Segoe UI", 9, "bold" if is_sel else "normal")
            )
        self._render_items()

    def _render_items(self):
        for child in self.scroll_content.winfo_children():
            child.destroy()

        items_to_show = [
            it for it in SHOP_ITEMS
            if self.active_category == "all" or it["category"] == self.active_category
        ]

        for item in items_to_show:
            item_id = item["id"]
            price = item["price"]
            owned = self.profile.owns(item_id)
            is_equipped = (
                (item["category"] == "animation" and self.profile.equipped_animation == item_id) or
                (item["category"] == "theme" and self.profile.equipped_theme == item_id)
            )

            # Card frame
            card = tk.Frame(self.scroll_content, bg=self.CARD_BG, bd=1, relief=tk.SOLID, padx=16, pady=12)
            card.pack(fill=tk.X, pady=6)

            # Left: Icon & Info
            left_f = tk.Frame(card, bg=self.CARD_BG)
            left_f.pack(side=tk.LEFT, fill=tk.X, expand=True)

            title_row = tk.Frame(left_f, bg=self.CARD_BG)
            title_row.pack(anchor="w")

            tk.Label(
                title_row,
                text=item["icon"],
                font=("Segoe UI", 20),
                bg=self.CARD_BG
            ).pack(side=tk.LEFT, padx=(0, 10))

            info_col = tk.Frame(title_row, bg=self.CARD_BG)
            info_col.pack(side=tk.LEFT)

            tk.Label(
                info_col,
                text=item["name"],
                font=("Segoe UI", 12, "bold"),
                fg="#ffffff",
                bg=self.CARD_BG
            ).pack(anchor="w")

            cat_tag = item["category"].upper()
            tk.Label(
                info_col,
                text=f"CATEGORY: {cat_tag}",
                font=("Segoe UI", 8, "bold"),
                fg="#2962ff" if cat_tag == "ANIMATION" else self.GOLD,
                bg=self.CARD_BG
            ).pack(anchor="w")

            tk.Label(
                left_f,
                text=item["description"],
                font=("Segoe UI", 9),
                fg=self.TEXT_MUTED,
                bg=self.CARD_BG,
                wraplength=420,
                justify=tk.LEFT
            ).pack(anchor="w", pady=(6, 0))

            # Right: Action Buttons & Price
            right_f = tk.Frame(card, bg=self.CARD_BG)
            right_f.pack(side=tk.RIGHT, padx=(10, 0))

            # Preview Button for Animations
            if item["category"] == "animation":
                btn_preview = tk.Button(
                    right_f,
                    text="🎬 Preview",
                    font=("Segoe UI", 9, "bold"),
                    bg="#222631",
                    fg="#c5c8d1",
                    activebackground="#2a2e39",
                    activeforeground="#ffffff",
                    relief=tk.FLAT,
                    padx=10, pady=4,
                    cursor="hand2",
                    command=lambda anim=item_id: self._preview_animation(anim)
                )
                btn_preview.pack(fill=tk.X, pady=(0, 6))

            # Buy / Equip / Status button
            if owned:
                if is_equipped:
                    lbl_eq = tk.Label(
                        right_f,
                        text="⭐ EQUIPPED",
                        font=("Segoe UI", 10, "bold"),
                        fg=self.GREEN,
                        bg="#1a2e22",
                        padx=12, pady=6
                    )
                    lbl_eq.pack(fill=tk.X)
                else:
                    btn_equip = tk.Button(
                        right_f,
                        text="Equip",
                        font=("Segoe UI", 9, "bold"),
                        bg="#2962ff",
                        fg="#ffffff",
                        activebackground="#3d72ff",
                        relief=tk.FLAT,
                        padx=14, pady=5,
                        cursor="hand2",
                        command=lambda it=item_id: self._handle_equip(it)
                    )
                    btn_equip.pack(fill=tk.X)
            else:
                can_buy = self.profile.can_afford(price)
                price_str = "FREE" if price == 0 else f"${price:,.0f}"
                if can_buy:
                    btn_buy = tk.Button(
                        right_f,
                        text=f"Unlock {price_str}",
                        font=("Segoe UI", 9, "bold"),
                        bg="#00c853",
                        fg="#ffffff",
                        activebackground="#00e676",
                        activeforeground="#000000",
                        relief=tk.FLAT,
                        padx=14, pady=5,
                        cursor="hand2",
                        command=lambda it=item_id: self._handle_buy(it)
                    )
                    btn_buy.pack(fill=tk.X)
                else:
                    needed = price - self.profile.menu_balance
                    btn_locked = tk.Button(
                        right_f,
                        text=f"{price_str} (Need +${needed:,.0f})",
                        font=("Segoe UI", 8),
                        bg="#222631",
                        fg="#787b86",
                        relief=tk.FLAT,
                        padx=8, pady=5,
                        state=tk.DISABLED
                    )
                    btn_locked.pack(fill=tk.X)

    def _preview_animation(self, animation_id: str):
        play_win_animation(self, animation_id=animation_id)

    def _handle_buy(self, item_id: str):
        item = SHOP_ITEM_MAP.get(item_id)
        if not item:
            return

        if self.profile.buy_item(item_id):
            self.lbl_vault_balance.config(text=f"${self.profile.menu_balance:,.2f}")
            messagebox.showinfo(
                "Purchase Successful!",
                f"🎉 You unlocked {item['name']}!\nIt has been automatically equipped."
            )
            self._render_items()
            if self.on_profile_updated:
                self.on_profile_updated()
        else:
            messagebox.showwarning("Insufficient Vault Balance", "You need to bank more trading profits to afford this item!")

    def _handle_equip(self, item_id: str):
        if self.profile.equip_item(item_id):
            self._render_items()
            if self.on_profile_updated:
                self.on_profile_updated()
