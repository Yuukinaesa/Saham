import unittest
import math
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pages_calculators import calculate_profit_loss
from pages_ara_arb import calculate_ara_arb_sequence
from utils import get_tick_size, get_ara_arb_percentage, round_price_to_tick

class TestFinancialLogic(unittest.TestCase):

    def test_calculate_profit_loss(self):
        # Basic case: Buy 100 lot at 1000, Sell at 1200, No fee
        # Modal = 100 * 100 * 1000 = 10,000,000
        # Sell = 100 * 100 * 1200 = 12,000,000
        # Profit = 2,000,000
        total_beli, total_jual, profit_loss, percentage = calculate_profit_loss(100, 1000, 1200, 0, 0)
        self.assertEqual(total_beli, 10000000)
        self.assertEqual(total_jual, 12000000)
        self.assertEqual(profit_loss, 2000000)
        self.assertAlmostEqual(percentage, 20.0)

        # Case with Fee: Buy 0.15%, Sell 0.25%
        # Fee Beli = 10,000,000 * 0.0015 = 15,000 -> Total Beli = 10,015,000
        # Fee Jual = 12,000,000 * 0.0025 = 30,000 -> Total Jual = 11,970,000
        # Profit = 11,970,000 - 10,015,000 = 1,955,000
        total_beli, total_jual, profit_loss, percentage = calculate_profit_loss(100, 1000, 1200, 0.0015, 0.0025)
        self.assertEqual(total_beli, 10015000)
        self.assertEqual(total_jual, 11970000)
        self.assertEqual(profit_loss, 1955000)

    def test_tick_size_rules(self):
        # Rule I: Price < 200 -> Tick 1
        self.assertEqual(get_tick_size(50), 1)
        self.assertEqual(get_tick_size(199), 1)
        
        # Rule II: 200 <= Price < 500 -> Tick 2
        self.assertEqual(get_tick_size(200), 2)
        self.assertEqual(get_tick_size(498), 2)
        
        # Rule III: 500 <= Price < 2000 -> Tick 5
        self.assertEqual(get_tick_size(500), 5)
        self.assertEqual(get_tick_size(1995), 5)
        
        # Rule IV: 2000 <= Price < 5000 -> Tick 10
        self.assertEqual(get_tick_size(2000), 10)
        self.assertEqual(get_tick_size(4990), 10)
        
        # Rule V: Price >= 5000 -> Tick 25
        self.assertEqual(get_tick_size(5000), 25)
        self.assertEqual(get_tick_size(10000), 25)

    def test_ara_arb_percentage_rules(self):
        # Regular Board
        # Price 50-200 -> 35%
        self.assertEqual(get_ara_arb_percentage(100), 0.35)
        
        # Price 200-5000 -> 25%
        self.assertEqual(get_ara_arb_percentage(1000), 0.25)
        
        # Price > 5000 -> 20%
        self.assertEqual(get_ara_arb_percentage(6000), 0.20)
        
        # Acceleration Board -> 10%
        self.assertEqual(get_ara_arb_percentage(100, board='acceleration'), 0.10)

    def test_round_price_to_tick(self):
        # Round 202 to tick 2 (Floor -> 202, Ceil -> 202) - already valid
        self.assertEqual(round_price_to_tick(202, 2, 'floor'), 202)
        
        # Round 203 to tick 2 (Floor -> 202, Ceil -> 204)
        self.assertEqual(round_price_to_tick(203, 2, 'floor'), 202)
        self.assertEqual(round_price_to_tick(203, 2, 'ceil'), 204)
        
        # Round 503 to tick 5 (Floor -> 500, Ceil -> 505)
        self.assertEqual(round_price_to_tick(503, 5, 'floor'), 500)
        self.assertEqual(round_price_to_tick(503, 5, 'ceil'), 505)

    def test_calculate_ara_arb_sequence(self):
        # Test sequences (just length and basic direction)
        ara_seq, arb_seq = calculate_ara_arb_sequence(1000, is_acceleration=False, max_steps=3) # 3 days ARA/ARB
        
        # Expect list of dicts. 
        self.assertTrue(len(ara_seq) > 0)
        self.assertTrue(len(arb_seq) > 0)
        
        # Check ARA logic
        if ara_seq:
            self.assertGreater(ara_seq[0]['harga'], 1000)
            self.assertEqual(ara_seq[0]['tipe'], 'ara')
            
        # Check ARB logic
        if arb_seq:
            self.assertLess(arb_seq[0]['harga'], 1000)
            self.assertEqual(arb_seq[0]['tipe'], 'arb')

if __name__ == '__main__':
    unittest.main()
