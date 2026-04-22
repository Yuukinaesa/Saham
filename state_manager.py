import math
import streamlit as st


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
        # Security: Reject null bytes and control characters
        if isinstance(val, str) and any(ord(c) < 32 for c in val):
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
