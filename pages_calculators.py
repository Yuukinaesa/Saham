from typing import Dict, List, Tuple
import pandas as pd
import streamlit as st

from config import PLATFORM_CONFIG, FRACSI_HARGA_DATA
from utils import format_rupiah, format_percent, format_csv_indonesia, get_tick_size, get_ara_arb_percentage, round_price_to_tick
import math


def calculate_profit_loss(jumlah_lot: int, harga_beli: float, harga_jual: float, fee_beli: float, fee_jual: float) -> Tuple[float, float, float, float]:
    jumlah_saham = jumlah_lot * 100
    total_beli = jumlah_saham * harga_beli
    total_fee_beli = total_beli * fee_beli
    total_beli += total_fee_beli
    total_jual = jumlah_saham * harga_jual
    total_fee_jual = total_jual * fee_jual
    total_jual -= total_fee_jual
    profit_loss = total_jual - total_beli
    profit_loss_percentage = (profit_loss / total_beli) * 100 if total_beli != 0 else 0
    return (
        round(total_beli, 2),
        round(total_jual, 2),
        round(profit_loss, 2),
        round(profit_loss_percentage, 2)
    )


def calculate_multiple_stocks_profit_loss(stocks_data: List[Dict]) -> Dict:
    total_investment = 0
    total_proceeds = 0
    total_profit_loss = 0
    total_fee_beli = 0
    total_fee_jual = 0
    stocks_results = []
    for stock in stocks_data:
        total_beli, total_jual, profit_loss, profit_loss_percentage = calculate_profit_loss(
            stock['jumlah_lot'], stock['harga_beli'], stock['harga_jual'], stock['fee_beli'], stock['fee_jual']
        )
        jumlah_saham = stock['jumlah_lot'] * 100
        fee_beli = jumlah_saham * stock['harga_beli'] * stock['fee_beli']
        fee_jual = jumlah_saham * stock['harga_jual'] * stock['fee_jual']
        total_investment += total_beli
        total_proceeds += total_jual
        total_profit_loss += profit_loss
        total_fee_beli += fee_beli
        total_fee_jual += fee_jual
        stocks_results.append({
            'symbol': stock['symbol'],
            'jumlah_lot': stock['jumlah_lot'],
            'harga_beli': stock['harga_beli'],
            'harga_jual': stock['harga_jual'],
            'total_beli': total_beli,
            'total_jual': total_jual,
            'profit_loss': profit_loss,
            'profit_loss_percentage': profit_loss_percentage,
            'fee_beli': fee_beli,
            'fee_jual': fee_jual
        })
    total_profit_loss_percentage = (total_profit_loss / total_investment) * 100 if total_investment != 0 else 0
    return {
        'total_investment': round(total_investment, 2),
        'total_proceeds': round(total_proceeds, 2),
        'total_profit_loss': round(total_profit_loss, 2),
        'total_profit_loss_percentage': round(total_profit_loss_percentage, 2),
        'total_fee_beli': round(total_fee_beli, 2),
        'total_fee_jual': round(total_fee_jual, 2),
        'stocks_results': stocks_results
    }


def display_fraksi_harga_table() -> None:
    headers = ["Harga Saham", "Fraksi Harga"]
    rows = list(zip(FRACSI_HARGA_DATA["Harga Saham"], FRACSI_HARGA_DATA["Fraksi Harga"]))
    df = pd.DataFrame(rows, columns=headers)
    st.table(df)


def calculator_page(title: str, fee_beli: float, fee_jual: float) -> None:
    with st.expander("📊 Tabel Fraksi Harga", expanded=False):
        st.markdown("""
        <h4 style='color: var(--text-color); margin: 0;'>Tabel Fraksi Harga IDX</h4>
        """, unsafe_allow_html=True)
        display_fraksi_harga_table()
        st.markdown("""
        <p style='margin: 8px 0 0 0; font-size: 13px; color: var(--text-color); opacity: 0.8;'>
            <i>Catatan: Fraksi harga adalah selisih harga minimum antara dua transaksi saham.</i>
        </p>
        """, unsafe_allow_html=True)

    calculator_mode = st.radio("Pilih Mode Kalkulator", ["Saham", "Multiple Saham", "HAKA vs Limit"], horizontal=True)
    if calculator_mode == "Saham":
        single_stock_calculator(title, fee_beli, fee_jual)
    elif calculator_mode == "HAKA vs Limit":
        haka_vs_limit_calculator(title, fee_beli)
    else:
        multiple_stocks_calculator(title, fee_beli, fee_jual)


