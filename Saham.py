import streamlit as st
import yfinance as yf
import pandas as pd
import pickle
import os
import time
from streamlit_option_menu import option_menu

HISTORY_FILE = "history.pkl"

def apply_global_css():
    button_style = """
    <style>
        div.stButton > button {
            background-color: #2B8CCE;
            color: white;
            width: 100%;
            height: 50px;
            font-size: 18px;
        }
        
    </style>
    """
    st.markdown(button_style, unsafe_allow_html=True)

def save_history(data, filename=HISTORY_FILE):
    if not isinstance(data, dict):
        data = {"scraper": [], "calculator": []}
    try:
        with open(filename, "wb") as f:
            pickle.dump(data, f)
    except Exception as e:
        st.error(f"Error saving history: {str(e)}")

def load_history(filename=HISTORY_FILE):
    if os.path.exists(filename):
        try:
            with open(filename, "rb") as f:
                return pickle.load(f)
        except pickle.UnpicklingError:
            st.error("History file is corrupted and cannot be loaded.")
            return {"scraper": [], "calculator": []}
        except Exception as e:
            st.error(f"An error occurred while loading history: {str(e)}")
            return {"scraper": [], "calculator": []}
    return {"scraper": [], "calculator": []}

def initialize_session_state(key, default_value):
    if key not in st.session_state:
        st.session_state[key] = default_value

def format_dataframe(df, columns):
    return df.style.format(columns)

def fetch_stock_data(symbols):
    data = {}
    for symbol in symbols:
        stock = yf.Ticker(symbol)
        info = stock.info
        current_price = round(info.get('regularMarketPrice', info.get('regularMarketPreviousClose')) or 0)
        forward_dividend_yield = round(info.get('dividendYield', 0) * 100, 2)
        data[symbol] = {
            'Symbol': symbol,
            'Current Price': current_price,
            'Price/Book (PBVR)': info.get('priceToBook') or 0,
            'Trailing P/E (PER)': info.get('trailingPE') or 0,
            'Total Debt/Equity (mrq) (DER)': info.get('debtToEquity') or 0,
            'Return on Equity (%) (ROE)': round((info.get('returnOnEquity') or 0) * 100),
            'Diluted EPS (ttm) (EPS)': round(info.get('trailingEps') or 0),
            'Forward Annual Dividend Rate (DPS)': round(info.get('dividendRate') or 0),
            'Forward Annual Dividend Yield (%)': forward_dividend_yield,
        }
    return data

def calculate_profit_loss(jumlah_lot, harga_beli, harga_jual, fee_beli, fee_jual):
    if harga_beli == 0 or harga_jual == 0:
        st.error("Harga beli atau harga jual tidak bisa 0.")
        return 0, 0, 0, 0
    total_beli = jumlah_lot * 100 * harga_beli * (1 + fee_beli)
    total_jual = jumlah_lot * 100 * harga_jual * (1 - fee_jual)
    profit_loss = total_jual - total_beli
    profit_loss_percentage = (profit_loss / total_beli) * 100 if total_beli != 0 else 0
    return total_beli, total_jual, profit_loss, profit_loss_percentage

def calculate_dividend(jumlah_lot, dividen_per_saham):
    if dividen_per_saham == 0:
        return 0
    return jumlah_lot * dividen_per_saham * 100

def calculate_dividend_yield(dividen_per_saham, harga_beli):
    if harga_beli == 0:
        return 0
    return (dividen_per_saham / harga_beli) * 100

