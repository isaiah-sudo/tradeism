import unittest
from simulation.engine import MarketEngine

class TestMarketEngine(unittest.TestCase):
    def setUp(self):
        self.engine = MarketEngine(initial_cash=25000.0)

    def test_stock_initialization(self):
        self.assertEqual(len(self.engine.stocks), 100)
        self.assertIn("NVXP", self.engine.stocks)
        nvxp = self.engine.stocks["NVXP"]
        self.assertGreater(len(nvxp.candles), 20)
        self.assertGreater(nvxp.price, 0)

    def test_order_execution_buy_sell(self):
        stock = self.engine.stocks["NVXP"]
        price = stock.price
        shares = 10
        # Buy
        success = self.engine.buy("NVXP", shares)
        self.assertTrue(success)
        pos = self.engine.positions["NVXP"]
        self.assertEqual(pos.shares, shares)
        self.assertAlmostEqual(self.engine.cash, 25000.0 - (shares * price), delta=0.01)

        # Sell
        success = self.engine.sell("NVXP", shares)
        self.assertTrue(success)
        self.assertEqual(pos.shares, 0)
        self.assertEqual(len(self.engine.trades), 2)

    def test_short_and_cover(self):
        stock = self.engine.stocks["MOON"]
        shares = 50
        success = self.engine.short("MOON", shares)
        self.assertTrue(success)
        pos = self.engine.positions["MOON"]
        self.assertEqual(pos.shares, -shares)
        self.assertEqual(pos.side, "SHORT")

        # Cover
        success = self.engine.cover("MOON", shares)
        self.assertTrue(success)
        self.assertEqual(pos.shares, 0)

    def test_simulation_step_and_news(self):
        # Step 30 times
        for _ in range(30):
            news = self.engine.step()
        # Verify candles exist and current candle is tracking
        for ticker, st in self.engine.stocks.items():
            self.assertGreater(st.price, 0)
            self.assertIsNotNone(st.current_candle)

if __name__ == "__main__":
    unittest.main()
