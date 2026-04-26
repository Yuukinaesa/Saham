import re
import time
import math
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st
import yfinance as yf
import numpy as np
import requests

from logger import get_logger, log_security_event, log_user_action
from rate_limiter import yfinance_limiter

# ── Security & Validation Constants ──────────────────────────
MAX_SYMBOL_LENGTH = 10
MAX_SYMBOLS_PER_REQUEST = 50
HTTP_REQUEST_TIMEOUT = 15  # seconds
MAX_INPUT_VALUE = 1_000_000_000_000  # 1 Trillion Rupiah cap
MAX_YEARS_COMPOUND = 100  # Max years for compound interest to prevent DoS
MAX_STEPS_ARA_ARB = 20  # Max steps for ARA/ARB calculation


def _safe_float(value, default=0.0):
    """Safely convert a value to float, returning default for None/NaN/Inf.
    
    Used across data-fetching functions to guard against bad upstream data.
    """
    try:
        if value is None:
            return default
        val = float(value)
        if math.isnan(val) or math.isinf(val):
            return default
        return val
    except (ValueError, TypeError):
        return default


def validate_numeric_input(value: float, min_val: float = 0, max_val: float = MAX_INPUT_VALUE, label: str = "Input") -> float:
    """Validate and clamp numeric input to prevent overflow/DoS.
    
    Args:
        value: The input value to validate.
        min_val: Minimum allowed value.
        max_val: Maximum allowed value.
        label: Human-readable label for error messages.
    
    Returns:
        The clamped value within [min_val, max_val].
    """
    try:
        value = float(value)
        if math.isnan(value) or math.isinf(value):
            return min_val
        return max(min_val, min(value, max_val))
    except (ValueError, TypeError):
        return min_val


def sanitize_url(url: str) -> str:
    """Validate URL to only allow http/https schemes. Prevents javascript: XSS."""
    if not isinstance(url, str):
        return '#'
    url = url.strip()
    if url.startswith(('http://', 'https://')):
        return url
    return '#'

# Financial Logic Constants
def get_tick_size(price: float) -> int:
    """
    Get BEI Tick Size (Fraksi Harga) based on price.
    """
    if price < 200:
        return 1
    elif 200 <= price < 500:
        return 2
    elif 500 <= price < 2000:
        return 5
    elif 2000 <= price < 5000:
        return 10
    else:
        return 25

def get_ara_arb_percentage(price: float, board: str = 'regular') -> float:
    """
    Get ARA Percentage limit based on price and board type.
    Note: ARB for regular board is flat 15% per BEI Kep-00003/BEI/04-2025.
    """
    if board == 'acceleration':
        if price <= 10:
            return 0 # Special case handled by absolutes
        return 0.10 # 10%
        
    # Regular Board Rules (Adjusted for recent BEI normalization)
    # Note: Using ranges provided in original code which likely reflect effective rules
    if price > 5000:
        return 0.20
    elif 200 <= price <= 5000:
        return 0.25
    else: # 50 - 200
        return 0.35



def round_price_to_tick(price: float, tick: int, mode: str = 'floor') -> int:
    """
    Round price to nearest tick.
    Mode 'floor' -> Round down to nearest tick (Safe for ARA Max)
    Mode 'ceil' -> Round up to nearest tick (Safe for ARB Min)
    Mode 'nearest' -> Standard rounding
    """
    if mode == 'floor':
        return math.floor(price / tick) * tick
    elif mode == 'ceil':
        return math.ceil(price / tick) * tick
    else:
        return round(price / tick) * tick



def apply_format_values(df: pd.DataFrame, formatters: Dict[str, callable]) -> pd.DataFrame:
    df_out = df.copy()
    for col, fn in formatters.items():
        if col in df_out.columns:
            try:
                df_out[col] = df_out[col].apply(fn)
            except Exception:
                pass
    return df_out


