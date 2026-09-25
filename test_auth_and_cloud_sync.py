"""
Unit tests for Name Persistence, Sign-In, Browser Auth Server, and Cloud Sync.
"""

import unittest
import os
import sys
import tempfile
import json
import urllib.request
from unittest.mock import MagicMock, patch

from profile_manager import UserProfile
from network.firebase_manager import FirebaseManager
from network.auth_server import AuthCallbackServer
from ui.mode_select import ModeSelectWindow
from ui.sign_in_dialog import SignInDialog, is_web_environment


class TestNameAndCloudSync(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.orig_storage = UserProfile._get_storage_path
        self.test_profile_path = os.path.join(self.tmp_dir, "test_user_profile.json")
        UserProfile._get_storage_path = lambda s: self.test_profile_path

        self.profile = UserProfile()

    def tearDown(self):
        UserProfile._get_storage_path = self.orig_storage
        try:
            if os.path.exists(self.test_profile_path):
                os.remove(self.test_profile_path)
            os.rmdir(self.tmp_dir)
        except Exception:
            pass

    def test_name_persists_across_sessions(self):
        """Test that setting a player name saves to disk and reloads on next launch."""
        self.profile.set_player_name("WolfOfWallSt")
        self.assertEqual(self.profile.player_name, "WolfOfWallSt")

        # Reload fresh profile from file
        reloaded = UserProfile()
        self.assertEqual(reloaded.player_name, "WolfOfWallSt")

        # Update name again
        reloaded.set_player_name("DiamondBull")
        fresh = UserProfile()
        self.assertEqual(fresh.player_name, "DiamondBull")

    def test_profile_to_dict_and_apply_cloud_data(self):
        """Test progress serialization and cloud data merging (money, inventory, name)."""
        self.profile.set_player_name("TraderAce")
        self.profile.menu_balance = 15000.0
        self.profile.total_profit_banked = 15000.0
        self.profile.inventory = ["money_rain", "rocket_moon"]
        self.profile.equipped_animation = "rocket_moon"
        self.profile.duels_won = 4

        p_dict = self.profile.to_dict()
        self.assertEqual(p_dict["player_name"], "TraderAce")
        self.assertEqual(p_dict["menu_balance"], 15000.0)
        self.assertEqual(p_dict["inventory"], ["money_rain", "rocket_moon"])
        self.assertEqual(p_dict["duels_won"], 4)

        # Merge with cloud profile that has more money and another item
        cloud_data = {
            "player_name": "TraderAceCloud",
            "menu_balance": 40000.0,
            "total_profit_banked": 50000.0,
            "inventory": ["money_rain", "matrix_glitch"],
            "equipped_animation": "matrix_glitch",
            "equipped_theme": "theme_cyberpunk",
            "duels_won": 10
        }
        self.profile.apply_cloud_data(cloud_data)

        # Money should be highest
        self.assertEqual(self.profile.menu_balance, 40000.0)
        self.assertEqual(self.profile.total_profit_banked, 50000.0)
        # Inventory should be union of both
        self.assertIn("rocket_moon", self.profile.inventory)
        self.assertIn("matrix_glitch", self.profile.inventory)
        self.assertEqual(self.profile.duels_won, 10)
        self.assertEqual(self.profile.player_name, "TraderAceCloud")

    def test_auth_state_management(self):
        """Test setting and clearing authentication info."""
        self.assertFalse(self.profile.is_authenticated())

        self.profile.set_auth(
            uid="uid_12345",
            email="trader@test.com",
            display_name="CloudTrader",
            id_token="token_abc",
            refresh_token="ref_xyz"
        )
        self.assertTrue(self.profile.is_authenticated())
        self.assertEqual(self.profile.auth_uid, "uid_12345")
        self.assertEqual(self.profile.auth_email, "trader@test.com")

        # Reload from disk
        fresh = UserProfile()
        self.assertTrue(fresh.is_authenticated())
        self.assertEqual(fresh.auth_uid, "uid_12345")

        # Log out
        fresh.clear_auth()
        self.assertFalse(fresh.is_authenticated())
        self.assertEqual(fresh.auth_uid, "")


class TestAuthServerAndUI(unittest.TestCase):
    def test_auth_callback_server(self):
        """Test local HTTP auth server serving login page and processing callback."""
        captured = []
        server = AuthCallbackServer(
            api_key="test_api_key",
            project_id="test_project",
            auth_domain="test.firebaseapp.com",
            on_success=lambda data: captured.append(data)
        )
        server.start()
        url = server.get_url()

        try:
            # 1. Test GET / renders page with injected config
            with urllib.request.urlopen(url) as resp:
                self.assertEqual(resp.status, 200)
                html = resp.read().decode("utf-8")
                self.assertIn("test_api_key", html)
                self.assertIn("Sign in with Google", html)
                self.assertIn("Create Account", html)

            # 2. Test POST /callback delivers data
            callback_url = f"{url}/callback"
            payload = {
                "uid": "google_user_789",
                "email": "trader@google.com",
                "displayName": "GoogleTrader",
                "idToken": "fake_token_jwt",
                "refreshToken": "fake_ref"
            }
            req = urllib.request.Request(
                callback_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req) as resp:
                self.assertEqual(resp.status, 200)
                res_data = json.loads(resp.read().decode("utf-8"))
                self.assertEqual(res_data.get("status"), "ok")

            self.assertEqual(len(captured), 1)
            self.assertEqual(captured[0]["uid"], "google_user_789")
            self.assertEqual(captured[0]["displayName"], "GoogleTrader")
        finally:
            server.stop()

    def test_auth_domain_guaranteed_in_server_and_manager(self):
        """Test that FirebaseManager and AuthCallbackServer never leave auth_domain empty."""
        fm = FirebaseManager()
        self.assertTrue(bool(fm.auth_domain))
        self.assertIn("firebaseapp.com", fm.auth_domain)

        # Even if saved with empty string, it automatically falls back
        with tempfile.NamedTemporaryFile("w", delete=False) as tf:
            cfg_file = tf.name
        try:
            with patch("network.firebase_manager.CONFIG_FILE", cfg_file):
                fm.save_config("test_key", "custom-proj", "")
                self.assertEqual(fm.auth_domain, "custom-proj.firebaseapp.com")
        finally:
            if os.path.exists(cfg_file):
                os.remove(cfg_file)

        # Server rendered HTML must contain valid authDomain
        server = AuthCallbackServer("fake_key", "custom-proj", "")
        html = server.get_rendered_html()
        self.assertIn("custom-proj.firebaseapp.com", html)
        self.assertNotIn('authDomain: ""', html)

    def test_mode_select_sign_in_controls(self):
        """Test that ModeSelectWindow creates the top-left sign in button and nickname persists."""
        window = ModeSelectWindow(on_start_solo=lambda: None, on_start_online=lambda m, f: None)
        try:
            # Check top_left_ctrls exists
            self.assertTrue(hasattr(window, "top_left_ctrls"))
            children = window.top_left_ctrls.winfo_children()
            self.assertTrue(len(children) > 0)
            # Default is unauthenticated -> "Sign In" button
            btn = children[0]
            self.assertIn("Sign In", btn.cget("text"))

            # Test nickname input
            self.assertTrue(hasattr(window, "ent_nickname"))
            window.ent_nickname.delete(0, "end")
            window.ent_nickname.insert(0, "CustomTraderName")
            window._on_nickname_changed()

            # Verify saved to profile
            self.assertEqual(window.profile.player_name, "CustomTraderName")
        finally:
            window.destroy()


if __name__ == "__main__":
    unittest.main()
