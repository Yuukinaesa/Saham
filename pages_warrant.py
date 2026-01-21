import pandas as pd
import streamlit as st

from config import PLATFORM_CONFIG
from utils import format_rupiah, format_percent, format_csv_indonesia


def warrant_calculator_page() -> None:
    st.info("📱 **Kalkulator Warrant menggunakan platform Stockbit**")
    fee_beli, fee_jual = PLATFORM_CONFIG.get("Stockbit", (0.0015, 0.0025))
    
    mode = st.radio("Pilih Mode Kalkulator", ["Single Warrant", "Multiple Warrant"], horizontal=True)

    if mode == "Single Warrant":
        single_warrant_calculator(fee_beli, fee_jual)
    else:
        multiple_warrant_calculator(fee_beli, fee_jual)


def single_warrant_calculator(fee_beli: float, fee_jual: float) -> None:
    col1, _ = st.columns(2, gap="small")
    with col1:
        st.markdown('<div class="section-title">💰 Input Transaksi</div>', unsafe_allow_html=True)
        harga_beli_warrant = st.number_input('Harga Beli Warrant', min_value=0, step=1, format="%d", value=1)
        harga_jual_warrant = st.number_input('Harga Jual Warrant', min_value=0, step=1, format="%d", value=47)
        jumlah_lot = st.number_input('Jumlah Lot', step=0.5, format="%.1f", value=3.0)

    # Tombol lebih pendek, tidak full width
    if st.button('Hitung', type='primary'):
        with st.spinner('Menghitung...'):
            harga_beli_warrant = max(0.0, float(harga_beli_warrant))
            harga_jual_warrant = max(0.0, float(harga_jual_warrant))
            jumlah_lot = max(0.5, abs(jumlah_lot))
            jumlah_saham = jumlah_lot * 100
            
            total_beli = harga_beli_warrant * jumlah_saham
            total_jual = harga_jual_warrant * jumlah_saham
            total_fee_beli = total_beli * fee_beli
            total_fee_jual = total_jual * fee_jual
            net_amount = total_jual - total_fee_jual
            total_modal = total_beli + total_fee_beli
            keuntungan = net_amount - total_modal
            persentase_keuntungan = (keuntungan / total_modal * 100) if total_modal > 0 else 0
            
            # Rounding for display
            total_beli = round(total_beli, 2)
            total_jual = round(total_jual, 2)
            total_fee_beli = round(total_fee_beli, 2)
            total_fee_jual = round(total_fee_jual, 2)
            total_modal = round(total_modal, 2)
            net_amount = round(net_amount, 2)
            keuntungan = round(keuntungan, 2)
            persentase_keuntungan = round(persentase_keuntungan, 2)
                
            is_profit = keuntungan > 0
            # Use semi-transparent backgrounds for badges to work in both light/dark
            bg_badge = "rgba(16, 185, 129, 0.2)" if is_profit else "rgba(239, 68, 68, 0.2)"
            # Use brighter colors for text to ensure visibility in dark mode
            text_color = "#10b981" if is_profit else "#ef4444"
            border_color = "#10b981" if is_profit else "#ef4444"
            
            st.markdown(
                    f"""
<div class='premium-card' style='border-top: 5px solid {border_color}; border-left: 1px solid rgba(128, 128, 128, 0.1);'>
<h4 style='color: var(--text-color); margin: 0 0 16px 0; font-size: 1.15rem; font-weight: 700; text-align: center;'>📊 Hasil Warrant (Stockbit)</h4>
<div style='text-align: center; margin-bottom: 24px;'>
<p style='color: {text_color}; margin: 0; font-weight: 600; font-size: 0.9rem;'>Realized Gain / Loss</p>
<h2 style='color: {text_color}; margin: 8px 0; font-size: 2.25rem; font-weight: 800;'>
{("+" if is_profit else "") + format_rupiah(keuntungan)}
</h2>
<span style='background-color: {bg_badge}; color: {text_color}; padding: 4px 12px; border-radius: 9999px; font-weight: 700; font-size: 0.9rem;'>
{format_percent(persentase_keuntungan, 2)}
</span>
</div>
<div style='display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; background-color: rgba(128, 128, 128, 0.1); padding: 16px; border-radius: 8px;'>
<div>
<p style='margin: 0; color: var(--text-color); opacity: 0.8; font-size: 0.8rem; font-weight: 500;'>Total Modal</p>
<p style='margin: 2px 0 0 0; color: var(--text-color); font-weight: 600;'>{format_rupiah(total_modal)}</p>
</div>
<div>
<p style='margin: 0; color: var(--text-color); opacity: 0.8; font-size: 0.8rem; font-weight: 500;'>Net Amount</p>
<p style='margin: 2px 0 0 0; color: var(--text-color); font-weight: 600;'>{format_rupiah(net_amount)}</p>
</div>
</div>
<div style='border-top: 1px solid rgba(128, 128, 128, 0.2); padding-top: 16px;'>
<p style='margin: 0 0 8px 0; color: var(--text-color); font-weight: 600; font-size: 0.9rem;'>Detail Transaksi</p>
<div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; font-size: 0.85rem;'>
<div>Price: <span style='color:var(--text-color); font-weight:500;'>{harga_jual_warrant}</span></div>
<div>Lot Done: <span style='color:var(--text-color); font-weight:500;'>{jumlah_lot}</span></div>
<div>Amount: <span style='color:var(--text-color); font-weight:500;'>{format_rupiah(total_jual)}</span></div>
<div>Total Fee: <span style='color:var(--text-color); font-weight:500;'>{format_rupiah(total_fee_jual)}</span></div>
</div>
</div>
</div>
""",
                    unsafe_allow_html=True,
                )
            
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
            st.download_button(label="📥 Download as CSV", data=csv, file_name="warrant_calculator.csv", mime="text/csv")


def multiple_warrant_calculator(fee_beli: float, fee_jual: float) -> None:
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

    # Tombol lebih pendek
    if st.button('Hitung', key='btn_multi_warrant', type='primary'):
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
            
            # Display DataFrame
            df_view = df_w_multi.copy()
            df_view['Harga Beli'] = df_view['Harga Beli'].apply(lambda x: format_rupiah(x))
            df_view['Harga Jual'] = df_view['Harga Jual'].apply(lambda x: format_rupiah(x))
            df_view['Total Modal'] = df_view['Total Modal'].apply(lambda x: format_rupiah(x))
            df_view['Net Amount'] = df_view['Net Amount'].apply(lambda x: format_rupiah(x))
            df_view['Keuntungan'] = df_view['Keuntungan'].apply(lambda x: format_rupiah(x))
            df_view['Persentase %'] = df_view['Persentase %'].apply(lambda x: format_percent(x, 2))
            
            st.dataframe(df_view, width='stretch', hide_index=True)
            
            # CSV Download
            df_download = df_w_multi.copy()
            for col in ['Harga Beli','Harga Jual','Total Modal','Net Amount','Keuntungan']:
                df_download[col] = df_download[col].apply(lambda x: format_csv_indonesia(x, 0))
            df_download['Persentase %'] = df_download['Persentase %'].apply(lambda x: format_csv_indonesia(x, 2))
            
            csv = df_download.to_csv(index=False, sep=';', encoding='utf-8-sig', quoting=1)
            st.download_button(label="📥 Download as CSV", data=csv, file_name="multiple_warrant_calculator.csv", mime="text/csv")
