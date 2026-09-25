"""
User Profile and Shop Data Manager for Day Trading Simulator.
Manages persistent local storage of player menu balance, banked profits,
shop inventory, equipped win animations, and themes.
"""

import os
import json
import threading
import random
from typing import Dict, List, Any, Optional

SHOP_ITEMS: List[Dict[str, Any]] = [
    {
        "id": "money_rain",
        "name": "Money Rain & Gold Confetti",
        "category": "animation",
        "price": 0.0,
        "icon": "💸",
        "description": "High-roller cash storm! 100-dollar bills and shimmering gold glitter shower down across your terminal."
    },
    {
        "id": "rocket_moon",
        "name": "To The Moon Rocket Blast",
        "category": "animation",
        "price": 25000.0,
        "icon": "🚀",
        "description": "Screen-shaking neon rocket blastoff with blazing particle thrusters, warp speed stars & lunar splashdown!"
    },
    {
        "id": "matrix_glitch",
        "name": "Cyber Matrix Glitch Rain",
        "category": "animation",
        "price": 75000.0,
        "icon": "⚡",
        "description": "Neon green digital rain cascades down with retro CRT distortion, scanlines, and lightning victory flashes!"
    },
    {
        "id": "diamond_hands",
        "name": "Diamond Hands Supernova",
        "category": "animation",
        "price": 200000.0,
        "icon": "💎",
        "description": "Glowing diamond hands rise up, shattering into thousands of shimmering prismatic gemstone particles with a cosmic shockwave!"
    },
    {
        "id": "golden_bull",
        "name": "Golden Bull Stampede",
        "category": "animation",
        "price": 500000.0,
        "icon": "👑",
        "description": "The ultimate Wall Street flex. Giant mechanical golden bull charges across screen with laser eyes & bullion explosions!"
    },
    {
        "id": "theme_cyberpunk",
        "name": "Cyberpunk Neon Theme",
        "category": "theme",
        "price": 50000.0,
        "icon": "🔮",
        "description": "Futuristic neon purple & electric cyan styling for your trading dashboard."
    },
    {
        "id": "theme_gold_vip",
        "name": "Golden Bull VIP Theme",
        "category": "theme",
        "price": 150000.0,
        "icon": "✨",
        "description": "Ultra-prestige obsidian and metallic gold luxury border accents."
    },
    {
        "id": "sfx_airhorn",
        "name": "DJ Airhorn & Cha-Ching!",
        "category": "sfx",
        "price": 15000.0,
        "icon": "📢",
        "description": "Stadium DJ victory airhorns and cash register cha-ching audio euphoria."
    },
    {
        "id": "title_whale",
        "name": "Title: 'Wall Street Whale'",
        "category": "title",
        "price": 100000.0,
        "icon": "🐋",
        "description": "Display the prestigious [WHALE] title on your trader badge in duels & menu."
    }
]

SHOP_ITEM_MAP: Dict[str, Dict[str, Any]] = {item["id"]: item for item in SHOP_ITEMS}


