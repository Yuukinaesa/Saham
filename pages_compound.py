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
            <h3 style='color: var(--text-color); margin-bottom: 12px;'>Input Investasi</h3>
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
                df_display = df.copy()
                df_display['Amount'] = df_display['Amount'].apply(lambda x: format_rupiah(x))
                st.markdown("""
                <div style='margin-bottom: 16px;'>
                    <h3 style='color: var(--text-color); margin-bottom: 5px; font-size: 16px;'>📊 Hasil perhitungan bunga berbunga</h3>
                </div>
                """, unsafe_allow_html=True)
                total_investment = firstm + (additional_investment * int(years * 12))
                final_amount = df_display['Amount'].iloc[-1]
                st.markdown(f"""
<div class='premium-card' style='border-top: 5px solid #2563eb;'>
<h4 style='color: var(--text-color); margin: 0 0 20px 0; font-size: 1.25rem; font-weight: 700; text-align: center;'>📊 Proyeksi Kekayaan</h4>
<div style='text-align: center; margin-bottom: 24px;'>
<p style='color: var(--text-color); opacity: 0.8; margin: 0; font-weight: 500; font-size: 0.9rem;'>Nilai Akhir Portfolio</p>
<h2 style='color: #3b82f6; margin: 8px 0; font-size: 2.25rem; font-weight: 800;'>
{final_amount}
</h2>
<span style='background-color: rgba(37, 99, 235, 0.2); color: #3b82f6; padding: 4px 12px; border-radius: 9999px; font-weight: 600; font-size: 0.85rem;'>
{years} Tahun
</span>
</div>
<div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; text-align: center; background-color: rgba(128, 128, 128, 0.1); padding: 16px; border-radius: 8px;'>
<div>
<div style='font-size: 0.8rem; color: var(--text-color); opacity: 0.8; margin-bottom: 4px;'>Modal Awal</div>
<div style='font-weight: 600; color: var(--text-color);'>{format_rupiah(firstm)}</div>
</div>
<div>
<div style='font-size: 0.8rem; color: var(--text-color); opacity: 0.8; margin-bottom: 4px;'>Investasi Bulanan</div>
<div style='font-weight: 600; color: var(--text-color);'>{format_rupiah(additional_investment)}</div>
</div>
<div>
<div style='font-size: 0.8rem; color: var(--text-color); opacity: 0.8; margin-bottom: 4px;'>Total Setor</div>
<div style='font-weight: 600; color: var(--text-color);'>{format_rupiah(total_investment)}</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)
                with st.expander('Tampilkan Data', expanded=True):
                    st.dataframe(df_display.set_index(df_display.index + 1), width='stretch', height=400)
                    df_download = df.copy()
                    df_download['Amount'] = df_download['Amount'].apply(lambda x: format_csv_indonesia(x, 0) if pd.notna(x) else "0")
                    csv = df_download.to_csv(index=False, sep=';', encoding='utf-8-sig', quoting=1)
                    st.download_button(label="📥 Download as CSV", data=csv, file_name="compound_interest.csv", mime="text/csv")
                for year_num in range(1, int(years) + 1):
                    yearly_data = df_display[df_display['Year'] == year_num]
                    with st.expander(f'📅 Tahun {year_num}', expanded=False):
                        st.dataframe(yearly_data[['Month', 'Amount']].set_index(yearly_data.index + 1), width='stretch')
            except Exception:
                st.error("Silakan masukkan nilai investasi awal dan tingkat bunga untuk menghitung compound interest")


