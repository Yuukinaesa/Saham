import time
import pandas as pd
import streamlit as st

from config import DEFAULT_SYMBOLS
from utils import (
    sanitize_stock_symbol,
    apply_format_values,
    format_rupiah,
    format_ratio,
    format_percent,
    format_number,
    format_short_number,
    format_csv_indonesia,
)
from utils import fetch_enhanced_stock_data


def get_simple_arrow(value: float) -> str:
    if pd.isna(value) or value == 0:
        return "—"
    if abs(value) < 1:
        value = value * 100
    if value > 0:
        return f"🟢↑ {value:.2f}%"
    else:
        return f"🔴↓ {abs(value):.2f}%"


def stock_screener_page() -> None:
    col1, col2 = st.columns(2, gap="small")
    with col1:
        symbols = st.text_area('Masukkan simbol saham (pisahkan dengan koma)', DEFAULT_SYMBOLS)
    # Tidak ada checkbox debug di screener

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

                df = pd.DataFrame(stocks_data).T

                numeric_columns = [
                    'Current Price', 'Market Cap', 'Shares Outstanding', 'Float Shares',
                    'Institutional Ownership %', 'Insider Ownership %', 'Number of Institutions',
                    'Price/Book (PBVR)', 'Trailing P/E (PER)', 'Return on Equity (%) (ROE)',
                    'Return on Assets (%) (ROA)', 'Return on Capital (%) (ROC)',
                    'Net Income', 'Cash from Operations', 'Free Cash Flow',
                    'Total Assets', 'Total Equity', 'Total Liabilities'
                ]

                for col in numeric_columns:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce').replace([pd.NA, float('inf'), float('-inf')], 0)

                if 'Return on Equity (%) (ROE)' in df.columns:
                    df['ROE Change'] = df['Return on Equity (%) (ROE)'].apply(lambda x: get_simple_arrow(x))
                if 'Return on Assets (%) (ROA)' in df.columns:
                    df['ROA Change'] = df['Return on Assets (%) (ROA)'].apply(lambda x: get_simple_arrow(x))

                for col in numeric_columns + ['Public Float %']:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                        df[col] = df[col].round(2)

                # Hitung Public Float % jika data ada
                if 'Float Shares' in df.columns and 'Shares Outstanding' in df.columns:
                    df['Public Float %'] = (df['Float Shares'] / df['Shares Outstanding'] * 100).fillna(0)
                    df['Public Float %'] = df['Public Float %'].replace([float('inf'), float('-inf')], 0)

                df_display = df[df['Current Price'] > 0].copy() if 'Current Price' in df.columns else df.copy()
                df_display = df_display.reset_index(drop=True)
                # Susun kolom sesuai permintaan pengguna
                desired_columns = [
                    'Symbol', 'Current Price', 'Market Cap', 'Public Float %', 'Insider Ownership %',
                    'Price/Book (PBVR)', 'ROE Change', 'ROA Change', 'Net Income', 'Free Cash Flow'
                ]
                available_columns = [c for c in desired_columns if c in df_display.columns]
                df_display = df_display[available_columns]
                df_display.index = df_display.index + 1
                st.session_state['screener_df_display'] = df_display
                st.session_state['screener_results'] = stocks_data

                st.markdown(
                    """
<div style='margin: 16px 0 16px 0;'>
<h3 style='margin: 0; color: var(--text-color);'>Hasil Screener</h3>
</div>
""",
                    unsafe_allow_html=True,
                )
                
                st.success(f"Berhasil menyaring data: {len(df_display)} saham.")

                def dash_or(fn):
                    return (lambda v: '—' if (pd.isna(v) or v == 0) else fn(v))

                # Hapus kolom yang tidak diperlukan untuk screener
                for col_drop in ['EPS', 'Dividend Yield %', 'Forward Annual Dividend Rate (DPS)',
                                 'Diluted EPS (ttm) (EPS)', 'Total Debt/Equity (mrq) (DER)']:
                    if col_drop in df_display.columns:
                        del df_display[col_drop]

                # Only include existing columns in the formatter
                fmt_candidates = {
                    'Current Price': dash_or(lambda x: format_rupiah(x)),
                    'Market Cap': dash_or(lambda x: format_short_number(x)),
                    'Shares Outstanding': dash_or(lambda x: format_number(x, 0)),
                    'Float Shares': dash_or(lambda x: format_number(x, 0)),
                    'Institutional Ownership %': dash_or(lambda x: format_percent(x, 2)),
                    'Insider Ownership %': dash_or(lambda x: format_percent(x, 2)),
                    'Public Float %': dash_or(lambda x: format_percent(x, 2)),
                    'Price/Book (PBVR)': dash_or(lambda x: format_ratio(x)),
                    'Trailing P/E (PER)': dash_or(lambda x: format_ratio(x)),
                    'Return on Equity (%) (ROE)': dash_or(lambda x: format_percent(x, 2)),
                    'Return on Assets (%) (ROA)': dash_or(lambda x: format_percent(x, 2)),
                    'Return on Capital (%) (ROC)': dash_or(lambda x: format_percent(x, 2)),
                    'Net Income': dash_or(lambda x: format_short_number(x)),
                    'Cash from Operations': dash_or(lambda x: format_number(x, 0)),
                    'Free Cash Flow': dash_or(lambda x: format_short_number(x)),
                    'Total Assets': dash_or(lambda x: format_number(x, 0)),
                    'Total Equity': dash_or(lambda x: format_number(x, 0)),
                    'Total Liabilities': dash_or(lambda x: format_number(x, 0)),
                }
                format_dict = {k: v for k, v in fmt_candidates.items() if k in df_display.columns}

                df_view = apply_format_values(df_display, format_dict)
                st.dataframe(df_view, width='stretch', hide_index=True)

                # Download CSV dengan struktur sesuai tabel screener
                df_download = df_display.copy()
                rupiah_cols = ['Current Price', 'Net Income', 'Free Cash Flow', 'Total Assets', 'Total Equity', 'Total Liabilities']
                ratio_cols = ['Price/Book (PBVR)', 'Trailing P/E (PER)']
                percent_cols = ['Institutional Ownership %', 'Insider Ownership %', 'Public Float %']
                for col in df_download.columns:
                    if col in rupiah_cols:
                        df_download[col] = df_download[col].apply(lambda x: format_csv_indonesia(x, 0) if pd.notna(x) else '0')
                    elif col in ratio_cols:
                        df_download[col] = df_download[col].apply(lambda x: format_csv_indonesia(x, 2) if pd.notna(x) else '0')
                    elif col in percent_cols:
                        df_download[col] = df_download[col].apply(lambda x: format_csv_indonesia(x, 2) if pd.notna(x) else '0')
                    else:
                        # keep strings like Symbol, ROE Change, ROA Change as-is
                        df_download[col] = df_download[col].astype(str)
                csv = df_download.to_csv(index=False, sep=';', encoding='utf-8-sig', quoting=1)
                st.download_button(label='📥 Download as CSV', data=csv, file_name='screener_saham.csv', mime='text/csv')

                # Hilangkan opsi debug/raw
            except Exception as e:
                st.error(f"Terjadi kesalahan: {str(e)}")

            # Hindari render ganda pada run yang sama
            return

    # Re-render last results without re-fetching so UI stays stable
    if 'screener_df_display' in st.session_state:
        df_display = st.session_state['screener_df_display']
        def dash_or(fn):
            return (lambda v: '—' if (pd.isna(v) or v == 0) else fn(v))
        fmt_candidates = {
            'Current Price': dash_or(lambda x: format_rupiah(x)),
            'Market Cap': dash_or(lambda x: format_number(x, 0)),
            'Shares Outstanding': dash_or(lambda x: format_number(x, 0)),
            'Float Shares': dash_or(lambda x: format_number(x, 0)),
            'Institutional Ownership %': dash_or(lambda x: format_percent(x, 2)),
            'Insider Ownership %': dash_or(lambda x: format_percent(x, 2)),
            'Public Float %': dash_or(lambda x: format_percent(x, 2)),
            'Price/Book (PBVR)': dash_or(lambda x: format_ratio(x)),
            'Trailing P/E (PER)': dash_or(lambda x: format_ratio(x)),
            'Return on Equity (%) (ROE)': dash_or(lambda x: format_percent(x, 2)),
        }
        format_dict = {k: v for k, v in fmt_candidates.items() if k in df_display.columns}
        st.dataframe(apply_format_values(df_display, format_dict), width='stretch', hide_index=True)


