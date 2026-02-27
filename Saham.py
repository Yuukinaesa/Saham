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
from pwa_setup import inject_pwa_support
from pages_trade_planner import trade_planner_page
from pages_analysis import analysis_dashboard_page
from pages_market_overview import market_overview_page
from pages_technical_tools import technical_tools_page
from pages_right_issue import right_issue_calculator_page
from state_manager import load_config

def apply_global_css() -> None:
    """Menerapkan styling global premium dengan Google Fonts (Inter) dan desain modern."""
    css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* Global Reset & Typography */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
            color: var(--text-color);
            background-color: var(--background-color);
        }

        /* Titles */
        h1, h2, h3 {
            color: var(--text-color); 
            font-weight: 700; 
            letter-spacing: -0.025em;
        }
        h1 { font-size: 2.25rem; }
        h2 { font-size: 1.5rem; }
        h3 { font-size: 1.25rem; }

        /* Buttons (Premium Gradient & Shadow) */
        div.stButton > button {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            font-size: 15px;
            transition: all 0.2s ease-in-out;
            box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
            height: auto;
            min-height: 44px;
        }
        div.stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 12px -1px rgba(37, 99, 235, 0.3);
            background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
            border-color: #1e40af;
        }
        div.stButton > button:active {
            transform: translateY(0);
        }

        /* Inputs (Clean & Focused) */
        .stTextInput > div > div > input, 
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > div {
            border-radius: 8px;
            border: 1px solid var(--secondary-background-color);
            background-color: var(--secondary-background-color);
            color: var(--text-color);
            padding: 10px 12px;
            font-size: 14px;
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        .stTextInput > div > div > input:focus, 
        .stNumberInput > div > div > input:focus {
            border-color: #2563eb;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
            outline: none;
        }

        /* Cards/Containers */
        .premium-card {
            background-color: var(--secondary-background-color);
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            border: 1px solid rgba(128, 128, 128, 0.1);
            margin-bottom: 20px;
        }

        /* DataFrames/Tables */
        .dataframe {
            border: 1px solid var(--secondary-background-color) !important;
            border-radius: 8px !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 13px !important;
        }
        
        /* Metric/Stats Cards */
        div[data-testid="stMetric"] {
            background-color: var(--secondary-background-color);
            padding: 16px;
            border-radius: 8px;
            border: 1px solid rgba(128, 128, 128, 0.1);
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); /* Subtle shadow even in dark mode */
        }
        div[data-testid="stMetricLabel"] { font-size: 13px; color: var(--text-color); opacity: 0.8; font-weight: 500; }
        div[data-testid="stMetricValue"] { font-size: 24px; color: var(--text-color); font-weight: 700; }
        div[data-testid="stMetric"] > div {
             color: var(--text-color) !important;
        }
        
        /* Custom Section Title */
        .section-title {
            color: var(--text-color);
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            margin-top: 2rem;
        }
        
        /* Sidebar Navigation */
        section[data-testid="stSidebar"] {
            background-color: var(--secondary-background-color);
            border-right: 1px solid rgba(128, 128, 128, 0.2);
        }
        
        /* Option Menu */
        .stOptionMenu {
            background: transparent !important;
        }
        .nav-link {
            border-radius: 6px !important;
            margin-bottom: 4px !important;
            font-weight: 500 !important;
            color: var(--text-color) !important;
        }
        .nav-link:hover {
            background-color: rgba(128, 128, 128, 0.1) !important;
            color: var(--text-color) !important;
        }
        .nav-link-selected {
            background-color: rgba(37, 99, 235, 0.1) !important;
            color: #3b82f6 !important;
            font-weight: 600 !important;
            border-left: 3px solid #2563eb;
            border-radius: 0 6px 6px 0 !important;
        }
        
        /* Custom Classes */
        .text-success { color: #10b981; font-weight: 600; }
        .text-danger { color: #ef4444; font-weight: 600; }
        .text-muted { color: var(--text-color); opacity: 0.7; font-size: 14px; }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: var(--secondary-background-color) !important;
            border-radius: 8px !important;
            border: 1px solid rgba(128, 128, 128, 0.2);
            color: var(--text-color) !important;
            font-weight: 600 !important;
        }
        
        /* Alert Info / Success / Warning / Error */
        .stAlert {
            background-color: transparent !important;
            border: 1px solid rgba(128, 128, 128, 0.2) !important;
            color: var(--text-color) !important;
            border-radius: 8px !important;
        }
        
        /* Adjust specific alert colors if possible, but stAlert catches inner content usually. 
           We can rely on Streamlit's default colorful left border, or style specific types if needed.
           For better dark mode, we just ensure the big block isn't white. 
        */
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
    # Load persistence
    load_config()
    
    apply_global_css()
    inject_pwa_support() # Inject PWA Manifest and Tags
    
    col1, col2 = st.columns([1, 4], gap="small")
    
    with col1:
        st.markdown(
            """
        <div style='padding: 12px 0;'>
            <h2>Menu</h2>
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
                "Market Overview",
                "Technical Tools",
                "Analisa Lengkap",
                "Trade Planner",
                "Compound Interest",
                "ARA ARB Calculator",
                "Right Issue Calculator",
                "Warrant Calculator"
            ],
            icons=["graph-up", "search", "calculator", "grid", "tools", "activity", "clipboard-data", "bookmark", "percent", "briefcase", "ticket-perforated"],
            menu_icon="cast",
            default_index=0,
            orientation="vertical",
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#2563eb", "font-size": "14px"}, 
                "nav-link": {"font-size": "14px", "text-align": "left", "margin": "0px", "--hover-color": "rgba(128, 128, 128, 0.1)"},
                "nav-link-selected": {"background-color": "rgba(37, 99, 235, 0.1)", "color": "#3b82f6"},
            },
        )

    with col2:
        st.markdown(
            """
        <div style='margin-bottom: 24px;'>
            <h1 style='margin-bottom: 8px;'>Saham IDX</h1>
            <p style='color: var(--text-color); opacity: 0.8; font-size: 1.1em; margin: 0; font-weight: 500;'>Investasi Saham Lebih Mudah dan Terstruktur</p>
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
                <h3 style='color: var(--text-color); margin-bottom: 12px;'>Pilih Platform</h3>
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
                    "nav-link": {"font-size": "14px", "text-align": "left", "margin": "0px", "--hover-color": "rgba(128, 128, 128, 0.1)"},
                    "nav-link-selected": {"background-color": "rgba(37, 99, 235, 0.1)", "color": "#3b82f6"},
                },
            )
            fee_beli, fee_jual = PLATFORM_CONFIG.get(calculator_submenu, (0, 0))
            calculator_page(calculator_submenu, fee_beli, fee_jual)
        elif menu_selection == "Market Overview":
            market_overview_page()
        elif menu_selection == "Technical Tools":
            technical_tools_page()
        elif menu_selection == "Analisa Lengkap":
            analysis_dashboard_page()
        elif menu_selection == "Trade Planner":
            trade_planner_page()
        elif menu_selection == "Compound Interest":
            compound_interest_page()
        elif menu_selection == "ARA ARB Calculator":
            ara_arb_calculator_page()
        elif menu_selection == "Right Issue Calculator":
            right_issue_calculator_page()
        elif menu_selection == "Warrant Calculator":
            warrant_calculator_page()


if __name__ == "__main__":
    main()
