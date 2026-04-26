from typing import Dict, List, Tuple
import pandas as pd
import streamlit as st

from config import PLATFORM_CONFIG
from utils import format_csv_indonesia, format_percent, format_rupiah, get_tick_size, get_ara_arb_percentage, round_price_to_tick


def calculate_preset_ara_beruntun(harga_dasar: float, is_acceleration: bool = False) -> List[Dict]:
    events = [
        {"name": "Listing ARA 1", "type": "ara", "icon": "🔵", "bg": ""},
        {"name": "ARA 2", "type": "ara", "icon": "🔵", "bg": ""},
        {"name": "ARA 3 BAGGER", "type": "ara", "icon": "🟡", "bg": ""},
        {"name": "ARA 4", "type": "ara", "icon": "🟡", "bg": ""},
        {"name": "ARA 5 MULTIBAGGER", "type": "ara", "icon": "🟡", "bg": ""},
        {"name": "ARA 6 MASUK UMA TRIPLEBAGGER", "type": "ara", "icon": "⭐", "bg": "linear-gradient(90deg, #0f3c75 0%, #1a569c 100%)", "text_color": "white"},
        {"name": "SUSPEND 1X", "type": "suspend", "duration": "1 Hari", "icon": "⏸️", "bg": "#f0f2f5"},
        {"name": "ARA 7", "type": "ara", "icon": "🔵", "bg": ""},
        {"name": "ARA 8 SAVAGEBAGGER", "type": "ara", "icon": "🔵", "bg": ""},
        {"name": "ARA 9", "type": "ara", "icon": "🔵", "bg": "linear-gradient(90deg, #0f3c75 0%, #1a569c 100%)", "text_color": "white"},
        {"name": "SUSPEND 2X", "type": "suspend", "duration": "1 Hari", "icon": "⏸️", "bg": "#f0f2f5"},
        {"name": "SUSPEND 2X", "type": "suspend", "duration": "2 Hari", "icon": "⏸️", "bg": "#f0f2f5"},
        {"name": "ARA 10X FCA HARI 1", "type": "fca", "icon": "⭐", "bg": "#fdf7e3"},
        {"name": "ARA 11X FCA HARI 2", "type": "fca", "icon": "⭐", "bg": "#fdf7e3"},
        {"name": "ARA 12X FCA HARI 3", "type": "fca", "icon": "⭐", "bg": "#fdf7e3"},
        {"name": "ARA 13X FCA HARI 4", "type": "fca", "icon": "⭐", "bg": "#fdf7e3"},
        {"name": "ARA 14X FCA HARI 5", "type": "fca", "icon": "⭐", "bg": "#fdf7e3"},
        {"name": "ARA 15X FCA HARI 6", "type": "fca", "icon": "⭐", "bg": "#fdf7e3"},
        {"name": "ARA 16X FCA HARI 7", "type": "fca", "icon": "⭐", "bg": "#fdf7e3"},
        {"name": "Keluar FCA", "type": "ara", "icon": "⭐", "bg": "linear-gradient(90deg, #091e42 0%, #0f3c75 100%)", "text_color": "white"}
    ]
    
    sequence = []
    harga_sekarang = harga_dasar
    
    for event in events:
        if event["type"] == "suspend":
            sequence.append({
                'name': event["name"],
                'harga': event["duration"],
                'persentase_kumulatif': event["duration"],
                'tipe': 'suspend',
                'icon': event.get('icon', ''),
                'bg': event.get('bg', ''),
                'text_color': event.get('text_color', 'var(--text-color)')
            })
        else:
            board_type = 'acceleration' if is_acceleration else 'regular'
            
            if event["type"] == "fca":
                pct = 0.10 # FCA is always 10% auto reject limit, regardless of board
            else:
                if is_acceleration and harga_sekarang <= 10:
                    pct = 0 # Handled manually
                else:
                    pct = get_ara_arb_percentage(harga_sekarang, board_type)
                    
            if event["type"] != "fca" and is_acceleration and harga_sekarang <= 10:
                harga_baru = harga_sekarang + 1
            else:
                limit_price = harga_sekarang * (1 + pct)
                tick = get_tick_size(limit_price)
                harga_baru = round_price_to_tick(limit_price, tick, 'floor')
                
            if harga_baru <= harga_sekarang:
                harga_baru = harga_sekarang + get_tick_size(harga_sekarang)
                
            persentase_kumulatif = ((harga_baru - harga_dasar) / harga_dasar) * 100 if harga_dasar > 0 else 0
            
            sequence.append({
                'name': event["name"],
                'harga': harga_baru,
                'persentase_kumulatif': persentase_kumulatif,
                'tipe': event["type"],
                'icon': event.get('icon', ''),
                'bg': event.get('bg', ''),
                'text_color': event.get('text_color', 'var(--text-color)')
            })
            harga_sekarang = harga_baru
            
    return sequence
