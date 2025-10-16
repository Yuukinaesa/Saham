import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_option_menu import option_menu
from typing import Dict, List, Tuple
import re
import locale
import numpy as np
import time

# Set locale untuk format Rupiah
try:
    locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
except Exception:
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except Exception:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except Exception:
            # Jika semua locale gagal, gunakan default
            pass

# Konstanta
DEFAULT_SYMBOLS = 'BBCA, BBRI, BYAN, BMRI, TLKM, ASII, TPIA, BBNI, UNVR, HMSP'
FRACSI_HARGA_DATA = {
    "Harga Saham": ["< Rp 200", "Rp 200 - Rp 500", "Rp 500 - Rp 2.000", "Rp 2.000 - Rp 5.000", "Rp 5.000+"],
    "Fraksi Harga": ["Rp 1", "Rp 2", "Rp 5", "Rp 10", "Rp 25"]
}

# Konfigurasi platform
PLATFORM_CONFIG = {
    "IPOT": (0.0019, 0.0029),
    "Stockbit": (0.0015, 0.0025),
    "BNI Bions": (0.0017, 0.0027),
    "Custom": (0, 0)
}

# Fokus pada Yahoo Finance untuk data saham Indonesia

def apply_global_css() -> None:
    """Menerapkan styling global ke aplikasi Streamlit."""
    css = """
    <style>
        /* Styling untuk container utama */
        .stContainer {
            background-color: #ffffff;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        /* Styling untuk header */
        h1, h2, h3 {
            color: #1a1a1a;
            margin-bottom: 20px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        
        /* Styling untuk tombol */
        div.stButton > button {
            background-color: #2563eb;
            color: white;
            width: 100%;
            height: 48px;
            font-size: 16px;
            border-radius: 8px;
            transition: all 0.2s ease;
            border: none;
            font-weight: 600;
            box-shadow: none;
        }
        div.stButton > button:hover {
            background-color: #1d4ed8;
            transform: translateY(-1px);
            box-shadow: 0 4px 6px rgba(37, 99, 235, 0.1);
        }
        
        /* Styling untuk input fields */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input {
            border-radius: 8px;
            border: 1px solid #e5e7eb;
            padding: 12px;
            font-size: 15px;
            transition: all 0.2s ease;
            background-color: #f9fafb;
        }
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus {
            border-color: #2563eb;
            box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
            background-color: #ffffff;
        }
        
        /* Styling untuk expander */
        .streamlit-expanderHeader {
            background-color: #f9fafb;
            padding: 12px;
            font-weight: 600;
            border-radius: 8px;
            color: #1a1a1a;
        }
        
        /* Styling untuk tabel */
        .dataframe {
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #e5e7eb;
        }
        
        /* Styling untuk alert messages */
        .stAlert {
            border-radius: 8px;
            padding: 12px;
        }
        
        /* Styling untuk info box */
        .info-box {
            background-color: #eff6ff;
            padding: 16px;
            margin-bottom: 16px;
            border-radius: 8px;
            border: 1px solid #dbeafe;
        }
        
        /* Styling untuk result box */
        .result-box {
            background-color: #f9fafb;
            padding: 20px;
            margin: 16px 0;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }
        
        /* Styling untuk radio buttons */
        .stRadio > div {
            background-color: #f9fafb;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }
        
        /* Styling untuk checkboxes */
        .stCheckbox > div {
            background-color: #f9fafb;
            padding: 8px;
            border-radius: 8px;
        }

        /* Styling untuk sidebar */
        .sidebar-container {
            background-color: #f9fafb;
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 16px;
            border: 1px solid #e5e7eb;
        }

        /* Styling untuk section title */
        .section-title {
            color: #1a1a1a;
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* Styling untuk menu */
        .stOptionMenu {
            background-color: #f9fafb;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }

        /* Styling untuk divider */
        .divider {
            height: 1px;
            background-color: #e5e7eb;
            margin: 16px 0;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def initialize_session_state(key: str, default_value: any) -> None:
    """Inisialisasi session state jika belum ada.
    
    Args:
        key (str): Kunci untuk session state
        default_value (any): Nilai default jika key belum ada
    """
    if key not in st.session_state:
        st.session_state[key] = default_value

def format_dataframe(df: pd.DataFrame, format_dict: Dict[str, str]) -> pd.DataFrame:
    """Memformat dataframe sesuai dengan format yang ditentukan.
    
    Args:
        df (pd.DataFrame): Dataframe yang akan diformat
        format_dict (Dict[str, str]): Dictionary berisi format untuk setiap kolom
        
    Returns:
        pd.DataFrame: Dataframe yang sudah diformat
    """
    return df.style.format(format_dict)

def sanitize_stock_symbol(symbol: str) -> str:
    """Membersihkan simbol saham dari karakter yang tidak valid.
    
    Args:
        symbol (str): Simbol saham yang akan dibersihkan
        
    Returns:
        str: Simbol saham yang sudah dibersihkan
    """
    # Hanya mengizinkan huruf, angka, dan titik
    return re.sub(r'[^a-zA-Z0-9.]', '', symbol)

def fetch_stock_data(symbols: List[str]) -> Dict[str, Dict[str, float]]:
    """Mengambil data saham dari Yahoo Finance.
    
    Args:
        symbols (List[str]): List simbol saham
        
    Returns:
        Dict[str, Dict[str, float]]: Dictionary berisi data saham
        
    Raises:
        Exception: Jika terjadi error saat mengambil data
    """
    data = {}
    for symbol in symbols:
        try:
            # Pastikan simbol memiliki format yang benar
            if not symbol.endswith('.JK'):
                symbol = f"{symbol}.JK"
                
            stock = yf.Ticker(symbol)
            info = stock.info
            
            if not info:
                st.warning(f"Tidak ada info untuk {symbol}")
                continue
                
            # Coba beberapa kunci untuk mendapatkan harga
            current_price = None
            price_keys = ['regularMarketPrice', 'regularMarketPreviousClose', 'currentPrice', 'previousClose']
            for key in price_keys:
                if key in info and info[key] is not None and info[key] > 0:
                    current_price = info[key]
                    break
            
            if current_price is None:
                st.warning(f"Tidak dapat menemukan harga valid untuk {symbol}")
                continue
            
            # Handle infinity values untuk semua metrics
            def safe_float(value, default=0):
                if value is None or pd.isna(value):
                    return default
                if value == float('inf') or value == float('-inf'):
                    return default
                return float(value)
            
            # Pastikan nilai persentase dalam bentuk desimal
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
            st.error(f"Error saat mengambil data {symbol}: {str(e)}")
            continue
            
    return data

def validate_calculator_inputs(jumlah_lot: int, harga_beli: float, harga_jual: float) -> Tuple[bool, str]:
    """Validasi input kalkulator.
    
    Args:
        jumlah_lot (int): Jumlah lot
        harga_beli (float): Harga beli per saham
        harga_jual (float): Harga jual per saham
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if jumlah_lot <= 0:
        return False, "Jumlah lot harus lebih dari 0"
    if harga_beli <= 0:
        return False, "Harga beli harus lebih dari 0"
    if harga_jual <= 0:
        return False, "Harga jual harus lebih dari 0"
    return True, ""

def calculate_profit_loss(jumlah_lot: int, harga_beli: float, harga_jual: float, 
                         fee_beli: float, fee_jual: float) -> Tuple[float, float, float, float]:
    """Menghitung profit atau loss dari transaksi saham.
    
    Args:
        jumlah_lot (int): Jumlah lot
        harga_beli (float): Harga beli per saham
        harga_jual (float): Harga jual per saham
        fee_beli (float): Fee beli dalam desimal
        fee_jual (float): Fee jual dalam desimal
        
    Returns:
        Tuple[float, float, float, float]: (total_beli, total_jual, profit_loss, profit_loss_percentage)
    """
    jumlah_saham = jumlah_lot * 100
    total_beli = jumlah_saham * harga_beli
    total_fee_beli = total_beli * fee_beli
    total_beli += total_fee_beli
    
    total_jual = jumlah_saham * harga_jual
    total_fee_jual = total_jual * fee_jual
    total_jual -= total_fee_jual
    
    profit_loss = total_jual - total_beli
    profit_loss_percentage = (profit_loss / total_beli) * 100 if total_beli != 0 else 0
    
    # Bulatkan ke 2 desimal
    return (
        round(total_beli, 2),
        round(total_jual, 2),
        round(profit_loss, 2),
        round(profit_loss_percentage, 2)
    )

def calculate_multiple_stocks_profit_loss(stocks_data: List[Dict]) -> Dict:
    """Menghitung profit/loss untuk multiple saham.
    
    Args:
        stocks_data (List[Dict]): List berisi data saham dengan format:
            {
                'symbol': str,
                'jumlah_lot': int,
                'harga_beli': float,
                'harga_jual': float,
                'fee_beli': float,
                'fee_jual': float
            }
        
    Returns:
        Dict: Dictionary berisi hasil perhitungan
    """
    total_investment = 0
    total_proceeds = 0
    total_profit_loss = 0
    total_fee_beli = 0
    total_fee_jual = 0
    stocks_results = []
    
    for stock in stocks_data:
        # Hitung per saham
        total_beli, total_jual, profit_loss, profit_loss_percentage = calculate_profit_loss(
            stock['jumlah_lot'], 
            stock['harga_beli'], 
            stock['harga_jual'], 
            stock['fee_beli'], 
            stock['fee_jual']
        )
        
        # Hitung fee
        jumlah_saham = stock['jumlah_lot'] * 100
        fee_beli = jumlah_saham * stock['harga_beli'] * stock['fee_beli']
        fee_jual = jumlah_saham * stock['harga_jual'] * stock['fee_jual']
        
        # Tambahkan ke total
        total_investment += total_beli
        total_proceeds += total_jual
        total_profit_loss += profit_loss
        total_fee_beli += fee_beli
        total_fee_jual += fee_jual
        
        # Simpan hasil per saham
        stocks_results.append({
            'symbol': stock['symbol'],
            'jumlah_lot': stock['jumlah_lot'],
            'harga_beli': stock['harga_beli'],
            'harga_jual': stock['harga_jual'],
            'total_beli': total_beli,
            'total_jual': total_jual,
            'profit_loss': profit_loss,
            'profit_loss_percentage': profit_loss_percentage,
            'fee_beli': fee_beli,
            'fee_jual': fee_jual
        })
    
    # Hitung total profit/loss percentage
    total_profit_loss_percentage = (total_profit_loss / total_investment) * 100 if total_investment != 0 else 0
    
    return {
        'total_investment': round(total_investment, 2),
        'total_proceeds': round(total_proceeds, 2),
        'total_profit_loss': round(total_profit_loss, 2),
        'total_profit_loss_percentage': round(total_profit_loss_percentage, 2),
        'total_fee_beli': round(total_fee_beli, 2),
        'total_fee_jual': round(total_fee_jual, 2),
        'stocks_results': stocks_results
    }

