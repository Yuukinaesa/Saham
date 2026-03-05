from typing import Dict, List, Tuple
import pandas as pd
import streamlit as st

from config import PLATFORM_CONFIG
from utils import format_csv_indonesia, format_percent, format_rupiah, get_tick_size, get_ara_arb_percentage, round_price_to_tick



def calculate_ara_arb_sequence(harga_dasar: float, is_acceleration: bool = False, max_steps: int = 10, arb_mode: str = "Simetris") -> Tuple[List[Dict], List[Dict]]:
    # Calculate ARA sequence
    ara_sequence = []
    harga_ara_sekarang = harga_dasar
    for i in range(max_steps):
        board_type = 'acceleration' if is_acceleration else 'regular'
        
        # Acceleration Board Logic for Low Prices
        if is_acceleration and harga_ara_sekarang <= 10:
             harga_ara_baru = harga_ara_sekarang + 1
        else:
            pct = get_ara_arb_percentage(harga_ara_sekarang, board_type)
            limit_price = harga_ara_sekarang * (1 + pct)
            tick = get_tick_size(limit_price)
            harga_ara_baru = round_price_to_tick(limit_price, tick, 'floor')
            
        if harga_ara_baru <= harga_ara_sekarang:
             harga_ara_baru = harga_ara_sekarang + get_tick_size(harga_ara_sekarang)

        perubahan = harga_ara_baru - harga_ara_sekarang
        persentase_perubahan = (perubahan / harga_ara_sekarang) * 100 if harga_ara_sekarang > 0 else 0
        persentase_kumulatif = ((harga_ara_baru - harga_dasar) / harga_dasar) * 100 if harga_dasar > 0 else 0
        
        ara_sequence.append({
            'step': i + 1,
            'harga': harga_ara_baru, 
            'perubahan': perubahan, 
            'persentase_perubahan': persentase_perubahan, 
            'persentase_kumulatif': persentase_kumulatif, 
            'tipe': 'ara'
        })
        harga_ara_sekarang = harga_ara_baru

    # Calculate ARB sequence
    arb_sequence = []
    harga_arb_sekarang = harga_dasar
    for i in range(max_steps):
        board_type = 'acceleration' if is_acceleration else 'regular'
        
        # Acceleration Board Logic for Low Prices
        if is_acceleration and harga_arb_sekarang <= 10:
             harga_arb_baru = max(1, harga_arb_sekarang - 1)
        else:
            if arb_mode == "Asimetris (15%)" and not is_acceleration:
                pct = 0.15
            else:
                pct = get_ara_arb_percentage(harga_arb_sekarang, board_type)
                
            limit_price = harga_arb_sekarang * (1 - pct)
            tick = get_tick_size(limit_price)
            harga_arb_baru = round_price_to_tick(limit_price, tick, 'ceil')
        
        if harga_arb_baru < 1:
            harga_arb_baru = 1

        if harga_arb_baru >= harga_arb_sekarang:
             pass

        perubahan = harga_arb_baru - harga_arb_sekarang
        persentase_perubahan = (perubahan / harga_arb_sekarang) * 100 if harga_arb_sekarang > 0 else 0
        persentase_kumulatif = ((harga_arb_baru - harga_dasar) / harga_dasar) * 100 if harga_dasar > 0 else 0
        
        arb_sequence.append({
            'step': i + 1,
            'harga': harga_arb_baru, 
            'perubahan': perubahan, 
            'persentase_perubahan': persentase_perubahan, 
            'persentase_kumulatif': persentase_kumulatif, 
            'tipe': 'arb'
        })
        harga_arb_sekarang = harga_arb_baru

    return ara_sequence, arb_sequence