def sanitize_stock_symbol(symbol: str) -> str:
    """Sanitize stock symbol to prevent injection. Only allows alphanumeric and dot."""
    if not isinstance(symbol, str):
        log_security_event('input_sanitized', f'Non-string symbol input rejected: {type(symbol).__name__}')
        return ''
    cleaned = re.sub(r'[^a-zA-Z0-9.]', '', symbol)
    result = cleaned[:MAX_SYMBOL_LENGTH]  # Enforce max length
    if result != symbol.strip():
        log_security_event('input_sanitized', f'Symbol sanitized: "{symbol[:20]}" -> "{result}"')
    return result


def format_percent(value: float, decimals: int = 2) -> str:
    try:
        value = float(value) if not isinstance(value, (int, float)) else value
        if pd.isna(value) or value == 0:
            return "0,00%"
        if decimals == 2:
            return f"{value:,.2f}%".replace(".", ",")
        return f"{value:,.{decimals}f}%".replace(".", ",")
    except (ValueError, TypeError):
        return "0,00%"


def format_rupiah(value: float) -> str:
    try:
        value = float(value) if not isinstance(value, (int, float)) else value
        if value is None or (isinstance(value, float) and (math.isnan(value) or math.isinf(value))) or value == 0:
            return "Rp 0"
        return f"Rp {value:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return "Rp 0"


def format_short_number(value: float) -> str:
    try:
        value = float(value) if not isinstance(value, (int, float)) else value
        if pd.isna(value) or value == 0:
            return "0"
        if abs(value) >= 1e12:
            return f"{value/1e12:.1f} T"
        elif abs(value) >= 1e9:
            return f"{value/1e9:.1f} B"
        elif abs(value) >= 1e6:
            return f"{value/1e6:.1f} M"
        elif abs(value) >= 1e3:
            return f"{value/1e3:.1f} K"
        else:
            return f"{value:.0f}"
    except (ValueError, TypeError):
        return "0"


def format_csv_indonesia(value: float, decimals: int = 2) -> str:
    try:
        value = float(value) if not isinstance(value, (int, float)) else value
        if pd.isna(value) or value == 0:
            return "0"
        if decimals == 0:
            return f"{value:,.0f}".replace(",", ".")
        else:
            return f"{value:,.{decimals}f}".replace(",", ".")
    except (ValueError, TypeError):
        return "0"


def format_number(value: float, decimals: int = 2) -> str:
    try:
        value = float(value) if not isinstance(value, (int, float)) else value
        if pd.isna(value) or value == 0:
            return "0"
        if decimals == 0:
            return f"{value:,.0f}".replace(",", ".")
        return f"{value:,.{decimals}f}".replace(".", ",")
    except (ValueError, TypeError):
        return "0"


def format_ratio(value: float) -> str:
    try:
        value = float(value) if not isinstance(value, (int, float)) else value
        if pd.isna(value) or value == 0:
            return "0,00"
        return f"{value:,.2f}".replace(".", ",")
    except (ValueError, TypeError):
        return "0,00"


def format_large_number(value: float) -> str:
    try:
        value = float(value) if not isinstance(value, (int, float)) else value
        if pd.isna(value) or value == 0:
            return "0"
        if abs(value) >= 1_000_000_000_000:
            return f"{value / 1_000_000_000_000:.2f} T"
        elif abs(value) >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f} M"
        elif abs(value) >= 1_000_000:
            return f"{value / 1_000_000:.2f} Jt"
        elif abs(value) >= 1_000:
            return f"{value / 1_000:.2f} K"
        else:
            return f"{value:,.0f}"
    except (ValueError, TypeError):
        return "0"