def calculate_realized_gain(initial_investment: float, current_value: float, 
                          dividends_received: float = 0, fees_paid: float = 0) -> Dict:
    """Menghitung realized gain/loss.
    
    Args:
        initial_investment (float): Investasi awal
        current_value (float): Nilai saat ini
        dividends_received (float): Total dividen yang diterima
        fees_paid (float): Total fee yang dibayar
        
    Returns:
        Dict: Dictionary berisi hasil perhitungan realized gain
    """
    # Hitung capital gain/loss
    capital_gain_loss = current_value - initial_investment
    
    # Hitung total return (capital gain + dividen - fees)
    total_return = capital_gain_loss + dividends_received - fees_paid
    
    # Hitung percentage return
    capital_gain_percentage = (capital_gain_loss / initial_investment) * 100 if initial_investment != 0 else 0
    total_return_percentage = (total_return / initial_investment) * 100 if initial_investment != 0 else 0
    
    # Hitung ROI (Return on Investment)
    roi = (total_return / initial_investment) * 100 if initial_investment != 0 else 0
    
    return {
        'initial_investment': round(initial_investment, 2),
        'current_value': round(current_value, 2),
        'capital_gain_loss': round(capital_gain_loss, 2),
        'dividends_received': round(dividends_received, 2),
        'fees_paid': round(fees_paid, 2),
        'total_return': round(total_return, 2),
        'capital_gain_percentage': round(capital_gain_percentage, 2),
        'total_return_percentage': round(total_return_percentage, 2),
        'roi': round(roi, 2)
    }

def calculate_dividend(jumlah_lot: int, dividen_per_saham: float) -> float:
    """Menghitung total dividen yang diterima.
    
    Args:
        jumlah_lot (int): Jumlah lot
        dividen_per_saham (float): Dividen per saham
        
    Returns:
        float: Total dividen
    """
    jumlah_saham = jumlah_lot * 100
    return jumlah_saham * dividen_per_saham if dividen_per_saham != 0 else 0

def calculate_dividend_yield(dividen_per_saham: float, harga_beli: float) -> float:
    """Menghitung dividend yield.
    
    Args:
        dividen_per_saham (float): Dividen per saham
        harga_beli (float): Harga beli per saham
        
    Returns:
        float: Dividend yield dalam persentase
    """
    return (dividen_per_saham / harga_beli) * 100 if harga_beli != 0 else 0

def display_loading_indicator(message: str = "Memproses...") -> None:
    """Menampilkan indikator loading.
    
    Args:
        message (str): Pesan yang ditampilkan
    """
    st.markdown(f'<div class="loading"></div> {message}', unsafe_allow_html=True)

def format_percent(value: float, decimals: int = 2) -> str:
    """Format angka menjadi persentase yang rapi.
    
    Args:
        value (float): Nilai yang akan diformat
        decimals (int): Jumlah desimal
        
    Returns:
        str: String yang sudah diformat dalam format persentase
    """
    try:
        # Konversi ke float jika belum
        value = float(value) if not isinstance(value, (int, float)) else value
        
        if pd.isna(value) or value == 0:
            return "0,00%"
            
        # Format langsung sebagai persentase (nilai sudah dalam bentuk persentase)
        if decimals == 2:
            return f"{value:,.2f}%".replace(".", ",")
        return f"{value:,.{decimals}f}%".replace(".", ",")
    except (ValueError, TypeError):
        return "0,00%"

def format_rupiah(value: float) -> str:
    """Format angka menjadi format Rupiah yang rapi.
    
    Args:
        value (float): Nilai yang akan diformat
        
    Returns:
        str: String yang sudah diformat dalam format Rupiah
    """
    try:
        # Konversi ke float jika belum
        value = float(value) if not isinstance(value, (int, float)) else value
        
        if pd.isna(value) or value == 0:
            return "Rp 0"
        return f"Rp {value:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return "Rp 0"

def format_short_number(value: float) -> str:
    """Format angka besar menjadi format singkat (T, M, B).
    
    Args:
        value (float): Nilai yang akan diformat
        
    Returns:
        str: String yang sudah diformat dalam format singkat
    """
    try:
        # Konversi ke float jika belum
        value = float(value) if not isinstance(value, (int, float)) else value
        
        if pd.isna(value) or value == 0:
            return "0"
        
        # Triliun (T)
        if abs(value) >= 1e12:
            return f"{value/1e12:.1f} T"
        # Miliar (B)
        elif abs(value) >= 1e9:
            return f"{value/1e9:.1f} B"
        # Juta (M)
        elif abs(value) >= 1e6:
            return f"{value/1e6:.1f} M"
        # Ribu (K)
        elif abs(value) >= 1e3:
            return f"{value/1e3:.1f} K"
        else:
            return f"{value:.0f}"
    except (ValueError, TypeError):
        return "0"

def format_csv_indonesia(value: float, decimals: int = 2) -> str:
    """Format angka untuk CSV dengan format Indonesia (koma sebagai desimal, titik sebagai ribuan).
    
    Args:
        value (float): Nilai yang akan diformat
        decimals (int): Jumlah desimal
        
    Returns:
        str: String yang sudah diformat untuk CSV Indonesia
    """
    try:
        value = float(value) if not isinstance(value, (int, float)) else value
        if pd.isna(value) or value == 0:
            return "0"
        
        # Format dengan koma sebagai desimal dan titik sebagai ribuan
        if decimals == 0:
            return f"{value:,.0f}".replace(",", ".")
        else:
            return f"{value:,.{decimals}f}".replace(",", ".")
    except (ValueError, TypeError):
        return "0"

def format_number(value: float, decimals: int = 2) -> str:
    """Format angka menjadi format yang rapi.
    
    Args:
        value (float): Nilai yang akan diformat
        decimals (int): Jumlah desimal
        
    Returns:
        str: String yang sudah diformat
    """
    try:
        # Konversi ke float jika belum
        value = float(value) if not isinstance(value, (int, float)) else value
        
        if pd.isna(value) or value == 0:
            return "0"
        if decimals == 0:
            return f"{value:,.0f}".replace(",", ".")
        return f"{value:,.{decimals}f}".replace(".", ",")
    except (ValueError, TypeError):
        return "0"

def format_ratio(value: float) -> str:
    """Format angka untuk rasio (PBVR, PER, DER).
    
    Args:
        value (float): Nilai yang akan diformat
        
    Returns:
        str: String yang sudah diformat
    """
    try:
        # Konversi ke float jika belum
        value = float(value) if not isinstance(value, (int, float)) else value
        
        if pd.isna(value) or value == 0:
            return "0,00"
        return f"{value:,.2f}".replace(".", ",")
    except (ValueError, TypeError):
        return "0,00"

