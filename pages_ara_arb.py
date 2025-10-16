from typing import Dict, List
import pandas as pd
import streamlit as st

from utils import format_csv_indonesia, format_percent, format_rupiah


def get_fraksi_harga(harga: float) -> float:
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


def calculate_ara_arb_sequence(harga_dasar: float, is_acceleration: bool = False, max_steps: int = 10) -> List[Dict]:
    sequence = []
    sequence.append({'harga': harga_dasar, 'perubahan': 0, 'persentase_perubahan': 0.0, 'persentase_kumulatif': 0.0, 'tipe': 'dasar'})
    harga_ara_sekarang = harga_dasar
    for _ in range(max_steps):
        if is_acceleration:
            if 1 <= harga_ara_sekarang <= 10:
                harga_ara_baru = harga_ara_sekarang + 1
            else:
                harga_ara_baru = harga_ara_sekarang * 1.10
        else:
            if harga_ara_sekarang >= 5000:
                persentase = 20.0
            elif 2000 <= harga_ara_sekarang < 5000:
                persentase = 25.0
            elif 1000 <= harga_ara_sekarang < 2000:
                persentase = 25.0
            elif 500 <= harga_ara_sekarang < 1000:
                persentase = 25.0
            elif 200 <= harga_ara_sekarang < 500:
                persentase = 25.0
            elif 100 <= harga_ara_sekarang < 200:
                persentase = 35.0
            elif 50 <= harga_ara_sekarang < 100:
                persentase = 35.0
            else:
                break
            harga_ara_baru = harga_ara_sekarang * (1 + persentase / 100)
        fraksi = get_fraksi_harga(harga_ara_baru)
        harga_ara_baru = int(harga_ara_baru / fraksi) * fraksi
        perubahan = harga_ara_baru - harga_ara_sekarang
        persentase_perubahan = (perubahan / harga_ara_sekarang) * 100 if harga_ara_sekarang > 0 else 0
        persentase_kumulatif = ((harga_ara_baru - harga_dasar) / harga_dasar) * 100 if harga_dasar > 0 else 0
        sequence.append({'harga': harga_ara_baru, 'perubahan': perubahan, 'persentase_perubahan': persentase_perubahan, 'persentase_kumulatif': persentase_kumulatif, 'tipe': 'ara'})
        harga_ara_sekarang = harga_ara_baru
    harga_arb_sekarang = harga_dasar
    for _ in range(max_steps):
        if is_acceleration:
            if 1 <= harga_arb_sekarang <= 10:
                harga_arb_baru = harga_arb_sekarang - 1
            else:
                harga_arb_baru = harga_arb_sekarang * 0.90
        else:
            if harga_arb_sekarang >= 5000:
                persentase = 20.0
            elif 2000 <= harga_arb_sekarang < 5000:
                persentase = 25.0
            elif 1000 <= harga_arb_sekarang < 2000:
                persentase = 25.0
            elif 500 <= harga_arb_sekarang < 1000:
                persentase = 25.0
            elif 200 <= harga_arb_sekarang < 500:
                persentase = 25.0
            elif 100 <= harga_arb_sekarang < 200:
                persentase = 35.0
            elif 50 <= harga_arb_sekarang < 100:
                persentase = 35.0
            else:
                break
            harga_arb_baru = harga_arb_sekarang * (1 - persentase / 100)
        harga_arb_baru = max(1, harga_arb_baru)
        fraksi = get_fraksi_harga(harga_arb_baru)
        harga_arb_baru = int(harga_arb_baru / fraksi) * fraksi
        perubahan = harga_arb_baru - harga_arb_sekarang
        persentase_perubahan = (perubahan / harga_arb_sekarang) * 100 if harga_arb_sekarang > 0 else 0
        persentase_kumulatif = ((harga_arb_baru - harga_dasar) / harga_dasar) * 100 if harga_dasar > 0 else 0
        sequence.append({'harga': harga_arb_baru, 'perubahan': perubahan, 'persentase_perubahan': persentase_perubahan, 'persentase_kumulatif': persentase_kumulatif, 'tipe': 'arb'})
        harga_arb_sekarang = harga_arb_baru
    sequence.sort(key=lambda x: x['harga'], reverse=True)
    return sequence


def ara_arb_calculator_page() -> None:
    st.info('Kalkulator untuk menghitung harga ARA (Auto Reject Above) dan ARB (Auto Reject Below) berdasarkan jenis papan')
    col1, _ = st.columns(2, gap="small")
    with col1:
        st.markdown("""
        <div style='margin-bottom: 16px;'>
            <h3 style='color: #1a1a1a; margin-bottom: 12px;'>Input Harga</h3>
        </div>
        """, unsafe_allow_html=True)
        board_type = st.radio("Pilih Jenis Papan", ["Papan Utama/Pengembangan", "Papan Akselerasi"], index=0, horizontal=True)
        is_acceleration = board_type == "Papan Akselerasi"
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
                sequence = calculate_ara_arb_sequence(harga_penutupan, is_acceleration, max_steps)
                display_data = []
                for item in sequence:
                    if item['tipe'] == 'ara':
                        warna = '#22c55e'
                        arrow = '↗️'
                    elif item['tipe'] == 'arb':
                        warna = '#ef4444'
                        arrow = '↘️'
                    else:
                        warna = '#6b7280'
                        arrow = ''
                    if item['perubahan'] > 0:
                        perubahan_str = f"+{item['perubahan']:,.0f}"
                    elif item['perubahan'] < 0:
                        perubahan_str = f"{item['perubahan']:,.0f}"
                    else:
                        perubahan_str = "0"
                    if item['persentase_perubahan'] > 0:
                        persentase_perubahan_str = f"(+{item['persentase_perubahan']:.2f}%)"
                    elif item['persentase_perubahan'] < 0:
                        persentase_perubahan_str = f"({item['persentase_perubahan']:.2f}%)"
                    else:
                        persentase_perubahan_str = "(0.00%)"
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
                st.markdown("""
                <div style='margin-bottom: 16px; background-color: #f8f9fa; padding: 16px; border-radius: 8px;'>
                    <h4 style='color: #1a1a1a; margin: 0 0 12px 0; font-size: 16px;'>📈 Urutan Harga ARA/ARB</h4>
                """, unsafe_allow_html=True)
                for data in display_data:
                    if '↗️' in data['Kumulatif']:
                        bg_color = '#dcfce7'
                        border_color = '#22c55e'
                    elif '↘️' in data['Kumulatif']:
                        bg_color = '#fef2f2'
                        border_color = '#ef4444'
                    else:
                        bg_color = '#f9fafb'
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
                df_ara_arb = pd.DataFrame(display_data)
                for col in df_ara_arb.columns:
                    if col in ['Harga', 'Perubahan']:
                        df_ara_arb[col] = df_ara_arb[col].apply(lambda x: format_csv_indonesia(x, 0) if pd.notna(x) else "0")
                    elif col in ['Persentase', 'Kumulatif']:
                        df_ara_arb[col] = df_ara_arb[col].apply(lambda x: format_csv_indonesia(x, 2) if pd.notna(x) else "0")
                csv = df_ara_arb.to_csv(index=False, sep=';', encoding='utf-8-sig', quoting=1)
                st.download_button(label="📥 Download as CSV", data=csv, file_name="ara_arb_calculator.csv", mime="text/csv")
            else:
                st.error(f"Harga saham harus minimal Rp {min_value}")


