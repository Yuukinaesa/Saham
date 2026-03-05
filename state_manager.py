import json
import os
import streamlit as st

CONFIG_FILE = 'user_config.json'

# ─────────────────────────────────────────────
#  JSON-based persistence (existing, for scraper)
# ─────────────────────────────────────────────

def load_config():
    """Load configuration from local JSON file into session state if available."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
            valid_keys = ['scraper_symbols', 'scraper_modal']
            for k, v in data.items():
                if k in valid_keys:
                    if k not in st.session_state:
                        st.session_state[k] = v
        except Exception:
            pass

def save_config():
    """Save current relevant session state to local JSON file."""
    valid_keys = ['scraper_symbols', 'scraper_modal']
    data = {}
    for k in valid_keys:
        if k in st.session_state:
            data[k] = st.session_state[k]
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f)
    except Exception:
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
    """
    try:
        val = st.query_params.get(key, None)
        if val is None:
            return default
        # Auto-cast berdasarkan tipe default
        if isinstance(default, bool):
            return val.lower() in ('true', '1', 'yes')
        if isinstance(default, int):
            return int(val)
        if isinstance(default, float):
            return float(val)
        return val  # string
    except Exception:
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
