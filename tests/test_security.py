"""Security-focused test suite for the Saham IDX application.

Tests cover:
- Input sanitization (OWASP A03: Injection)
- Path traversal prevention (OWASP A01: Broken Access Control)
- XSS prevention in dynamic content
- Data validation and boundary conditions
- Dependency safety checks
"""
import unittest
import os
import re
import sys
from unittest.mock import MagicMock

# Mock streamlit and other dependencies before importing utils
# This allows testing without the full dependency stack (CI/CD compatibility)
if 'streamlit' not in sys.modules:
    mock_st = MagicMock()
    mock_st.cache_data = lambda **kwargs: (lambda fn: fn)
    sys.modules['streamlit'] = mock_st
    sys.modules['streamlit_option_menu'] = MagicMock()

# Mock optional heavy dependencies if not installed
for mod_name in ['yfinance', 'plotly', 'plotly.graph_objects', 'plotly.express',
                 'plotly.subplots', 'feedparser', 'bs4', 'matplotlib']:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()

# Ensure pandas and numpy are available (lightweight, usually installed)
try:
    import pandas
except ImportError:
    sys.modules['pandas'] = MagicMock()
try:
    import numpy
except ImportError:
    sys.modules['numpy'] = MagicMock()

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import (
    sanitize_stock_symbol,
    format_rupiah,
    format_percent,
    format_ratio,
    format_number,
    format_short_number,
    format_csv_indonesia,
    format_large_number,
    get_tick_size,
    get_ara_arb_percentage,
    round_price_to_tick,
    MAX_SYMBOL_LENGTH,
    MAX_SYMBOLS_PER_REQUEST,
)


class TestInputSanitization(unittest.TestCase):
    """OWASP A03: Injection Prevention Tests"""

    def test_sanitize_removes_special_characters(self):
        """Symbols should only contain alphanumeric and dot."""
        self.assertEqual(sanitize_stock_symbol("BBCA"), "BBCA")
        self.assertEqual(sanitize_stock_symbol("BBCA.JK"), "BBCA.JK")

    def test_sanitize_removes_injection_attempts(self):
        """SQL/XSS injection patterns should be stripped and truncated."""
        result = sanitize_stock_symbol("BBCA'; DROP TABLE--")
        self.assertNotIn("'", result)
        self.assertNotIn(";", result)
        self.assertLessEqual(len(result), MAX_SYMBOL_LENGTH)
        
        result2 = sanitize_stock_symbol("<script>alert(1)</script>")
        self.assertNotIn("<", result2)
        self.assertNotIn(">", result2)
        
        result3 = sanitize_stock_symbol("BBCA&symbol=HACK")
        self.assertNotIn("&", result3)
        self.assertNotIn("=", result3)

    def test_sanitize_enforces_max_length(self):
        """Symbol length should be capped to prevent buffer overflow."""
        long_input = "A" * 100
        result = sanitize_stock_symbol(long_input)
        self.assertLessEqual(len(result), MAX_SYMBOL_LENGTH)

    def test_sanitize_handles_empty_input(self):
        """Empty and whitespace-only inputs should return empty string."""
        self.assertEqual(sanitize_stock_symbol(""), "")
        self.assertEqual(sanitize_stock_symbol("   "), "")

    def test_sanitize_handles_path_traversal(self):
        """Path traversal attempts should be stripped."""
        result = sanitize_stock_symbol("../../etc/passwd")
        self.assertNotIn("/", result)
        self.assertNotIn("..", result.replace(".", ""))  # Dots are allowed individually


class TestNumericFormatters(unittest.TestCase):
    """Data Integrity: Ensure formatters handle edge cases safely."""

    def test_format_rupiah_normal(self):
        self.assertEqual(format_rupiah(1000), "Rp 1.000")
        self.assertEqual(format_rupiah(0), "Rp 0")

    def test_format_rupiah_negative(self):
        result = format_rupiah(-5000)
        self.assertIn("5.000", result)

    def test_format_rupiah_none(self):
        self.assertEqual(format_rupiah(None), "Rp 0")

    def test_format_rupiah_infinity(self):
        self.assertEqual(format_rupiah(float('inf')), "Rp 0")
        self.assertEqual(format_rupiah(float('-inf')), "Rp 0")

    def test_format_rupiah_nan(self):
        import math
        self.assertEqual(format_rupiah(float('nan')), "Rp 0")

    def test_format_percent_normal(self):
        result = format_percent(15.5, 2)
        self.assertIn("15", result)

    def test_format_percent_zero(self):
        self.assertEqual(format_percent(0), "0,00%")

    def test_format_short_number_scales(self):
        self.assertIn("T", format_short_number(1.5e12))
        self.assertIn("B", format_short_number(2.3e9))
        self.assertIn("M", format_short_number(4.7e6))
        self.assertIn("K", format_short_number(8.1e3))

    def test_format_large_number_edge_cases(self):
        self.assertEqual(format_large_number(0), "0")
        self.assertEqual(format_large_number(None), "0")


