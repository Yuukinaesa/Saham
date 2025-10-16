import pandas as pd
import streamlit as st

from config import PLATFORM_CONFIG
from utils import format_rupiah, format_percent, format_csv_indonesia


def warrant_calculator_page() -> None:
    st.info("📱 **Kalkulator Warrant menggunakan platform Stockbit**")
    fee_beli, fee_jual = PLATFORM_CONFIG.get("Stockbit", (0.0015, 0.0025))
    col1, _ = st.columns(2, gap="small")
    with col1:
        st.markdown('<div class="section-title">💰 Input Transaksi</div>', unsafe_allow_html=True)
        harga_beli_warrant = st.number_input('Harga Beli Warrant', min_value=0, step=1, format="%d", value=1)
        harga_jual_warrant = st.number_input('Harga Jual Warrant', min_value=0, step=1, format="%d", value=47)
        jumlah_lot = st.number_input('Jumlah Lot', step=0.5, format="%.1f", value=3.0)
    if st.button('Hitung Realized Gain', type='primary', use_container_width=True):
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
            total_beli = round(total_beli, 2)
            total_jual = round(total_jual, 2)
            total_fee_beli = round(total_fee_beli, 2)
            total_fee_jual = round(total_fee_jual, 2)
            total_modal = round(total_modal, 2)
            net_amount = round(net_amount, 2)
            keuntungan = round(keuntungan, 2)
            persentase_keuntungan = round(persentase_keuntungan, 2)
            st.markdown("""
            <div style='margin-bottom: 16px;'>
                <h3 style='color: #1a1a1a; margin-bottom: 5px; font-size: 16px;'>📊 Hasil Perhitungan Warrant (Stockbit)</h3>
            </div>
            """, unsafe_allow_html=True)
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
            st.markdown(f"""
            <div style='margin-bottom: 8px; background-color: #f8f9fa; padding: 12px 8px 12px 16px; border-radius: 6px; border-left: 3px solid #2563eb;'>
                <h4 style='color: #1a1a1a; margin: 0; font-size: 16px;'>💰 Modal Awal: {format_rupiah(total_modal)}</h4>
                <p style='margin: 4px 0 0 0; color: #6b7280; font-size: 14px;'>Harga Beli: {format_rupiah(harga_beli_warrant)} × {jumlah_lot} lot</p>
                <p style='margin: 4px 0 0 0; color: #6b7280; font-size: 14px;'>Fee Beli: {format_rupiah(total_fee_beli)} ({fee_beli*100:.2f}%)</p>
            </div>
            """, unsafe_allow_html=True)
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
            df_view = df_w_multi.copy()
            df_view['Harga Beli'] = df_view['Harga Beli'].apply(lambda x: format_rupiah(x))
            df_view['Harga Jual'] = df_view['Harga Jual'].apply(lambda x: format_rupiah(x))
            df_view['Total Modal'] = df_view['Total Modal'].apply(lambda x: format_rupiah(x))
            df_view['Net Amount'] = df_view['Net Amount'].apply(lambda x: format_rupiah(x))
            df_view['Keuntungan'] = df_view['Keuntungan'].apply(lambda x: format_rupiah(x))
            df_view['Persentase %'] = df_view['Persentase %'].apply(lambda x: format_percent(x, 2))
            st.dataframe(df_view, use_container_width=True, hide_index=True)
            df_download = df_w_multi.copy()
            for col in ['Harga Beli','Harga Jual','Total Modal','Net Amount','Keuntungan']:
                df_download[col] = df_download[col].apply(lambda x: format_csv_indonesia(x, 0))
            df_download['Persentase %'] = df_download['Persentase %'].apply(lambda x: format_csv_indonesia(x, 2))
            csv_multi = df_download.to_csv(index=False, sep=';', encoding='utf-8-sig', quoting=1)
            st.download_button(label='📥 Download Multiple Warrant CSV', data=csv_multi, file_name='multiple_warrant.csv', mime='text/csv')