def calculate_ara_arb_sequence(harga_dasar: float, is_acceleration: bool = False, max_steps: int = 10) -> Tuple[List[Dict], List[Dict]]:
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
            # ARB for regular board: flat 15% (BEI regulation effective 8 April 2025)
            # ARB for acceleration board: 10% (same as ARA)
            if not is_acceleration:
                pct = 0.15
            else:
                pct = get_ara_arb_percentage(harga_arb_sekarang, board_type)
                
            limit_price = harga_arb_sekarang * (1 - pct)
            tick = get_tick_size(limit_price)
            harga_arb_baru = round_price_to_tick(limit_price, tick, 'ceil')
        
        if harga_arb_baru < 1:
            harga_arb_baru = 1

        if harga_arb_baru >= harga_arb_sekarang:
             break  # Price stalled — no further meaningful ARB steps

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
        
        if not is_acceleration:
            st.markdown("<p style='font-size:13px; margin-bottom:4px; color:var(--text-color); opacity:0.7;'>ARB: 15% (seragam, sesuai regulasi BEI efektif 8 April 2025)</p>", unsafe_allow_html=True)
            
        st.markdown("<p style='font-size:14px; margin-bottom:4px; margin-top:12px; font-weight:500;'>Mode Kalkulator</p>", unsafe_allow_html=True)
        calc_mode = st.radio("Mode Kalkulator", ["Manual (Berdasarkan Langkah)", "Preset Skenario (ARA Beruntun, FCA)"], index=0, horizontal=True, label_visibility="collapsed")
            
    with col_input2:
        st.markdown("""<div style='margin-bottom: 12px;'><h3 style='color: var(--text-color); margin-bottom: 12px;'>Data Harga & Sekuritas</h3></div>""", unsafe_allow_html=True)
        harga_penutupan = st.number_input('💰 Harga Penutupan / Harga Dasar', step=100, format="%d", min_value=1, value=400)
        harga_beli = st.number_input('🛒 Harga Beli / Modal (Opsional)', step=100, format="%d", min_value=0, value=200, help="Isi untuk melihat estimasi Net Profit / Loss.")
        jumlah_lot = st.number_input('📦 Jumlah Lot (Opsional)', min_value=1, value=1, format="%d", help="Masukkan jumlah lot untuk estimasi nilai aset.")
        
        if calc_mode == "Manual (Berdasarkan Langkah)":
            max_steps = st.number_input('📊 Jumlah Langkah', min_value=1, max_value=20, value=5, step=1)
        else:
            max_steps = 1 # Dummy value for preset mode
        
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

        c1, c2 = st.columns(2)
        with c1:
            include_fee_beli = st.checkbox("Masukkan Fee Beli", value=True)
        with c2:
            include_fee_jual = st.checkbox("Masukkan Fee Jual", value=True)

    st.markdown("---")
    
    if st.button('Hitung', type='primary', use_container_width=True):
        fee_beli_final = fee_beli if include_fee_beli else 0
        fee_jual_final = fee_jual if include_fee_jual else 0
        
        if calc_mode == "Preset Skenario (ARA Beruntun, FCA)":
            preset_sequence = calculate_preset_ara_beruntun(harga_penutupan, is_acceleration)
            # --- Compute initial (base) values for header ---
            base_gross = harga_penutupan * jumlah_lot * 100
            base_net = base_gross * (1 - fee_jual_final)
            
            # 1) Header card — uses indigo gradient visible in both light & dark mode
            st.markdown(f"""
<div style="max-width:640px; margin:0 auto 14px; background:linear-gradient(135deg,#4f46e5 0%,#7c3aed 50%,#a855f7 100%); border-radius:16px; padding:24px 20px; box-shadow:0 8px 32px rgba(79,70,229,0.25);">
<div style="display:flex; align-items:center; gap:10px; margin-bottom:18px;">
<div style="width:38px; height:38px; border-radius:10px; background:rgba(255,255,255,0.2); display:flex; align-items:center; justify-content:center; font-size:1.2rem;">🚀</div>
<div>
<div style="font-size:1.05rem; font-weight:700; color:white;">Simulasi ARA Beruntun</div>
<div style="font-size:0.75rem; color:rgba(255,255,255,0.6);">{'Papan Akselerasi' if is_acceleration else 'Papan Utama / Pengembangan'}</div>
</div>
</div>
<div style="display:grid; grid-template-columns:repeat(3,1fr); gap:8px;">
<div style="background:rgba(255,255,255,0.15); border-radius:10px; padding:10px 6px; text-align:center; backdrop-filter:blur(4px);">
<div style="font-size:0.6rem; color:rgba(255,255,255,0.6); text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">Lot</div>
<div style="font-size:1.05rem; font-weight:700; color:white;">{jumlah_lot:,}</div>
</div>
<div style="background:rgba(255,255,255,0.15); border-radius:10px; padding:10px 6px; text-align:center; backdrop-filter:blur(4px);">
<div style="font-size:0.6rem; color:rgba(255,255,255,0.6); text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">Harga</div>
<div style="font-size:1.05rem; font-weight:700; color:white;">{harga_penutupan:,}</div>
</div>
<div style="background:rgba(255,255,255,0.15); border-radius:10px; padding:10px 6px; text-align:center; backdrop-filter:blur(4px);">
<div style="font-size:0.6rem; color:rgba(255,255,255,0.6); text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">Net</div>
<div style="font-size:1.05rem; font-weight:700; color:white;">{format_rupiah(base_net)}</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)
            
            # 2) Build timeline rows
            rows_html = ""
            step_num = 0
            for idx, item in enumerate(preset_sequence):
                is_suspend = item['tipe'] == 'suspend'
                is_highlight = "UMA" in item.get('name','') or item.get('name','') == "ARA 9" or "Keluar" in item.get('name','')
                is_last = idx == len(preset_sequence) - 1
                
                if not is_suspend:
                    step_num += 1
                    hv = float(item['harga'])
                    h_str = f"{hv:,.0f}"
                    pv = item['persentase_kumulatif']
                    # Keep 2 decimal places, remove trailing zeros if they are .00
                    p_str_val = f"+{pv:.2f}"
                    if p_str_val.endswith(".00"):
                        p_str_val = p_str_val[:-3]
                    elif p_str_val.endswith("0"):
                        p_str_val = p_str_val[:-1]
                    p_str = f"{p_str_val}%"
                else:
                    h_str = item['harga']
                    p_str = ""
                    pv = 0
                
                # Accent bar + row colors
                if is_suspend:
                    accent = "#f59e0b"; row_bg = "#fffdf5"; nm_col = "#92400e"; h_col = "#92400e"; p_col = "#b45309"
                elif is_highlight:
                    accent = "#7c3aed"; row_bg = "linear-gradient(135deg,#4f46e5,#6d28d9)"; nm_col = "#ffffff"; h_col = "white"; p_col = "#ffffff"
                elif item['tipe'] == 'fca':
                    accent = "#f59e0b"; row_bg = "#fefce8"; nm_col = "#78350f"; h_col = "#1e293b"; p_col = "#059669"
                elif pv >= 100:
                    accent = "#10b981"; row_bg = "white"; nm_col = "#1e293b"; h_col = "#1e293b"; p_col = "#059669"
                else:
                    accent = "#6366f1"; row_bg = "white"; nm_col = "#1e293b"; h_col = "#1e293b"; p_col = "#10b981"
                
                # Sub info: Harga, Net, P/L, % (Using Chips for Clarity)
                sub_html = ""
                if not is_suspend:
                    gv = hv * jumlah_lot * 100
                    fee_jual_val = gv * fee_jual_final
                    nv = gv - fee_jual_val
                    pl_part = ""
                    fee_part = ""
                    if harga_beli > 0:
                        gross_beli = harga_beli * jumlah_lot * 100
                        fee_beli_val = gross_beli * fee_beli_final
                        tb = gross_beli + fee_beli_val
                        pl = nv - tb
                        plp = (pl / tb * 100) if tb > 0 else 0
                        
                        # Chip styling for P/L
                        if is_highlight:
                            pc_bg = "#ffffff"
                            pc_text = "#059669" if pl >= 0 else "#dc2626"
                        else:
                            pc_bg = "rgba(16,185,129,0.12)" if pl >= 0 else "rgba(239,68,68,0.12)"
                            pc_text = "#059669" if pl >= 0 else "#dc2626"
                            
                        pl_part = f"<div style='background:{pc_bg}; color:{pc_text}; padding:4px 10px; border-radius:6px; font-weight:700;'>P/L {format_rupiah(pl)}</div>"
                        
                        # Fee breakdown chips
                        total_fee = fee_beli_val + fee_jual_val
                        if total_fee > 0:
                            fb_bg = "rgba(255,255,255,0.1)" if is_highlight else "#fef3c7"
                            fb_text = "rgba(255,255,255,0.85)" if is_highlight else "#92400e"
                            fee_part = f"""<div style='display:flex; align-items:center; gap:6px; margin-top:4px; font-size:0.75rem; flex-wrap:wrap;'>
<div style='background:{fb_bg}; color:{fb_text}; padding:2px 8px; border-radius:4px;'>Fee Beli {format_rupiah(fee_beli_val)}</div>
<div style='background:{fb_bg}; color:{fb_text}; padding:2px 8px; border-radius:4px;'>Fee Jual {format_rupiah(fee_jual_val)}</div>
<div style='background:{fb_bg}; color:{fb_text}; padding:2px 8px; border-radius:4px; font-weight:600;'>Total Fee {format_rupiah(total_fee)}</div>
</div>"""
                    elif fee_jual_val > 0:
                        fb_bg = "rgba(255,255,255,0.1)" if is_highlight else "#fef3c7"
                        fb_text = "rgba(255,255,255,0.85)" if is_highlight else "#92400e"
                        fee_part = f"""<div style='display:flex; align-items:center; gap:6px; margin-top:4px; font-size:0.75rem; flex-wrap:wrap;'>
<div style='background:{fb_bg}; color:{fb_text}; padding:2px 8px; border-radius:4px;'>Fee Jual {format_rupiah(fee_jual_val)}</div>
</div>"""
                    
                    # Chip styling for Net
                    sc_bg = "rgba(255,255,255,0.15)" if is_highlight else "#f1f5f9"
                    sc_text = "#ffffff" if is_highlight else "#334155"
                    sc_border = "1px solid rgba(255,255,255,0.2)" if is_highlight else "1px solid transparent"
                    
                    sub_html = f"""
<div style='display:flex; align-items:center; gap:8px; margin-top:8px; font-size:0.85rem; flex-wrap:wrap;'>
<div style='background:{sc_bg}; color:{sc_text}; border:{sc_border}; padding:3px 9px; border-radius:6px; font-weight:700;'>Net {format_rupiah(nv)}</div>
{pl_part}
</div>
{fee_part}
"""
                
                # Border radius
                if idx == 0:
                    br = "12px 12px 0 0"
                elif is_last:
                    br = "0 0 12px 12px"
                else:
                    br = "0"
                
                border_col = "rgba(255,255,255,0.08)" if is_highlight else "#e2e8f0"
                badge_bg = "rgba(255,255,255,0.15)" if is_highlight else "#f1f5f9"
                
                rows_html += f"""
<div style="display:flex; background:{row_bg}; border-bottom:1px solid {border_col}; min-height:64px; border-radius:{br};">
<div style="width:4px; background:{accent}; flex-shrink:0;"></div>
<div style="flex:1; display:flex; align-items:center; padding:14px 18px; gap:14px;">
<div style="width:32px; height:32px; border-radius:50%; background:{badge_bg}; display:flex; align-items:center; justify-content:center; font-size:0.85rem; font-weight:700; color:{nm_col}; flex-shrink:0;">{'⏸' if is_suspend else step_num}</div>
<div style="flex:1; min-width:0;">
<div style="font-size:1rem; font-weight:700; color:{nm_col};">{item['name']}</div>
{sub_html}
</div>
<div style="text-align:right; min-width:70px;">
<div style="font-size:1.1rem; font-weight:800; color:{h_col}; font-variant-numeric:tabular-nums; margin-bottom:4px;">{h_str}</div>
<div style="font-size:0.9rem; font-weight:800; color:{p_col}; font-variant-numeric:tabular-nums;">{p_str}</div>
</div>
</div>
</div>
"""
            
            st.markdown(f"""
<div style="max-width:640px; margin:0 auto; border-radius:12px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04); border:1px solid #e2e8f0;">
{rows_html}
</div>
""", unsafe_allow_html=True)
            
        else:
            ara_list, arb_list = calculate_ara_arb_sequence(harga_penutupan, is_acceleration, max_steps)
            
            # --- Compute initial (base) values for header ---
            base_gross = harga_penutupan * jumlah_lot * 100
            base_net = base_gross * (1 - fee_jual_final)
            
            st.markdown(f"""
<div style="margin:0 auto 24px; background:linear-gradient(135deg,#4f46e5 0%,#7c3aed 50%,#a855f7 100%); border-radius:16px; padding:24px 20px; box-shadow:0 8px 32px rgba(79,70,229,0.25);">
<div style="display:flex; align-items:center; gap:10px; margin-bottom:18px;">
<div style="width:38px; height:38px; border-radius:10px; background:rgba(255,255,255,0.2); display:flex; align-items:center; justify-content:center; font-size:1.2rem;">📊</div>
<div>
<div style="font-size:1.05rem; font-weight:700; color:white;">Proyeksi Manual ARA & ARB</div>
<div style="font-size:0.75rem; color:rgba(255,255,255,0.6);">{'Papan Akselerasi' if is_acceleration else 'Papan Utama / Pengembangan'}</div>
</div>
</div>
<div style="display:grid; grid-template-columns:repeat(3,1fr); gap:8px;">
<div style="background:rgba(255,255,255,0.15); border-radius:10px; padding:10px 6px; text-align:center; backdrop-filter:blur(4px);">
<div style="font-size:0.6rem; color:rgba(255,255,255,0.6); text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">Lot</div>
<div style="font-size:1.05rem; font-weight:700; color:white;">{jumlah_lot:,}</div>
</div>
<div style="background:rgba(255,255,255,0.15); border-radius:10px; padding:10px 6px; text-align:center; backdrop-filter:blur(4px);">
<div style="font-size:0.6rem; color:rgba(255,255,255,0.6); text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">Harga</div>
<div style="font-size:1.05rem; font-weight:700; color:white;">{harga_penutupan:,}</div>
</div>
<div style="background:rgba(255,255,255,0.15); border-radius:10px; padding:10px 6px; text-align:center; backdrop-filter:blur(4px);">
<div style="font-size:0.6rem; color:rgba(255,255,255,0.6); text-transform:uppercase; letter-spacing:1px; margin-bottom:4px;">Net</div>
<div style="font-size:1.05rem; font-weight:700; color:white;">{format_rupiah(base_net)}</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)
    
            # Loop through steps
            for i in range(max_steps):
                col_l, col_r = st.columns(2, gap="medium")
                
                # --- ARA CARD (Left) ---
                with col_l:
                    if i < len(ara_list):
                        item = ara_list[i]
                        hv = float(item['harga'])
                        h_str = f"{hv:,.0f}"
                        pv = item['persentase_kumulatif']
                        p_str_val = f"+{pv:.2f}"
                        if p_str_val.endswith(".00"): p_str_val = p_str_val[:-3]
                        elif p_str_val.endswith("0"): p_str_val = p_str_val[:-1]
                        p_str = f"{p_str_val}%"
                        
                        gv = hv * jumlah_lot * 100
                        fee_jual_val = gv * fee_jual_final
                        nv = gv - fee_jual_val
                        pl_part = ""
                        fee_part = ""
                        if harga_beli > 0:
                            gross_beli = harga_beli * jumlah_lot * 100
                            fee_beli_val = gross_beli * fee_beli_final
                            tb = gross_beli + fee_beli_val
                            pl = nv - tb
                            pc_bg = "rgba(16,185,129,0.12)" if pl >= 0 else "rgba(239,68,68,0.12)"
                            pc_text = "#059669" if pl >= 0 else "#dc2626"
                            pl_part = f"<div style='background:{pc_bg}; color:{pc_text}; padding:4px 10px; border-radius:6px; font-weight:700;'>P/L {format_rupiah(pl)}</div>"
                            total_fee = fee_beli_val + fee_jual_val
                            if total_fee > 0:
                                fee_part = f"""<div style='display:flex; align-items:center; gap:6px; margin-top:4px; font-size:0.75rem; flex-wrap:wrap;'>
<div style='background:#fef3c7; color:#92400e; padding:2px 8px; border-radius:4px;'>Fee Beli {format_rupiah(fee_beli_val)}</div>
<div style='background:#fef3c7; color:#92400e; padding:2px 8px; border-radius:4px;'>Fee Jual {format_rupiah(fee_jual_val)}</div>
<div style='background:#fef3c7; color:#92400e; padding:2px 8px; border-radius:4px; font-weight:600;'>Total Fee {format_rupiah(total_fee)}</div>
</div>"""
                        elif fee_jual_val > 0:
                            fee_part = f"""<div style='display:flex; align-items:center; gap:6px; margin-top:4px; font-size:0.75rem; flex-wrap:wrap;'>
<div style='background:#fef3c7; color:#92400e; padding:2px 8px; border-radius:4px;'>Fee Jual {format_rupiah(fee_jual_val)}</div>
</div>"""
                        
                        sub_html = f"""
<div style='display:flex; align-items:center; gap:8px; margin-top:8px; font-size:0.85rem; flex-wrap:wrap;'>
<div style='background:#f1f5f9; color:#334155; border:1px solid transparent; padding:3px 9px; border-radius:6px; font-weight:700;'>Net {format_rupiah(nv)}</div>
{pl_part}
</div>
{fee_part}
"""
                        
                        st.markdown(f"""
<div style="display:flex; background:white; border:1px solid #e2e8f0; min-height:64px; border-radius:12px; margin-bottom:12px; box-shadow:0 1px 2px rgba(0,0,0,0.02);">
<div style="width:4px; background:#10b981; border-radius:12px 0 0 12px; flex-shrink:0;"></div>
<div style="flex:1; display:flex; align-items:center; padding:14px 18px; gap:14px;">
<div style="width:32px; height:32px; border-radius:50%; background:#f1f5f9; display:flex; align-items:center; justify-content:center; font-size:0.85rem; font-weight:700; color:#1e293b; flex-shrink:0;">{item['step']}</div>
<div style="flex:1; min-width:0;">
<div style="font-size:1rem; font-weight:700; color:#1e293b;">Naik (ARA #{item['step']})</div>
{sub_html}
</div>
<div style="text-align:right; min-width:70px;">
<div style="font-size:1.1rem; font-weight:800; color:#1e293b; font-variant-numeric:tabular-nums; margin-bottom:4px;">{h_str}</div>
<div style="font-size:0.9rem; font-weight:800; color:#059669; font-variant-numeric:tabular-nums;">{p_str}</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)
                
                # --- ARB CARD (Right) ---
                with col_r:
                    if i < len(arb_list):
                        item = arb_list[i]
                        hv = float(item['harga'])
                        h_str = f"{hv:,.0f}"
                        pv = item['persentase_kumulatif']
                        p_str_val = f"{pv:.2f}"
                        if p_str_val.endswith(".00"): p_str_val = p_str_val[:-3]
                        elif p_str_val.endswith("0"): p_str_val = p_str_val[:-1]
                        p_str = f"{p_str_val}%"
                        
                        gv = hv * jumlah_lot * 100
                        fee_jual_val = gv * fee_jual_final
                        nv = gv - fee_jual_val
                        pl_part = ""
                        fee_part = ""
                        if harga_beli > 0:
                            gross_beli = harga_beli * jumlah_lot * 100
                            fee_beli_val = gross_beli * fee_beli_final
                            tb = gross_beli + fee_beli_val
                            pl = nv - tb
                            pc_bg = "rgba(16,185,129,0.12)" if pl >= 0 else "rgba(239,68,68,0.12)"
                            pc_text = "#059669" if pl >= 0 else "#dc2626"
                            pl_part = f"<div style='background:{pc_bg}; color:{pc_text}; padding:4px 10px; border-radius:6px; font-weight:700;'>P/L {format_rupiah(pl)}</div>"
                            total_fee = fee_beli_val + fee_jual_val
                            if total_fee > 0:
                                fee_part = f"""<div style='display:flex; align-items:center; gap:6px; margin-top:4px; font-size:0.75rem; flex-wrap:wrap;'>
<div style='background:#fef3c7; color:#92400e; padding:2px 8px; border-radius:4px;'>Fee Beli {format_rupiah(fee_beli_val)}</div>
<div style='background:#fef3c7; color:#92400e; padding:2px 8px; border-radius:4px;'>Fee Jual {format_rupiah(fee_jual_val)}</div>
<div style='background:#fef3c7; color:#92400e; padding:2px 8px; border-radius:4px; font-weight:600;'>Total Fee {format_rupiah(total_fee)}</div>
</div>"""
                        elif fee_jual_val > 0:
                            fee_part = f"""<div style='display:flex; align-items:center; gap:6px; margin-top:4px; font-size:0.75rem; flex-wrap:wrap;'>
<div style='background:#fef3c7; color:#92400e; padding:2px 8px; border-radius:4px;'>Fee Jual {format_rupiah(fee_jual_val)}</div>
</div>"""
                        
                        sub_html = f"""
<div style='display:flex; align-items:center; gap:8px; margin-top:8px; font-size:0.85rem; flex-wrap:wrap;'>
<div style='background:#f1f5f9; color:#334155; border:1px solid transparent; padding:3px 9px; border-radius:6px; font-weight:700;'>Net {format_rupiah(nv)}</div>
{pl_part}
</div>
{fee_part}
"""
                        
                        st.markdown(f"""
<div style="display:flex; background:white; border:1px solid #e2e8f0; min-height:64px; border-radius:12px; margin-bottom:12px; box-shadow:0 1px 2px rgba(0,0,0,0.02);">
<div style="width:4px; background:#ef4444; border-radius:12px 0 0 12px; flex-shrink:0;"></div>
<div style="flex:1; display:flex; align-items:center; padding:14px 18px; gap:14px;">
<div style="width:32px; height:32px; border-radius:50%; background:#f1f5f9; display:flex; align-items:center; justify-content:center; font-size:0.85rem; font-weight:700; color:#1e293b; flex-shrink:0;">{item['step']}</div>
<div style="flex:1; min-width:0;">
<div style="font-size:1rem; font-weight:700; color:#1e293b;">Turun (ARB #{item['step']})</div>
{sub_html}
</div>
<div style="text-align:right; min-width:70px;">
<div style="font-size:1.1rem; font-weight:800; color:#1e293b; font-variant-numeric:tabular-nums; margin-bottom:4px;">{h_str}</div>
<div style="font-size:0.9rem; font-weight:800; color:#dc2626; font-variant-numeric:tabular-nums;">{p_str}</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)



