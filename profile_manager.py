"""
User Profile and Shop Data Manager for Day Trading Simulator.
Manages persistent local storage of player menu balance, banked profits,
shop inventory, equipped win animations, and themes.
"""

import os
import json
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
    """Manages locally saved user balance, inventory, and customizations."""

    def __init__(self):
        self.menu_balance: float = 0.0
        self.total_profit_banked: float = 0.0
        self.inventory: List[str] = ["money_rain"]
        self.equipped_animation: str = "money_rain"
        self.equipped_theme: str = "default"
        self.duels_won: int = 0
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
                self.menu_balance = float(data.get("menu_balance", 0.0))
                self.total_profit_banked = float(data.get("total_profit_banked", 0.0))
                self.inventory = list(data.get("inventory", ["money_rain"]))
                if "money_rain" not in self.inventory:
                    self.inventory.append("money_rain")
                self.equipped_animation = str(data.get("equipped_animation", "money_rain"))
                self.equipped_theme = str(data.get("equipped_theme", "default"))
                self.duels_won = int(data.get("duels_won", 0))
        except Exception:
            pass

    def save(self):
        """Persists profile data to local JSON file."""
        data = {
            "menu_balance": round(self.menu_balance, 2),
            "total_profit_banked": round(self.total_profit_banked, 2),
            "inventory": self.inventory,
            "equipped_animation": self.equipped_animation,
            "equipped_theme": self.equipped_theme,
            "duels_won": self.duels_won
        }
        try:
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

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