@st.cache_data(ttl=300, show_spinner=False)
def fetch_stock_data(symbols: List[str]) -> Dict[str, Dict[str, float]]:
    logger = get_logger()
    data = {}
    failed_symbols = []
    for i, symbol in enumerate(symbols):
        try:
            if not yfinance_limiter.acquire():
                log_security_event('rate_limit', f'Rate limit hit for {symbol}', 'WARNING')
                failed_symbols.append((symbol, 'Rate limited'))
                continue
            if not symbol.endswith('.JK'):
                symbol = f"{symbol}.JK"

            # Small delay between requests to avoid Yahoo throttling on cloud
            if i > 0:
                time.sleep(0.5)

            stock = yf.Ticker(symbol)
            info = {}
            try:
                info = stock.info or {}
            except Exception as e:
                logger.warning(f"yfinance info failed for {symbol}: {e}")

            # If info is empty or only has minimal keys, try fast_info as fallback
            if not info or len(info) <= 1:
                logger.warning(f"Empty info for {symbol}, trying fast_info fallback")
                try:
                    fi = stock.fast_info
                    current_price = getattr(fi, 'last_price', None) or getattr(fi, 'regular_market_previous_close', None)
                    if current_price and current_price > 0:
                        data[symbol] = {
                            'Symbol': symbol.replace('.JK', ''),
                            'Current Price': float(current_price),
                            'Price/Book (PBVR)': 0,
                            'Trailing P/E (PER)': 0,
                            'Total Debt/Equity (mrq) (DER)': 0,
                            'Return on Equity (%) (ROE)': 0,
                            'Diluted EPS (ttm) (EPS)': 0,
                            'Forward Annual Dividend Rate (DPS)': 0,
                            'Forward Annual Dividend Yield (%)': 0,
                        }
                        logger.info(f"Got price for {symbol} via fast_info: {current_price}")
                        continue
                except Exception as e2:
                    logger.warning(f"fast_info also failed for {symbol}: {e2}")
                failed_symbols.append((symbol, 'Empty info from Yahoo'))
                continue

            current_price = None
            price_keys = ['regularMarketPrice', 'regularMarketPreviousClose', 'currentPrice', 'previousClose']
            for key in price_keys:
                if key in info and info[key] is not None and info[key] > 0:
                    current_price = info[key]
                    break
            if current_price is None:
                failed_symbols.append((symbol, 'No price data in response'))
                continue
            forward_dividend_yield = _safe_float(info.get('dividendYield', 0))
            roe = _safe_float(info.get('returnOnEquity', 0))
            trailing_pe = _safe_float(info.get('trailingPE', 0))
            price_to_book = _safe_float(info.get('priceToBook', 0))
            debt_to_equity = _safe_float(info.get('debtToEquity', 0))
            data[symbol] = {
                'Symbol': symbol.replace('.JK', ''),
                'Current Price': current_price,
                'Price/Book (PBVR)': price_to_book,
                'Trailing P/E (PER)': trailing_pe,
                'Total Debt/Equity (mrq) (DER)': debt_to_equity,
                'Return on Equity (%) (ROE)': roe,
                'Diluted EPS (ttm) (EPS)': round(_safe_float(info.get('trailingEps', 0))),
                'Forward Annual Dividend Rate (DPS)': round(_safe_float(info.get('dividendRate', 0))),
                'Forward Annual Dividend Yield (%)': forward_dividend_yield,
            }
        except Exception as e:
            logger.error(f"Exception fetching {symbol}: {type(e).__name__}: {e}")
            failed_symbols.append((symbol, str(e)[:100]))
            continue

    if failed_symbols:
        logger.warning(f"Failed symbols: {failed_symbols}")
    if not data and failed_symbols:
        logger.error(f"ALL symbols failed! Details: {failed_symbols}")

    return data


# StockAnalysis helpers removed; we use Yahoo Finance only


@st.cache_data(ttl=300, show_spinner=False)
def fetch_enhanced_stock_data(symbols: List[str]) -> Dict[str, Dict[str, float]]:
    """Fetch richer set of metrics for screener (modeled from SahamBackup).

    Returns data including: Current Price, Market Cap, Shares Outstanding,
    Float Shares, Institutional/Insider Ownership %, PBV, PER, ROE, ROA,
    Net Income, Free Cash Flow, Cash from Operations, Total Assets/Equity/Liabilities.
    """
    logger = get_logger()
    data: Dict[str, Dict[str, float]] = {}
    failed_symbols = []
    for i, symbol in enumerate(symbols):
        try:
            if not yfinance_limiter.acquire():
                log_security_event('rate_limit', f'Rate limit hit for enhanced fetch: {symbol}', 'WARNING')
                failed_symbols.append((symbol, 'Rate limited'))
                continue
            if not symbol.endswith('.JK'):
                symbol = f"{symbol}.JK"

            # Small delay between requests to avoid Yahoo throttling
            if i > 0:
                time.sleep(0.5)

            stock = yf.Ticker(symbol)
            info = {}
            try:
                info = stock.info or {}
            except Exception as e:
                logger.warning(f"yfinance info failed for enhanced {symbol}: {e}")

            if not info or len(info) <= 1:
                logger.warning(f"Empty info for enhanced {symbol}, trying fast_info fallback")
                try:
                    fi = stock.fast_info
                    current_price = getattr(fi, 'last_price', None) or getattr(fi, 'regular_market_previous_close', None)
                    market_cap = getattr(fi, 'market_cap', 0)
                    if current_price and current_price > 0:
                        data[symbol] = {
                            'Symbol': symbol.replace('.JK', ''),
                            'Current Price': float(current_price),
                            'Market Cap': float(market_cap) if market_cap else 0,
                            'Shares Outstanding': 0, 'Float Shares': 0,
                            'Institutional Ownership %': 0, 'Insider Ownership %': 0,
                            'Price/Book (PBVR)': 0, 'Trailing P/E (PER)': 0,
                            'Return on Equity (%) (ROE)': 0, 'Return on Assets (%) (ROA)': 0,
                            'Net Income': 0, 'Cash from Operations': 0,
                            'Free Cash Flow': 0, 'Total Assets': 0,
                            'Total Equity': 0, 'Total Liabilities': 0,
                            'EPS': 0, 'Dividend Yield %': 0,
                        }
                        continue
                except Exception as e2:
                    logger.warning(f"fast_info also failed for enhanced {symbol}: {e2}")
                failed_symbols.append((symbol, 'Empty info from Yahoo'))
                continue

            # Determine a valid current price using several candidates
            current_price = None
            for key in ['regularMarketPrice', 'currentPrice', 'regularMarketPreviousClose', 'previousClose', 'ask', 'bid', 'open']:
                try:
                    v = info.get(key)
                    if v is not None and float(v) > 0:
                        current_price = float(v)
                        break
                except Exception:
                    pass
            if current_price is None:
                failed_symbols.append((symbol, 'No price data'))
                continue

            data[symbol] = {
                'Symbol': symbol.replace('.JK', ''),
                'Current Price': current_price,
                'Market Cap': _safe_float(info.get('marketCap', 0)),
                'Shares Outstanding': _safe_float(info.get('sharesOutstanding', 0)),
                'Float Shares': _safe_float(info.get('floatShares', 0)),
                'Institutional Ownership %': _safe_float(info.get('institutionOwnership', 0)) * 100,
                'Insider Ownership %': _safe_float(info.get('heldPercentInsiders', 0)) * 100,
                'Price/Book (PBVR)': _safe_float(info.get('priceToBook', 0)),
                'Trailing P/E (PER)': _safe_float(info.get('trailingPE', 0)),
                'Return on Equity (%) (ROE)': _safe_float(info.get('returnOnEquity', 0)) * 100,
                'Return on Assets (%) (ROA)': _safe_float(info.get('returnOnAssets', 0)) * 100,
                'Net Income': _safe_float(info.get('netIncomeToCommon', 0)),
                'Cash from Operations': _safe_float(info.get('operatingCashflow', 0)),
                'Free Cash Flow': _safe_float(info.get('freeCashflow', info.get('freeCashFlow', info.get('operatingCashflow', 0)))),
                'Total Assets': _safe_float(info.get('totalAssets', 0)),
                'Total Equity': _safe_float(info.get('totalStockholderEquity', 0)),
                'Total Liabilities': _safe_float(info.get('totalDebt', 0)),
                'EPS': _safe_float(info.get('trailingEps', 0)),
                'Dividend Yield %': _safe_float(info.get('dividendYield', 0)) * 100,
            }
        except Exception as e:
            logger.error(f"Exception in enhanced fetch for {symbol}: {type(e).__name__}: {e}")
            failed_symbols.append((symbol, str(e)[:100]))
            continue

    if failed_symbols:
        logger.warning(f"Enhanced fetch failed symbols: {failed_symbols}")

    return data