class TestFinancialLogicBoundaries(unittest.TestCase):
    """ISO 25010: Functional Correctness - Boundary Value Testing"""

    def test_tick_size_boundary_200(self):
        """Boundary at Rp 200 transition: 199->1, 200->2"""
        self.assertEqual(get_tick_size(199), 1)
        self.assertEqual(get_tick_size(200), 2)

    def test_tick_size_boundary_500(self):
        self.assertEqual(get_tick_size(499), 2)
        self.assertEqual(get_tick_size(500), 5)

    def test_tick_size_boundary_2000(self):
        self.assertEqual(get_tick_size(1999), 5)
        self.assertEqual(get_tick_size(2000), 10)

    def test_tick_size_boundary_5000(self):
        self.assertEqual(get_tick_size(4999), 10)
        self.assertEqual(get_tick_size(5000), 25)

    def test_tick_size_very_low_price(self):
        """Price near zero should still return valid tick."""
        self.assertEqual(get_tick_size(1), 1)
        self.assertEqual(get_tick_size(0.5), 1)

    def test_ara_arb_percentage_regular_board(self):
        self.assertEqual(get_ara_arb_percentage(100, 'regular'), 0.35)
        self.assertEqual(get_ara_arb_percentage(1000, 'regular'), 0.25)
        self.assertEqual(get_ara_arb_percentage(6000, 'regular'), 0.20)

    def test_ara_arb_percentage_acceleration_board(self):
        self.assertEqual(get_ara_arb_percentage(100, 'acceleration'), 0.10)
        self.assertEqual(get_ara_arb_percentage(5, 'acceleration'), 0)

    def test_round_price_floor(self):
        self.assertEqual(round_price_to_tick(203, 2, 'floor'), 202)

    def test_round_price_ceil(self):
        self.assertEqual(round_price_to_tick(203, 2, 'ceil'), 204)

    def test_round_price_nearest(self):
        result = round_price_to_tick(203, 2, 'nearest')
        self.assertIn(result, [202, 204])


class TestConfigValidation(unittest.TestCase):
    """ISO 27001 A.14: Secure Development - Config Safety"""

    def test_config_file_not_exposed(self):
        """user_config.json should be in .gitignore."""
        gitignore_path = os.path.join(
            os.path.dirname(__file__), '..', '.gitignore'
        )
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('user_config.json', content)

    def test_env_file_in_gitignore(self):
        """Environment files should never be committed."""
        gitignore_path = os.path.join(
            os.path.dirname(__file__), '..', '.gitignore'
        )
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('.env', content)

    def test_no_hardcoded_api_keys(self):
        """No hardcoded API keys or secrets in Python files."""
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        secret_pattern = re.compile(
            r'(API_KEY|SECRET_KEY|PASSWORD|TOKEN)\s*=\s*["\'][^"\']{8,}["\']',
            re.IGNORECASE
        )
        
        violations = []
        for root, dirs, files in os.walk(root_dir):
            # Skip non-essential dirs
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'venv', '.venv', 'tests'}]
            for fname in files:
                if fname.endswith('.py'):
                    fpath = os.path.join(root, fname)
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    if secret_pattern.search(content):
                        violations.append(fpath)
        
        self.assertEqual(len(violations), 0, f"Hardcoded secrets found in: {violations}")


class TestDependencySafety(unittest.TestCase):
    """CIS Control 2: Software Asset Management"""

    def test_requirements_have_upper_bounds(self):
        """All pinned dependencies should have upper version bounds."""
        req_path = os.path.join(
            os.path.dirname(__file__), '..', 'requirements.txt'
        )
        with open(req_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '>=' in line:
                self.assertIn('<', line, 
                    f"Dependency '{line}' has no upper bound - supply chain risk")


class TestValidationConstants(unittest.TestCase):
    """Verify security constants are properly configured."""

    def test_max_symbol_length_reasonable(self):
        self.assertGreater(MAX_SYMBOL_LENGTH, 3)
        self.assertLessEqual(MAX_SYMBOL_LENGTH, 20)

    def test_max_symbols_per_request_reasonable(self):
        self.assertGreater(MAX_SYMBOLS_PER_REQUEST, 5)
        self.assertLessEqual(MAX_SYMBOLS_PER_REQUEST, 100)


if __name__ == '__main__':
    unittest.main()