def haka_vs_limit_calculator(title: str, fee_beli: float) -> None:
    st.markdown('<div class="section-title">⚡ HAKA (Market) vs Limit Order</div>', unsafe_allow_html=True)
    st.info("Bandingkan berapa lot yang didapat jika ANTRE (Limit Order) vs HAKA (Market Order). Market order menggunakan harga ARA sebagai basis perhitungan agar order tidak rejected.")

    col_config, col_input = st.columns([1, 1], gap="medium")
    
    with col_config:
        if title == "Custom":
            st.markdown('**Pengaturan Fee**')
            fee_beli = st.number_input("Fee Beli (%)", min_value=0.0, value=0.15, step=0.01) / 100
        
        st.markdown('**Kriteria Saham**')
        is_acceleration = st.checkbox("Saham Papan Akselerasi", value=False)
        board_type = 'acceleration' if is_acceleration else 'regular'

    with col_input:
        st.markdown('**Input Modal & Harga**')
        modal = st.number_input("Total Modal (Buying Power)", min_value=100000, step=100000, value=1000000)
        harga_input = st.number_input("Harga Saham Saat Ini (Offer)", min_value=50, step=1, value=200)

    # Calculate ARA logic locally to determine safe HAKA price
    if is_acceleration and harga_input <= 10:
        harga_ara = harga_input + 1
    else:
        pct = get_ara_arb_percentage(harga_input, board_type)
        limit_price = harga_input * (1 + pct)
        tick = get_tick_size(limit_price)
        harga_ara = round_price_to_tick(limit_price, tick, 'floor')
        
        # Ensure ARA is at least 1 tick above if price didn't move
        if harga_ara <= harga_input:
             harga_ara = harga_input + get_tick_size(harga_input)

    if st.button("Hitung Perbandingan", type="primary", width='stretch'):
        # 1. Limit Order Calculation
        # Formula: Lot = Modal / (Price * 100 * (1 + Fee))
        harga_per_lot_limit = harga_input * 100 * (1 + fee_beli)
        max_lot_limit = math.floor(modal / harga_per_lot_limit)
        total_modal_limit = max_lot_limit * harga_per_lot_limit
        sisa_modal_limit = modal - total_modal_limit

        # 2. HAKA (Market Order) Calculation
        # Uses ARA price for safety margin
        harga_per_lot_ara = harga_ara * 100 * (1 + fee_beli)
        max_lot_haka = math.floor(modal / harga_per_lot_ara)
        
        # Actual cost if executed at ARA (Worst case)
        total_modal_haka_ara = max_lot_haka * harga_per_lot_ara
        
        # Actual cost if executed at Current Price (Best case, but with reduced lot count)
        realized_cost_haka = max_lot_haka * harga_per_lot_limit
        sisa_modal_haka = modal - realized_cost_haka

        st.markdown("---")
        
        col_res1, col_res2 = st.columns(2, gap="large")
        
        with col_res1:
            st.markdown(f"""
            <div class='premium-card' style='border-left: 4px solid #3b82f6;'>
                <h4 style="margin:0; color:#3b82f6;">🟢 Limit Order</h4>
                <p style="font-size:0.85rem; opacity:0.8;">Antre di harga {format_rupiah(harga_input)}</p>
                <div style="margin-top:10px;">
                    <div style="font-size:2rem; font-weight:700;">{max_lot_limit:,} <span style="font-size:1rem; font-weight:400;">Lot</span></div>
                    <div style="font-size:0.9rem; margin-top:5px;">Est. Total: {format_rupiah(total_modal_limit)}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_res2:
            st.markdown(f"""
            <div class='premium-card' style='border-left: 4px solid #f59e0b;'>
                <h4 style="margin:0; color:#f59e0b;">⚡ HAKA (Market Order)</h4>
                <p style="font-size:0.85rem; opacity:0.8;">Safety Price (ARA): {format_rupiah(harga_ara)}</p>
                <div style="margin-top:10px;">
                    <div style="font-size:2rem; font-weight:700;">{max_lot_haka:,} <span style="font-size:1rem; font-weight:400;">Lot</span></div>
                    <div style="font-size:0.9rem; margin-top:5px;">Est. Total: {format_rupiah(realized_cost_haka)}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # Comparison
        diff_lot = max_lot_limit - max_lot_haka
        
        st.markdown("### 💡 Insight")
        if diff_lot > 0:
            st.warning(f"""
            **Selisih: {diff_lot} Lot**
            
            Jika Anda melakukan **Market Order (HAKA)**, sistem akan menahan modal seolah-olah Anda membeli di harga ARA ({format_rupiah(harga_ara)}).
            Akibatnya, Anda mendapatkan **{diff_lot} lot lebih sedikit** dibandingkan jika Anda menggunakan Limit Order di harga {harga_input}.
            
            Namun, Market Order menjamin order Anda tereksekusi instan (selama antrian jual tersedia), sedangkan Limit Order mungkin perlu menunggu.
            """)
        else:
            st.success("Jumlah lot sama antara Limit dan Market Order untuk modal ini.")
            
        st.markdown(f"""
        <div style="background-color:var(--secondary-background-color); padding:10px; border-radius:8px; font-size:0.85rem; margin-top:10px;">
            <strong>Rincian Perhitungan:</strong><br>
            • Modal: {format_rupiah(modal)}<br>
            • Fee Beli: {fee_beli*100:.2f}%<br>
            • Harga ARA (Basis HAKA): {format_rupiah(harga_ara)}<br>
            • Max Lot Limit = Floor({modal} / ({harga_input} × 100 × {1+fee_beli})) = {max_lot_limit}<br>
            • Max Lot HAKA = Floor({modal} / ({harga_ara} × 100 × {1+fee_beli})) = {max_lot_haka}
        </div>
        """, unsafe_allow_html=True)


def single_stock_calculator(title: str, fee_beli: float, fee_jual: float) -> None:
    col1, _ = st.columns(2, gap="small")
    with col1:
        if title == "Custom":
            st.markdown('<div class="section-title">💰 Masukkan Fee Kustom</div>', unsafe_allow_html=True)
            fee_beli = st.number_input("Fee Beli (persentase):", step=0.1, format="%.2f") / 100
            fee_jual = st.number_input("Fee Jual (persentase):", step=0.1, format="%.2f") / 100
        st.markdown('<div class="section-title">📈 Input Transaksi</div>', unsafe_allow_html=True)
        jumlah_lot = st.number_input("Jumlah Lot:", step=1, format="%d", value=10)
        harga_beli = st.number_input("Harga Beli (per saham):", step=1000.0, format="%0.0f", value=1000.0)
        harga_jual = st.number_input("Harga Jual (per saham):", step=1000.0, format="%0.0f", value=2000.0)
        st.markdown(f"""
        <div style='margin-bottom: 16px; background-color: rgba(37, 99, 235, 0.1); padding: 12px 8px 12px 16px; border-radius: 6px; border-left: 3px solid #2563eb;'>
            <h4 style='color: var(--text-color); margin: 0; font-size: 16px;'>💸 Fee Platform</h4>
            <p style='margin: 4px 0 0 0; color: var(--text-color); opacity: 0.9; font-size: 14px;'>Fee Beli: {fee_beli*100:.2f}% | Fee Jual: {fee_jual*100:.2f}%</p>
        </div>
        """, unsafe_allow_html=True)
        include_fee_beli = st.checkbox("Masukkan Fee Beli", value=True)
        include_fee_jual = st.checkbox("Masukkan Fee Jual", value=True)
        include_dividend = st.checkbox("Masukkan Dividen")
        dividen_per_saham = 0
        if include_dividend:
            dividen_per_saham = st.number_input("Dividen per Saham:", step=1, format="%d")
        st.markdown('<div style="text-align: center; margin: 16px 0;">', unsafe_allow_html=True)
        if st.button("Hitung", key="calculate_single"):
            with st.spinner('Menghitung...'):
                fee_beli_final = fee_beli if include_fee_beli else 0
                fee_jual_final = fee_jual if include_fee_jual else 0
                total_beli, total_jual, profit_loss, profit_loss_percentage = calculate_profit_loss(
                    jumlah_lot, harga_beli, harga_jual, fee_beli_final, fee_jual_final
                )
                
                # Determine color class and background based on profit/loss
                is_profit = profit_loss > 0
                is_loss = profit_loss < 0
                
                if is_profit:
                    card_border = "#10b981"
                    # Brighter text for dark mode visibility
                    text_color = "#10b981" 
                    # Transparent background
                    bg_badge = "rgba(16, 185, 129, 0.2)"
                elif is_loss:
                    card_border = "#ef4444"
                    text_color = "#ef4444"
                    bg_badge = "rgba(239, 68, 68, 0.2)"
                else:
                    card_border = "#6b7280"
                    text_color = "var(--text-color)"
                    bg_badge = "rgba(128, 128, 128, 0.1)"

                # Calculate Fee Amounts
                jumlah_saham = jumlah_lot * 100
                bs_fee_beli = (jumlah_saham * harga_beli) * fee_beli_final
                bs_fee_jual = (jumlah_saham * harga_jual) * fee_jual_final
                total_fee_transaksi = bs_fee_beli + bs_fee_jual

                # Dividend Calculations
                dividend_html = ""
                if include_dividend and dividen_per_saham > 0:
                    total_dividen = jumlah_saham * dividen_per_saham
                    dividend_yield = (dividen_per_saham / harga_beli) * 100 if harga_beli != 0 else 0
                    dividend_html = f"""
<div style='margin-top: 16px; padding-top: 16px; border-top: 1px dashed rgba(128, 128, 128, 0.2);'>
<div style='display: grid; grid-template-columns: 1fr 1fr; gap: 16px;'>
<div>
<p style='margin: 0; color: var(--text-color); opacity: 0.8; font-size: 0.85rem; font-weight: 500;'>Total Dividen</p>
<p style='margin: 4px 0 0 0; color: #059669; font-size: 1.1rem; font-weight: 600;'>+{format_rupiah(total_dividen)}</p>
</div>
<div>
<p style='margin: 0; color: var(--text-color); opacity: 0.8; font-size: 0.85rem; font-weight: 500;'>Dividend Yield</p>
<p style='margin: 4px 0 0 0; color: #059669; font-size: 1.1rem; font-weight: 600;'>{format_percent(dividend_yield, 2)}</p>
</div>
</div>
</div>
"""

                st.markdown(
                    f"""
<div class='premium-card' style='border-left: 5px solid {card_border};'>
<div style='display: flex; justify-content: space-between; align-items: start; margin-bottom: 16px;'>
<h4 style='color: var(--text-color); margin: 0; font-size: 1.15rem; font-weight: 700;'>📊 Hasil Transaksi</h4>
<span style='background-color: {bg_badge}; color: {text_color}; padding: 4px 12px; border-radius: 9999px; font-weight: 600; font-size: 0.85rem;'>
{format_percent(profit_loss_percentage, 2)}
</span>
</div>
<div style='display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px;'>
<div>
<p style='margin: 0; color: var(--text-color); opacity: 0.8; font-size: 0.85rem; font-weight: 500;'>Total Beli (All-in)</p>
<p style='margin: 4px 0 0 0; color: var(--text-color); font-size: 1.1rem; font-weight: 600;'>{format_rupiah(total_beli)}</p>
</div>
<div>
<p style='margin: 0; color: var(--text-color); opacity: 0.8; font-size: 0.85rem; font-weight: 500;'>Total Jual (Net)</p>
<p style='margin: 4px 0 0 0; color: var(--text-color); font-size: 1.1rem; font-weight: 600;'>{format_rupiah(total_jual)}</p>
</div>
</div>
<div style='margin-bottom: 16px; padding: 12px; background-color: rgba(128, 128, 128, 0.1); border-radius: 8px;'>
<p style='margin: 0 0 8px 0; color: var(--text-color); font-weight: 600; font-size: 0.9rem;'>Rincian Biaya (Fee)</p>
<div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; font-size: 0.85rem;'>
<div>
<p style='margin: 0; color: var(--text-color); opacity: 0.8; font-size: 0.75rem;'>Fee Beli</p>
<p style='margin: 0; color: var(--text-color); font-weight: 600;'>{format_rupiah(bs_fee_beli)}</p>
</div>
<div>
<p style='margin: 0; color: var(--text-color); opacity: 0.8; font-size: 0.75rem;'>Fee Jual</p>
<p style='margin: 0; color: var(--text-color); font-weight: 600;'>{format_rupiah(bs_fee_jual)}</p>
</div>
<div>
<p style='margin: 0; color: var(--text-color); opacity: 0.8; font-size: 0.75rem;'>Total Fee</p>
<p style='margin: 0; color: var(--text-color); font-weight: 600;'>{format_rupiah(total_fee_transaksi)}</p>
</div>
</div>
</div>
<div style='background-color: {bg_badge}; padding: 16px; border-radius: 8px;'>
<div style='display: flex; justify-content: space-between; align-items: center;'>
<span style='color: {text_color}; font-weight: 600;'>Net Profit / Loss</span>
<span style='color: {text_color}; font-weight: 700; font-size: 1.25rem;'>{format_rupiah(profit_loss)}</span>
</div>
</div>
{dividend_html}
</div>
""",
                    unsafe_allow_html=True,
                )

                # Download hasil single kalkulator sebagai CSV (format Indonesia)
                df_download = pd.DataFrame([
                    {
                        'Jumlah Lot': jumlah_lot,
                        'Harga Beli': format_csv_indonesia(harga_beli, 0),
                        'Harga Jual': format_csv_indonesia(harga_jual, 0),
                        'Total Beli': format_csv_indonesia(total_beli, 0),
                        'Total Jual': format_csv_indonesia(total_jual, 0),
                        'Profit/Loss': format_csv_indonesia(profit_loss, 0),
                        'Profit/Loss %': format_csv_indonesia(profit_loss_percentage, 2),
                    }
                ])
                csv = df_download.to_csv(index=False, sep=';', encoding='utf-8-sig', quoting=1)
                st.download_button(label="📥 Download as CSV", data=csv, file_name="kalkulator_saham_single.csv", mime="text/csv")


def multiple_stocks_calculator(title: str, fee_beli: float, fee_jual: float) -> None:
    st.markdown('<div class="section-title">📊 Kalkulator Multiple Saham</div>', unsafe_allow_html=True)
    num_stocks = st.number_input("Jumlah Saham yang Dihitung:", min_value=1, max_value=10, value=2, step=1)
    if title == "Custom":
        st.markdown('<div class="section-title">💰 Masukkan Fee Kustom</div>', unsafe_allow_html=True)
        fee_beli = st.number_input("Fee Beli (persentase):", step=0.1, format="%.2f") / 100
        fee_jual = st.number_input("Fee Jual (persentase):", step=0.1, format="%.2f") / 100
    stocks_data = []
    for i in range(num_stocks):
        st.markdown(f"### Saham {i+1}")
        col1, col2, col3 = st.columns(3)
        with col1:
            symbol = st.text_input(f"Simbol Saham {i+1}", value=f"STOCK{i+1}", key=f"symbol_{i}")
            jumlah_lot = st.number_input(f"Jumlah Lot {i+1}", step=1, format="%d", value=10, key=f"lot_{i}")
        with col2:
            harga_beli = st.number_input(f"Harga Beli {i+1}", step=1000.0, format="%0.0f", value=1000.0, key=f"beli_{i}")
            harga_jual = st.number_input(f"Harga Jual {i+1}", step=1000.0, format="%0.0f", value=2000.0, key=f"jual_{i}")
        with col3:
            include_fee_beli = st.checkbox(f"Fee Beli {i+1}", value=True, key=f"fee_beli_{i}")
            include_fee_jual = st.checkbox(f"Fee Jual {i+1}", value=True, key=f"fee_jual_{i}")
        stocks_data.append({
            'symbol': symbol,
            'jumlah_lot': jumlah_lot,
            'harga_beli': harga_beli,
            'harga_jual': harga_jual,
            'fee_beli': fee_beli if include_fee_beli else 0,
            'fee_jual': fee_jual if include_fee_jual else 0
        })
    st.markdown(f"""
    <div style='margin-bottom: 16px; background-color: rgba(37, 99, 235, 0.1); padding: 12px 16px; border-radius: 8px; border-left: 4px solid #2563eb;'>
        <h4 style='color: var(--text-color); margin: 0 0 4px 0; font-size: 1rem; font-weight: 600;'>💸 Fee Platform</h4>
        <p style='margin: 0; color: var(--text-color); opacity: 0.9; font-size: 0.9rem;'>Fee Beli: <strong>{fee_beli*100:.2f}%</strong> | Fee Jual: <strong>{fee_jual*100:.2f}%</strong></p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Hitung Multiple Saham", key="calculate_multiple"):
        with st.spinner('Menghitung multiple saham...'):
            result = calculate_multiple_stocks_profit_loss(stocks_data)
            # Multiple Stocks Layout
            is_profitable = result['total_profit_loss'] > 0
            card_border = "#10b981" if is_profitable else "#ef4444"
            header_text_color = "#047857" if is_profitable else "#b91c1c"
            
            st.markdown(
                f"""
<div class='premium-card' style='border-top: 5px solid {card_border}; border-left: 1px solid rgba(128, 128, 128, 0.1);'>
<h4 style='color: var(--text-color); margin: 0 0 20px 0; font-size: 1.25rem; font-weight: 700; text-align: center;'>📊 Ringkasan Portfolio</h4>
<div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 24px;'>
<div style='text-align: center; padding: 12px; background-color: rgba(128, 128, 128, 0.1); border-radius: 8px;'>
<p style='margin: 0; color: var(--text-color); opacity: 0.8; font-size: 0.85rem; font-weight: 500;'>Total Investasi</p>
<p style='margin: 4px 0 0 0; color: var(--text-color); font-size: 1.1rem; font-weight: 600;'>{format_rupiah(result['total_investment'])}</p>
</div>
<div style='text-align: center; padding: 12px; background-color: rgba(128, 128, 128, 0.1); border-radius: 8px;'>
<p style='margin: 0; color: var(--text-color); opacity: 0.8; font-size: 0.85rem; font-weight: 500;'>Total Proceeds</p>
<p style='margin: 4px 0 0 0; color: var(--text-color); font-size: 1.1rem; font-weight: 600;'>{format_rupiah(result['total_proceeds'])}</p>
</div>
</div>
<div style='text-align: center; padding: 20px; border-radius: 8px; background-color: {"rgba(16, 185, 129, 0.1)" if is_profitable else "rgba(239, 68, 68, 0.1)"};'>
<p style='margin: 0; color: {header_text_color}; font-size: 0.9rem; font-weight: 600;'>Total Profit / Loss</p>
<h2 style='margin: 8px 0 0 0; color: {header_text_color}; font-size: 2rem; font-weight: 800;'>{format_rupiah(result['total_profit_loss'])}</h2>
<span style='display: inline-block; margin-top: 8px; padding: 4px 12px; border-radius: 9999px; background-color: rgba(128, 128, 128, 0.1); color: {header_text_color}; font-weight: 700; font-size: 0.9rem; box-shadow: 0 1px 2px rgba(0,0,0,0.05);'>
{format_percent(result['total_profit_loss_percentage'], 2)}
</span>
</div>
<div style='margin-top: 20px; border-top: 1px solid rgba(128, 128, 128, 0.2); padding-top: 16px; font-size: 0.85rem; color: var(--text-color); opacity: 0.8; display: flex; justify-content: space-between;'>
<span>Total Fee Beli: {format_rupiah(result['total_fee_beli'])}</span>
<span>Total Fee Jual: {format_rupiah(result['total_fee_jual'])}</span>
</div>
</div>
""",
                unsafe_allow_html=True,
            )
            st.markdown("### Detail Per Saham")
            detail_data = []
            for stock in result['stocks_results']:
                detail_data.append({
                    'Symbol': stock['symbol'],
                    'Lot': stock['jumlah_lot'],
                    'Harga Beli': format_rupiah(stock['harga_beli']),
                    'Harga Jual': format_rupiah(stock['harga_jual']),
                    'Total Beli': format_rupiah(stock['total_beli']),
                    'Total Jual': format_rupiah(stock['total_jual']),
                    'Profit/Loss': format_rupiah(stock['profit_loss']),
                    'Profit/Loss %': format_percent(stock['profit_loss_percentage'], 2)
                })
            df_detail = pd.DataFrame(detail_data)
            st.dataframe(df_detail, width='stretch', hide_index=True)
            df_download = df_detail.copy()
            for col in df_download.columns:
                if col in ['Harga Beli', 'Harga Jual', 'Total Beli', 'Total Jual', 'Profit/Loss']:
                    df_download[col] = df_download[col].apply(lambda x: format_csv_indonesia(x, 0) if pd.notna(x) else "0")
                elif col in ['Profit/Loss %']:
                    df_download[col] = df_download[col].apply(lambda x: format_csv_indonesia(x, 2) if pd.notna(x) else "0")
            csv = df_download.to_csv(index=False, sep=';', encoding='utf-8-sig', quoting=1)
            st.download_button(label="📥 Download as CSV", data=csv, file_name="kalkulator_saham.csv", mime="text/csv")


