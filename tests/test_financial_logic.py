import unittest
import math
import sys
import os

# Mock streamlit and heavy dependencies before importing application modules
# This allows testing without the full dependency stack (CI/CD compatibility)
from unittest.mock import MagicMock

if 'streamlit' not in sys.modules:
    mock_st = MagicMock()
    mock_st.cache_data = lambda **kwargs: (lambda fn: fn)
    sys.modules['streamlit'] = mock_st
    sys.modules['streamlit_option_menu'] = MagicMock()

for mod_name in ['yfinance', 'plotly', 'plotly.graph_objects', 'plotly.express',
                 'plotly.subplots', 'feedparser', 'bs4', 'matplotlib']:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()

try:
    import pandas
except ImportError:
    sys.modules['pandas'] = MagicMock()
try:
    import numpy
except ImportError:
    sys.modules['numpy'] = MagicMock()

# Add parent directory to path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pages_calculators import calculate_profit_loss
from pages_ara_arb import calculate_ara_arb_sequence, calculate_preset_ara_beruntun
from utils import (
    get_tick_size,
    get_ara_percentage,
    get_arb_percentage,
    get_ara_arb_percentage,
    round_price_to_tick,
    normalize_pbv,
)

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

    def test_normalize_pbv(self):
        # Normal IDR company - no adjustment
        self.assertEqual(normalize_pbv(2.5, 'IDR', 'IDR'), 2.5)
        # Zero or negative
        self.assertEqual(normalize_pbv(0, 'IDR', 'IDR'), 0.0)
        self.assertEqual(normalize_pbv(-1, 'IDR', 'IDR'), 0.0)
        # USD company with distorted raw PBV (~16,500)
        norm = normalize_pbv(16500.0, 'USD', 'IDR')
        self.assertAlmostEqual(norm, 1.0, delta=0.5)

    def test_fca_preset_uses_tick_one(self):
        # Calculate preset sequence starting from 100
        preset = calculate_preset_ara_beruntun(100)
        fca_items = [p for p in preset if p['tipe'] == 'fca']
        self.assertTrue(len(fca_items) > 0)
        # Prices in FCA must be integers because tick size is Rp 1
        for item in fca_items:
            self.assertEqual(item['harga'], int(item['harga']))

    def test_ara_percentage_and_arb_percentage_regimes(self):
        # Test get_ara_percentage
        self.assertEqual(get_ara_percentage(5), 0)  # Nominal Rp 1 per Kep-00158/BEI/10-2026
        self.assertEqual(get_ara_percentage(100), 0.35)
        self.assertEqual(get_ara_percentage(1000), 0.25)
        self.assertEqual(get_ara_percentage(6000), 0.20)
        self.assertEqual(get_ara_percentage(100, board='acceleration'), 0.10)
        self.assertEqual(get_ara_percentage(100, board='fca'), 0.10)
        
        # Test get_arb_percentage under different regimes
        self.assertEqual(get_arb_percentage(1000, regime='current_2026'), 0.07)
        self.assertEqual(get_arb_percentage(1000, regime='flat_15'), 0.15)
        self.assertEqual(get_arb_percentage(1000, regime='symmetric'), 0.25)
        self.assertEqual(get_arb_percentage(100, board='acceleration'), 0.10)
        self.assertEqual(get_arb_percentage(100, board='fca'), 0.10)

    def test_calculate_ara_arb_sequence_current_2026_asymmetric_7pct(self):
        # Regular board with price 1000: ARA 25% (tick 10), ARB 7% (tick 5)
        ara_seq, arb_seq = calculate_ara_arb_sequence(1000, max_steps=2, board_type='regular', regime='current_2026')
        # Step 1 ARA: 1000 * 1.25 = 1250
        self.assertEqual(ara_seq[0]['harga'], 1250)
        # Step 1 ARB: 1000 * (1 - 0.07) = 930
        self.assertEqual(arb_seq[0]['harga'], 930)

    def test_calculate_ara_arb_sequence_low_prices_nominal_rp1(self):
        # SK Direksi BEI No. Kep-00158/BEI/10-2026:
        # Prices <= 10 have nominal Rp 1 rejection
        ara_seq, arb_seq = calculate_ara_arb_sequence(5, max_steps=1, board_type='regular', regime='current_2026')
        self.assertEqual(ara_seq[0]['harga'], 6)
        self.assertEqual(arb_seq[0]['harga'], 4)
        
        # Prices 11 to 14: ARB is nominal Rp 1 because 7% of 11-14 < 1
        _, arb_seq_14 = calculate_ara_arb_sequence(14, max_steps=1, board_type='regular', regime='current_2026')
        self.assertEqual(arb_seq_14[0]['harga'], 13)

    def test_calculate_ara_arb_sequence_fca_board(self):
        # FCA: Peraturan BEI No. II-X -> ARA 10%, ARB 10%, fraksi flat Rp 1, harga min Rp 1
        ara_seq, arb_seq = calculate_ara_arb_sequence(100, max_steps=1, board_type='fca')
        self.assertEqual(ara_seq[0]['harga'], 110)
        self.assertEqual(arb_seq[0]['harga'], 90)

    def test_penghapusan_batas_gocap_to_rp1(self):
        # Under new BEI rules, price can fall below Rp 50 down to Rp 1 (no stall at 50)
        _, arb_seq = calculate_ara_arb_sequence(50, max_steps=5, board_type='regular', regime='current_2026')
        self.assertTrue(len(arb_seq) > 0)
        # Price at step 1 should drop below 50: 50 * 0.93 = 46.5 -> round ceil tick 1 = 47
        self.assertEqual(arb_seq[0]['harga'], 47)
        self.assertLess(arb_seq[0]['harga'], 50)

if __name__ == '__main__':
    unittest.main()
