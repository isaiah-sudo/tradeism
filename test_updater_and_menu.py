"""
Automated unit tests for Auto-Updater and Return to Menu functionality.
"""

import unittest
import os
import sys
import tempfile
import threading
from unittest.mock import MagicMock, patch

from version import __version__, GITHUB_REPO
from network.updater import parse_version, check_for_update, download_file
from ui.app import DayTradeSimApp
from ui.mode_select import ModeSelectWindow


class TestUpdaterLogic(unittest.TestCase):
    def test_version_parsing(self):
        self.assertEqual(parse_version("1.1.0"), (1, 1, 0))
        self.assertEqual(parse_version("v1.1.0"), (1, 1, 0))
        self.assertEqual(parse_version("V2.0.4"), (2, 0, 4))
        self.assertEqual(parse_version("1.2"), (1, 2, 0))
        self.assertEqual(parse_version("v1.10.3-rc1"), (1, 10, 3))
        self.assertEqual(parse_version(""), (0, 0, 0))

    def test_version_comparison(self):
        self.assertTrue(parse_version("1.2.0") > parse_version("1.1.0"))
        self.assertTrue(parse_version("v2.0.0") > parse_version("v1.9.9"))
        self.assertTrue(parse_version("1.1.1") > parse_version("1.1.0"))
        self.assertFalse(parse_version("1.1.0") > parse_version("1.1.0"))
        self.assertFalse(parse_version("1.0.5") > parse_version("1.1.0"))

    @patch("urllib.request.urlopen")
    def test_check_for_update_newer_available(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'''{
            "tag_name": "v1.2.0",
            "name": "Day Trading Simulator v1.2.0",
            "body": "Added auto-updater and solo menu return button!",
            "html_url": "https://github.com/isaiah-sudo/daytradesim/releases/tag/v1.2.0",
            "assets": [
                {
                    "name": "DayTradeSim-Setup-v1.2.0.exe",
                    "browser_download_url": "https://github.com/isaiah-sudo/daytradesim/releases/download/v1.2.0/DayTradeSim-Setup-v1.2.0.exe",
                    "size": 18000000
                },
                {
                    "name": "DayTradeSim.exe",
                    "browser_download_url": "https://github.com/isaiah-sudo/daytradesim/releases/download/v1.2.0/DayTradeSim.exe",
                    "size": 17000000
                }
            ]
        }'''
        mock_urlopen.return_value.__enter__.return_value = mock_response

        res = check_for_update(current_version="1.1.0", repo=GITHUB_REPO)
        self.assertTrue(res["update_available"])
        self.assertEqual(res["latest_version"], "1.2.0")
        self.assertEqual(res["installer_asset"]["name"], "DayTradeSim-Setup-v1.2.0.exe")
        self.assertEqual(res["portable_asset"]["name"], "DayTradeSim.exe")
        self.assertEqual(res["selected_asset"]["name"], "DayTradeSim-Setup-v1.2.0.exe")
        self.assertIn("auto-updater", res["release_notes"])

    @patch("urllib.request.urlopen")
    def test_check_for_update_already_up_to_date(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'''{
            "tag_name": "v1.1.0",
            "name": "Day Trading Simulator v1.1.0",
            "body": "Current release",
            "html_url": "https://github.com/isaiah-sudo/daytradesim/releases/tag/v1.1.0",
            "assets": []
        }'''
        mock_urlopen.return_value.__enter__.return_value = mock_response

        res = check_for_update(current_version="1.1.0", repo=GITHUB_REPO)
        self.assertFalse(res["update_available"])

    @patch("urllib.request.urlopen")
    def test_download_file_progress(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.headers.get.return_value = "100"
        # Simulate returning 2 chunks of 50 bytes
        mock_response.read.side_effect = [b"x" * 50, b"y" * 50, b""]
        mock_urlopen.return_value.__enter__.return_value = mock_response

        progress_reports = []
        def on_prog(downloaded, total):
            progress_reports.append((downloaded, total))

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name

        try:
            ok = download_file("http://example.com/file.exe", tmp_path, progress_callback=on_prog)
            self.assertTrue(ok)
            self.assertEqual(progress_reports[-1], (100, 100))
            self.assertEqual(os.path.getsize(tmp_path), 100)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class TestGUIIntegration(unittest.TestCase):
    def test_solo_return_to_menu_callback(self):
        returned = {"called": False}
        def on_return():
            returned["called"] = True

        app = DayTradeSimApp(mode="solo", on_return_to_menu=on_return)
        app.update()

        # Find the Return to Menu button in the top bar
        menu_button_found = False
        for child in app.winfo_children():
            # Look inside top bar frames
            for subchild in child.winfo_children():
                if getattr(subchild, "winfo_children", None):
                    for btn in subchild.winfo_children():
                        if getattr(btn, "cget", None):
                            try:
                                if "Menu" in btn.cget("text"):
                                    menu_button_found = True
                                    break
                            except Exception:
                                pass

        self.assertTrue(menu_button_found, "Return to Menu button not found in UI!")

        # Trigger return to menu
        app._handle_return_to_menu()
        self.assertTrue(returned["called"], "on_return_to_menu callback was not called!")

    def test_mode_select_update_button(self):
        window = ModeSelectWindow(
            on_start_solo=lambda: None,
            on_start_online=lambda m, f: None
        )
        window.update()

        self.assertIsNotNone(getattr(window, "btn_update", None))
        self.assertIn("Check for Updates", window.btn_update.cget("text"))

        # Test state change when update is available
        fake_update_info = {
            "update_available": True,
            "latest_version": "1.2.0",
            "release_notes": "Awesome features",
            "selected_asset": {"name": "DayTradeSim-Setup-v1.2.0.exe"}
        }
        window._handle_update_check_result(fake_update_info, user_initiated=False)
        self.assertIn("1.2.0", window.btn_update.cget("text"))
        self.assertEqual(window._latest_update_info, fake_update_info)

        window.destroy()


if __name__ == "__main__":
    unittest.main()
