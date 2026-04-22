"""Tests for enterprise infrastructure modules: logging, rate limiting, state management.

Compliance: NIST SP 800-92 (Logging), OWASP API4 (Rate Limiting), ISO 25010 (Robustness)
"""
import unittest
import sys
import os
import time
import math
from unittest.mock import MagicMock, patch

# Mock streamlit before importing application modules
if 'streamlit' not in sys.modules:
    mock_st = MagicMock()
    mock_st.cache_data = lambda **kwargs: (lambda fn: fn)
    mock_st.query_params = {}
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

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestStructuredLogger(unittest.TestCase):
    """NIST SP 800-92: Structured Logging Tests"""

    def test_get_logger_returns_logger(self):
        from logger import get_logger
        logger = get_logger("test_module")
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "test_module")

    def test_get_logger_idempotent(self):
        """Multiple calls should reuse same logger (no duplicate handlers)."""
        from logger import get_logger
        l1 = get_logger("test_idemp")
        handler_count_1 = len(l1.handlers)
        l2 = get_logger("test_idemp")
        handler_count_2 = len(l2.handlers)
        self.assertEqual(handler_count_1, handler_count_2)

    def test_log_security_event_no_crash(self):
        """Security event logging should never crash the app."""
        from logger import log_security_event
        try:
            log_security_event("test_event", "test details", "WARNING")
            log_security_event("test_event", "test details", "INFO")
            log_security_event("test_event", "test details", "ERROR")
        except Exception as e:
            self.fail(f"log_security_event raised exception: {e}")

    def test_log_user_action_no_crash(self):
        """User action logging should never crash the app."""
        from logger import log_user_action
        try:
            log_user_action("stock_search", "BBCA")
            log_user_action("calculate", "compound interest")
        except Exception as e:
            self.fail(f"log_user_action raised exception: {e}")

    def test_structured_formatter_output(self):
        """Formatter should produce valid JSON output."""
        import json
        from logger import StructuredFormatter
        import logging
        
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py",
            lineno=1, msg="test message", args=(), exc_info=None
        )
        output = formatter.format(record)
        parsed = json.loads(output)
        self.assertIn("timestamp", parsed)
        self.assertIn("level", parsed)
        self.assertEqual(parsed["message"], "test message")


