import pandas as pd
import streamlit as st
from state_manager import save_config

from config import DEFAULT_SYMBOLS
from utils import (

    sanitize_stock_symbol,
    fetch_stock_data,
    apply_format_values,
    format_rupiah,
    format_ratio,
    format_percent,
    format_number,
    format_csv_indonesia,
)


def stock_scraper_page() -> None:
    st.info('Data menggunakan Yahoo Finance. Perhitungan jumlah lot, dividen, dan modal mengikuti input modal Anda.')

    col1, col2 = st.columns(2, gap="small")
    with col1:
        if 'scraper_symbols' not in st.session_state:
            st.session_state['scraper_symbols'] = DEFAULT_SYMBOLS
        symbols = st.text_area('Masukkan simbol saham (pisahkan dengan koma)', value=st.session_state['scraper_symbols'], key='scraper_symbols', on_change=save_config)
    with col2:
        if 'scraper_modal' not in st.session_state:
            st.session_state['scraper_modal'] = 1000000
        modal_rupiah = st.number_input("Masukkan modal dalam Rupiah", step=1000000, format="%d", min_value=0, value=st.session_state['scraper_modal'], key='scraper_modal', on_change=save_config)

    if st.button('Ambil Data', key='fetch_data'):
        with st.spinner('Menganalisis saham...'):
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

                df = pd.DataFrame(stocks_data).T
                st.session_state['scraper_df_raw'] = df.copy()

                numeric_columns = ['Current Price', 'Price/Book (PBVR)', 'Trailing P/E (PER)', 
                                 'Total Debt/Equity (mrq) (DER)', 'Return on Equity (%) (ROE)',
                                 'Diluted EPS (ttm) (EPS)', 'Forward Annual Dividend Rate (DPS)',
                                 'Forward Annual Dividend Yield (%)']

                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce').replace([pd.NA, float('inf'), float('-inf')], 0)

                df['Current Price'] = df['Current Price'].abs()
                df['Current Price'] = df['Current Price'].replace(0, pd.NA)
                df['Current Price'] = df['Current Price'].apply(lambda x: max(1, x) if pd.notna(x) else x)

                modal_rupiah = max(0, abs(modal_rupiah))

                df['Jumlah Saham'] = (modal_rupiah / df['Current Price']).fillna(0)
                df['Jumlah Saham'] = pd.to_numeric(df['Jumlah Saham'], errors='coerce')
                df['Jumlah Lot'] = (df['Jumlah Saham'] // 100).fillna(0).astype('Int64')
                df['Jumlah Saham'] = df['Jumlah Lot'] * 100

                if 'Forward Annual Dividend Rate (DPS)' in df.columns:
                    df['Forward Annual Dividend Rate (DPS)'] = df['Forward Annual Dividend Rate (DPS)'].abs()
                    df['Forward Annual Dividend Rate (DPS)'] = df['Forward Annual Dividend Rate (DPS)'].fillna(0)
                else:
                    df['Forward Annual Dividend Rate (DPS)'] = 0
                df['Dividen'] = df['Jumlah Saham'] * df['Forward Annual Dividend Rate (DPS)']

                df['Modal'] = df['Jumlah Saham'] * df['Current Price']

                numeric_columns = ['Current Price', 'Price/Book (PBVR)', 'Trailing P/E (PER)', 
                                 'Total Debt/Equity (mrq) (DER)', 'Return on Equity (%) (ROE)',
                                 'Diluted EPS (ttm) (EPS)', 'Forward Annual Dividend Rate (DPS)',
                                 'Forward Annual Dividend Yield (%)', 'Dividen', 'Modal']

                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                        df[col] = df[col].round(2)

                def dash_or(fn):
                    return (lambda v: '-' if (pd.isna(v) or v == 0) else fn(v))

                format_dict = {
                    'Current Price': dash_or(lambda x: format_rupiah(x)),
                    'Price/Book (PBVR)': (lambda x: '-' if (pd.isna(x) or x == 0 or x > 1000) else format_ratio(x)),
                    'Trailing P/E (PER)': dash_or(lambda x: format_ratio(x)),
                    'Total Debt/Equity (mrq) (DER)': dash_or(lambda x: format_ratio(x)),
                    'Return on Equity (%) (ROE)': dash_or(lambda x: f"{round((x or 0)*100):.0f}%"),
                    'Diluted EPS (ttm) (EPS)': dash_or(lambda x: format_rupiah(x)),
                    'Forward Annual Dividend Rate (DPS)': dash_or(lambda x: format_rupiah(x)),
                    'Forward Annual Dividend Yield (%)': dash_or(lambda x: format_percent(x, 2)),
                    'Jumlah Saham': dash_or(lambda x: format_number(x, 0)),
                    'Dividen': dash_or(lambda x: format_rupiah(x)),
                    'Jumlah Lot': dash_or(lambda x: format_number(x, 0)),
                    'Modal': dash_or(lambda x: format_rupiah(x))
                }

                # Removed Expander to avoid potential rendering issues
                df_display = df[df['Current Price'] > 0].copy()
                df_display = df_display.reset_index(drop=True)
                # Urutan kolom sesuai permintaan
                display_columns = [
                    'Symbol', 'Current Price', 'Price/Book (PBVR)', 'Trailing P/E (PER)',
                    'Total Debt/Equity (mrq) (DER)', 'Return on Equity (%) (ROE)',
                    'Diluted EPS (ttm) (EPS)', 'Forward Annual Dividend Rate (DPS)',
                    'Forward Annual Dividend Yield (%)', 'Jumlah Saham', 'Jumlah Lot',
                    'Dividen', 'Modal'
                ]
                available_columns = [c for c in display_columns if c in df_display.columns]
                df_display = df_display[available_columns]
                
                if df_display.empty:
                    st.warning("Data saham ditemukan tetapi tidak memenuhi kriteria filter (Harga > 0) atau kolom data kosong.")
                else:
                    df_display.index = df_display.index + 1
                    st.success(f"Berhasil mengambil data: {len(df_display)} saham.")
                
                # Simplified Dataframe Rendering
                df_view = apply_format_values(df_display, format_dict)
                st.dataframe(
                    df_view,
                    width='stretch',
                    hide_index=True
                )

                df_download = df_display.copy()
                for col in df_download.columns:
                    if col in ['Current Price', 'Forward Annual Dividend Rate (DPS)', 'Dividen', 'Modal']:
                        df_download[col] = df_download[col].apply(lambda x: '-' if (pd.isna(x) or x == 0) else format_csv_indonesia(x, 0))
                    elif col in ['Price/Book (PBVR)', 'Trailing P/E (PER)', 'Total Debt/Equity (mrq) (DER)']:
                        df_download[col] = df_download[col].apply(lambda x: '-' if (pd.isna(x) or x == 0) else format_csv_indonesia(x, 2))
                    elif col in ['Return on Equity (%) (ROE)', 'Forward Annual Dividend Yield (%)']:
                        df_download[col] = df_download[col].apply(lambda x: '-' if (pd.isna(x) or x == 0) else format_csv_indonesia(x, 2))
                    elif col in ['Diluted EPS (ttm) (EPS)']:
                        df_download[col] = df_download[col].apply(lambda x: '-' if (pd.isna(x) or x == 0) else format_csv_indonesia(x, 0))

                csv = df_download.to_csv(index=False, sep=';', encoding='utf-8-sig', quoting=1)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name="scraper_saham.csv",
                    mime="text/csv",
                    key="download_scraper_csv"
                )

                # Debug/raw dihapus agar UI sederhana
            except Exception as e:
                st.error(f"Terjadi kesalahan: {str(e)}")
