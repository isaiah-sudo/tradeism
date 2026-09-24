"""
Unit tests for UserProfile, Shop purchase, and profit banking logic.
"""

import unittest
import os
import tempfile
import shutil
from profile_manager import UserProfile, SHOP_ITEMS, SHOP_ITEM_MAP

class TestProfileAndShop(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.profile_path = os.path.join(self.test_dir, "test_profile.json")

        # Patch storage path
        UserProfile._get_storage_path = lambda self: os.path.join(tempfile.gettempdir(), f"test_profile_{os.getpid()}.json")
        self.profile = UserProfile()
        self.profile.menu_balance = 0.0
        self.profile.total_profit_banked = 0.0
        self.profile.inventory = ["money_rain"]
        self.profile.equipped_animation = "money_rain"
        self.profile.save()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)
        try:
            if os.path.exists(self.profile._file_path):
                os.remove(self.profile._file_path)
        except Exception:
            pass

    def test_bank_profit(self):
        self.assertEqual(self.profile.menu_balance, 0.0)
        # Bank $3,500 net profit
        new_bal = self.profile.bank_profit(3500.0)
        self.assertEqual(new_bal, 3500.0)
        self.assertEqual(self.profile.menu_balance, 3500.0)
        self.assertEqual(self.profile.total_profit_banked, 3500.0)

        # Bank another $1,250
        new_bal = self.profile.bank_profit(1250.0)
        self.assertEqual(new_bal, 4750.0)

        # Reload from disk
        fresh = UserProfile()
        self.assertEqual(fresh.menu_balance, 4750.0)
        self.assertEqual(fresh.total_profit_banked, 4750.0)

    def test_buy_item_affordability(self):
        # Rocket costs 25000
        self.profile.menu_balance = 10000.0
        self.assertFalse(self.profile.buy_item("rocket_moon"))
        self.assertFalse(self.profile.owns("rocket_moon"))

        # Add balance to reach 30,000
        self.profile.bank_profit(20000.0) # total 30000
        self.assertTrue(self.profile.buy_item("rocket_moon"))
        self.assertTrue(self.profile.owns("rocket_moon"))
        self.assertEqual(self.profile.menu_balance, 5000.0)
        self.assertEqual(self.profile.equipped_animation, "rocket_moon")

        # Reload from disk
        fresh = UserProfile()
        self.assertTrue(fresh.owns("rocket_moon"))
        self.assertEqual(fresh.equipped_animation, "rocket_moon")
        self.assertEqual(fresh.menu_balance, 5000.0)

    def test_equip_item(self):
        self.profile.inventory.append("matrix_glitch")
        self.assertTrue(self.profile.equip_item("matrix_glitch"))
        self.assertEqual(self.profile.equipped_animation, "matrix_glitch")

        # Non-owned item cannot be equipped
        self.assertFalse(self.profile.equip_item("golden_bull"))
        self.assertEqual(self.profile.equipped_animation, "matrix_glitch")

if __name__ == "__main__":
    unittest.main()
