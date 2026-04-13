import json
import os
import streamlit as st

CONFIG_FILE = 'user_config.json'

# ─────────────────────────────────────────────
#  JSON-based persistence (existing, for scraper)
# ─────────────────────────────────────────────

def load_config():
    """Load configuration from local JSON file into session state if available.
    
    Security: Validates file path and data types before loading.
    """
    # Security: Ensure CONFIG_FILE is a simple filename (no path traversal)
    if os.path.sep in CONFIG_FILE or '/' in CONFIG_FILE or '..' in CONFIG_FILE:
        return
    
    if os.path.exists(CONFIG_FILE):
        try:
            # Security: Check file size before reading (max 1MB)
            if os.path.getsize(CONFIG_FILE) > 1_048_576:
                return
            
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, dict):
                return
            
            valid_keys = ['scraper_symbols', 'scraper_modal']
            for k, v in data.items():
                if k in valid_keys:
                    # Type validation
                    if k == 'scraper_symbols' and not isinstance(v, str):
                        continue
                    if k == 'scraper_modal' and not isinstance(v, (int, float)):
                        continue
                    if k not in st.session_state:
                        st.session_state[k] = v
        except (json.JSONDecodeError, IOError, OSError):
            pass

def save_config():
    """Save current relevant session state to local JSON file.
    
    Security: Validates data before writing and uses safe encoding.
    """
    # Security: Ensure CONFIG_FILE is a simple filename
    if os.path.sep in CONFIG_FILE or '/' in CONFIG_FILE or '..' in CONFIG_FILE:
        return
    
    valid_keys = ['scraper_symbols', 'scraper_modal']
    data = {}
    for k in valid_keys:
        if k in st.session_state:
            val = st.session_state[k]
            # Type validation before saving
            if k == 'scraper_symbols' and isinstance(val, str):
                data[k] = val[:500]  # Cap length
            elif k == 'scraper_modal' and isinstance(val, (int, float)):
                data[k] = val
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=True)
    except (IOError, OSError):
        pass


# ─────────────────────────────────────────────
#  URL Query-Params based persistence
#  Cara pakai:
#    get_param("key", default)   → baca dari URL
#    set_param("key", value)     → tulis ke URL (instantly persist on refresh)
#    init_session_from_url()     → panggil sekali di awal setiap page function
# ─────────────────────────────────────────────

def get_param(key: str, default=None):
    """
    Baca nilai dari URL query params.
    Otomatis convert ke tipe yang tepat berdasarkan nilai default.
    
    Security: Validates and caps string length to prevent injection.
    """
    try:
        val = st.query_params.get(key, None)
        if val is None:
            return default
        # Security: Cap value length to prevent abuse
        if isinstance(val, str) and len(val) > 200:
            return default
        # Auto-cast berdasarkan tipe default
        if isinstance(default, bool):
            return val.lower() in ('true', '1', 'yes')
        if isinstance(default, int):
            result = int(val)
            # Guard against extreme values
            if abs(result) > 10**15:
                return default
            return result
        if isinstance(default, float):
            result = float(val)
            import math
            if math.isnan(result) or math.isinf(result):
                return default
            return result
        return val  # string
    except (ValueError, TypeError, OverflowError):
        return default


def set_param(key: str, value):
    """
    Tulis nilai ke URL query params.
    Value None akan menghapus param tersebut.
    """
    try:
        if value is None:
            if key in st.query_params:
                del st.query_params[key]
        else:
            st.query_params[key] = str(value)
    except Exception:
        pass


def set_params(**kwargs):
    """Set multiple params sekaligus."""
    for k, v in kwargs.items():
        set_param(k, v)
