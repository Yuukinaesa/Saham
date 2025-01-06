import streamlit as st
import yfinance as yf
import pandas as pd
from streamlit_option_menu import option_menu

# Konstanta
DEFAULT_SYMBOLS = 'BBCA,BBRI,GOTO,TLKM,WSKT,ASII'
FRACSI_HARGA_DATA = {
    "Harga Saham": ["< Rp 200", "Rp 200 - Rp 500", "Rp 500 - Rp 2.000", "Rp 2.000 - Rp 5.000", "Rp 5.000+"],
    "Fraksi Harga": ["Rp 1", "Rp 2", "Rp 5", "Rp 10", "Rp 25"]
}

def apply_global_css():
    """Menerapkan styling global ke aplikasi Streamlit."""
    css = """
    <style>
        div.stButton > button {
            background-color: #2B8CCE;
            color: white;
            width: 100%;
            height: 50px;
            font-size: 18px;
        }
        /* Styling untuk tabel fraksi harga */
        .fraksi-table {
            background-color: #f0f8ff;
            padding: 10px;
            border-radius: 5px;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def initialize_session_state(key, default_value):
    """Inisialisasi session state jika belum ada."""
    if key not in st.session_state:
        st.session_state[key] = default_value

def format_dataframe(df, format_dict):
    """Memformat dataframe sesuai dengan format yang ditentukan."""
    return df.style.format(format_dict)

def fetch_stock_data(symbols):
    """Mengambil data saham dari Yahoo Finance."""
    data = {}
    for symbol in symbols:
        stock = yf.Ticker(symbol)
        info = stock.info
        current_price = round(info.get('regularMarketPrice', info.get('regularMarketPreviousClose', 0)))
        forward_dividend_yield = round(info.get('dividendYield', 0) * 100, 2)
        data[symbol] = {
            'Symbol': symbol.replace('.JK', ''),
            'Current Price': current_price,
            'Price/Book (PBVR)': info.get('priceToBook', 0),
            'Trailing P/E (PER)': info.get('trailingPE', 0),
            'Total Debt/Equity (mrq) (DER)': info.get('debtToEquity', 0),
            'Return on Equity (%) (ROE)': round((info.get('returnOnEquity', 0) * 100)),
            'Diluted EPS (ttm) (EPS)': round(info.get('trailingEps', 0)),
            'Forward Annual Dividend Rate (DPS)': round(info.get('dividendRate', 0)),
            'Forward Annual Dividend Yield (%)': forward_dividend_yield,
        }
    return data

def calculate_profit_loss(jumlah_lot, harga_beli, harga_jual, fee_beli, fee_jual):
    """Menghitung profit atau loss dari transaksi saham."""
    total_beli = jumlah_lot * 100 * harga_beli * (1 + fee_beli)
    total_jual = jumlah_lot * 100 * harga_jual * (1 - fee_jual)
    profit_loss = total_jual - total_beli
    profit_loss_percentage = (profit_loss / total_beli) * 100 if total_beli != 0 else 0
    return total_beli, total_jual, profit_loss, profit_loss_percentage

def calculate_dividend(jumlah_lot, dividen_per_saham):
    """Menghitung total dividen yang diterima."""
    return jumlah_lot * dividen_per_saham * 100 if dividen_per_saham != 0 else 0

def calculate_dividend_yield(dividen_per_saham, harga_beli):
    """Menghitung dividend yield."""
    return (dividen_per_saham / harga_beli) * 100 if harga_beli != 0 else 0

def stock_scraper_page():
    """Halaman untuk scraper saham."""
    st.info('Catatan: Data berasal dari Yahoo Finance. Pembelian disesuaikan dengan modal untuk jumlah lot yang sesuai.')
    symbols = st.text_area('Masukkan simbol saham (pisahkan dengan koma)', DEFAULT_SYMBOLS)
    symbols_list = [
        symbol.strip().upper() + '.JK' if '.JK' not in symbol.strip().upper() else symbol.strip().upper()
        for symbol in symbols.split(',')
    ]
    modal_rupiah = st.number_input("Masukkan modal dalam Rupiah", step=1000000, format="%d")

    if st.button('Ambil Data'):
        try:
            stocks_data = fetch_stock_data(symbols_list)
            df = pd.DataFrame(stocks_data).T

            # Menghitung jumlah saham dan lot
            df['Jumlah Saham'] = modal_rupiah / df['Current Price'].replace(0, pd.NA)
            df['Jumlah Saham'] = pd.to_numeric(df['Jumlah Saham'], errors='coerce')
            df['Jumlah Lot'] = (df['Jumlah Saham'] // 100).fillna(0).astype('Int64')
            df['Jumlah Saham'] = df['Jumlah Lot'] * 100

            # Menghitung dividen dan modal
            df['Dividen'] = df['Jumlah Saham'] * df['Forward Annual Dividend Rate (DPS)']
            df['Modal'] = df['Jumlah Lot'] * 100 * df['Current Price']

            # Memformat dataframe
            format_dict = {
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
            }

            st.subheader('Data Statistik Terbaru')
            with st.expander("Tampilkan Data Statistik"):
                st.dataframe(format_dataframe(df.reset_index(drop=True), format_dict))

        except Exception as e:
            st.error(f"Terjadi kesalahan: {str(e)}")

def display_fraksi_harga_table():
    """Menampilkan tabel fraksi harga dengan styling."""
    df_fraksi = pd.DataFrame(FRACSI_HARGA_DATA)
    df_fraksi.index += 1

    styled_df = df_fraksi.style.set_properties(**{
        'background-color': '#f0f8ff',
        'color': '#000000',
        'border': '1px solid black',
        'font-weight': 'bold',
        'text-align': 'center'
    }).set_table_styles([
        {'selector': 'th', 'props': [('background-color', '#2B8CCE'), ('color', 'white'), ('font-size', '16px')]},
        {'selector': 'td', 'props': [('font-size', '14px')]}
    ])

    html = styled_df.to_html(index=True)
    st.markdown(html, unsafe_allow_html=True)

def calculator_page(title, fee_beli, fee_jual):
    """Halaman kalkulator profit/loss saham."""
    st.header(title)
    st.markdown("<hr>", unsafe_allow_html=True)

    with st.expander("📄 **Tabel Fraksi Harga**"):
        display_fraksi_harga_table()

    # Jika memilih Custom, memungkinkan pengguna untuk memasukkan fee kustom
    if title == "Custom":
        st.subheader("Masukkan Fee Kustom")
        fee_beli = st.number_input("Fee Beli (persentase):", min_value=0.0, step=0.1, format="%.2f") / 100
        fee_jual = st.number_input("Fee Jual (persentase):", min_value=0.0, step=0.1, format="%.2f") / 100

    # Input pengguna
    jumlah_lot = st.number_input("Jumlah Lot:", min_value=0, step=1, format="%d")
    harga_beli = st.number_input("Harga Beli (per saham):", min_value=0.0, step=1000.0, format="%0.0f")
    harga_jual = st.number_input("Harga Jual (per saham):", min_value=0.0, step=1000.0, format="%0.0f")
    include_fee_beli = st.checkbox("Masukkan Fee Beli", value=True)
    include_fee_jual = st.checkbox("Masukkan Fee Jual", value=True)
    include_dividend = st.checkbox("Masukkan Dividen")

    # Penyesuaian fee berdasarkan checkbox
    fee_beli_final = fee_beli if include_fee_beli else 0
    fee_jual_final = fee_jual if include_fee_jual else 0

    # Inisialisasi variabel hasil
    profit_loss = 0
    profit_loss_percentage = 0
    total_dividen = 0
    dividend_yield = 0
    hasil = "Tidak ada perubahan"

    # Penghitungan dividen
    if include_dividend:
        dividen_per_saham = st.number_input("Dividen per Saham:", min_value=0, step=1, format="%d")
        if jumlah_lot > 0 and harga_beli > 0:
            total_dividen = calculate_dividend(jumlah_lot, dividen_per_saham)
            dividend_yield = calculate_dividend_yield(dividen_per_saham, harga_beli)
            st.write(f"Total Dividen: Rp {total_dividen:,.0f}")
            st.write(f"Dividend Yield: {dividend_yield:.2f}%")
            st.markdown('<hr style="border: 1px solid #e0e0e0;">', unsafe_allow_html=True)

    # Penghitungan profit/loss
    if st.button("Hitung", key="calculate"):
        total_beli, total_jual, profit_loss, profit_loss_percentage = calculate_profit_loss(
            jumlah_lot, harga_beli, harga_jual, fee_beli_final, fee_jual_final
        )
        if profit_loss > 0:
            hasil = "Profit"
        elif profit_loss < 0:
            hasil = "Loss"

        st.write(f"Total Beli: Rp {total_beli:,.0f}")
        st.write(f"Total Jual: Rp {total_jual:,.0f}")
        st.write(f"Profit/Loss: Rp {profit_loss:,.0f}")
        st.write(f"Profit/Loss Percentage: {profit_loss_percentage:.2f}%")

        # Menampilkan hasil berdasarkan profit/loss
        if hasil == "Profit":
            st.success("Profit!")
        elif hasil == "Loss":
            st.error("Loss!")
        else:
            st.info("Break Even!")

def calculate_compound_interest(firstm, rate, years, additional_investment=0, metode='EOP'):
    """Menghitung bunga berbunga."""
    data = []
    total_months = int(years * 12)
    amount = firstm
    for month in range(1, total_months + 1):
        if metode == "Beginning-of-Period (BOP)":
            amount += additional_investment  
            amount *= (1 + rate / 100 / 12)  
        else:
            amount *= (1 + rate / 100 / 12)  
            amount += additional_investment  
        year = (month - 1) // 12 + 1
        data.append({
            'Year': year,
            'Month': month,
            'Amount': round(amount, 2)
        })
    return pd.DataFrame(data)

def display_metode_penjelasan(metode):
    """Menampilkan penjelasan metode perhitungan bunga berbunga."""
    if metode == "Beginning-of-Period (BOP)":
        st.markdown("""
        **Beginning-of-Period (BOP)** berarti investasi tambahan ditambahkan **sebelum** bunga diterapkan setiap bulan. Dengan metode ini, investasi bulanan baru langsung mulai menghasilkan bunga sejak bulan tersebut.
        
        **Keuntungan:**
        - Potensi pertumbuhan yang lebih cepat karena investasi tambahan mulai menghasilkan bunga segera.
        
        **Kekurangan:**
        - Memerlukan perencanaan yang lebih cermat terkait waktu penambahan investasi.
        """)
    else:
        st.markdown("""
        **End-of-Period (EOP)** berarti bunga diterapkan **sebelum** investasi tambahan ditambahkan setiap bulan. Dengan metode ini, investasi bulanan baru tidak menghasilkan bunga pada bulan tersebut.
        
        **Keuntungan:**
        - Perhitungan yang lebih sederhana dan umum digunakan dalam banyak perhitungan finansial.
        
        **Kekurangan:**
        - Potensi pertumbuhan yang sedikit lebih lambat dibandingkan dengan metode BOP karena investasi tambahan tidak langsung menghasilkan bunga.
        """)

def compound_interest_page():
    """Halaman untuk menghitung bunga berbunga."""
    st.info('Bunga-berbunga atau compound interest adalah jenis bunga yang dihitung tidak hanya dari jumlah pokok awal, tetapi juga dari bunga yang sudah diperoleh.')

    # Pilihan metode perhitungan
    metode = st.radio(
        "Pilih Metode Perhitungan Bunga Berbunga:",
        ("End-of-Period (EOP)", "Beginning-of-Period (BOP)"),
        horizontal=True
    )

    # Menampilkan penjelasan metode
    with st.expander("📚 **Penjelasan Metode**"):
        display_metode_penjelasan(metode)

    # Input pengguna
    firstm = st.number_input('💰 Masukkan nilai awal investasi', step=1000000, format="%d", min_value=0)
    rate = st.number_input('📈 Masukkan tingkat bunga per tahun (%)', step=0.1, format="%.2f", min_value=0.0)
    years = st.number_input('🗓️ Masukkan jumlah tahun (misal: 5.5 untuk 5 tahun 5 bulan)', step=0.1, format="%.1f", min_value=0.0)
    additional_investment = st.number_input('➕ Masukkan tambahan investasi per bulan', step=1000000, format="%d", min_value=0)

    # Penghitungan bunga berbunga
    if st.button('Hitung'):
        df = calculate_compound_interest(firstm, rate, years, additional_investment, metode=metode)
        with st.expander('📊 Hasil perhitungan bunga berbunga:', expanded=True):
            st.dataframe(df.set_index(df.index + 1), use_container_width=True, hide_index=True)

        st.markdown('<hr style="border: 1px solid #e0e0e0;">', unsafe_allow_html=True)
        for year_num in range(1, int(years) + 1):
            yearly_data = df[df['Year'] == year_num]
            with st.expander(f'📅 Tahun {year_num}', expanded=False):
                st.dataframe(yearly_data[['Month', 'Amount']].set_index(yearly_data.index + 1), use_container_width=True, hide_index=True)

def main():
    """Fungsi utama untuk menjalankan aplikasi Streamlit."""
    st.set_page_config(page_title="Saham IDX", layout="wide")
    apply_global_css()
    st.latex(r"Yuukinaesa ~|~ Arfan")

    # Menu utama
    menu_selection = option_menu(
        "Menu Utama",
        ["Scraper Saham", "Calculator", "Compound Interest"],
        icons=["graph-up", "calculator", "bookmark"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
    )

    if menu_selection == "Scraper Saham":
        stock_scraper_page()

    elif menu_selection == "Calculator":
        # Submenu untuk Calculator
        calculator_submenu = option_menu(
            "Calculator",
            ["IPOT", "Stockbit", "BNI Bions", "Custom"],
            icons=["calculator", "calculator", "calculator", "calculator"],
            menu_icon="calculator",
            default_index=0,
            orientation="horizontal",
        )
        
        # Mapping platform ke fee beli dan fee jual
        platforms = {
            "IPOT": (0.0019, 0.0029),
            "Stockbit": (0.0015, 0.0025),
            "BNI Bions": (0.0017, 0.0027),
            "Custom": (0, 0)
        }
        fee_beli, fee_jual = platforms.get(calculator_submenu, (0, 0))
        calculator_page(calculator_submenu, fee_beli, fee_jual)

    elif menu_selection == "Compound Interest":
        compound_interest_page()

if __name__ == "__main__":
    main()
