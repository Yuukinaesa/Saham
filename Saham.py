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
from pwa_setup import inject_pwa_support, inject_keepalive
from pages_trade_planner import trade_planner_page
from pages_analysis import analysis_dashboard_page
from pages_market_overview import market_overview_page
from pages_technical_tools import technical_tools_page
from pages_right_issue import right_issue_calculator_page
from state_manager import get_param, set_param

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

        /* Titles (Fluid Clamp Typography) */
        h1, h2, h3 {
            color: var(--text-color); 
            font-weight: 700; 
            letter-spacing: -0.025em;
        }
        h1 { font-size: clamp(1.5rem, 3.5vw + 0.8rem, 2.25rem); line-height: 1.25; }
        h2 { font-size: clamp(1.25rem, 2.5vw + 0.6rem, 1.65rem); line-height: 1.3; }
        h3 { font-size: clamp(1.05rem, 2vw + 0.5rem, 1.35rem); line-height: 1.35; }

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
        
        /* Touch-friendly input heights (WCAG 2.2 AA) */
        .stTextInput input,
        .stNumberInput input,
        .stSelectbox select {
            min-height: 44px !important;
        }

        /* Smooth touch scrolling for tables and charts */
        [data-testid="stDataFrame"],
        div[data-testid="stTable"] {
            -webkit-overflow-scrolling: touch !important;
            border-radius: 8px !important;
        }

        /* =======================================================
           RESPONSIVE MOBILE BREAKPOINTS (< 768px & < 640px)
           ======================================================= */
        @media screen and (max-width: 768px) {
            /* Transform left-column menu into a modern horizontal scrollable pill bar */
            div[data-testid="column"]:first-child {
                width: 100% !important;
                flex: 1 1 100% !important;
                margin-bottom: 0px !important;
            }
            div[data-testid="column"]:first-child h2 {
                display: none !important; /* Hide redundant Menu heading on mobile */
            }
            div[data-testid="column"]:first-child > div {
                padding: 0 !important;
            }

            .stOptionMenu ul.nav {
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                overflow-x: auto !important;
                overflow-y: hidden !important;
                -webkit-overflow-scrolling: touch !important;
                gap: 8px !important;
                padding: 4px 2px 12px 2px !important;
                scrollbar-width: thin !important;
            }
            .stOptionMenu ul.nav::-webkit-scrollbar {
                height: 4px;
            }
            .stOptionMenu ul.nav::-webkit-scrollbar-thumb {
                background: rgba(128, 128, 128, 0.35);
                border-radius: 4px;
            }
            .stOptionMenu ul.nav li.nav-item {
                flex: 0 0 auto !important;
                width: auto !important;
            }
            .stOptionMenu ul.nav a.nav-link {
                white-space: nowrap !important;
                padding: 8px 14px !important;
                font-size: 13px !important;
                border-radius: 9999px !important;
                border: 1px solid rgba(128, 128, 128, 0.25) !important;
                background-color: var(--secondary-background-color) !important;
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
                min-height: 40px !important;
                display: inline-flex !important;
                align-items: center !important;
            }
            .stOptionMenu ul.nav a.nav-link-selected {
                background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
                color: #ffffff !important;
                border-color: #1d4ed8 !important;
                border-left: none !important;
                font-weight: 600 !important;
                box-shadow: 0 3px 8px rgba(37, 99, 235, 0.3) !important;
            }
            .stOptionMenu ul.nav a.nav-link-selected i,
            .stOptionMenu ul.nav a.nav-link-selected svg {
                color: #ffffff !important;
            }
        }

        @media screen and (max-width: 640px) {
            /* Compact card padding on mobile screens to maximize readable area */
            .premium-card {
                padding: 16px !important;
                margin-bottom: 14px !important;
                border-radius: 10px !important;
            }

            /* Responsive stacking for custom multi-column grids in cards */
            .premium-card div[style*="grid-template-columns"] {
                grid-template-columns: 1fr !important;
                gap: 10px !important;
            }

            /* Full-width primary action buttons on mobile */
            div.stButton > button,
            div.stDownloadButton > button {
                width: 100% !important;
            }

            /* Compact metrics on mobile */
            div[data-testid="stMetric"] {
                padding: 10px 12px !important;
            }
            div[data-testid="stMetricLabel"] {
                font-size: 11px !important;
                white-space: normal !important;
                line-height: 1.25 !important;
            }
            div[data-testid="stMetricValue"] {
                font-size: 18px !important;
                line-height: 1.2 !important;
            }
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def main() -> None:
    try:
        locale.setlocale(locale.LC_ALL, "id_ID.UTF-8")
    except Exception:
        try:
            locale.setlocale(locale.LC_ALL, "Indonesian_Indonesia.1252")
        except Exception:
            pass

    st.set_page_config(
        page_title="Saham IDX",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    apply_global_css()
    inject_pwa_support()    # Inject PWA Manifest and Tags
    inject_keepalive(5)     # Ping setiap 5 menit agar tidak sleep
    
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
        
        _menu_items = [
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
            ]
        _saved_menu = get_param("menu", "Scraper Saham")
        _default_idx = _menu_items.index(_saved_menu) if _saved_menu in _menu_items else 0

        menu_selection = option_menu(
            None,
            _menu_items,
            icons=["graph-up", "search", "calculator", "grid", "tools", "activity", "clipboard-data", "bookmark", "percent", "briefcase", "ticket-perforated"],
            menu_icon="cast",
            default_index=_default_idx,
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

        # Simpan menu aktif ke URL agar ingat setelah refresh
        set_param("menu", menu_selection)

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
            platforms = list(PLATFORM_CONFIG.keys())
            calculator_submenu = option_menu(
                None,
                platforms,
                icons=["calculator"] * len(platforms),
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
