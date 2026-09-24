import unittest
from simulation.engine import MarketEngine

class TestShortAndReverse(unittest.TestCase):
    def setUp(self):
        self.engine = MarketEngine(initial_cash=25000.0)

    def test_short_margin_and_equity(self):
        stock = self.engine.stocks["NVXP"]
        price = stock.price
        # Initial state
        self.assertEqual(self.engine.total_equity, 25000.0)
        self.assertEqual(self.engine.cash, 25000.0)

        # Short 100 shares
        ok = self.engine.short("NVXP", 100)
        self.assertTrue(ok)
        pos = self.engine.positions["NVXP"]
        self.assertEqual(pos.shares, -100)
        self.assertEqual(pos.side, "SHORT")
        # 50% margin should be deducted from cash
        expected_cash = 25000.0 - (100 * price * 0.5)
        self.assertAlmostEqual(self.engine.cash, expected_cash, delta=0.01)
        # Total equity should be exactly 25000.0 right after trade (no PnL yet)
        self.assertAlmostEqual(self.engine.total_equity, 25000.0, delta=0.01)

        # Check marker recorded
        self.assertEqual(len(stock.trade_markers), 1)
        self.assertEqual(stock.trade_markers[0].action, "SHORT")
        self.assertEqual(stock.trade_markers[0].shares, 100)

    def test_position_reversal_short_to_long(self):
        stock = self.engine.stocks["NVXP"]
        # Short 50 shares
        self.engine.short("NVXP", 50)
        pos = self.engine.positions["NVXP"]
        self.assertEqual(pos.shares, -50)

        # Buy 120 shares -> Should cover 50 short shares and end up LONG 70 shares!
        ok = self.engine.buy("NVXP", 120)
        self.assertTrue(ok)
        self.assertEqual(pos.shares, 70)
        self.assertEqual(pos.side, "LONG")

    def test_position_reversal_long_to_short(self):
        stock = self.engine.stocks["NVXP"]
        # Buy 50 shares
        self.engine.buy("NVXP", 50)
        pos = self.engine.positions["NVXP"]
        self.assertEqual(pos.shares, 50)

        # Short 120 shares -> Should sell 50 long shares and end up SHORT 70 shares!
        ok = self.engine.short("NVXP", 120)
        self.assertTrue(ok)
        self.assertEqual(pos.shares, -70)
        self.assertEqual(pos.side, "SHORT")

    def test_reverse_position_method(self):
        stock = self.engine.stocks["NVXP"]
        self.engine.buy("NVXP", 40)
        pos = self.engine.positions["NVXP"]
        self.assertEqual(pos.shares, 40)

        # Reverse position -> should become SHORT 40 shares
        ok = self.engine.reverse_position("NVXP")
        self.assertTrue(ok)
        self.assertEqual(pos.shares, -40)

        # Reverse position back -> should become LONG 40 shares
        ok = self.engine.reverse_position("NVXP")
        self.assertTrue(ok)
        self.assertEqual(pos.shares, 40)

if __name__ == "__main__":
    unittest.main()
