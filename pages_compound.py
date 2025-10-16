import pandas as pd
import streamlit as st

from utils import format_rupiah, format_csv_indonesia


def calculate_compound_interest(firstm: float, rate: float, years: float, additional_investment: float = 0) -> pd.DataFrame:
    data = []
    total_months = int(years * 12)
    amount = firstm
    for month in range(1, total_months + 1):
        amount += additional_investment
        amount *= (1 + rate / 100 / 12)
        amount = round(amount, 2)
        year = (month - 1) // 12 + 1
        data.append({'Year': year, 'Month': month, 'Amount': amount})
    return pd.DataFrame(data)


def compound_interest_page() -> None:
    st.info('Bunga-berbunga atau compound interest adalah jenis bunga yang dihitung tidak hanya dari jumlah pokok awal, tetapi juga dari bunga yang sudah diperoleh.')

    col1, _ = st.columns(2, gap="small")
    with col1:
        st.markdown("""
        <div style='margin-bottom: 16px;'>
            <h3 style='color: #1a1a1a; margin-bottom: 12px;'>Input Investasi</h3>
        </div>
        """, unsafe_allow_html=True)
        firstm = st.number_input('💰 Masukkan nilai awal investasi', step=1000000, format="%d", value=1000000)
        rate = st.number_input('📈 Masukkan tingkat bunga per tahun (%)', step=0.1, format="%.2f", value=10.0)
        years = st.number_input('🗓️ Masukkan jumlah tahun (misal: 5.5 untuk 5 tahun 5 bulan)', step=0.1, format="%.1f", value=5.0)
        additional_investment = st.number_input('➕ Masukkan tambahan investasi per bulan', step=1000000, format="%d", value=1000000)

    if st.button('Hitung', key='calculate_compound'):
        with st.spinner('Menghitung bunga berbunga...'):
            try:
                if firstm == 0 and rate == 0:
                    st.error("Silakan masukkan nilai investasi awal dan tingkat bunga untuk menghitung compound interest")
                    return
                df = calculate_compound_interest(firstm, rate, years, additional_investment)
                df['Amount'] = df['Amount'].apply(lambda x: format_rupiah(x))
                st.markdown("""
                <div style='margin-bottom: 16px;'>
                    <h3 style='color: #1a1a1a; margin-bottom: 5px; font-size: 16px;'>📊 Hasil perhitungan bunga berbunga</h3>
                </div>
                """, unsafe_allow_html=True)
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
                    st.dataframe(df.set_index(df.index + 1), use_container_width=True, height=400)
                    df_download = df.copy()
                    df_download['Amount'] = df_download['Amount'].apply(lambda x: format_csv_indonesia(x, 0) if pd.notna(x) else "0")
                    csv = df_download.to_csv(index=False, sep=';', encoding='utf-8-sig', quoting=1)
                    st.download_button(label="📥 Download as CSV", data=csv, file_name="compound_interest.csv", mime="text/csv")
                for year_num in range(1, int(years) + 1):
                    yearly_data = df[df['Year'] == year_num]
                    with st.expander(f'📅 Tahun {year_num}', expanded=False):
                        st.dataframe(yearly_data[['Month', 'Amount']].set_index(yearly_data.index + 1), use_container_width=True)
            except Exception:
                st.error("Silakan masukkan nilai investasi awal dan tingkat bunga untuk menghitung compound interest")