def stock_scraper_page() -> None:
    """Halaman untuk scraper saham."""
    st.info('**Catatan: Data berasal dari Yahoo Finance. Pembelian disesuaikan dengan modal untuk jumlah lot yang sesuai.**')
    
    # Input section
    col1, col2 = st.columns(2, gap="small")
    with col1:
        symbols = st.text_area('Masukkan simbol saham (pisahkan dengan koma)', DEFAULT_SYMBOLS)
    with col2:
        modal_rupiah = st.number_input("Masukkan modal dalam Rupiah", step=1000000, format="%d", min_value=0, value=1000000)

    if st.button('Ambil Data', key='fetch_data'):
        with st.spinner('Mengambil data saham...'):
            try:
                symbols_list = [
                    sanitize_stock_symbol(symbol.strip().upper()) + '.JK' 
                    if '.JK' not in symbol.strip().upper() 
                    else sanitize_stock_symbol(symbol.strip().upper())
                    for symbol in symbols.split(',')
                ]

                stocks_data = fetch_stock_data(symbols_list)
                if not stocks_data:
                    st.error("Tidak ada data saham yang berhasil diambil")
                    return
                    
                # Konversi ke DataFrame
                df = pd.DataFrame(stocks_data).T
                
                # Konversi kolom numerik dan handle infinity
                numeric_columns = ['Current Price', 'Price/Book (PBVR)', 'Trailing P/E (PER)', 
                                 'Total Debt/Equity (mrq) (DER)', 'Return on Equity (%) (ROE)',
                                 'Diluted EPS (ttm) (EPS)', 'Forward Annual Dividend Rate (DPS)',
                                 'Forward Annual Dividend Yield (%)']
                
                for col in numeric_columns:
                    if col in df.columns:
                        # Konversi ke float dan ganti infinity dengan 0
                        df[col] = pd.to_numeric(df[col], errors='coerce').replace([np.inf, -np.inf], 0)

                # Menghitung jumlah saham dan lot
                # Pastikan Current Price tidak 0 atau negatif
                df['Current Price'] = df['Current Price'].abs()
                df['Current Price'] = df['Current Price'].replace(0, pd.NA)
                # Pastikan harga tidak terlalu kecil
                df['Current Price'] = df['Current Price'].apply(lambda x: max(1, x) if pd.notna(x) else x)
                
                # Pastikan modal valid
                modal_rupiah = max(0, abs(modal_rupiah))
                
                # Hitung jumlah saham dan lot
                df['Jumlah Saham'] = (modal_rupiah / df['Current Price']).fillna(0)
                df['Jumlah Saham'] = pd.to_numeric(df['Jumlah Saham'], errors='coerce')
                # Pastikan jumlah saham dalam kelipatan 100
                df['Jumlah Lot'] = (df['Jumlah Saham'] // 100).fillna(0).astype('Int64')
                df['Jumlah Saham'] = df['Jumlah Lot'] * 100

                # Menghitung dividen dan modal
                # Pastikan Forward Annual Dividend Rate (DPS) valid
                df['Forward Annual Dividend Rate (DPS)'] = df['Forward Annual Dividend Rate (DPS)'].abs()
                df['Forward Annual Dividend Rate (DPS)'] = df['Forward Annual Dividend Rate (DPS)'].fillna(0)
                df['Dividen'] = df['Jumlah Saham'] * df['Forward Annual Dividend Rate (DPS)']
                
                # Hitung modal
                df['Modal'] = df['Jumlah Saham'] * df['Current Price']
                
                # Bulatkan semua nilai numerik
                numeric_columns = ['Current Price', 'Price/Book (PBVR)', 'Trailing P/E (PER)', 
                                 'Total Debt/Equity (mrq) (DER)', 'Return on Equity (%) (ROE)',
                                 'Diluted EPS (ttm) (EPS)', 'Forward Annual Dividend Rate (DPS)',
                                 'Forward Annual Dividend Yield (%)', 'Dividen', 'Modal']
                
                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = df[col].round(2)

                # Memformat dataframe
                format_dict = {
                    'Current Price': lambda x: format_rupiah(x),
                    'Price/Book (PBVR)': lambda x: format_ratio(x),
                    'Trailing P/E (PER)': lambda x: format_ratio(x),
                    'Total Debt/Equity (mrq) (DER)': lambda x: format_ratio(x),
                    'Return on Equity (%) (ROE)': lambda x: f"{round((x or 0)*100):.0f}%",
                    'Diluted EPS (ttm) (EPS)': lambda x: format_rupiah(x),
                    'Forward Annual Dividend Rate (DPS)': lambda x: format_rupiah(x),
                    'Forward Annual Dividend Yield (%)': lambda x: format_percent(x, 2),
                    'Jumlah Saham': lambda x: format_number(x, 0),
                    'Dividen': lambda x: format_rupiah(x),
                    'Jumlah Lot': lambda x: format_number(x, 0),
                    'Modal': lambda x: format_rupiah(x)
                }
                
                with st.expander("Tampilkan Data Statistik", expanded=True):
                    # Filter hanya saham yang valid (harga > 0)
                    df_display = df[df['Current Price'] > 0].copy()
                    df_display = df_display.reset_index(drop=True)
                    df_display.index = df_display.index + 1
                    
                    # Hitung tinggi tabel berdasarkan jumlah saham valid
                    table_height = min(400, len(df_display) * 40 + 50)
                    
                    st.dataframe(
                        format_dataframe(df_display, format_dict),
                        use_container_width=True,
                        height=table_height
                    )
                    
                    # Download CSV untuk scraper saham dengan format Indonesia
                    df_download = df_display.copy()
                    
                    # Format kolom untuk download dengan format Indonesia
                    for col in df_download.columns:
                        if col in ['Current Price', 'Forward Annual Dividend Rate (DPS)', 'Dividen', 'Modal']:
                            # Format Rupiah untuk download dengan format Indonesia
                            df_download[col] = df_download[col].apply(lambda x: format_csv_indonesia(x, 0) if pd.notna(x) else "0")
                        elif col in ['Price/Book (PBVR)', 'Trailing P/E (PER)', 'Total Debt/Equity (mrq) (DER)']:
                            # Format ratio untuk download dengan format Indonesia
                            df_download[col] = df_download[col].apply(lambda x: format_csv_indonesia(x, 2) if pd.notna(x) else "0")
                        elif col in ['Return on Equity (%) (ROE)', 'Forward Annual Dividend Yield (%)']:
                            # Format persentase untuk download dengan format Indonesia
                            df_download[col] = df_download[col].apply(lambda x: format_csv_indonesia(x, 2) if pd.notna(x) else "0")
                        elif col in ['Diluted EPS (ttm) (EPS)']:
                            # Format EPS untuk download dengan format Indonesia
                            df_download[col] = df_download[col].apply(lambda x: format_csv_indonesia(x, 0) if pd.notna(x) else "0")
                    
                    csv = df_download.to_csv(index=False, sep=';', encoding='utf-8-sig', quoting=1)
                    st.download_button(
                        label="📥 Download as CSV",
                        data=csv,
                        file_name="scraper_saham.csv",
                        mime="text/csv"
                    )

            except Exception as e:
                st.error(f"Terjadi kesalahan: {str(e)}")


def fetch_enhanced_stock_data(symbols: List[str]) -> Dict[str, Dict[str, float]]:
    """Mengambil data saham yang lebih lengkap untuk screener dengan multiple sources.
    
    Args:
        symbols (List[str]): List simbol saham
        
    Returns:
        Dict[str, Dict[str, float]]: Dictionary berisi data saham yang lebih lengkap
    """
    data = {}
    
    # Loading indicator sederhana
    if len(symbols) > 5:
        with st.spinner("Menganalisis saham..."):
            pass
    
    for i, symbol in enumerate(symbols):
        try:
            
            # Pastikan simbol memiliki format yang benar
            if not symbol.endswith('.JK'):
                symbol = f"{symbol}.JK"
                
            # Coba mengambil data dengan retry mechanism
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    stock = yf.Ticker(symbol)
                    info = stock.info
                    
                    # Jika info kosong, coba lagi
                    if not info or len(info) < 5:
                        if attempt < max_retries - 1:
                            time.sleep(1)  # Tunggu 1 detik sebelum retry
                            continue
                        else:
                            st.warning(f"Tidak ada data lengkap untuk {symbol}")
                            break
                    
                    # Coba beberapa kunci untuk mendapatkan harga dengan prioritas
                    current_price = None
                    price_keys = [
                        'regularMarketPrice', 'currentPrice', 'regularMarketPreviousClose', 
                        'previousClose', 'ask', 'bid', 'open'
                    ]
                    
                    for key in price_keys:
                        if key in info and info[key] is not None and info[key] > 0:
                            current_price = info[key]
                            break
                    
                    if current_price is None:
                        if attempt < max_retries - 1:
                            time.sleep(1)
                            continue
                        else:
                            st.warning(f"Tidak dapat menemukan harga valid untuk {symbol}")
                            break
                    
                    # Handle infinity dan NaN values dengan lebih baik
                    def safe_float(value, default=0):
                        if value is None or pd.isna(value):
                            return default
                        if value == float('inf') or value == float('-inf'):
                            return default
                        return float(value)
                    
                    # Data untuk screener - fokus pada kepemilikan dan market cap
                    data[symbol] = {
                        'Symbol': symbol.replace('.JK', ''),
                        'Current Price': current_price,
                        'Market Cap': safe_float(info.get('marketCap', 0)),
                        'Shares Outstanding': safe_float(info.get('sharesOutstanding', 0)),
                        'Float Shares': safe_float(info.get('floatShares', 0)),
                        'Institutional Ownership %': safe_float(info.get('institutionOwnership', 0)) * 100,
                        'Insider Ownership %': safe_float(info.get('heldPercentInsiders', 0)) * 100,
                        'Public Float %': 0,  # Akan dihitung nanti
                        'Number of Institutions': safe_float(info.get('numberOfAnalystOpinions', 0)),
                        'Price/Book (PBVR)': safe_float(info.get('priceToBook', 0)),
                        'Trailing P/E (PER)': safe_float(info.get('trailingPE', 0)),
                        'Return on Equity (%) (ROE)': safe_float(info.get('returnOnEquity', 0)),
                        'Return on Assets (%) (ROA)': safe_float(info.get('returnOnAssets', 0)),
                        'Return on Capital (%) (ROC)': safe_float(info.get('returnOnCapital', 0)),
                        'Net Income': safe_float(info.get('netIncomeToCommon', 0)),
                        'Cash from Operations': safe_float(info.get('operatingCashflow', 0)),
                        'Free Cash Flow': safe_float(info.get('freeCashflow', info.get('freeCashFlow', info.get('operatingCashflow', 0)))),
                        'Total Assets': safe_float(info.get('totalAssets', 0)),
                        'Total Equity': safe_float(info.get('totalStockholderEquity', 0)),
                        'Total Liabilities': safe_float(info.get('totalDebt', 0)),
                        'EPS': safe_float(info.get('trailingEps', 0)),
                        'Dividend Yield %': safe_float(info.get('dividendYield', 0)) * 100,
                    }
                    
                    # Jika berhasil, keluar dari retry loop
                    break
                    
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(2)  # Tunggu lebih lama untuk retry
                        continue
                    else:
                        st.error(f"Error saat mengambil data {symbol}: {str(e)}")
                        continue
            
            # Rate limiting untuk menghindari block
            if i < len(symbols) - 1:
                time.sleep(0.5)
                
        except Exception as e:
            st.error(f"Error umum saat mengambil data {symbol}: {str(e)}")
            continue
    
    # Clear progress indicator
    if len(symbols) > 5:
        st.empty()
            
    return data

def get_simple_arrow(value: float) -> str:
    """Mendapatkan arrow sederhana untuk financial indicators dengan emoji berwarna.
    
    Args:
        value (float): Nilai yang akan dievaluasi (dalam persentase)
        
    Returns:
        str: Arrow dengan persentase dan emoji berwarna (contoh: 🟢↑ 5.97%)
    """
    if pd.isna(value) or value == 0:
        return "—"
    
    # Konversi ke persentase jika belum
    if abs(value) < 1:
        value = value * 100
    
    if value > 0:
        return f"🟢↑ {value:.2f}%"
    else:
        return f"🔴↓ {abs(value):.2f}%"

def stock_screener_page() -> None:
    """Halaman untuk screener saham dengan fokus pada kepemilikan dan indikator inti."""
    
    # Input section
    col1, col2 = st.columns(2, gap="small")
    with col1:
        symbols = st.text_area('Masukkan simbol saham (pisahkan dengan koma)', DEFAULT_SYMBOLS)
    with col2:
        st.empty()

    if st.button('Screener Saham', key='screener_data'):
        with st.spinner('Menganalisis saham...'):
            try:
                symbols_list = [
                    sanitize_stock_symbol(symbol.strip().upper()) + '.JK' 
                    if '.JK' not in symbol.strip().upper() 
                    else sanitize_stock_symbol(symbol.strip().upper())
                    for symbol in symbols.split(',')
                ]

                stocks_data = fetch_enhanced_stock_data(symbols_list)
                if not stocks_data:
                    st.error("Tidak ada data saham yang berhasil diambil")
                    return
                    
                # Konversi ke DataFrame
                df = pd.DataFrame(stocks_data).T
                
                # Konversi kolom numerik dan handle infinity
                numeric_columns = ['Current Price', 'Market Cap', 'Shares Outstanding', 'Float Shares',
                                 'Institutional Ownership %', 'Insider Ownership %', 'Number of Institutions',
                                 'Price/Book (PBVR)', 'Trailing P/E (PER)', 'Return on Equity (%) (ROE)',
                                 'Return on Assets (%) (ROA)', 'Return on Capital (%) (ROC)',
                                 'Net Income', 'Cash from Operations', 'Free Cash Flow',
                                 'Total Assets', 'Total Equity', 'Total Liabilities']
                
                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce').replace([np.inf, -np.inf], 0)

                # Hitung persentase public float (saham yang dapat diperdagangkan publik)
                df['Public Float %'] = (df['Float Shares'] / df['Shares Outstanding'] * 100).fillna(0)
                
                # Tambahkan arrow sederhana untuk financial indicators
                df['ROE Change'] = df['Return on Equity (%) (ROE)'].apply(lambda x: get_simple_arrow(x))
                df['ROA Change'] = df['Return on Assets (%) (ROA)'].apply(lambda x: get_simple_arrow(x))
                df['ROC Change'] = df['Return on Capital (%) (ROC)'].apply(lambda x: get_simple_arrow(x))
                
                # Bulatkan semua nilai numerik
                for col in numeric_columns + ['Public Float %']:
                    if col in df.columns:
                        df[col] = df[col].round(2)

                # Filter hanya saham yang valid (harga > 0)
                df_display = df[df['Current Price'] > 0].copy()
                df_display = df_display.reset_index(drop=True)
                df_display.index = df_display.index + 1
                
                # Tampilkan hasil screener
                st.markdown("""
                <div style='margin-bottom: 16px;'>
                    <h3 style='color: #1a1a1a; margin-bottom: 5px; font-size: 18px;'>📊 Hasil Screener Saham</h3>
                </div>
                """, unsafe_allow_html=True)
                
                
                # Tampilkan tabel utama dengan expander
                with st.expander("📈 Tampilkan Data Screener Lengkap", expanded=True):
                    # Pilih kolom yang akan ditampilkan - fokus ringkas sesuai permintaan
                    display_columns = [
                        'Symbol', 'Current Price', 'Market Cap', 
                        'Public Float %', 'Insider Ownership %',
                        'Price/Book (PBVR)',
                        'ROE Change', 'ROA Change',
                        'Net Income', 'Free Cash Flow'
                    ]
                    
                    # Filter kolom yang ada
                    available_columns = [col for col in display_columns if col in df_display.columns]
                    df_screener = df_display[available_columns].copy()
                    
                    # Format dataframe
                    format_dict = {
                        'Current Price': lambda x: format_rupiah(x),
                        'Market Cap': lambda x: format_short_number(x),
                        'Public Float %': lambda x: format_percent(x, 1),
                        'Insider Ownership %': lambda x: format_percent(x, 1),
                        'Price/Book (PBVR)': lambda x: format_ratio(x),
                        'Net Income': lambda x: format_short_number(x),
                        'Free Cash Flow': lambda x: format_short_number(x),
                    }
                    
                    # Hitung tinggi tabel
                    table_height = min(600, len(df_screener) * 40 + 50)
                    
                    st.dataframe(
                        format_dataframe(df_screener, format_dict),
                        use_container_width=True,
                        height=table_height
                    )
                    
                    # Download CSV dengan format yang lebih baik
                    # Buat copy dataframe untuk download
                    df_download = df_screener.copy()
                    
                    # Format kolom untuk download dengan format Indonesia
                    for col in df_download.columns:
                        if 'Change' in col:
                            # Hapus emoji dan HTML tags untuk download
                            df_download[col] = df_download[col].astype(str).str.replace('🟢↑', '↑').str.replace('🔴↓', '↓')
                        elif col in ['Current Price', 'Market Cap', 'Net Income', 'Free Cash Flow', 'EPS']:
                            # Format angka untuk download dengan format Indonesia
                            df_download[col] = df_download[col].apply(lambda x: format_csv_indonesia(x, 0) if pd.notna(x) else "0")
                        elif col in ['Public Float %', 'Insider Ownership %', 'Return on Equity (%) (ROE)', 'Return on Assets (%) (ROA)', 'Dividend Yield %']:
                            # Format persentase untuk download dengan format Indonesia
                            df_download[col] = df_download[col].apply(lambda x: format_csv_indonesia(x, 2) if pd.notna(x) else "0")
                        elif col in ['Price/Book (PBVR)', 'Trailing P/E (PER)']:
                            # Format ratio untuk download dengan format Indonesia
                            df_download[col] = df_download[col].apply(lambda x: format_csv_indonesia(x, 2) if pd.notna(x) else "0")
                    
                    # Download CSV dengan separator yang tepat dan quote semua field
                    csv = df_download.to_csv(index=False, sep=';', encoding='utf-8-sig', quoting=1)
                    st.download_button(
                        label="📥 Download as CSV",
                        data=csv,
                        file_name="screener_saham.csv",
                        mime="text/csv"
                    )
                
                # Penjelasan indikator dihapus sesuai permintaan

            except Exception as e:
                st.error(f"Terjadi kesalahan: {str(e)}")

def display_fraksi_harga_table() -> None:
    """Menampilkan tabel fraksi harga dengan styling."""
    df_fraksi = pd.DataFrame(FRACSI_HARGA_DATA)
    df_fraksi.index += 1

    # Styling untuk tabel
    styled_df = df_fraksi.style.set_properties(**{
        'background-color': '#ffffff',
        'color': '#212529',
        'text-align': 'center',
        'padding': '4px',
        'font-size': '14px'
    }).set_table_styles([
        {'selector': 'th', 'props': [
            ('background-color', '#ffffff'),
            ('color', '#212529'),
            ('font-size', '14px'),
            ('font-weight', 'bold'),
            ('padding', '4px')
        ]},
        {'selector': 'td', 'props': [
            ('padding', '4px')
        ]},
        {'selector': 'tr:nth-child(even)', 'props': [
            ('background-color', '#ffffff')
        ]},
        {'selector': 'tr:hover', 'props': [
            ('background-color', '#ffffff')
        ]}
    ])

    st.markdown(styled_df.to_html(index=True), unsafe_allow_html=True)

def calculator_page(title: str, fee_beli: float, fee_jual: float) -> None:
    """Halaman kalkulator profit/loss saham."""
    # Tampilkan tabel fraksi harga di bagian atas
    with st.expander("📊 Tabel Fraksi Harga", expanded=False):
        st.markdown("""
        <h4 style='color: #1a1a1a; margin: 0;'>Tabel Fraksi Harga IDX</h4>
        """, unsafe_allow_html=True)
        display_fraksi_harga_table()
        st.markdown("""
        <p style='margin: 8px 0 0 0; font-size: 13px; color: #6b7280;'>
            <i>Catatan: Fraksi harga adalah selisih harga minimum antara dua transaksi saham.</i>
        </p>
        """, unsafe_allow_html=True)
    
    # Pilih mode kalkulator
    calculator_mode = st.radio(
        "Pilih Mode Kalkulator",
        ["Saham", "Multiple Saham"],
        horizontal=True
    )
    
    if calculator_mode == "Saham":
        single_stock_calculator(title, fee_beli, fee_jual)
    else:
        multiple_stocks_calculator(title, fee_beli, fee_jual)

def single_stock_calculator(title: str, fee_beli: float, fee_jual: float) -> None:
    """Kalkulator untuk single stock."""
    # Input section dalam grid
    col1, col2 = st.columns(2, gap="small")
    
    with col1:
        if title == "Custom":
            st.markdown('<div class="section-title">💰 Masukkan Fee Kustom</div>', unsafe_allow_html=True)
            fee_beli = st.number_input("Fee Beli (persentase):", step=0.1, format="%.2f") / 100
            fee_jual = st.number_input("Fee Jual (persentase):", step=0.1, format="%.2f") / 100

        st.markdown('<div class="section-title">📈 Input Transaksi</div>', unsafe_allow_html=True)
        jumlah_lot = st.number_input("Jumlah Lot:", step=1, format="%d", value=10)
        harga_beli = st.number_input("Harga Beli (per saham):", step=1000.0, format="%0.0f", value=1000.0)
        harga_jual = st.number_input("Harga Jual (per saham):", step=1000.0, format="%0.0f", value=2000.0)
        
        # Tampilkan fee platform
        st.markdown(f"""
        <div style='margin-bottom: 16px; background-color: #f8f9fa; padding: 12px 8px 12px 16px; border-radius: 6px; border-left: 3px solid #2563eb;'>
            <h4 style='color: #1a1a1a; margin: 0; font-size: 16px;'>💸 Fee Platform</h4>
            <p style='margin: 4px 0 0 0; color: #6b7280; font-size: 14px;'>Fee Beli: {fee_beli*100:.2f}% | Fee Jual: {fee_jual*100:.2f}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="section-title">⚙️ Pengaturan</div>', unsafe_allow_html=True)
        include_fee_beli = st.checkbox("Masukkan Fee Beli", value=True)
        include_fee_jual = st.checkbox("Masukkan Fee Jual", value=True)
        include_dividend = st.checkbox("Masukkan Dividen")

        # Input dividen
        dividen_per_saham = 0
        if include_dividend:
            dividen_per_saham = st.number_input("Dividen per Saham:", step=1, format="%d")

        # Button section
        st.markdown('<div style="text-align: center; margin: 16px 0;">', unsafe_allow_html=True)
        if st.button("Hitung", key="calculate_single"):
            with st.spinner('Menghitung...'):
                # Gunakan fee yang sesuai dengan checkbox
                fee_beli_final = fee_beli if include_fee_beli else 0
                fee_jual_final = fee_jual if include_fee_jual else 0
                
                total_beli, total_jual, profit_loss, profit_loss_percentage = calculate_profit_loss(
                    jumlah_lot, harga_beli, harga_jual, fee_beli_final, fee_jual_final
                )
                
                # Results section
                st.markdown(
                    f"""
                    <div style='margin-bottom: 16px; background-color: #f8f9fa; padding: 16px 12px 16px 20px; border-radius: 8px; border-left: 4px solid #2563eb;'>
                        <h4 style='color: #1a1a1a; margin: 0 0 8px 0; font-size: 16px;'>📊 Hasil Perhitungan</h4>
                        <p style='margin: 0; color: #6b7280; font-size: 15px;'>
                            Total Beli: {format_rupiah(total_beli)}<br>
                            Total Jual: {format_rupiah(total_jual)}<br>
                            <span style='color:{"#4CA16B" if profit_loss > 0 else ("#AD3E3E" if profit_loss < 0 else "#423D3D")}; font-weight:bold;'>
                                Profit/Loss: {format_rupiah(profit_loss)}<br>
                                Profit/Loss Percentage: {format_percent(profit_loss_percentage, 2)}
                            </span>
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Tambahkan hasil dividen jika ada
                if include_dividend and dividen_per_saham > 0:
                    total_dividen = calculate_dividend(jumlah_lot, dividen_per_saham)
                    dividend_yield = calculate_dividend_yield(dividen_per_saham, harga_beli)
                    st.write(f"Total Dividen: {format_rupiah(total_dividen)}")
                    st.write(f"Dividend Yield: {format_percent(dividend_yield, 2)}")

def multiple_stocks_calculator(title: str, fee_beli: float, fee_jual: float) -> None:
    """Kalkulator untuk multiple saham."""
    st.markdown('<div class="section-title">📊 Kalkulator Multiple Saham</div>', unsafe_allow_html=True)
    
    # Input jumlah saham
    num_stocks = st.number_input("Jumlah Saham yang Dihitung:", min_value=1, max_value=10, value=2, step=1)
    
    if title == "Custom":
        st.markdown('<div class="section-title">💰 Masukkan Fee Kustom</div>', unsafe_allow_html=True)
        fee_beli = st.number_input("Fee Beli (persentase):", step=0.1, format="%.2f") / 100
        fee_jual = st.number_input("Fee Jual (persentase):", step=0.1, format="%.2f") / 100
    
    # Input untuk setiap saham
    stocks_data = []
    
    for i in range(num_stocks):
        st.markdown(f"### Saham {i+1}")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            symbol = st.text_input(f"Simbol Saham {i+1}", value=f"STOCK{i+1}", key=f"symbol_{i}")
            jumlah_lot = st.number_input(f"Jumlah Lot {i+1}", step=1, format="%d", value=10, key=f"lot_{i}")
        
        with col2:
            harga_beli = st.number_input(f"Harga Beli {i+1}", step=1000.0, format="%0.0f", value=1000.0, key=f"beli_{i}")
            harga_jual = st.number_input(f"Harga Jual {i+1}", step=1000.0, format="%0.0f", value=2000.0, key=f"jual_{i}")
        
        with col3:
            include_fee_beli = st.checkbox(f"Fee Beli {i+1}", value=True, key=f"fee_beli_{i}")
            include_fee_jual = st.checkbox(f"Fee Jual {i+1}", value=True, key=f"fee_jual_{i}")
        
        stocks_data.append({
            'symbol': symbol,
            'jumlah_lot': jumlah_lot,
            'harga_beli': harga_beli,
            'harga_jual': harga_jual,
            'fee_beli': fee_beli if include_fee_beli else 0,
            'fee_jual': fee_jual if include_fee_jual else 0
        })
    
    # Tampilkan fee platform
    st.markdown(f"""
    <div style='margin-bottom: 16px; background-color: #f8f9fa; padding: 12px 8px 12px 16px; border-radius: 6px; border-left: 3px solid #2563eb;'>
        <h4 style='color: #1a1a1a; margin: 0; font-size: 16px;'>💸 Fee Platform</h4>
        <p style='margin: 4px 0 0 0; color: #6b7280; font-size: 14px;'>Fee Beli: {fee_beli*100:.2f}% | Fee Jual: {fee_jual*100:.2f}%</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Hitung Multiple Saham", key="calculate_multiple"):
        with st.spinner('Menghitung multiple saham...'):
            result = calculate_multiple_stocks_profit_loss(stocks_data)
            
            # Tampilkan hasil total
            st.markdown(
                f"""
                <div style='margin-bottom: 16px; background-color: #f8f9fa; padding: 16px 12px 16px 20px; border-radius: 8px; border-left: 4px solid #2563eb;'>
                    <h4 style='color: #1a1a1a; margin: 0 0 8px 0; font-size: 16px;'>📊 Hasil Total Portfolio</h4>
                    <p style='margin: 0; color: #6b7280; font-size: 15px;'>
                        Total Investasi: {format_rupiah(result['total_investment'])}<br>
                        Total Proceeds: {format_rupiah(result['total_proceeds'])}<br>
                        Total Fee Beli: {format_rupiah(result['total_fee_beli'])}<br>
                        Total Fee Jual: {format_rupiah(result['total_fee_jual'])}<br>
                        <span style='color:{"#4CA16B" if result['total_profit_loss'] > 0 else ("#AD3E3E" if result['total_profit_loss'] < 0 else "#423D3D")}; font-weight:bold;'>
                            Total Profit/Loss: {format_rupiah(result['total_profit_loss'])}<br>
                            Total Profit/Loss Percentage: {format_percent(result['total_profit_loss_percentage'], 2)}
                        </span>
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            # Tampilkan detail per saham
            st.markdown("### Detail Per Saham")
            detail_data = []
            for stock in result['stocks_results']:
                detail_data.append({
                    'Symbol': stock['symbol'],
                    'Lot': stock['jumlah_lot'],
                    'Harga Beli': format_rupiah(stock['harga_beli']),
                    'Harga Jual': format_rupiah(stock['harga_jual']),
                    'Total Beli': format_rupiah(stock['total_beli']),
                    'Total Jual': format_rupiah(stock['total_jual']),
                    'Profit/Loss': format_rupiah(stock['profit_loss']),
                    'Profit/Loss %': format_percent(stock['profit_loss_percentage'], 2)
                })
            
            df_detail = pd.DataFrame(detail_data)
            st.dataframe(df_detail, use_container_width=True, hide_index=True)
            
            # Download CSV untuk kalkulator saham dengan format Indonesia
            df_download = df_detail.copy()
            
            # Format kolom untuk download dengan format Indonesia
            for col in df_download.columns:
                if col in ['Harga Beli', 'Harga Jual', 'Total Beli', 'Total Jual', 'Profit/Loss']:
                    # Format Rupiah untuk download dengan format Indonesia
                    df_download[col] = df_download[col].apply(lambda x: format_csv_indonesia(x, 0) if pd.notna(x) else "0")
                elif col in ['Profit/Loss %']:
                    # Format persentase untuk download dengan format Indonesia
                    df_download[col] = df_download[col].apply(lambda x: format_csv_indonesia(x, 2) if pd.notna(x) else "0")
            
            csv = df_download.to_csv(index=False, sep=';', encoding='utf-8-sig', quoting=1)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name="kalkulator_saham.csv",
                mime="text/csv"
            )

def realized_gain_calculator() -> None:
    """Kalkulator untuk realized gain."""
    st.markdown('<div class="section-title">💰 Kalkulator Realized Gain</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="small")
    
    with col1:
        st.markdown('<div class="section-title">📈 Input Investasi</div>', unsafe_allow_html=True)
        initial_investment = st.number_input("Investasi Awal (Rp):", step=1000000, format="%d", value=10000000)
        current_value = st.number_input("Nilai Saat Ini (Rp):", step=1000000, format="%d", value=12000000)
    
    with col2:
        st.markdown('<div class="section-title">💸 Input Tambahan</div>', unsafe_allow_html=True)
        dividends_received = st.number_input("Total Dividen Diterima (Rp):", step=100000, format="%d", value=500000)
        fees_paid = st.number_input("Total Fee Dibayar (Rp):", step=10000, format="%d", value=100000)
    
    if st.button("Hitung Realized Gain", key="calculate_realized"):
        with st.spinner('Menghitung realized gain...'):
            result = calculate_realized_gain(initial_investment, current_value, dividends_received, fees_paid)
            
            # Tampilkan hasil
            st.markdown(
                f"""
                <div style='margin-bottom: 16px; background-color: #f8f9fa; padding: 16px 12px 16px 20px; border-radius: 8px; border-left: 4px solid #2563eb;'>
                    <h4 style='color: #1a1a1a; margin: 0 0 8px 0; font-size: 16px;'>📊 Hasil Realized Gain</h4>
                    <p style='margin: 0; color: #6b7280; font-size: 15px;'>
                        Investasi Awal: {format_rupiah(result['initial_investment'])}<br>
                        Nilai Saat Ini: {format_rupiah(result['current_value'])}<br>
                        Dividen Diterima: {format_rupiah(result['dividends_received'])}<br>
                        Fee Dibayar: {format_rupiah(result['fees_paid'])}<br>
                        <span style='color:{"#4CA16B" if result['capital_gain_loss'] > 0 else ("#AD3E3E" if result['capital_gain_loss'] < 0 else "#423D3D")}; font-weight:bold;'>
                            Capital Gain/Loss: {format_rupiah(result['capital_gain_loss'])} ({format_percent(result['capital_gain_percentage'], 2)})<br>
                            Total Return: {format_rupiah(result['total_return'])} ({format_percent(result['total_return_percentage'], 2)})<br>
                            ROI: {format_percent(result['roi'], 2)}
                        </span>
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
                

def calculate_compound_interest(firstm: float, rate: float, years: float, 
                              additional_investment: float = 0) -> pd.DataFrame:
    """Menghitung bunga berbunga.
    
    Args:
        firstm (float): Investasi awal
        rate (float): Tingkat bunga per tahun dalam persen
        years (float): Jumlah tahun
        additional_investment (float): Investasi tambahan per bulan
        
    Returns:
        pd.DataFrame: DataFrame berisi hasil perhitungan
    """
    data = []
    total_months = int(years * 12)
    amount = firstm
    
    for month in range(1, total_months + 1):
        # Tambahkan investasi bulanan terlebih dahulu
        amount += additional_investment  
        # Hitung bunga bulanan pada total amount
        amount *= (1 + rate / 100 / 12)  
        # Bulatkan ke 2 desimal
        amount = round(amount, 2)
        
        year = (month - 1) // 12 + 1
        data.append({
            'Year': year,
            'Month': month,
            'Amount': amount
        })
        
    return pd.DataFrame(data)

def compound_interest_page() -> None:
    """Halaman untuk menghitung bunga berbunga."""
    st.info('Bunga-berbunga atau compound interest adalah jenis bunga yang dihitung tidak hanya dari jumlah pokok awal, tetapi juga dari bunga yang sudah diperoleh.')

    # Input section
    col1, col2 = st.columns(2, gap="small")
    
    with col1:
        # Input pengguna dengan validasi
        st.markdown("""
        <div style='margin-bottom: 16px;'>
            <h3 style='color: #1a1a1a; margin-bottom: 12px;'>Input Investasi</h3>
        </div>
        """, unsafe_allow_html=True)
        
        firstm = st.number_input('💰 Masukkan nilai awal investasi', step=1000000, format="%d", value=1000000)
        rate = st.number_input('📈 Masukkan tingkat bunga per tahun (%)', step=0.1, format="%.2f", value=10.0)
        years = st.number_input('🗓️ Masukkan jumlah tahun (misal: 5.5 untuk 5 tahun 5 bulan)', step=0.1, format="%.1f", value=5.0)
        additional_investment = st.number_input('➕ Masukkan tambahan investasi per bulan', step=1000000, format="%d", value=1000000)

    # Button section
    if st.button('Hitung', key='calculate_compound'):
        with st.spinner('Menghitung bunga berbunga...'):
            try:
                if firstm == 0 and rate == 0:
                    st.error("Silakan masukkan nilai investasi awal dan tingkat bunga untuk menghitung compound interest")
                    return
                    
                df = calculate_compound_interest(firstm, rate, years, additional_investment)
                
                # Format kolom Amount
                df['Amount'] = df['Amount'].apply(lambda x: format_rupiah(x))
                
                # Results section
                st.markdown("""
                <div style='margin-bottom: 16px;'>
                    <h3 style='color: #1a1a1a; margin-bottom: 5px; font-size: 16px;'>📊 Hasil perhitungan bunga berbunga</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Tampilkan total investasi
                total_investment = firstm + (additional_investment * int(years * 12))
                final_amount = df['Amount'].iloc[-1]
                
                st.markdown(f"""
                <div style='margin-bottom: 16px; background-color: #f8f9fa; padding: 12px 8px 12px 16px; border-radius: 6px; border-left: 3px solid #2563eb;'>
                    <h4 style='color: #1a1a1a; margin: 0; font-size: 16px;'>💰 Total Investasi</h4>
                    <p style='margin: 4px 0 0 0; color: #6b7280; font-size: 14px;'>Modal Awal: {format_rupiah(firstm)}</p>
                    <p style='margin: 4px 0 0 0; color: #6b7280; font-size: 14px;'>Investasi Bulanan: {format_rupiah(additional_investment)}</p>
                    <p style='margin: 4px 0 0 0; color: #6b7280; font-size: 14px;'>Total Investasi: {format_rupiah(total_investment)}</p>
                    <p style='margin: 4px 0 0 0; color: #6b7280; font-size: 14px;'>Total Akhir: {final_amount}</p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander('Tampilkan Data', expanded=True):
                    st.dataframe(
                        df.set_index(df.index + 1),
                        use_container_width=True,
                        height=400
                    )
                    
                    # Download CSV untuk compound interest dengan format Indonesia
                    df_download = df.copy()
                    
                    # Format kolom Amount untuk download dengan format Indonesia
                    df_download['Amount'] = df_download['Amount'].apply(lambda x: format_csv_indonesia(x, 0) if pd.notna(x) else "0")
                    
                    csv = df_download.to_csv(index=False, sep=';', encoding='utf-8-sig', quoting=1)
                    st.download_button(
                        label="📥 Download as CSV",
                        data=csv,
                        file_name="compound_interest.csv",
                        mime="text/csv"
                    )

                for year_num in range(1, int(years) + 1):
                    yearly_data = df[df['Year'] == year_num]
                    with st.expander(f'📅 Tahun {year_num}', expanded=False):
                        st.dataframe(
                            yearly_data[['Month', 'Amount']].set_index(yearly_data.index + 1),
                            use_container_width=True
                        )
            except Exception:
                st.error("Silakan masukkan nilai investasi awal dan tingkat bunga untuk menghitung compound interest")

def get_fraksi_harga(harga: float) -> float:
    """Mendapatkan fraksi harga berdasarkan standar IDX."""
    if harga < 200:
        return 1
    elif 200 <= harga < 500:
        return 2
    elif 500 <= harga < 2000:
        return 5
    elif 2000 <= harga < 5000:
        return 10
    else:
        return 25

def get_ara_arb_percentage(harga: float, is_acceleration: bool = False) -> float:
    """Mendapatkan persentase ARA/ARB berdasarkan jenis papan."""
    if is_acceleration:
        if 1 <= harga <= 10:
            return 1.0  # Rp1 di atas/bawah harga acuan
        else:
            return 10.0  # 10% dari harga acuan
    else:
        # Pola persentase berdasarkan harga sesuai IDX
        if harga >= 5000:
            return 20.0
        elif 2000 <= harga < 5000:
            return 25.0
        elif 1000 <= harga < 2000:
            return 25.0
        elif 500 <= harga < 1000:
            return 25.0
        elif 200 <= harga < 500:
            return 25.0
        elif 100 <= harga < 200:
            return 35.0
        elif 50 <= harga < 100:
            return 35.0
        else:
            return 0.0  # Untuk harga di bawah Rp50

def calculate_ara_arb_sequence(harga_dasar: float, is_acceleration: bool = False, max_steps: int = 10) -> List[Dict]:
    """Menghitung urutan harga ARA dan ARB sesuai standar IDX.
    
    Args:
        harga_dasar (float): Harga dasar/penutupan
        is_acceleration (bool): True untuk papan akselerasi
        max_steps (int): Jumlah maksimal langkah yang dihitung
        
    Returns:
        List[Dict]: List berisi urutan harga ARA dan ARB
    """
    sequence = []
    
    # Tambahkan harga dasar sebagai referensi
    sequence.append({
        'harga': harga_dasar,
        'perubahan': 0,
        'persentase_perubahan': 0.0,
        'persentase_kumulatif': 0.0,
        'tipe': 'dasar'
    })
    
    # Hitung ARA (Auto Reject Above)
    harga_ara_sekarang = harga_dasar
    for step in range(max_steps):
        if is_acceleration:
            if 1 <= harga_ara_sekarang <= 10:
                # Untuk papan akselerasi, harga Rp1-Rp10: +Rp1
                harga_ara_baru = harga_ara_sekarang + 1
            else:
                # Untuk papan akselerasi, harga > Rp10: +10%
                harga_ara_baru = harga_ara_sekarang * 1.10
        else:
            # Untuk papan utama/pengembangan - gunakan persentase yang tepat
            if harga_ara_sekarang >= 5000:
                # Harga ≥ Rp 5.000: +20%
                persentase = 20.0
            elif 2000 <= harga_ara_sekarang < 5000:
                # Harga Rp 1.000 - Rp 5.000: +25%
                persentase = 25.0
            elif 1000 <= harga_ara_sekarang < 2000:
                # Harga Rp 1.000 - Rp 2.000: +25%
                persentase = 25.0
            elif 500 <= harga_ara_sekarang < 1000:
                # Harga Rp 500 - Rp 1.000: +25%
                persentase = 25.0
            elif 200 <= harga_ara_sekarang < 500:
                # Harga Rp 200 - Rp 500: +25%
                persentase = 25.0
            elif 100 <= harga_ara_sekarang < 200:
                # Harga Rp 100 - Rp 200: +35%
                persentase = 35.0
            elif 50 <= harga_ara_sekarang < 100:
                # Harga Rp 50 - Rp 100: +35%
                persentase = 35.0
            else:
                # Harga < Rp 50: tidak ada ARA
                break
            
            # Hitung harga baru dengan persentase
            harga_ara_baru = harga_ara_sekarang * (1 + persentase / 100)
        
        # Bulatkan sesuai fraksi harga dengan metode yang benar
        fraksi = get_fraksi_harga(harga_ara_baru)
        # Untuk ARA, gunakan floor division untuk mendapatkan harga yang tidak melebihi batas
        harga_ara_baru = int(harga_ara_baru / fraksi) * fraksi
        
        # Hitung perubahan dan persentase
        perubahan = harga_ara_baru - harga_ara_sekarang
        persentase_perubahan = (perubahan / harga_ara_sekarang) * 100 if harga_ara_sekarang > 0 else 0
        persentase_kumulatif = ((harga_ara_baru - harga_dasar) / harga_dasar) * 100 if harga_dasar > 0 else 0
        
        sequence.append({
            'harga': harga_ara_baru,
            'perubahan': perubahan,
            'persentase_perubahan': persentase_perubahan,
            'persentase_kumulatif': persentase_kumulatif,
            'tipe': 'ara'
        })
        
        harga_ara_sekarang = harga_ara_baru
    
    # Hitung ARB (Auto Reject Below)
    harga_arb_sekarang = harga_dasar
    for step in range(max_steps):
        if is_acceleration:
            if 1 <= harga_arb_sekarang <= 10:
                # Untuk papan akselerasi, harga Rp1-Rp10: -Rp1
                harga_arb_baru = harga_arb_sekarang - 1
            else:
                # Untuk papan akselerasi, harga > Rp10: -10%
                harga_arb_baru = harga_arb_sekarang * 0.90
        else:
            # Untuk papan utama/pengembangan - gunakan persentase yang tepat
            if harga_arb_sekarang >= 5000:
                # Harga ≥ Rp 5.000: -20%
                persentase = 20.0
            elif 2000 <= harga_arb_sekarang < 5000:
                # Harga Rp 1.000 - Rp 5.000: -25%
                persentase = 25.0
            elif 1000 <= harga_arb_sekarang < 2000:
                # Harga Rp 1.000 - Rp 2.000: -25%
                persentase = 25.0
            elif 500 <= harga_arb_sekarang < 1000:
                # Harga Rp 500 - Rp 1.000: -25%
                persentase = 25.0
            elif 200 <= harga_arb_sekarang < 500:
                # Harga Rp 200 - Rp 500: -25%
                persentase = 25.0
            elif 100 <= harga_arb_sekarang < 200:
                # Harga Rp 100 - Rp 200: -35%
                persentase = 35.0
            elif 50 <= harga_arb_sekarang < 100:
                # Harga Rp 50 - Rp 100: -35%
                persentase = 35.0
            else:
                # Harga < Rp 50: tidak ada ARB
                break
            
            # Hitung harga baru dengan persentase
            harga_arb_baru = harga_arb_sekarang * (1 - persentase / 100)
        
        # Pastikan harga tidak di bawah minimum
        harga_arb_baru = max(1, harga_arb_baru)
        
        # Bulatkan sesuai fraksi harga dengan metode yang benar
        fraksi = get_fraksi_harga(harga_arb_baru)
        # Untuk ARB, gunakan floor division untuk mendapatkan harga yang tidak melebihi batas
        harga_arb_baru = int(harga_arb_baru / fraksi) * fraksi
        
        # Hitung perubahan dan persentase
        perubahan = harga_arb_baru - harga_arb_sekarang
        persentase_perubahan = (perubahan / harga_arb_sekarang) * 100 if harga_arb_sekarang > 0 else 0
        persentase_kumulatif = ((harga_arb_baru - harga_dasar) / harga_dasar) * 100 if harga_dasar > 0 else 0
        
        sequence.append({
            'harga': harga_arb_baru,
            'perubahan': perubahan,
            'persentase_perubahan': persentase_perubahan,
            'persentase_kumulatif': persentase_kumulatif,
            'tipe': 'arb'
        })
        
        harga_arb_sekarang = harga_arb_baru
    
    # Urutkan berdasarkan harga (dari tertinggi ke terendah)
    sequence.sort(key=lambda x: x['harga'], reverse=True)
    
    return sequence

def calculate_ara_price(harga_dasar: float, is_acceleration: bool = False) -> float:
    """Menghitung harga ARA (Auto Reject Above) sesuai standar IDX.
    
    Args:
        harga_dasar (float): Harga dasar/penutupan
        is_acceleration (bool): True untuk papan akselerasi
        
    Returns:
        float: Harga ARA yang sudah dibulatkan sesuai fraksi
    """
    if is_acceleration:
        if 1 <= harga_dasar <= 10:
            # Untuk papan akselerasi, harga Rp1-Rp10: +Rp1
            harga_ara = harga_dasar + 1
        else:
            # Untuk papan akselerasi, harga > Rp10: +10%
            harga_ara = harga_dasar * 1.10
    else:
        # Untuk papan utama/pengembangan
        if harga_dasar >= 5000:
            # Harga ≥ Rp 5.000: +20%
            harga_ara = harga_dasar * 1.20
        elif 2000 <= harga_dasar < 5000:
            # Harga Rp 1.000 - Rp 5.000: +25%
            harga_ara = harga_dasar * 1.25
        elif 1000 <= harga_dasar < 2000:
            # Harga Rp 1.000 - Rp 2.000: +25%
            harga_ara = harga_dasar * 1.25
        elif 500 <= harga_dasar < 1000:
            # Harga Rp 500 - Rp 1.000: +25%
            harga_ara = harga_dasar * 1.25
        elif 200 <= harga_dasar < 500:
            # Harga Rp 200 - Rp 500: +25%
            harga_ara = harga_dasar * 1.25
        elif 100 <= harga_dasar < 200:
            # Harga Rp 100 - Rp 200: +35%
            harga_ara = harga_dasar * 1.35
        elif 50 <= harga_dasar < 100:
            # Harga Rp 50 - Rp 100: +35%
            harga_ara = harga_dasar * 1.35
        else:
            # Harga < Rp 50: tidak ada ARA
            return harga_dasar
    
    # Bulatkan sesuai fraksi harga
    fraksi = get_fraksi_harga(harga_ara)
    return int(harga_ara / fraksi) * fraksi

def calculate_arb_price(harga_dasar: float, is_acceleration: bool = False) -> float:
    """Menghitung harga ARB (Auto Reject Below) sesuai standar IDX.
    
    Args:
        harga_dasar (float): Harga dasar/penutupan
        is_acceleration (bool): True untuk papan akselerasi
        
    Returns:
        float: Harga ARB yang sudah dibulatkan sesuai fraksi
    """
    if is_acceleration:
        if 1 <= harga_dasar <= 10:
            # Untuk papan akselerasi, harga Rp1-Rp10: -Rp1
            harga_arb = harga_dasar - 1
        else:
            # Untuk papan akselerasi, harga > Rp10: -10%
            harga_arb = harga_dasar * 0.90
    else:
        # Untuk papan utama/pengembangan
        if harga_dasar >= 5000:
            # Harga ≥ Rp 5.000: -20%
            harga_arb = harga_dasar * 0.80
        elif 2000 <= harga_dasar < 5000:
            # Harga Rp 1.000 - Rp 5.000: -25%
            harga_arb = harga_dasar * 0.75
        elif 1000 <= harga_dasar < 2000:
            # Harga Rp 1.000 - Rp 2.000: -25%
            harga_arb = harga_dasar * 0.75
        elif 500 <= harga_dasar < 1000:
            # Harga Rp 500 - Rp 1.000: -25%
            harga_arb = harga_dasar * 0.75
        elif 200 <= harga_dasar < 500:
            # Harga Rp 200 - Rp 500: -25%
            harga_arb = harga_dasar * 0.75
        elif 100 <= harga_dasar < 200:
            # Harga Rp 100 - Rp 200: -35%
            harga_arb = harga_dasar * 0.65
        elif 50 <= harga_dasar < 100:
            # Harga Rp 50 - Rp 100: -35%
            harga_arb = harga_dasar * 0.65
        else:
            # Harga < Rp 50: tidak ada ARB
            return harga_dasar
    
    # Pastikan harga tidak di bawah minimum
    harga_arb = max(1, harga_arb)
    
    # Bulatkan sesuai fraksi harga
    fraksi = get_fraksi_harga(harga_arb)
    return int(harga_arb / fraksi) * fraksi

def calculate_next_price(harga_sekarang: float, persentase: float, is_ara: bool) -> float:
    """Menghitung harga berikutnya dengan persentase yang fleksibel.
    
    Args:
        harga_sekarang (float): Harga saat ini
        persentase (float): Persentase kenaikan/penurunan
        is_ara (bool): True untuk ARA, False untuk ARB
        
    Returns:
        float: Harga berikutnya yang sudah dibulatkan
    """
    # Pastikan nilai harga dan persentase valid
    harga_sekarang = max(1, abs(harga_sekarang))
    persentase = max(0, abs(persentase))
    
    fraksi = get_fraksi_harga(harga_sekarang)

    if is_ara:
        # Hitung harga maksimum yang diizinkan
        harga_maks = harga_sekarang * (1 + persentase / 100)
        harga_baru = harga_sekarang
        while harga_baru < harga_maks:
            harga_baru += fraksi
            fraksi = get_fraksi_harga(harga_baru)
        harga_baru -= fraksi
    else:
        # Hitung harga minimum yang diizinkan
        harga_min = harga_sekarang * (1 - persentase / 100)
        harga_baru = harga_sekarang
        while harga_baru > harga_min:
            harga_baru -= fraksi
            fraksi = get_fraksi_harga(harga_baru)
        harga_baru += fraksi

    fraksi = get_fraksi_harga(harga_baru)
    return round(harga_baru / fraksi) * fraksi

def calculate_actual_percentage(harga_awal: float, harga_baru: float) -> float:
    """Menghitung persentase aktual kenaikan/penurunan."""
    return abs((harga_baru - harga_awal) / harga_awal * 100)

def ara_arb_calculator_page() -> None:
    """Halaman untuk menghitung harga ARA dan ARB berdasarkan jenis papan."""
    st.info('Kalkulator untuk menghitung harga ARA (Auto Reject Above) dan ARB (Auto Reject Below) berdasarkan jenis papan')
    
    col1, col2 = st.columns(2, gap="small")
    
    with col1:
        st.markdown("""
        <div style='margin-bottom: 16px;'>
            <h3 style='color: #1a1a1a; margin-bottom: 12px;'>Input Harga</h3>
        </div>
        """, unsafe_allow_html=True)
        
        board_type = st.radio(
            "Pilih Jenis Papan",
            ["Papan Utama/Pengembangan", "Papan Akselerasi"],
            index=0,
            horizontal=True
        )
        is_acceleration = board_type == "Papan Akselerasi"
        
        with st.expander("📋 Ketentuan Harga ARA ARB", expanded=False):
            if is_acceleration:
                st.markdown("""
                <h4 style='color: #1a1a1a; margin: 0;'>ARA/ARB Papan Akselerasi</h4>
                <p style='margin: 0;'>• Harga Rp 1 - Rp 10: ±Rp 1 dari harga acuan</p>
                <p style='margin: 0;'>• Harga > Rp 10: ±10% dari harga acuan</p>
                <p style='margin: 0 0 8px 0;'>• Minimum harga: Rp 1</p>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <h4 style='color: #1a1a1a; margin: 0;'>ARA/ARB Papan Utama/Pengembangan</h4>
                <p style='margin: 0;'>• Harga ≥ Rp 5.000: +20% / -20%</p>
                <p style='margin: 0;'>• Harga Rp 1.000 - Rp 5.000: +25% / -25%</p>
                <p style='margin: 0;'>• Harga Rp 100 - Rp 1.000: +25% / -25%</p>
                <p style='margin: 0;'>• Harga Rp 50 - Rp 100: +35% / -35%</p>
                <p style='margin: 0 0 8px 0;'>• Minimum harga: Rp 1</p>
                """, unsafe_allow_html=True)
        
        min_value = 1
        harga_penutupan = st.number_input('💰 Harga Penutupan', step=100, format="%d", min_value=min_value, value=975)
        
        max_steps = st.number_input('📊 Jumlah Langkah', min_value=1, max_value=20, value=6, step=1)
        
        if st.button('Hitung ARA ARB', type='primary'):
            if harga_penutupan >= min_value:
                st.markdown("""
                <div style='margin-bottom: 16px;'>
                    <h3 style='color: #1a1a1a; margin-bottom: 5px; font-size: 16px;'>📊 Hasil Perhitungan ARA/ARB</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Hitung urutan ARA/ARB
                sequence = calculate_ara_arb_sequence(harga_penutupan, is_acceleration, max_steps)
                
                # Buat DataFrame untuk ditampilkan
                display_data = []
                for i, item in enumerate(sequence):
                    # Tentukan warna berdasarkan tipe
                    if item['tipe'] == 'ara':
                        warna = '#22c55e'  # Hijau untuk ARA
                        arrow = '↗️'
                    elif item['tipe'] == 'arb':
                        warna = '#ef4444'  # Merah untuk ARB
                        arrow = '↘️'
                    else:
                        warna = '#6b7280'  # Abu-abu untuk harga dasar
                        arrow = ''
                    
                    # Format perubahan
                    if item['perubahan'] > 0:
                        perubahan_str = f"+{item['perubahan']:,.0f}"
                    elif item['perubahan'] < 0:
                        perubahan_str = f"{item['perubahan']:,.0f}"
                    else:
                        perubahan_str = "0"
                    
                    # Format persentase perubahan
                    if item['persentase_perubahan'] > 0:
                        persentase_perubahan_str = f"(+{item['persentase_perubahan']:.2f}%)"
                    elif item['persentase_perubahan'] < 0:
                        persentase_perubahan_str = f"({item['persentase_perubahan']:.2f}%)"
                    else:
                        persentase_perubahan_str = "(0.00%)"
                    
                    # Format persentase kumulatif
                    if item['persentase_kumulatif'] > 0:
                        persentase_kumulatif_str = f"{item['persentase_kumulatif']:.2f}%"
                    elif item['persentase_kumulatif'] < 0:
                        persentase_kumulatif_str = f"{item['persentase_kumulatif']:.2f}%"
                    else:
                        persentase_kumulatif_str = "0.00%"
                    
                    display_data.append({
                        'Harga': f"Rp {item['harga']:,.0f}",
                        'Perubahan': perubahan_str,
                        'Persentase': persentase_perubahan_str,
                        'Kumulatif': f"{arrow} {persentase_kumulatif_str}",
                        'Warna': warna
                    })
                
                # Tampilkan hasil dalam format yang mirip dengan gambar
                st.markdown("""
                <div style='margin-bottom: 16px; background-color: #f8f9fa; padding: 16px; border-radius: 8px;'>
                    <h4 style='color: #1a1a1a; margin: 0 0 12px 0; font-size: 16px;'>📈 Urutan Harga ARA/ARB</h4>
                """, unsafe_allow_html=True)
                
                for i, data in enumerate(display_data):
                    # Tentukan background color berdasarkan tipe
                    if '↗️' in data['Kumulatif']:
                        bg_color = '#dcfce7'  # Light green background
                        border_color = '#22c55e'
                    elif '↘️' in data['Kumulatif']:
                        bg_color = '#fef2f2'  # Light red background
                        border_color = '#ef4444'
                    else:
                        bg_color = '#f9fafb'  # Light gray background
                        border_color = '#6b7280'
                    
                    st.markdown(f"""
                    <div style='margin-bottom: 8px; background-color: {bg_color}; padding: 12px; border-radius: 6px; border-left: 3px solid {border_color};'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div style='flex: 1;'>
                                <div style='font-weight: bold; font-size: 16px; color: {data["Warna"]};'>{data['Harga']}</div>
                                <div style='font-size: 14px; color: #6b7280;'>{data['Perubahan']} {data['Persentase']}</div>
                            </div>
                            <div style='font-size: 14px; color: {data["Warna"]}; font-weight: bold;'>{data['Kumulatif']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Download CSV untuk ARA ARB dengan format Indonesia
                df_ara_arb = pd.DataFrame(display_data)
                
                # Format kolom untuk download dengan format Indonesia
                for col in df_ara_arb.columns:
                    if col in ['Harga', 'Perubahan']:
                        # Format Rupiah untuk download dengan format Indonesia
                        df_ara_arb[col] = df_ara_arb[col].apply(lambda x: format_csv_indonesia(x, 0) if pd.notna(x) else "0")
                    elif col in ['Persentase', 'Kumulatif']:
                        # Format persentase untuk download dengan format Indonesia
                        df_ara_arb[col] = df_ara_arb[col].apply(lambda x: format_csv_indonesia(x, 2) if pd.notna(x) else "0")
                
                csv = df_ara_arb.to_csv(index=False, sep=';', encoding='utf-8-sig', quoting=1)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name="ara_arb_calculator.csv",
                    mime="text/csv"
                )
                
                # Penjelasan dihapus sesuai permintaan
                
            else:
                st.error(f"Harga saham harus minimal Rp {min_value}")

def warrant_calculator_page() -> None:
    """Halaman untuk menghitung keuntungan jual warrant."""
    
    # Notification bahwa menggunakan Stockbit
    st.info("📱 **Kalkulator Warrant menggunakan platform Stockbit**")
    
    # Set fee Stockbit (fixed)
    fee_beli, fee_jual = PLATFORM_CONFIG.get("Stockbit", (0.0015, 0.0025))
    
    col1, col2 = st.columns(2, gap="small")
    
    with col1:
        # Input transaksi (single)
        st.markdown('<div class="section-title">💰 Input Transaksi</div>', unsafe_allow_html=True)
        harga_beli_warrant = st.number_input('Harga Beli Warrant', min_value=0, step=1, format="%d", value=1)
        harga_jual_warrant = st.number_input('Harga Jual Warrant', min_value=0, step=1, format="%d", value=47)
        jumlah_lot = st.number_input('Jumlah Lot', step=0.5, format="%.1f", value=3.0)
    
    if st.button('Hitung Realized Gain', type='primary', use_container_width=True):
        with st.spinner('Menghitung...'):
            # Hitung total beli dan jual
            harga_beli_warrant = max(0.0, float(harga_beli_warrant))
            harga_jual_warrant = max(0.0, float(harga_jual_warrant))
            jumlah_lot = max(0.5, abs(jumlah_lot))
            
            # Hitung berdasarkan lot (seperti Stockbit)
            jumlah_saham = jumlah_lot * 100
            total_beli = harga_beli_warrant * jumlah_saham
            total_jual = harga_jual_warrant * jumlah_saham
            
            # Hitung fee (otomatis apply Stockbit fees)
            total_fee_beli = total_beli * fee_beli
            total_fee_jual = total_jual * fee_jual
            
            # Hitung net amount (total jual - fee jual)
            net_amount = total_jual - total_fee_jual
            
            # Hitung realized gain (net amount - total modal)
            total_modal = total_beli + total_fee_beli
            keuntungan = net_amount - total_modal
            persentase_keuntungan = (keuntungan / total_modal * 100) if total_modal > 0 else 0
            
            # Bulatkan semua nilai
            total_beli = round(total_beli, 2)
            total_jual = round(total_jual, 2)
            total_fee_beli = round(total_fee_beli, 2)
            total_fee_jual = round(total_fee_jual, 2)
            total_modal = round(total_modal, 2)
            net_amount = round(net_amount, 2)
            keuntungan = round(keuntungan, 2)
            persentase_keuntungan = round(persentase_keuntungan, 2)
            
            # Tampilkan hasil dalam format Stockbit
            st.markdown("""
            <div style='margin-bottom: 16px;'>
                <h3 style='color: #1a1a1a; margin-bottom: 5px; font-size: 16px;'>📊 Hasil Perhitungan Warrant (Stockbit)</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Tampilkan detail transaksi seperti Stockbit
            st.markdown(f"""
            <div style='margin-bottom: 8px; background-color: #f8f9fa; padding: 12px 8px 12px 16px; border-radius: 6px; border-left: 3px solid #2563eb;'>
                <h4 style='color: #1a1a1a; margin: 0; font-size: 16px;'>📋 Detail Transaksi</h4>
                <p style='margin: 4px 0 0 0; color: #6b7280; font-size: 14px;'>Price: {harga_jual_warrant}</p>
                <p style='margin: 4px 0 0 0; color: #6b7280; font-size: 14px;'>Lot Done: {jumlah_lot}</p>
                <p style='margin: 4px 0 0 0; color: #6b7280; font-size: 14px;'>Amount: {format_rupiah(total_jual)}</p>
                <p style='margin: 4px 0 0 0; color: #6b7280; font-size: 14px;'>Total Fee: {format_rupiah(total_fee_jual)}</p>
                <p style='margin: 4px 0 0 0; color: #6b7280; font-size: 14px;'>Net Amount: {format_rupiah(net_amount)}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Tampilkan total beli (modal awal)
            st.markdown(f"""
            <div style='margin-bottom: 8px; background-color: #f8f9fa; padding: 12px 8px 12px 16px; border-radius: 6px; border-left: 3px solid #2563eb;'>
                <h4 style='color: #1a1a1a; margin: 0; font-size: 16px;'>💰 Modal Awal: {format_rupiah(total_modal)}</h4>
                <p style='margin: 4px 0 0 0; color: #6b7280; font-size: 14px;'>Harga Beli: {format_rupiah(harga_beli_warrant)} × {jumlah_lot} lot</p>
                <p style='margin: 4px 0 0 0; color: #6b7280; font-size: 14px;'>Fee Beli: {format_rupiah(total_fee_beli)} ({fee_beli*100:.2f}%)</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Tampilkan realized gain
            if keuntungan > 0:
                st.markdown(f"""
                <div style='margin-bottom: 8px; background-color: #f8f9fa; padding: 12px 8px 12px 16px; border-radius: 6px; border-left: 3px solid #22c55e;'>
                    <h4 style='color: #1a1a1a; margin: 0; font-size: 16px;'>📈 Realized Gain: +{format_rupiah(keuntungan)} (+{persentase_keuntungan:.2f}%)</h4>
                    <p style='margin: 4px 0 0 0; color: #6b7280; font-size: 14px;'>Net Amount: {format_rupiah(net_amount)} - Modal: {format_rupiah(total_modal)}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='margin-bottom: 8px; background-color: #f8f9fa; padding: 12px 8px 12px 16px; border-radius: 6px; border-left: 3px solid #ef4444;'>
                    <h4 style='color: #1a1a1a; margin: 0; font-size: 16px;'>📉 Realized Loss: {format_rupiah(keuntungan)} ({persentase_keuntungan:.2f}%)</h4>
                    <p style='margin: 4px 0 0 0; color: #6b7280; font-size: 14px;'>Net Amount: {format_rupiah(net_amount)} - Modal: {format_rupiah(total_modal)}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Download CSV untuk warrant calculator (single) dengan format Indonesia
            warrant_data = {
                'Harga Beli': [format_csv_indonesia(harga_beli_warrant, 0)],
                'Jumlah Lot': [jumlah_lot],
                'Total Modal': [format_csv_indonesia(total_modal, 0)],
                'Fee Beli': [format_csv_indonesia(total_fee_beli, 0)],
                'Harga Jual': [format_csv_indonesia(harga_jual_warrant, 0)],
                'Net Amount': [format_csv_indonesia(net_amount, 0)],
                'Keuntungan': [format_csv_indonesia(keuntungan, 0)],
                'Persentase Keuntungan': [format_csv_indonesia(persentase_keuntungan, 2)]
            }
            
            df_warrant = pd.DataFrame(warrant_data)
            csv = df_warrant.to_csv(index=False, sep=';', encoding='utf-8-sig', quoting=1)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name="warrant_calculator.csv",
                mime="text/csv"
            )
    
    # Multiple warrant calculator
    st.markdown('<div class="section-title">📚 Multiple Warrant</div>', unsafe_allow_html=True)
    jumlah_warrant = st.number_input('Jumlah baris warrant', min_value=1, step=1, value=2)
    multiple_rows = []
    for i in range(int(jumlah_warrant)):
        c1, c2, c3, c4 = st.columns(4, gap="small")
        with c1:
            sym = st.text_input(f'Symbol #{i+1}', value=f'W{i+1}', key=f'w_sym_{i}').strip().upper()
        with c2:
            beli = st.number_input(f'Harga Beli #{i+1}', min_value=0.0, step=1.0, format="%0.0f", value=1.0, key=f'w_beli_{i}')
        with c3:
            jual = st.number_input(f'Harga Jual #{i+1}', min_value=0.0, step=1.0, format="%0.0f", value=47.0, key=f'w_jual_{i}')
        with c4:
            lot = st.number_input(f'Lot #{i+1}', step=0.5, format="%.1f", value=3.0, key=f'w_lot_{i}')
        multiple_rows.append((sym, beli, jual, lot))

    if st.button('Hitung Multiple Warrant', use_container_width=True):
        with st.spinner('Menghitung...'):
            hasil_rows = []
            total_modal_all = 0.0
            total_keuntungan_all = 0.0
            for sym, beli, jual, lot in multiple_rows:
                lot = max(0.5, abs(float(lot)))
                beli = max(0.0, float(beli))
                jual = max(0.0, float(jual))
                jumlah_saham = lot * 100
                total_beli = beli * jumlah_saham
                total_jual = jual * jumlah_saham
                fee_b = total_beli * fee_beli
                fee_j = total_jual * fee_jual
                net_amt = total_jual - fee_j
                modal = total_beli + fee_b
                untung = net_amt - modal
                pct = (untung / modal * 100) if modal > 0 else 0
                total_modal_all += modal
                total_keuntungan_all += untung
                hasil_rows.append({
                    'Symbol': sym,
                    'Harga Beli': beli,
                    'Harga Jual': jual,
                    'Lot': lot,
                    'Total Modal': modal,
                    'Net Amount': net_amt,
                    'Keuntungan': untung,
                    'Persentase %': pct,
                })

            df_w_multi = pd.DataFrame(hasil_rows)
            # Tampilkan tabel terformat
            df_view = df_w_multi.copy()
            df_view['Harga Beli'] = df_view['Harga Beli'].apply(lambda x: format_rupiah(x))
            df_view['Harga Jual'] = df_view['Harga Jual'].apply(lambda x: format_rupiah(x))
            df_view['Total Modal'] = df_view['Total Modal'].apply(lambda x: format_rupiah(x))
            df_view['Net Amount'] = df_view['Net Amount'].apply(lambda x: format_rupiah(x))
            df_view['Keuntungan'] = df_view['Keuntungan'].apply(lambda x: format_rupiah(x))
            df_view['Persentase %'] = df_view['Persentase %'].apply(lambda x: format_percent(x, 2))
            st.dataframe(df_view, use_container_width=True, hide_index=True)

            # Download CSV format Indonesia dengan ;
            df_download = df_w_multi.copy()
            for col in ['Harga Beli','Harga Jual','Total Modal','Net Amount','Keuntungan']:
                df_download[col] = df_download[col].apply(lambda x: format_csv_indonesia(x, 0))
            df_download['Persentase %'] = df_download['Persentase %'].apply(lambda x: format_csv_indonesia(x, 2))
            csv_multi = df_download.to_csv(index=False, sep=';', encoding='utf-8-sig', quoting=1)
            st.download_button(label='📥 Download Multiple Warrant CSV', data=csv_multi, file_name='multiple_warrant.csv', mime='text/csv')

def main() -> None:
    """Fungsi utama untuk menjalankan aplikasi Streamlit."""
    st.set_page_config(
        page_title="Saham IDX",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    apply_global_css()
    
    # Layout utama dengan sidebar dan content
    col1, col2 = st.columns([1, 4], gap="small")
    
    with col1:
        # Sidebar dengan menu utama
        st.markdown("""
        <div style='padding: 12px;'>
            <h2 style='color: #1a1a1a; margin-bottom: 16px;'>Menu</h2>
        </div>
        """, unsafe_allow_html=True)
        
        menu_selection = option_menu(
            None,
            ["Scraper Saham", "Screener Saham", "Kalkulator Saham", "Compound Interest", "ARA ARB Calculator", "Warrant Calculator"],
            icons=["graph-up", "search", "calculator", "bookmark", "percent", "ticket-perforated"],
            menu_icon="cast",
            default_index=0,
            orientation="vertical",
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#2563eb", "font-size": "14px"}, 
                "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "#e5e7eb"},
                "nav-link-selected": {"background-color": "#2563eb"},
            }
        )

        # Tambahkan link Instagram dan AI Studio di sidebar
        st.markdown("""
        <div style='margin-top: 32px; padding: 12px; background-color: #f8f9fa; border-radius: 8px;'>
            <h4 style='color: #1a1a1a; margin-bottom: 12px;'>AI Screener Saham</h4>
            <a href='https://aistudio.instagram.com/ai/704778415445100?utm_source=ai_agent' target='_blank' style='text-decoration: none; color: #2563eb; display: flex; align-items: center;'>
                <span style='margin-right: 8px;'>🤖</span> Check out this AI on Instagram!
            </a>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Header content
        st.markdown("""
        <div style='margin-bottom: 16px;'>
            <h1 style='color: #1a1a1a; font-size: 2em; margin-bottom: 4px; letter-spacing: -1px;'>Saham IDX</h1>
            <p style='color: #6b7280; font-size: 1em; margin: 0;'>Investasi Saham Lebih Mudah dan Terstruktur</p>
        </div>
        """, unsafe_allow_html=True)

        if menu_selection == "Scraper Saham":
            stock_scraper_page()
        elif menu_selection == "Screener Saham":
            stock_screener_page()
        elif menu_selection == "Kalkulator Saham":
            # Submenu untuk Calculator
            st.markdown("""
            <div style='margin-bottom: 16px;'>
                <h3 style='color: #1a1a1a; margin-bottom: 12px;'>Pilih Platform</h3>
            </div>
            """, unsafe_allow_html=True)
            
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
                    "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px", "--hover-color": "#e5e7eb"},
                    "nav-link-selected": {"background-color": "#2563eb"},
                }
            )
            
            # Mapping platform ke fee beli dan fee jual
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
