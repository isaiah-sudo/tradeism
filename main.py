"""
Day Trading Simulator
An action-packed intraday stock simulator featuring super-volatile stocks,
breaking news catalysts, real-time candlestick charts, and multiple speed difficulties.
"""

from ui.app import DayTradeSimApp

def main():
    app = DayTradeSimApp()
    app.mainloop()

if __name__ == "__main__":
    main()
