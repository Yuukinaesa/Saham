import locale
import streamlit as st
from streamlit_option_menu import option_menu

from config import PLATFORM_CONFIG
from pages_scraper import stock_scraper_page
from pages_screener import stock_screener_page
from pages_calculators import calculator_page
from pages_compound import compound_interest_page
from pages_ara_arb import ara_arb_calculator_page
from pages_warrant import warrant_calculator_page


def apply_global_css() -> None:
    css = """
    <style>
        h1, h2, h3 { color: #1a1a1a; margin-bottom: 20px; font-weight: 700; letter-spacing: -0.5px; }
        div.stButton > button { background-color: #2563eb; color: white; width: 100%; height: 48px; font-size: 16px; border-radius: 8px; border: none; font-weight: 600; }
        div.stButton > button:hover { background-color: #1d4ed8; }
        .stTextInput > div > div > input, .stNumberInput > div > div > input { border-radius: 8px; border: 1px solid #e5e7eb; padding: 12px; font-size: 15px; background-color: #f9fafb; }
        .stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus { border-color: #2563eb; box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1); background-color: #ffffff; }
        .streamlit-expanderHeader { background-color: #f9fafb; padding: 12px; font-weight: 600; border-radius: 8px; color: #1a1a1a; }
        .dataframe { border-radius: 8px; overflow: hidden; border: 1px solid #e5e7eb; }
        .stAlert { border-radius: 8px; padding: 12px; }
        .section-title { color: #1a1a1a; font-size: 1.1em; font-weight: 600; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
        .stOptionMenu { background-color: #f9fafb; border-radius: 8px; border: 1px solid #e5e7eb; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def main() -> None:
    try:
        locale.setlocale(locale.LC_ALL, "id_ID.UTF-8")
    except Exception:
        pass

    st.set_page_config(
        page_title="Saham IDX",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_global_css()
    
    col1, col2 = st.columns([1, 4], gap="small")
    
    with col1:
        st.markdown(
            """
        <div style='padding: 12px;'>
            <h2 style='color: #1a1a1a; margin-bottom: 16px;'>Menu</h2>
        </div>
            """,
            unsafe_allow_html=True,
        )
        
        menu_selection = option_menu(
            None,
            [
                "Scraper Saham",
                "Screener Saham",
                "Kalkulator Saham",
                "Compound Interest",
                "ARA ARB Calculator",
                "Warrant Calculator",
            ],
            icons=["graph-up", "search", "calculator", "bookmark", "percent", "ticket-perforated"],
            menu_icon="cast",
            default_index=0,
            orientation="vertical",
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#2563eb", "font-size": "14px"}, 
                "nav-link": {"font-size": "14px", "text-align": "left", "margin": "0px", "--hover-color": "#e5e7eb"},
                "nav-link-selected": {"background-color": "#2563eb"},
            },
        )

    with col2:
        st.markdown(
            """
        <div style='margin-bottom: 16px;'>
            <h1 style='color: #1a1a1a; font-size: 2em; margin-bottom: 4px; letter-spacing: -1px;'>Saham IDX</h1>
            <p style='color: #6b7280; font-size: 1em; margin: 0;'>Investasi Saham Lebih Mudah dan Terstruktur</p>
        </div>
            """,
            unsafe_allow_html=True,
        )

        if menu_selection == "Scraper Saham":
            stock_scraper_page()
        elif menu_selection == "Screener Saham":
            stock_screener_page()
        elif menu_selection == "Kalkulator Saham":
            st.markdown(
                """
            <div style='margin-bottom: 16px;'>
                <h3 style='color: #1a1a1a; margin-bottom: 12px;'>Pilih Platform</h3>
            </div>
                """,
                unsafe_allow_html=True,
            )
            calculator_submenu = option_menu(
                None,
                ["IPOT", "Stockbit", "BNI Bions", "Custom"],
                icons=["calculator", "calculator", "calculator", "calculator"],
                menu_icon="calculator",
                default_index=0,
                orientation="horizontal",
                styles={
                    "container": {"padding": "0!important", "background-color": "transparent"},
                    "icon": {"color": "#2563eb", "font-size": "14px"}, 
                    "nav-link": {"font-size": "14px", "text-align": "left", "margin": "0px", "--hover-color": "#e5e7eb"},
                    "nav-link-selected": {"background-color": "#2563eb"},
                },
            )
            fee_beli, fee_jual = PLATFORM_CONFIG.get(calculator_submenu, (0, 0))
            calculator_page(calculator_submenu, fee_beli, fee_jual)
        elif menu_selection == "Compound Interest":
            compound_interest_page()
        elif menu_selection == "ARA ARB Calculator":
            ara_arb_calculator_page()
        elif menu_selection == "Warrant Calculator":
            warrant_calculator_page()


if __name__ == "__main__":
    main()