def ara_arb_calculator_page() -> None:
    st.info('Kalkulator untuk menghitung harga ARA (Auto Reject Above) dan ARB (Auto Reject Below) berdasarkan jenis papan')
    
    col_input1, col_input2 = st.columns(2, gap="medium")
    
    with col_input1:
        st.markdown("""<div style='margin-bottom: 12px;'><h3 style='color: var(--text-color); margin-bottom: 12px;'>Kriteria Saham</h3></div>""", unsafe_allow_html=True)
        board_type = st.radio("Pilih Jenis Papan", ["Papan Utama/Pengembangan", "Papan Akselerasi"], index=0, horizontal=True)
        is_acceleration = board_type == "Papan Akselerasi"
        
        arb_mode = "Simetris"
        if not is_acceleration:
            st.markdown("<p style='font-size:14px; margin-bottom:4px; font-weight:500;'>Mode ARB</p>", unsafe_allow_html=True)
            arb_mode = st.radio("Mode ARB", ["Simetris (Sesuai ARA)", "Asimetris (15%)"], index=0, horizontal=True, label_visibility="collapsed")
            
    with col_input2:
        st.markdown("""<div style='margin-bottom: 12px;'><h3 style='color: var(--text-color); margin-bottom: 12px;'>Data Harga & Sekuritas</h3></div>""", unsafe_allow_html=True)
        harga_penutupan = st.number_input('💰 Harga Penutupan', step=100, format="%d", min_value=1, value=975)
        jumlah_lot = st.number_input('📦 Jumlah Lot (Opsional)', min_value=1, value=1, format="%d", help="Masukkan jumlah lot untuk estimasi nilai aset.")
        max_steps = st.number_input('📊 Jumlah Langkah', min_value=1, max_value=20, value=5, step=1)
        
        # Broker Selection
        broker = st.selectbox("Pilih Sekuritas (Fee)", list(PLATFORM_CONFIG.keys()), index=0)
        fee_beli_default, fee_jual_default = PLATFORM_CONFIG[broker]
        
        if broker == "Custom":
            c1, c2 = st.columns(2)
            with c1:
                fee_beli = st.number_input("Fee Beli (%)", min_value=0.0, value=0.15, step=0.01) / 100
            with c2:
                fee_jual = st.number_input("Fee Jual (%)", min_value=0.0, value=0.25, step=0.01) / 100
        else:
            fee_beli, fee_jual = fee_beli_default, fee_jual_default
            # Display info text about fee
            st.markdown(f"<p style='font-size:0.8rem; color:var(--text-color); opacity:0.7; margin-top:-10px; margin-bottom:10px;'>Fee: Beli {fee_beli*100:.2f}%, Jual {fee_jual*100:.2f}%</p>", unsafe_allow_html=True)

    st.markdown("---")
    
    if st.button('Hitung ARA ARB', type='primary', use_container_width=True):
        ara_list, arb_list = calculate_ara_arb_sequence(harga_penutupan, is_acceleration, max_steps, arb_mode)
        
        st.markdown("""
        <div style='margin-bottom: 20px; text-align: center;'>
            <h3 style='color: var(--text-color); margin-bottom: 5px; font-size: 1.25rem;'>📊 Proyeksi Harga & Aset</h3>
            <p style='opacity: 0.8; font-size: 0.95rem;'>Estimasi pergerakan harga dan nilai bersih aset (setelah fee).</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Calculate Base Net Value (Cost Basis if Buying, or Net Proceeds if Selling Now)
        # Usually user inputs 'Close Price' as their 'Buy Price' or current price.
        # Let's assume we want to see "If I sell at this sequence price, what do I get?"
        # Asset Value Raw = Price * Lot * 100
        # Net Sell Value = Asset Value Raw * (1 - Fee Jual)
        
        # Base Value (Gross)
        base_value_gross = harga_penutupan * jumlah_lot * 100
        base_value_net_sell = base_value_gross * (1 - fee_jual)
        
        st.markdown(f"""
        <div style='background-color: var(--secondary-background-color); padding: 12px; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2); text-align: center; margin-bottom: 24px; max-width: 400px; margin-left: auto; margin-right: auto;'>
            <div style='font-size: 0.9rem; opacity: 0.8;'>💰 Estimasi Net Jual (Saat Ini)</div>
            <div style='font-size: 1.5rem; font-weight: 700; color: #3b82f6;'>{format_rupiah(base_value_net_sell)}</div>
            <div style='font-size: 0.85rem; opacity: 0.7;'>Bruto: {format_rupiah(base_value_gross)}</div>
        </div>
        """, unsafe_allow_html=True)

        # Loop through steps
        for i in range(max_steps):
            col_l, col_r = st.columns(2, gap="medium")
            
            # --- ARA CARD (Left) ---
            with col_l:
                if i < len(ara_list):
                    item = ara_list[i]
                    gross_value = item['harga'] * jumlah_lot * 100
                    net_value = gross_value * (1 - fee_jual)
                    
                    st.markdown(f"""
                    <div style='
                        background-color: rgba(16, 185, 129, 0.05); 
                        border: 1px solid rgba(16, 185, 129, 0.2); 
                        border-left: 4px solid #10b981; 
                        border-radius: 8px; 
                        padding: 16px; 
                        margin-bottom: 12px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    '>
                        <div style='text-align: left;'>
                            <div style='font-size: 0.8rem; color: #10b981; font-weight: 600; text-transform: uppercase; margin-bottom: 4px;'>Naik (ARA #{item['step']})</div>
                            <div style='font-size: 1rem; color: #10b981; font-weight: 700;'>↑ {item['persentase_perubahan']:.2f}%</div>
                        </div>
                        <div style='text-align: right;'>
                            <div style='font-size: 1.4rem; font-weight: 800; color: #10b981;'>{item['harga']:,.0f}</div>
                            <div style='font-size: 0.9rem; opacity: 0.9; font-weight: 500; color: var(--text-color);'>{format_rupiah(net_value)}</div>
                            <div style='font-size: 0.75rem; color: #10b981; margin-top: 4px; font-weight: 600;'>Total Naik: {item['persentase_kumulatif']:.2f}%</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # --- ARB CARD (Right) ---
            with col_r:
                if i < len(arb_list):
                    item = arb_list[i]
                    gross_value = item['harga'] * jumlah_lot * 100
                    net_value = gross_value * (1 - fee_jual)
                    
                    st.markdown(f"""
                    <div style='
                        background-color: rgba(239, 68, 68, 0.05); 
                        border: 1px solid rgba(239, 68, 68, 0.2); 
                        border-left: 4px solid #ef4444; 
                        border-radius: 8px; 
                        padding: 16px; 
                        margin-bottom: 12px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    '>
                        <div style='text-align: left;'>
                            <div style='font-size: 0.8rem; color: #ef4444; font-weight: 600; text-transform: uppercase; margin-bottom: 4px;'>Turun (ARB #{item['step']})</div>
                            <div style='font-size: 1rem; color: #ef4444; font-weight: 700;'>↓ {abs(item['persentase_perubahan']):.2f}%</div>
                        </div>
                        <div style='text-align: right;'>
                            <div style='font-size: 1.4rem; font-weight: 800; color: #ef4444;'>{item['harga']:,.0f}</div>
                            <div style='font-size: 0.9rem; opacity: 0.9; font-weight: 500; color: var(--text-color);'>{format_rupiah(net_value)}</div>
                             <div style='font-size: 0.75rem; color: #ef4444; margin-top: 4px; font-weight: 600;'>Total Turun: {item['persentase_kumulatif']:.2f}%</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)



