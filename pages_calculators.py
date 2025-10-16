from typing import Dict, List, Tuple
import pandas as pd
import streamlit as st

from config import PLATFORM_CONFIG, FRACSI_HARGA_DATA
from utils import format_rupiah, format_percent, format_csv_indonesia


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
        <h4 style='color: #1a1a1a; margin: 0;'>Tabel Fraksi Harga IDX</h4>
        """, unsafe_allow_html=True)
        display_fraksi_harga_table()
        st.markdown("""
        <p style='margin: 8px 0 0 0; font-size: 13px; color: #6b7280;'>
            <i>Catatan: Fraksi harga adalah selisih harga minimum antara dua transaksi saham.</i>
        </p>
        """, unsafe_allow_html=True)

    calculator_mode = st.radio("Pilih Mode Kalkulator", ["Saham", "Multiple Saham"], horizontal=True)
    if calculator_mode == "Saham":
        single_stock_calculator(title, fee_beli, fee_jual)
    else:
        multiple_stocks_calculator(title, fee_beli, fee_jual)


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
        <div style='margin-bottom: 16px; background-color: #f8f9fa; padding: 12px 8px 12px 16px; border-radius: 6px; border-left: 3px solid #2563eb;'>
            <h4 style='color: #1a1a1a; margin: 0; font-size: 16px;'>💸 Fee Platform</h4>
            <p style='margin: 4px 0 0 0; color: #6b7280; font-size: 14px;'>Fee Beli: {fee_beli*100:.2f}% | Fee Jual: {fee_jual*100:.2f}%</p>
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
                st.markdown(
                    f"""
                    <div style='margin-bottom: 16px; background-color: #f8f9fa; padding: 16px 12px 16px 20px; border-radius: 8px; border-left: 4px solid #2563eb;'>
                        <h4 style='color: #1a1a1a; margin: 0 0 8px 0; font-size: 16px;'>📊 Hasil Perhitungan</h4>
                        <p style='margin: 0; color: #6b7280; font-size: 15px;'>
                            Total Beli: {format_rupiah(total_beli)}<br>
                            Total Jual: {format_rupiah(total_jual)}<br>
                            <span style='color:{"#4CA16B" if profit_loss > 0 else ("#AD3E3E" if profit_loss < 0 else "#423D3D")}; font-weight:bold;'>
                                Profit/Loss: {format_rupiah(profit_loss)}<br>
                                Profit/Loss Percentage: {format_percent(profit_loss_percentage, 2)}
                            </span>
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if include_dividend and dividen_per_saham > 0:
                    jumlah_saham = jumlah_lot * 100
                    total_dividen = jumlah_saham * dividen_per_saham
                    dividend_yield = (dividen_per_saham / harga_beli) * 100 if harga_beli != 0 else 0
                    st.write(f"Total Dividen: {format_rupiah(total_dividen)}")
                    st.write(f"Dividend Yield: {format_percent(dividend_yield, 2)}")

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
    <div style='margin-bottom: 16px; background-color: #f8f9fa; padding: 12px 8px 12px 16px; border-radius: 6px; border-left: 3px solid #2563eb;'>
        <h4 style='color: #1a1a1a; margin: 0; font-size: 16px;'>💸 Fee Platform</h4>
        <p style='margin: 4px 0 0 0; color: #6b7280; font-size: 14px;'>Fee Beli: {fee_beli*100:.2f}% | Fee Jual: {fee_jual*100:.2f}%</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Hitung Multiple Saham", key="calculate_multiple"):
        with st.spinner('Menghitung multiple saham...'):
            result = calculate_multiple_stocks_profit_loss(stocks_data)
            st.markdown(
                f"""
                <div style='margin-bottom: 16px; background-color: #f8f9fa; padding: 16px 12px 16px 20px; border-radius: 8px; border-left: 4px solid #2563eb;'>
                    <h4 style='color: #1a1a1a; margin: 0 0 8px 0; font-size: 16px;'>📊 Hasil Total Portfolio</h4>
                    <p style='margin: 0; color: #6b7280; font-size: 15px;'>
                        Total Investasi: {format_rupiah(result['total_investment'])}<br>
                        Total Proceeds: {format_rupiah(result['total_proceeds'])}<br>
                        Total Fee Beli: {format_rupiah(result['total_fee_beli'])}<br>
                        Total Fee Jual: {format_rupiah(result['total_fee_jual'])}<br>
                        <span style='color:{"#4CA16B" if result['total_profit_loss'] > 0 else ("#AD3E3E" if result['total_profit_loss'] < 0 else "#423D3D")}; font-weight:bold;'>
                            Total Profit/Loss: {format_rupiah(result['total_profit_loss'])}<br>
                            Total Profit/Loss Percentage: {format_percent(result['total_profit_loss_percentage'], 2)}
                        </span>
                    </p>
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
            st.dataframe(df_detail, use_container_width=True, hide_index=True)
            df_download = df_detail.copy()
            for col in df_download.columns:
                if col in ['Harga Beli', 'Harga Jual', 'Total Beli', 'Total Jual', 'Profit/Loss']:
                    df_download[col] = df_download[col].apply(lambda x: format_csv_indonesia(x, 0) if pd.notna(x) else "0")
                elif col in ['Profit/Loss %']:
                    df_download[col] = df_download[col].apply(lambda x: format_csv_indonesia(x, 2) if pd.notna(x) else "0")
            csv = df_download.to_csv(index=False, sep=';', encoding='utf-8-sig', quoting=1)
            st.download_button(label="📥 Download as CSV", data=csv, file_name="kalkulator_saham.csv", mime="text/csv")