class UserProfile:
    """Manages locally saved user balance, inventory, trader name, and cloud customizations."""

    def __init__(self):
        self.player_name: str = ""
        self.menu_balance: float = 0.0
        self.total_profit_banked: float = 0.0
        self.inventory: List[str] = ["money_rain"]
        self.equipped_animation: str = "money_rain"
        self.equipped_theme: str = "default"
        self.duels_won: int = 0
        # Cloud Authentication Info
        self.auth_uid: str = ""
        self.auth_email: str = ""
        self.auth_display_name: str = ""
        self.auth_id_token: str = ""
        self.auth_refresh_token: str = ""

        self._file_path = self._get_storage_path()
        self.load()

    def _get_storage_path(self) -> str:
        try:
            home_dir = os.path.expanduser("~")
            app_dir = os.path.join(home_dir, ".daytradesim")
            os.makedirs(app_dir, exist_ok=True)
            return os.path.join(app_dir, "user_profile.json")
        except Exception:
            return "user_profile.json"

    def load(self):
        """Loads profile data from local JSON file."""
        if not os.path.exists(self._file_path):
            self.save()
            return

        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.player_name = str(data.get("player_name", "") or "")
                self.menu_balance = float(data.get("menu_balance", 0.0))
                self.total_profit_banked = float(data.get("total_profit_banked", 0.0))
                self.inventory = list(data.get("inventory", ["money_rain"]))
                if "money_rain" not in self.inventory:
                    self.inventory.append("money_rain")
                self.equipped_animation = str(data.get("equipped_animation", "money_rain"))
                self.equipped_theme = str(data.get("equipped_theme", "default"))
                self.duels_won = int(data.get("duels_won", 0))
                self.auth_uid = str(data.get("auth_uid", "") or "")
                self.auth_email = str(data.get("auth_email", "") or "")
                self.auth_display_name = str(data.get("auth_display_name", "") or "")
                self.auth_id_token = str(data.get("auth_id_token", "") or "")
                self.auth_refresh_token = str(data.get("auth_refresh_token", "") or "")
        except Exception:
            pass

    def save(self, sync_cloud: bool = True):
        """Persists profile data to local JSON file and syncs to cloud if logged in."""
        data = {
            "player_name": self.player_name,
            "menu_balance": round(self.menu_balance, 2),
            "total_profit_banked": round(self.total_profit_banked, 2),
            "inventory": self.inventory,
            "equipped_animation": self.equipped_animation,
            "equipped_theme": self.equipped_theme,
            "duels_won": self.duels_won,
            "auth_uid": self.auth_uid,
            "auth_email": self.auth_email,
            "auth_display_name": self.auth_display_name,
            "auth_id_token": self.auth_id_token,
            "auth_refresh_token": self.auth_refresh_token
        }
        try:
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

        if sync_cloud and self.is_authenticated():
            self.sync_to_cloud()

    def set_player_name(self, name: str) -> None:
        """Sets trader nickname and persists it."""
        cleaned = name.strip()
        if cleaned and cleaned != self.player_name:
            self.player_name = cleaned
            self.save()

    def is_authenticated(self) -> bool:
        return bool(self.auth_uid)

    def set_auth(self, uid: str, email: str = "", display_name: str = "",
                 id_token: str = "", refresh_token: str = ""):
        """Saves authentication credentials and updates trader name if appropriate."""
        self.auth_uid = uid
        self.auth_email = email
        self.auth_display_name = display_name
        self.auth_id_token = id_token
        self.auth_refresh_token = refresh_token
        if display_name and (not self.player_name or self.player_name.startswith("Trader_")):
            self.player_name = display_name
        self.save()

    def clear_auth(self):
        """Logs out trader and removes stored credentials."""
        self.auth_uid = ""
        self.auth_email = ""
        self.auth_display_name = ""
        self.auth_id_token = ""
        self.auth_refresh_token = ""
        self.save(sync_cloud=False)

    def to_dict(self) -> Dict[str, Any]:
        """Returns the game progress dict to save to Firestore."""
        return {
            "player_name": self.player_name,
            "menu_balance": round(self.menu_balance, 2),
            "total_profit_banked": round(self.total_profit_banked, 2),
            "inventory": self.inventory,
            "equipped_animation": self.equipped_animation,
            "equipped_theme": self.equipped_theme,
            "duels_won": self.duels_won
        }

    def apply_cloud_data(self, cloud_data: Dict[str, Any]) -> None:
        """Merges remote cloud data into local profile (taking max balances and union of items)."""
        if not cloud_data or not isinstance(cloud_data, dict):
            return

        # Name
        cloud_name = cloud_data.get("player_name")
        if cloud_name and isinstance(cloud_name, str) and cloud_name.strip():
            self.player_name = cloud_name.strip()
        elif not self.player_name and self.auth_display_name:
            self.player_name = self.auth_display_name

        # Balance & Profits: take higher of local or cloud
        cloud_bal = float(cloud_data.get("menu_balance", 0.0))
        if cloud_bal > self.menu_balance:
            self.menu_balance = cloud_bal

        cloud_profit = float(cloud_data.get("total_profit_banked", 0.0))
        if cloud_profit > self.total_profit_banked:
            self.total_profit_banked = cloud_profit

        # Inventory: merge items
        cloud_inv = cloud_data.get("inventory", [])
        if isinstance(cloud_inv, list):
            for item in cloud_inv:
                if item and item not in self.inventory:
                    self.inventory.append(item)

        if "money_rain" not in self.inventory:
            self.inventory.append("money_rain")

        # Equipped items
        cloud_anim = cloud_data.get("equipped_animation")
        if cloud_anim and cloud_anim in self.inventory:
            self.equipped_animation = cloud_anim

        cloud_theme = cloud_data.get("equipped_theme")
        if cloud_theme:
            self.equipped_theme = cloud_theme

        # Duels won
        cloud_duels = int(cloud_data.get("duels_won", 0))
        if cloud_duels > self.duels_won:
            self.duels_won = cloud_duels

        self.save(sync_cloud=True)

    def sync_to_cloud(self):
        """Asynchronously syncs local profile progress to Firestore."""
        if not self.auth_uid:
            return

        uid = self.auth_uid
        p_dict = self.to_dict()
        token = self.auth_id_token

        def _worker():
            try:
                from network.firebase_manager import FirebaseManager
                fb = FirebaseManager()
                fb.id_token = token
                fb.save_user_profile(uid, p_dict)
            except Exception as e:
                print(f"[UserProfile] Background cloud sync error: {e}")

        threading.Thread(target=_worker, daemon=True).start()

    def bank_profit(self, profit_amount: float) -> float:
        """
        Adds profit (anything above starting $25,000) into the saved menu balance.
        Returns the new total menu balance.
        """
        if profit_amount <= 0:
            return self.menu_balance

        self.menu_balance += profit_amount
        self.total_profit_banked += profit_amount
        self.save()
        return self.menu_balance

    def can_afford(self, price: float) -> bool:
        return self.menu_balance >= price

    def owns(self, item_id: str) -> bool:
        return item_id in self.inventory

    def buy_item(self, item_id: str) -> bool:
        """Purchases an item from the shop if affordable and not already owned."""
        if self.owns(item_id):
            return True

        item = SHOP_ITEM_MAP.get(item_id)
        if not item:
            return False

        price = item["price"]
        if self.menu_balance < price:
            return False

        self.menu_balance -= price
        self.inventory.append(item_id)

        # Auto-equip if animation or theme
        if item["category"] == "animation":
            self.equipped_animation = item_id
        elif item["category"] == "theme":
            self.equipped_theme = item_id

        self.save()
        return True

    def equip_item(self, item_id: str) -> bool:
        """Equips an item if owned."""
        if not self.owns(item_id):
            return False

        item = SHOP_ITEM_MAP.get(item_id)
        if not item:
            return False

        if item["category"] == "animation":
            self.equipped_animation = item_id
        elif item["category"] == "theme":
            self.equipped_theme = item_id

        self.save()
        return True


# Global profile singleton
_profile_instance: Optional[UserProfile] = None

def get_profile() -> UserProfile:
    global _profile_instance
    if _profile_instance is None:
        _profile_instance = UserProfile()
    return _profile_instance