def stock_scraper_page():
    st.info('Catatan: Data yang digunakan berasal dari yahoo finance, dan kemampuan membeli sudah disesuaikan dengan modal untuk mendapatkan jumlah lot yang sesuai.')
    symbols = st.text_area('Masukkan simbol saham (pisahkan dengan koma)', 'BBCA,BBRI,GOTO,TLKM,WSKT,ASII')
    symbols_list = [symbol.strip().upper() + '.JK' if '.JK' not in symbol else symbol.strip().upper() for symbol in symbols.split(',')]
    modal_rupiah = st.number_input("Masukkan modal dalam Rupiah", step=1000000, format="%d")

    if st.button('Ambil Data'):
        try:
            stocks_data = fetch_stock_data(symbols_list)
            df = pd.DataFrame(stocks_data).T
            df['Jumlah Saham'] = modal_rupiah / df['Current Price'].replace(0, pd.NA)
            df['Jumlah Saham'] = pd.to_numeric(df['Jumlah Saham'], errors='coerce')
            df['Jumlah Lot'] = (df['Jumlah Saham'] // 100).fillna(0).astype('Int64')
            df['Jumlah Saham'] = df['Jumlah Lot'] * 100
            df['Dividen'] = df['Jumlah Saham'] * df['Forward Annual Dividend Rate (DPS)']
            df['Modal'] = df['Jumlah Lot'] * 100 * df['Current Price']
            df['Symbol'] = df['Symbol'].str.replace('.JK', '', regex=False)
            pd.set_option('future.no_silent_downcasting', True)

            st.subheader('Data Statistik Terbaru')
            with st.expander("Tampilkan Data Statistik"):
                st.dataframe(format_dataframe(df.reset_index(drop=True), {
                    'Current Price': 'Rp{:,.0f}',
                    'Price/Book (PBVR)': '{:.2f}',
                    'Trailing P/E (PER)': '{:.2f}',
                    'Total Debt/Equity (mrq) (DER)': '{:.2f}',
                    'Return on Equity (%) (ROE)': '{:.0f}%',
                    'Diluted EPS (ttm) (EPS)': '{:.0f}',
                    'Forward Annual Dividend Rate (DPS)': 'Rp{:,.0f}',
                    'Forward Annual Dividend Yield (%)': '{:.2f}%',
                    'Jumlah Saham': '{:,.0f}',
                    'Dividen': 'Rp{:,.0f}',
                    'Jumlah Lot': '{:,.0f}',
                    'Modal': 'Rp{:,.0f}'
                }))

            if "scraper_history" not in st.session_state:
                st.session_state.scraper_history = []
            st.session_state.scraper_history.append(df.to_dict('records'))
            save_history({"scraper": st.session_state.scraper_history, 
                         "calculator": st.session_state.get("calculator_history", [])})

        except Exception as e:
            st.error(f"Terjadi kesalahan: {str(e)}")

def calculator_page(title, fee_beli, fee_jual):
    st.header(title)
    st.markdown("<hr>", unsafe_allow_html=True)

    if title == "Custom":
        st.subheader("Masukkan Fee Kustom")
        fee_beli = st.number_input("Fee Beli (persentase):", min_value=0.0, step=0.1, format="%.2f") / 100
        fee_jual = st.number_input("Fee Jual (persentase):", min_value=0.0, step=0.1, format="%.2f") / 100

    jumlah_lot = st.number_input("Jumlah Lot:", min_value=0, step=1, format="%d")
    harga_beli = st.number_input("Harga Beli (per saham):", min_value=0.0, step=1000.0, format="%.0f")
    harga_jual = st.number_input("Harga Jual (per saham):", min_value=0.0, step=1000.0, format="%.0f")
    include_fee_beli = st.checkbox("Masukkan Fee Beli", value=True)
    include_fee_jual = st.checkbox("Masukkan Fee Jual", value=True)
    include_dividend = st.checkbox("Masukkan Dividen")

    fee_beli_final = fee_beli if include_fee_beli else 0
    fee_jual_final = fee_jual if include_fee_jual else 0

    profit_loss = 0
    profit_loss_percentage = 0
    total_dividen = 0
    dividend_yield = 0
    hasil = "Tidak ada perubahan"

    if include_dividend:
        dividen_per_saham = st.number_input("Dividen per Saham:", min_value=0, step=1, format="%d")
        if jumlah_lot > 0 and harga_beli > 0:
            total_dividen = calculate_dividend(jumlah_lot, dividen_per_saham)
            dividend_yield = calculate_dividend_yield(dividen_per_saham, harga_beli)
            st.write(f"Total Dividen: Rp {total_dividen:,.0f}")
            st.write(f"Dividend Yield: {dividend_yield:.2f}%")
            st.markdown('<hr style="border: 1px solid #e0e0e0;">', unsafe_allow_html=True)

    if st.button("Hitung", key="calculate"):
        if jumlah_lot > 0 and harga_beli > 0 and harga_jual > 0:
            total_beli, total_jual, profit_loss, profit_loss_percentage = calculate_profit_loss(
                jumlah_lot, harga_beli, harga_jual, fee_beli_final, fee_jual_final
            )
            hasil = "Profit" if profit_loss > 0 else "Loss" if profit_loss < 0 else "Tidak ada perubahan"
            st.write(f"Total Beli: Rp {total_beli:,.0f}")
            st.write(f"Total Jual: Rp {total_jual:,.0f}")
            st.write(f"Profit/Loss: Rp {profit_loss:,.0f}")
            st.write(f"Profit/Loss Percentage: {profit_loss_percentage:.2f}%")
            if hasil == "Profit":
                st.success("Profit!")
            elif hasil == "Loss":
                st.error("Loss!")
            else:
                st.info("Break Even!")

        else:
            st.error("Jumlah Lot, Harga Beli, dan Harga Jual harus lebih besar dari 0.")

        if "calculator_history" not in st.session_state:
            st.session_state.calculator_history = []

        calculation_record = {
            "platform": title,
            "jumlah_lot": jumlah_lot,
            "harga_beli": harga_beli,
            "harga_jual": harga_jual,
            "profit_loss": profit_loss,
            "profit_loss_percentage": profit_loss_percentage,
            "dividen": total_dividen,
            "dividend_yield": dividend_yield,
            "hasil": hasil
        }

        st.session_state.calculator_history.append(calculation_record)
        save_history({"scraper": st.session_state.get("scraper_history", []), 
                     "calculator": st.session_state.calculator_history})

def compound_interest_page():
    st.info('Bunga-berbunga atau compound interest adalah jenis bunga yang dihitung tidak hanya dari jumlah pokok awal, tetapi juga dari bunga yang sudah diperoleh.')

    def calculate_compound_interest(firstm, rate, years, additional_investment=0, frequency='monthly'):
        data = []
        total_months = int(years * 12)
        amount = firstm
        for month in range(1, total_months + 1):
            amount = (amount + additional_investment) * (1 + rate / 100 / 12)
            year = (month - 1) // 12 + 1
            data.append({
                'Year': year,
                'Month': month,
                'Amount': round(amount, 2)
            })
        return pd.DataFrame(data)

    firstm = st.number_input('💰 Masukkan nilai awal investasi', step=1000000, format="%d")
    rate = st.number_input('📈 Masukkan tingkat bunga per tahun (%)', step=5, format="%d")
    years = st.number_input('🗓️ Masukkan jumlah tahun (misal: 5.5 untuk 5 tahun 5 bulan)', step=0.1, format="%.1f")
    additional_investment = st.number_input('➕ Masukkan tambahan investasi per bulan', step=1000000, format="%d")

    if st.button('Hitung'):
        df = calculate_compound_interest(firstm, rate, years, additional_investment)
        with st.expander('📊 Hasil perhitungan bunga berbunga:', expanded=True):
            st.dataframe(df.set_index(df.index + 1), use_container_width=True, hide_index=True)

        st.markdown('<hr style="border: 1px solid #e0e0e0;">', unsafe_allow_html=True)
        for year in range(1, int(years) + 1):
            yearly_data = df[df['Year'] == year]
            with st.expander(f'📅 Tahun {year}', expanded=False):
                st.dataframe(yearly_data[['Month', 'Amount']].set_index(yearly_data.index + 1), use_container_width=True, hide_index=True)

def main():
    st.set_page_config(page_title="Saham IDX", layout="wide")
    st.toast('📢 Beberapa fitur tidak di publish, terima kasih!')
    apply_global_css()
    st.latex("Yuukinaesa ~|~ Arfan")

    initialize_session_state("scraper_history", [])
    initialize_session_state("calculator_history", [])

    try:
        history = load_history()
        if isinstance(history, dict):
            st.session_state.scraper_history = history.get("scraper", [])
            st.session_state.calculator_history = history.get("calculator", [])
        else:
            st.session_state.scraper_history = []
            st.session_state.calculator_history = []
    except:
        st.session_state.scraper_history = []
        st.session_state.calculator_history = []

    menu_selection = option_menu(
        "Menu Utama",
        ["Scraper Saham", "Calculator", "Compound Interest", "History"],
        icons=["graph-up", "calculator", "bookmark", "clock-history"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
    )

    if menu_selection == "Scraper Saham":
        stock_scraper_page()

    elif menu_selection == "Calculator":
        calculator_submenu = option_menu(
            "Calculator",
            ["IPOT", "Stockbit", "BNI Bions", "Custom"],
            icons=["calculator", "calculator", "calculator", "calculator"],
            menu_icon="calculator",
            default_index=0,
            orientation="horizontal",
        )
        
        platforms = {
            "IPOT": (0.0019, 0.0029),
            "Stockbit": (0.0015, 0.0025),
            "BNI Bions": (0.0017, 0.0027),
            "Custom": (0, 0)
        }
        calculator_page(calculator_submenu, *platforms[calculator_submenu])


    elif menu_selection == "Compound Interest":
        compound_interest_page()

    elif menu_selection == "History":
        st.title("History")

        st.subheader("Scraper Saham History")
        if st.session_state.scraper_history:
            for idx, history_entry in enumerate(st.session_state.scraper_history):
                with st.expander(f"Scraper History #{idx + 1}"):
                    df = pd.DataFrame(history_entry)
                    st.dataframe(format_dataframe(df, {
                        'Current Price': 'Rp{:,.0f}',
                        'Price/Book (PBVR)': '{:.2f}',
                        'Trailing P/E (PER)': '{:.2f}',
                        'Total Debt/Equity (mrq) (DER)': '{:.2f}',
                        'Return on Equity (%) (ROE)': '{:.0f}%',
                        'Diluted EPS (ttm) (EPS)': '{:.0f}',
                        'Forward Annual Dividend Rate (DPS)': 'Rp{:,.0f}',
                        'Forward Annual Dividend Yield (%)': '{:.2f}%'
                    }))
        else:
            st.write("No scraper history available")

        st.subheader("Calculator History")
        if st.session_state.calculator_history:
            df = pd.DataFrame(st.session_state.calculator_history)
            st.dataframe(format_dataframe(df, {
                'harga_beli': 'Rp{:,.0f}',
                'harga_jual': 'Rp{:,.0f}',
                'profit_loss': 'Rp{:,.0f}',
                'profit_loss_percentage': '{:.2f}%',
                'dividend_yield': '{:.2f}%'
            }))
        else:
            st.write("No calculator history available")

        if st.button("Clear All History"):
            st.session_state.scraper_history = []
            st.session_state.calculator_history = []
            save_history({"scraper": [], "calculator": []})
            st.success("All history cleared successfully!")
            st.rerun()

if __name__ == "__main__":
    main()
