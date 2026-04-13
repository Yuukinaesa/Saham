"""Rate Limiter Module for External API Calls.

Provides token-bucket rate limiting to prevent abuse and API bans
when calling external services (Yahoo Finance, Google News RSS).

Compliance: OWASP API4 (Unrestricted Resource Consumption), CWE-770
"""
import time
import threading
from functools import wraps


class RateLimiter:
    """Thread-safe token-bucket rate limiter.
    
    Args:
        max_calls: Maximum number of calls allowed per period.
        period: Time period in seconds for the rate limit window.
    """

    def __init__(self, max_calls: int = 30, period: float = 60.0):
        self.max_calls = max_calls
        self.period = period
        self._calls = []
        self._lock = threading.Lock()

    def _cleanup(self):
        """Remove expired timestamps outside the current window."""
        now = time.monotonic()
        cutoff = now - self.period
        self._calls = [t for t in self._calls if t > cutoff]

    def acquire(self) -> bool:
        """Attempt to acquire a rate limit token.
        
        Returns:
            True if the call is allowed, False if rate-limited.
        """
        with self._lock:
            self._cleanup()
            if len(self._calls) < self.max_calls:
                self._calls.append(time.monotonic())
                return True
            return False

    def wait_and_acquire(self, timeout: float = 10.0) -> bool:
        """Wait until a token is available or timeout.
        
        Args:
            timeout: Maximum seconds to wait for a token.
        
        Returns:
            True if token acquired, False on timeout.
        """
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.acquire():
                return True
            time.sleep(0.1)
        return False

    @property
    def remaining(self) -> int:
        """Number of remaining calls in current window."""
        with self._lock:
            self._cleanup()
            return max(0, self.max_calls - len(self._calls))


# Global rate limiters for different services
yfinance_limiter = RateLimiter(max_calls=30, period=60.0)   # 30 calls/min for Yahoo Finance
news_limiter = RateLimiter(max_calls=20, period=60.0)       # 20 calls/min for RSS feeds


def rate_limited(limiter: RateLimiter, timeout: float = 10.0):
    """Decorator to apply rate limiting to a function.
    
    Args:
        limiter: RateLimiter instance to use.
        timeout: Max seconds to wait for rate limit token.
    
    Usage:
        @rate_limited(yfinance_limiter)
        def fetch_data(symbol):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not limiter.wait_and_acquire(timeout):
                from logger import log_security_event
                log_security_event(
                    "rate_limit_exceeded",
                    f"Rate limit exceeded for {func.__name__}",
                    "WARNING"
                )
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator
