import re
import time
import math
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st
import yfinance as yf
import numpy as np
import requests

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
    Get ARA/ARB Percentage limit based on price and board type.
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
    return re.sub(r'[^a-zA-Z0-9.]', '', symbol)


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
        if pd.isna(value) or value == 0:
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
    data = {}
    for symbol in symbols:
        try:
            if not symbol.endswith('.JK'):
                symbol = f"{symbol}.JK"
            stock = yf.Ticker(symbol)
            info = stock.info
            if not info:
                st.warning(f"Tidak ada info untuk {symbol}")
                continue
            current_price = None
            price_keys = ['regularMarketPrice', 'regularMarketPreviousClose', 'currentPrice', 'previousClose']
            for key in price_keys:
                if key in info and info[key] is not None and info[key] > 0:
                    current_price = info[key]
                    break
            if current_price is None:
                st.warning(f"Tidak dapat menemukan harga valid untuk {symbol}")
                continue
            def safe_float(value, default=0):
                if value is None or pd.isna(value):
                    return default
                if value == float('inf') or value == float('-inf'):
                    return default
                return float(value)
            forward_dividend_yield = safe_float(info.get('dividendYield', 0))
            roe = safe_float(info.get('returnOnEquity', 0))
            trailing_pe = safe_float(info.get('trailingPE', 0))
            price_to_book = safe_float(info.get('priceToBook', 0))
            debt_to_equity = safe_float(info.get('debtToEquity', 0))
            data[symbol] = {
                'Symbol': symbol.replace('.JK', ''),
                'Current Price': current_price,
                'Price/Book (PBVR)': price_to_book,
                'Trailing P/E (PER)': trailing_pe,
                'Total Debt/Equity (mrq) (DER)': debt_to_equity,
                'Return on Equity (%) (ROE)': roe,
                'Diluted EPS (ttm) (EPS)': round(info.get('trailingEps', 0)),
                'Forward Annual Dividend Rate (DPS)': round(info.get('dividendRate', 0)),
                'Forward Annual Dividend Yield (%)': forward_dividend_yield,
            }
        except Exception as e:
            st.toast(f"🚨 Gagal mengambil data {symbol}: {str(e)}", icon="🚨")
            st.error(f"Error saat mengambil data {symbol}: {str(e)}")
            continue
    return data


# StockAnalysis helpers removed; we use Yahoo Finance only


@st.cache_data(ttl=300, show_spinner=False)
def fetch_enhanced_stock_data(symbols: List[str]) -> Dict[str, Dict[str, float]]:
    """Fetch richer set of metrics for screener (modeled from SahamBackup).

    Returns data including: Current Price, Market Cap, Shares Outstanding,
    Float Shares, Institutional/Insider Ownership %, PBV, PER, ROE, ROA,
    Net Income, Free Cash Flow, Cash from Operations, Total Assets/Equity/Liabilities.
    """
    data: Dict[str, Dict[str, float]] = {}
    for symbol in symbols:
        try:
            if not symbol.endswith('.JK'):
                symbol = f"{symbol}.JK"
            stock = yf.Ticker(symbol)
            info = stock.info
            if not info or len(info) == 0:
                st.warning(f"Tidak ada info untuk {symbol}")
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
                st.warning(f"Tidak dapat menemukan harga valid untuk {symbol}")
                continue

            def safe_float(value, default=0.0):
                try:
                    if value is None or pd.isna(value):
                        return default
                    if value == float('inf') or value == float('-inf'):
                        return default
                    return float(value)
                except Exception:
                    return default

            data[symbol] = {
                'Symbol': symbol.replace('.JK', ''),
                'Current Price': current_price,
                'Market Cap': safe_float(info.get('marketCap', 0)),
                'Shares Outstanding': safe_float(info.get('sharesOutstanding', 0)),
                'Float Shares': safe_float(info.get('floatShares', 0)),
                'Institutional Ownership %': safe_float(info.get('institutionOwnership', 0)) * 100,
                'Insider Ownership %': safe_float(info.get('heldPercentInsiders', 0)) * 100,
                'Price/Book (PBVR)': safe_float(info.get('priceToBook', 0)),
                'Trailing P/E (PER)': safe_float(info.get('trailingPE', 0)),
                'Return on Equity (%) (ROE)': safe_float(info.get('returnOnEquity', 0)) * 100,
                'Return on Assets (%) (ROA)': safe_float(info.get('returnOnAssets', 0)) * 100,
                'Net Income': safe_float(info.get('netIncomeToCommon', 0)),
                'Cash from Operations': safe_float(info.get('operatingCashflow', 0)),
                'Free Cash Flow': safe_float(info.get('freeCashflow', info.get('freeCashFlow', info.get('operatingCashflow', 0)))),
                'Total Assets': safe_float(info.get('totalAssets', 0)),
                'Total Equity': safe_float(info.get('totalStockholderEquity', 0)),
                'Total Liabilities': safe_float(info.get('totalDebt', 0)),
                'EPS': safe_float(info.get('trailingEps', 0)),
                'Dividend Yield %': safe_float(info.get('dividendYield', 0)) * 100,
            }
        except Exception as e:
            st.toast(f"🚨 Gagal mengambil data {symbol}: {str(e)}", icon="🚨")
            st.error(f"Error saat mengambil data {symbol}: {str(e)}")
            continue
    return data


