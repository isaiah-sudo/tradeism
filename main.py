"""
Day Trading Simulator
An action-packed intraday stock simulator featuring super-volatile stocks,
breaking news catalysts, real-time candlestick charts, and 1v1 Omegle-style PvP duels.
"""

from typing import Optional, Dict, Any
from ui.mode_select import ModeSelectWindow
from ui.app import DayTradeSimApp
from network.firebase_manager import FirebaseManager

def start_game():
    def on_start_solo():
        def return_to_launcher():
            start_game()
        app = DayTradeSimApp(mode="solo", on_return_to_menu=return_to_launcher)
        app.mainloop()

    def on_start_online(match_data: Dict[str, Any], fb_manager: FirebaseManager):
        def return_to_launcher():
            start_game()
        app = DayTradeSimApp(
            mode="online",
            match_data=match_data,
            fb_manager=fb_manager,
            on_return_to_menu=return_to_launcher
        )
        app.mainloop()

    launcher = ModeSelectWindow(
        on_start_solo=on_start_solo,
        on_start_online=on_start_online
    )
    launcher.mainloop()

def main():
    start_game()

if __name__ == "__main__":
    main()
