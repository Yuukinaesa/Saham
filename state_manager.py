import json
import os
import streamlit as st

CONFIG_FILE = 'user_config.json'

def load_config():
    """Load configuration from local JSON file into session state if available."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
            
            # Whitelist of keys to restore
            valid_keys = ['scraper_symbols', 'scraper_modal']
            for k, v in data.items():
                if k in valid_keys:
                    # Only set if not already set (to avoid overwriting user interaction in current session?)
                    # Actually, if we reload (F5), session state is empty. So this populates it.
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