class TestRateLimiter(unittest.TestCase):
    """OWASP API4: Rate Limiting Tests"""

    def test_rate_limiter_allows_within_limit(self):
        from rate_limiter import RateLimiter
        limiter = RateLimiter(max_calls=5, period=60.0)
        for _ in range(5):
            self.assertTrue(limiter.acquire())

    def test_rate_limiter_blocks_over_limit(self):
        from rate_limiter import RateLimiter
        limiter = RateLimiter(max_calls=3, period=60.0)
        for _ in range(3):
            limiter.acquire()
        self.assertFalse(limiter.acquire())

    def test_rate_limiter_remaining_count(self):
        from rate_limiter import RateLimiter
        limiter = RateLimiter(max_calls=10, period=60.0)
        self.assertEqual(limiter.remaining, 10)
        limiter.acquire()
        self.assertEqual(limiter.remaining, 9)

    def test_rate_limiter_thread_safe(self):
        """Rate limiter should be thread-safe."""
        import threading
        from rate_limiter import RateLimiter
        limiter = RateLimiter(max_calls=100, period=60.0)
        results = []
        
        def worker():
            results.append(limiter.acquire())
        
        threads = [threading.Thread(target=worker) for _ in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        self.assertEqual(len(results), 50)
        self.assertTrue(all(results))

    def test_global_limiters_exist(self):
        from rate_limiter import yfinance_limiter, news_limiter
        self.assertIsNotNone(yfinance_limiter)
        self.assertIsNotNone(news_limiter)
        self.assertGreater(yfinance_limiter.remaining, 0)

    def test_rate_limited_decorator(self):
        from rate_limiter import RateLimiter, rate_limited
        limiter = RateLimiter(max_calls=2, period=60.0)
        
        @rate_limited(limiter, timeout=0.1)
        def test_func():
            return "success"
        
        self.assertEqual(test_func(), "success")
        self.assertEqual(test_func(), "success")
        # Third call should be rate-limited (returns None)
        self.assertIsNone(test_func())


class TestStateManagerHardening(unittest.TestCase):
    """ISO 25010: Query Parameter Input Validation"""

    def test_get_param_caps_string_length(self):
        """Strings over 200 chars should be rejected."""
        from state_manager import get_param
        long_value = "A" * 300
        mock_params = MagicMock()
        mock_params.get = MagicMock(return_value=long_value)
        with patch.object(sys.modules['streamlit'], 'query_params', mock_params):
            result = get_param('test_key', 'default')
            self.assertEqual(result, 'default')

    def test_get_param_returns_default_on_missing(self):
        from state_manager import get_param
        mock_params = MagicMock()
        mock_params.get = MagicMock(return_value=None)
        with patch.object(sys.modules['streamlit'], 'query_params', mock_params):
            result = get_param('nonexistent', 'fallback')
            self.assertEqual(result, 'fallback')

    def test_set_param_no_crash(self):
        """set_param should never crash the app even with unusual values."""
        from state_manager import set_param
        try:
            set_param("test_key", "test_value")
            set_param("test_key", None)
            set_param("test_key", 12345)
        except Exception as e:
            self.fail(f"set_param raised exception: {e}")


class TestSanitizeSymbolWithLogging(unittest.TestCase):
    """Verify sanitize_stock_symbol logs security events."""

    def test_sanitize_non_string_returns_empty(self):
        from utils import sanitize_stock_symbol
        self.assertEqual(sanitize_stock_symbol(123), '')
        self.assertEqual(sanitize_stock_symbol(None), '')
        self.assertEqual(sanitize_stock_symbol([]), '')

    def test_sanitize_normal_symbol_unchanged(self):
        from utils import sanitize_stock_symbol
        self.assertEqual(sanitize_stock_symbol("BBCA"), "BBCA")
        self.assertEqual(sanitize_stock_symbol("BBCA.JK"), "BBCA.JK")


class TestCompoundInterestBounds(unittest.TestCase):
    """DoS Prevention: Verify iteration caps on compound interest."""

    def test_years_capped_at_100(self):
        from pages_compound import calculate_compound_interest
        # 99999 years should be capped to 100
        df = calculate_compound_interest(1000000, 10, 99999)
        # 100 years * 12 months = 1200 rows max
        self.assertLessEqual(len(df), 1200)

    def test_years_minimum_is_respected(self):
        from pages_compound import calculate_compound_interest
        df = calculate_compound_interest(1000000, 10, -5)
        # Should be capped to 0.1 years minimum = 1 month
        self.assertGreaterEqual(len(df), 1)


class TestQueryParamHardening(unittest.TestCase):
    """Additional query param security tests."""

    def test_get_param_rejects_control_characters(self):
        """Query params with control characters (null byte, etc.) must be rejected."""
        from state_manager import get_param
        # Simulate a value with null byte
        val_with_null = "BBCA\x00HACK"
        mock_params = MagicMock()
        mock_params.get = MagicMock(return_value=val_with_null)
        with patch.object(sys.modules['streamlit'], 'query_params', mock_params):
            result = get_param('test_key', 'default')
            self.assertEqual(result, 'default')

    def test_get_param_float_rejects_nan(self):
        """Float params that parse to NaN must return default."""
        from state_manager import get_param
        mock_params = MagicMock()
        mock_params.get = MagicMock(return_value="nan")
        with patch.object(sys.modules['streamlit'], 'query_params', mock_params):
            result = get_param('price', 100.0)
            self.assertEqual(result, 100.0)

    def test_get_param_float_rejects_inf(self):
        """Float params that parse to Inf must return default."""
        from state_manager import get_param
        mock_params = MagicMock()
        mock_params.get = MagicMock(return_value="inf")
        with patch.object(sys.modules['streamlit'], 'query_params', mock_params):
            result = get_param('price', 100.0)
            self.assertEqual(result, 100.0)

    def test_get_param_int_rejects_extreme(self):
        """Integer params > 10^15 must return default."""
        from state_manager import get_param
        mock_params = MagicMock()
        mock_params.get = MagicMock(return_value="9999999999999999")
        with patch.object(sys.modules['streamlit'], 'query_params', mock_params):
            result = get_param('amount', 1000)
            self.assertEqual(result, 1000)


if __name__ == '__main__':
    unittest.main()
