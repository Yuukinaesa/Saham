import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_option_menu import option_menu
from typing import Dict, List, Tuple, Optional
import re
import locale
import numpy as np
from scipy.stats import norm

# Set locale untuk format Rupiah
try:
    locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except:
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
            stock = yf.Ticker(symbol)
            info = stock.info
            
            if not info:
                st.warning(f"Tidak dapat mengambil data untuk {symbol}")
                continue
                
            current_price = round(info.get('regularMarketPrice', info.get('regularMarketPreviousClose', 0)))
            
            # Pastikan nilai persentase dalam bentuk desimal
            forward_dividend_yield = float(info.get('dividendYield', 0))
            roe = float(info.get('returnOnEquity', 0))
            
            # Handle infinity values
            trailing_pe = info.get('trailingPE', 0)
            if trailing_pe == float('inf') or trailing_pe == float('-inf'):
                trailing_pe = 0
                
            price_to_book = info.get('priceToBook', 0)
            if price_to_book == float('inf') or price_to_book == float('-inf'):
                price_to_book = 0
                
            debt_to_equity = info.get('debtToEquity', 0)
            if debt_to_equity == float('inf') or debt_to_equity == float('-inf'):
                debt_to_equity = 0
            
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

def calculate_dividend(jumlah_lot: int, dividen_per_saham: float) -> float:
    """Menghitung total dividen yang diterima.
    
    Args:
        jumlah_lot (int): Jumlah lot
        dividen_per_saham (float): Dividen per saham
        
    Returns:
        float: Total dividen
    """
    return jumlah_lot * dividen_per_saham * 100 if dividen_per_saham != 0 else 0

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
            
        # Pastikan nilai dalam bentuk desimal (0-1)
        if value > 1:
            value = value / 100
            
        # Format khusus untuk Forward Annual Dividend Yield
        if decimals == 2:
            return f"{value*100:,.2f}%".replace(".", ",")
        return f"{value*100:,.{decimals}f}%".replace(".", ",")
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
    st.info('Catatan: Data berasal dari Yahoo Finance. Pembelian disesuaikan dengan modal untuk jumlah lot yang sesuai.')
    
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
                
                # Hitung rasio dividen terhadap modal (hanya jika modal > 0)
                df['Dividend Yield'] = 0.0
                mask = df['Modal'] > 0
                df.loc[mask, 'Dividend Yield'] = (df.loc[mask, 'Dividen'] / df.loc[mask, 'Modal'] * 100).astype(float)
                
                # Bulatkan semua nilai numerik
                numeric_columns = ['Current Price', 'Price/Book (PBVR)', 'Trailing P/E (PER)', 
                                 'Total Debt/Equity (mrq) (DER)', 'Return on Equity (%) (ROE)',
                                 'Diluted EPS (ttm) (EPS)', 'Forward Annual Dividend Rate (DPS)',
                                 'Forward Annual Dividend Yield (%)', 'Dividen', 'Modal', 'Dividend Yield']
                
                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = df[col].round(2)

                # Memformat dataframe
                format_dict = {
                    'Current Price': lambda x: format_rupiah(x),
                    'Price/Book (PBVR)': lambda x: format_ratio(x),
                    'Trailing P/E (PER)': lambda x: format_ratio(x),
                    'Total Debt/Equity (mrq) (DER)': lambda x: format_ratio(x),
                    'Return on Equity (%) (ROE)': lambda x: format_percent(x, 0),
                    'Diluted EPS (ttm) (EPS)': lambda x: format_rupiah(x),
                    'Forward Annual Dividend Rate (DPS)': lambda x: format_rupiah(x),
                    'Forward Annual Dividend Yield (%)': lambda x: format_percent(x, 2),
                    'Jumlah Saham': lambda x: format_number(x, 0),
                    'Dividen': lambda x: format_rupiah(x),
                    'Jumlah Lot': lambda x: format_number(x, 0),
                    'Modal': lambda x: format_rupiah(x),
                    'Dividend Yield': lambda x: format_percent(x, 2)
                }
                
                with st.expander("Tampilkan Data Statistik", expanded=True):
                    df_display = df.reset_index(drop=True)
                    df_display.index = df_display.index + 1
                    
                    st.dataframe(
                        format_dataframe(df_display, format_dict),
                        use_container_width=True,
                        height=400
                    )

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
        
        st.markdown('<div class="section-title">⚙️ Pengaturan Fee</div>', unsafe_allow_html=True)
        include_fee_beli = st.checkbox("Masukkan Fee Beli", value=True)
        include_fee_jual = st.checkbox("Masukkan Fee Jual", value=True)
        include_dividend = st.checkbox("Masukkan Dividen")

        # Input dividen
        dividen_per_saham = 0
        if include_dividend:
            dividen_per_saham = st.number_input("Dividen per Saham:", step=1, format="%d")

        # Button section
        st.markdown('<div style="text-align: center; margin: 16px 0;">', unsafe_allow_html=True)
        if st.button("Hitung", key="calculate"):
            with st.spinner('Menghitung...'):
                # Gunakan fee yang sesuai dengan checkbox
                fee_beli_final = fee_beli if include_fee_beli else 0
                fee_jual_final = fee_jual if include_fee_jual else 0
                
                total_beli, total_jual, profit_loss, profit_loss_percentage = calculate_profit_loss(
                    jumlah_lot, harga_beli, harga_jual, fee_beli_final, fee_jual_final
                )
                
                # Results section
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">📊 Hasil Perhitungan</div>', unsafe_allow_html=True)
                st.write(f"Total Beli: {format_rupiah(total_beli)}")
                st.write(f"Total Jual: {format_rupiah(total_jual)}")
                st.write(f"Profit/Loss: {format_rupiah(profit_loss)}")
                st.write(f"Profit/Loss Percentage: {format_percent(profit_loss_percentage, 2)}")
                
                # Tambahkan hasil dividen jika ada
                if include_dividend and dividen_per_saham > 0:
                    total_dividen = calculate_dividend(jumlah_lot, dividen_per_saham)
                    dividend_yield = calculate_dividend_yield(dividen_per_saham, harga_beli)
                    st.write(f"Total Dividen: {format_rupiah(total_dividen)}")
                    st.write(f"Dividend Yield: {format_percent(dividend_yield, 2)}")
                
                st.markdown('</div>', unsafe_allow_html=True)

                if profit_loss > 0:
                    st.success("🎉 Profit!")
                elif profit_loss < 0:
                    st.error("😢 Loss!")
                else:
                    st.info("⚖️ Break Even!")

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
        # Hitung bunga bulanan
        amount *= (1 + rate / 100 / 12)  
        # Tambahkan investasi bulanan
        amount += additional_investment  
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

                for year_num in range(1, int(years) + 1):
                    yearly_data = df[df['Year'] == year_num]
                    with st.expander(f'📅 Tahun {year_num}', expanded=False):
                        st.dataframe(
                            yearly_data[['Month', 'Amount']].set_index(yearly_data.index + 1),
                            use_container_width=True
                        )
            except Exception as e:
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
        # Pola persentase berdasarkan harga
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

def calculate_next_price(harga_sekarang: float, persentase: float, is_ara: bool) -> float:
    """Menghitung harga berikutnya dengan persentase yang fleksibel.
    
    Args:
        harga_sekarang (float): Harga saat ini
        persentase (float): Persentase kenaikan/penurunan
        is_ara (bool): True untuk ARA, False untuk ARB
        
    Returns:
        float: Harga berikutnya yang sudah dibulatkan
    """
    # Pastikan nilai positif
    harga_sekarang = abs(harga_sekarang)
    persentase = abs(persentase)
    
    if is_ara:
        # Hitung harga maksimum yang diizinkan
        harga_maks = harga_sekarang * (1 + persentase/100)
        # Cari harga terdekat yang tidak melebihi batas
        harga_baru = harga_sekarang
        while harga_baru < harga_maks:
            harga_baru += 5  # Kelipatan 5
        harga_baru -= 5  # Kembali ke harga sebelumnya yang masih dalam batas
    else:
        # Hitung harga minimum yang diizinkan
        harga_min = harga_sekarang * (1 - persentase/100)
        # Cari harga terdekat yang tidak melebihi batas
        harga_baru = harga_sekarang
        while harga_baru > harga_min:
            harga_baru -= 5  # Kelipatan 5
        harga_baru += 5  # Kembali ke harga sebelumnya yang masih dalam batas
    
    # Bulatkan ke kelipatan 5 terdekat
    return round(harga_baru / 5) * 5

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
                <p style='margin: 0;'>• Harga ≥ Rp 5.000: ±20%</p>
                <p style='margin: 0;'>• Harga Rp 1.000 - Rp 5.000: ±25%</p>
                <p style='margin: 0;'>• Harga Rp 100 - Rp 1.000: ±25%</p>
                <p style='margin: 0;'>• Harga Rp 50 - Rp 100: ±35%</p>
                <p style='margin: 0 0 8px 0;'>• Minimum harga: Rp 1</p>
                """, unsafe_allow_html=True)
        
        min_value = 1
        harga_penutupan = st.number_input('💰 Harga Penutupan', step=100, format="%d", min_value=min_value, value=150)
        
        jumlah_hari = st.number_input('📅 Jumlah Hari', min_value=1, max_value=30, value=7, step=1)
        
        if st.button('Hitung ARA ARB', type='primary'):
            if harga_penutupan >= min_value:
                st.markdown("""
                <div style='margin-bottom: 16px;'>
                    <h3 style='color: #1a1a1a; margin-bottom: 5px; font-size: 16px;'>📊 Hasil Perhitungan</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Tampilkan harga penutupan
                st.markdown(f"""
                <div style='margin-bottom: 8px; background-color: #f8f9fa; padding: 12px 8px 12px 16px; border-radius: 6px; border-left: 3px solid #2563eb;'>
                    <h4 style='color: #1a1a1a; margin: 0; font-size: 16px;'>💰 Harga Penutupan: {format_rupiah(harga_penutupan)}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                ara_data = []
                harga_ara_sekarang = harga_penutupan
                for hari in range(1, jumlah_hari + 1):
                    persentase_ara = get_ara_arb_percentage(harga_ara_sekarang, is_acceleration)
                    if is_acceleration and harga_ara_sekarang <= 10:
                        harga_ara_baru = harga_ara_sekarang + persentase_ara
                    else:
                        harga_ara_baru = calculate_next_price(harga_ara_sekarang, persentase_ara, True)
                    
                    # Hitung persentase aktual
                    persentase_aktual = calculate_actual_percentage(harga_ara_sekarang, harga_ara_baru)
                    
                    ara_data.append({
                        'Hari': f'Hari {hari}',
                        'Harga ARA': f'Rp {harga_ara_baru:,.0f}',
                        'Kenaikan': f'{persentase_aktual:.2f}%',
                        'Harga Dasar': f'Rp {harga_ara_sekarang:,.0f}'
                    })
                    
                    harga_ara_sekarang = harga_ara_baru
                
                arb_data = []
                harga_arb_sekarang = harga_penutupan
                for hari in range(1, jumlah_hari + 1):
                    persentase_arb = get_ara_arb_percentage(harga_arb_sekarang, is_acceleration)
                    if is_acceleration and harga_arb_sekarang <= 10:
                        harga_arb_baru = harga_arb_sekarang - persentase_arb
                    else:
                        harga_arb_baru = calculate_next_price(harga_arb_sekarang, persentase_arb, False)
                    
                    # Hitung persentase aktual
                    persentase_aktual = calculate_actual_percentage(harga_arb_sekarang, harga_arb_baru)
                    
                    arb_data.append({
                        'Hari': f'Hari {hari}',
                        'Harga ARB': f'Rp {harga_arb_baru:,.0f}',
                        'Penurunan': f'{persentase_aktual:.2f}%',
                        'Harga Dasar': f'Rp {harga_arb_sekarang:,.0f}'
                    })
                    
                    harga_arb_sekarang = harga_arb_baru
                
                st.markdown("""
                <div style='margin-bottom: 8px; background-color: #f8f9fa; padding: 12px 8px 12px 16px; border-radius: 6px; border-left: 3px solid #22c55e;'>
                    <h4 style='color: #1a1a1a; margin: 0; font-size: 16px;'>📈 Harga ARA (Auto Reject Above)</h4>
                </div>
                """, unsafe_allow_html=True)
                
                df_ara = pd.DataFrame(ara_data)
                st.dataframe(
                    df_ara,
                    column_config={
                        "Hari": st.column_config.TextColumn("Hari", width="small"),
                        "Harga ARA": st.column_config.TextColumn("Harga ARA", width="medium"),
                        "Kenaikan": st.column_config.TextColumn("Kenaikan", width="small"),
                        "Harga Dasar": st.column_config.TextColumn("Harga Dasar", width="medium")
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                st.markdown("""
                <div style='margin-top: 8px; margin-bottom: 8px; background-color: #f8f9fa; padding: 12px 8px 12px 16px; border-radius: 6px; border-left: 3px solid #ef4444;'>
                    <h4 style='color: #1a1a1a; margin: 0; font-size: 16px;'>📉 Harga ARB (Auto Reject Below)</h4>
                </div>
                """, unsafe_allow_html=True)
                
                df_arb = pd.DataFrame(arb_data)
                st.dataframe(
                    df_arb,
                    column_config={
                        "Hari": st.column_config.TextColumn("Hari", width="small"),
                        "Harga ARB": st.column_config.TextColumn("Harga ARB", width="medium"),
                        "Penurunan": st.column_config.TextColumn("Penurunan", width="small"),
                        "Harga Dasar": st.column_config.TextColumn("Harga Dasar", width="medium")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.error(f"Harga saham harus minimal Rp {min_value}")

def warrant_calculator_page() -> None:
    """Halaman untuk menghitung keuntungan jual warrant."""
    
    col1, col2 = st.columns(2, gap="small")
    
    with col1:
        # Pilih platform
        st.markdown("""
        <div style='margin-bottom: 16px;'>
            <h3 style='color: #1a1a1a; margin-bottom: 12px;'>Pilih Platform</h3>
        </div>
        """, unsafe_allow_html=True)
        
        platform = option_menu(
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
        
        # Ambil fee dari platform
        fee_beli, fee_jual = PLATFORM_CONFIG.get(platform, (0, 0))
        
        # Input harga beli dan jual warrant
        harga_beli_warrant = st.number_input('💰 Harga Beli Warrant', step=100, format="%d", value=100)
        harga_jual_warrant = st.number_input('💵 Harga Jual Warrant', step=100, format="%d", value=150)
        jumlah_lot = st.number_input('📦 Jumlah Lot', step=0.5, format="%.1f", value=1.0)
        
        # Jika platform Custom, tampilkan input fee
        if platform == "Custom":
            st.markdown("""
            <div style='margin-bottom: 16px;'>
                <h3 style='color: #1a1a1a; margin-bottom: 12px;'>Masukkan Fee Kustom</h3>
            </div>
            """, unsafe_allow_html=True)
            fee_beli = st.number_input("Fee Beli (persentase):", step=0.1, format="%.2f") / 100
            fee_jual = st.number_input("Fee Jual (persentase):", step=0.1, format="%.2f") / 100
        
        # Tampilkan fee platform
        st.markdown(f"""
        <div style='margin-bottom: 16px; background-color: #f8f9fa; padding: 12px 8px 12px 16px; border-radius: 6px; border-left: 3px solid #2563eb;'>
            <h4 style='color: #1a1a1a; margin: 0; font-size: 16px;'>💸 Fee Platform</h4>
            <p style='margin: 4px 0 0 0; color: #6b7280; font-size: 14px;'>Fee Beli: {fee_beli*100:.2f}% | Fee Jual: {fee_jual*100:.2f}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Opsi untuk mengaktifkan/menonaktifkan fee
        include_fee_beli = st.checkbox("Masukkan Fee Beli", value=True)
        include_fee_jual = st.checkbox("Masukkan Fee Jual", value=True)
        
        if st.button('Hitung Keuntungan', type='primary'):
            # Hitung total beli dan jual
            # Pastikan nilai positif dan valid
            harga_beli_warrant = max(1, abs(harga_beli_warrant))  # Minimal Rp 1
            harga_jual_warrant = max(1, abs(harga_jual_warrant))  # Minimal Rp 1
            jumlah_lot = max(0.5, abs(jumlah_lot))  # Minimal 0.5 lot
            fee_beli = min(1, abs(fee_beli))  # Maksimal 100%
            fee_jual = min(1, abs(fee_jual))  # Maksimal 100%
            
            total_beli = harga_beli_warrant * jumlah_lot * 100
            total_jual = harga_jual_warrant * jumlah_lot * 100
            
            # Hitung fee
            total_fee_beli = total_beli * fee_beli if include_fee_beli else 0
            total_fee_jual = total_jual * fee_jual if include_fee_jual else 0
            
            # Hitung total modal dan hasil
            total_modal = total_beli + total_fee_beli
            total_hasil = total_jual - total_fee_jual
            
            # Hitung keuntungan
            keuntungan = total_hasil - total_modal
            persentase_keuntungan = (keuntungan / total_modal * 100) if total_modal > 0 else 0
            
            # Bulatkan semua nilai
            total_beli = round(total_beli, 2)
            total_jual = round(total_jual, 2)
            total_fee_beli = round(total_fee_beli, 2)
            total_fee_jual = round(total_fee_jual, 2)
            total_modal = round(total_modal, 2)
            total_hasil = round(total_hasil, 2)
            keuntungan = round(keuntungan, 2)
            persentase_keuntungan = round(persentase_keuntungan, 2)
            
            # Tampilkan hasil
            st.markdown("""
            <div style='margin-bottom: 16px;'>
                <h3 style='color: #1a1a1a; margin-bottom: 5px; font-size: 16px;'>📊 Hasil Perhitungan</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Tampilkan total beli
            st.markdown(f"""
            <div style='margin-bottom: 8px; background-color: #f8f9fa; padding: 12px 8px 12px 16px; border-radius: 6px; border-left: 3px solid #2563eb;'>
                <h4 style='color: #1a1a1a; margin: 0; font-size: 16px;'>💰 Total Beli: {format_rupiah(total_beli)}</h4>
                {f'<p style="margin: 4px 0 0 0; color: #6b7280; font-size: 14px;">Fee Beli: {format_rupiah(total_fee_beli)} ({fee_beli*100:.2f}%)</p>' if include_fee_beli else ''}
            </div>
            """, unsafe_allow_html=True)
            
            # Tampilkan total jual
            st.markdown(f"""
            <div style='margin-bottom: 8px; background-color: #f8f9fa; padding: 12px 8px 12px 16px; border-radius: 6px; border-left: 3px solid #22c55e;'>
                <h4 style='color: #1a1a1a; margin: 0; font-size: 16px;'>💵 Total Jual: {format_rupiah(total_jual)}</h4>
                {f'<p style="margin: 4px 0 0 0; color: #6b7280; font-size: 14px;">Fee Jual: {format_rupiah(total_fee_jual)} ({fee_jual*100:.2f}%)</p>' if include_fee_jual else ''}
            </div>
            """, unsafe_allow_html=True)
            
            # Tampilkan keuntungan
            if keuntungan > 0:
                st.markdown(f"""
                <div style='margin-bottom: 8px; background-color: #f8f9fa; padding: 12px 8px 12px 16px; border-radius: 6px; border-left: 3px solid #22c55e;'>
                    <h4 style='color: #1a1a1a; margin: 0; font-size: 16px;'>📈 Keuntungan: {format_rupiah(keuntungan)}</h4>
                    <p style='margin: 4px 0 0 0; color: #6b7280; font-size: 14px;'>Persentase: {persentase_keuntungan:.2f}%</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='margin-bottom: 8px; background-color: #f8f9fa; padding: 12px 8px 12px 16px; border-radius: 6px; border-left: 3px solid #ef4444;'>
                    <h4 style='color: #1a1a1a; margin: 0; font-size: 16px;'>📉 Kerugian: {format_rupiah(abs(keuntungan))}</h4>
                    <p style='margin: 4px 0 0 0; color: #6b7280; font-size: 14px;'>Persentase: {abs(persentase_keuntungan):.2f}%</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Tampilkan informasi tambahan
            with st.expander("ℹ️ Informasi Perhitungan", expanded=False):
                st.markdown("""
                <h4 style='color: #1a1a1a; margin: 0;'>Rumus Perhitungan:</h4>
                <ul style='margin: 8px 0 0 0; padding-left: 20px;'>
                    <li style='margin-bottom: 8px;'><strong>Total Beli:</strong> Harga Beli × Jumlah Lot × 100</li>
                    <li style='margin-bottom: 8px;'><strong>Total Jual:</strong> Harga Jual × Jumlah Lot × 100</li>
                    <li style='margin-bottom: 8px;'><strong>Fee Beli:</strong> Total Beli × Persentase Fee Beli</li>
                    <li style='margin-bottom: 8px;'><strong>Fee Jual:</strong> Total Jual × Persentase Fee Jual</li>
                    <li style='margin-bottom: 8px;'><strong>Keuntungan:</strong> (Total Jual - Fee Jual) - (Total Beli + Fee Beli)</li>
                </ul>
                """, unsafe_allow_html=True)

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
            ["Scraper Saham", "Kalkulator Saham", "Compound Interest", "ARA ARB Calculator", "Warrant Calculator"],
            icons=["graph-up", "calculator", "bookmark", "percent", "ticket-perforated"],
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
