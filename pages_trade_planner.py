import streamlit as st
import pandas as pd
import yfinance as yf
from utils import format_rupiah, format_percent

def get_realtime_price(symbol):
    try:
        # Tambahkan .JK jika belum ada dan bukan kode komposit/indeks tertentu
        ticker_symbol = f"{symbol}.JK" if not symbol.endswith(".JK") and not symbol.startswith("^") else symbol
        
        # Menggunakan yfinance dengan periode '1d' untuk mendapatkan data real-time/terbaru
        ticker = yf.Ticker(ticker_symbol)
        history = ticker.history(period="1d")
        
        if not history.empty:
            # Mengambil harga penutupan terakhir (bisa jadi harga saat ini jika pasar buka)
            current_price = history['Close'].iloc[-1]
            return current_price
        return None
    except Exception as e:
        return None

def trade_planner_page():
    st.markdown("""
    <div style='margin-bottom: 24px;'>
        <h2 style='color: var(--text-color); margin-bottom: 8px;'>🎯 Trade Planner Realtime</h2>
        <p style='color: var(--text-color); opacity: 0.8; font-size: 1.1em;'>Hitung posisi entry, stop loss, dan take profit berdasarkan Risk Reward Ratio.</p>
    </div>
    """, unsafe_allow_html=True)

    # Input Section
    col_input1, col_input2 = st.columns([1, 1], gap="large")
    
    with col_input1:
        st.markdown("### 1. Data Saham & Modal")
        symbol = st.text_input("Kode Saham (Contoh: BBRI, TLKM)", value="BBRI").upper()
        
        # Opsi Harga Manual
        use_manual_price = st.checkbox("Input Harga Entry Manual")
        if use_manual_price:
            manual_entry_price = st.number_input("Harga Entry Manual (Rp)", min_value=1, value=1, step=5)
        else:
            manual_entry_price = 0
        
        calc_mode = st.radio(
            "Metode Perhitungan",
            ["Hitung Lot dari Resiko (Money Management)", "Hitung Resiko dari Modal Entry (Fixed Capital)"],
            index=0,
            help="Pilih apakah ingin menghitung jumlah lot berdasarkan batas resiko portfolio, atau menghitung resiko berdasarkan jumlah uang yang ingin ditradingkan."
        )

        if calc_mode == "Hitung Lot dari Resiko (Money Management)":
            modal = st.number_input("Total Portfolio (Rp)", min_value=100000, value=10000000, step=1000000, help="Total seluruh uang di akun sekuritas Anda.")
            risk_label = "Resiko per Trade (% dari Portfolio)"
            show_risk_input = True
        else:
            modal = st.number_input("Modal Entry (Rp)", min_value=100000, value=1000000, step=100000, help="Total uang yang ingin Anda masukkan ke saham ini.")
            risk_label = "N/A"
            show_risk_input = False
    
    with col_input2:
        st.markdown("### 2. Parameter Risiko")
        if show_risk_input:
            risk_per_trade_pct = st.number_input(risk_label, min_value=0.1, max_value=100.0, value=2.0, step=0.1, help="Berapa persen dari Portfolio yang siap Anda pertaruhkan.")
        else:
            risk_per_trade_pct = 0.0 # Not used in this mode
            
        stop_loss_pct = st.number_input("Jarak Stop Loss (% dari Harga Entry)", min_value=0.5, max_value=50.0, value=3.0, step=0.5, help="Jarak teknikal untuk Cut Loss.")
        rrr = st.number_input("Risk Reward Ratio (1 : X)", min_value=1.0, value=2.0, step=0.1, help="Target profit minimal berapa kali lipat dari resiko.")

    # Action Button
    if st.button("Analisa Trade", type="primary"):
        current_price = None
        if use_manual_price and manual_entry_price > 0:
             current_price = manual_entry_price
        else:
            with st.spinner(f"Mengambil harga realtime {symbol}..."):
                current_price = get_realtime_price(symbol)
        
        
        if current_price:
            # 2. Stop Loss Price & Take Profit Price (Technical levels are same regardless of money logic)
            stop_loss_price = int(current_price * (1 - (stop_loss_pct / 100)))
            price_risk_per_share = current_price - stop_loss_price
            price_reward_per_share = price_risk_per_share * rrr
            take_profit_price = int(current_price + price_reward_per_share)

            # Calculations based on Mode
            if calc_mode == "Hitung Lot dari Resiko (Money Management)":
                # Mode A: Determine Lot based on Portfolio Risk
                risk_amount = modal * (risk_per_trade_pct / 100)
                
                if price_risk_per_share > 0:
                    max_lot_by_risk = int(risk_amount / (100 * price_risk_per_share))
                else:
                    max_lot_by_risk = 0
                
                # Check capital limit
                capital_required = max_lot_by_risk * 100 * current_price
                if capital_required > modal:
                    max_lot = int(modal / (100 * current_price))
                    limit_reason = "Terbatas oleh Total Modal (Portfolio)"
                else:
                    max_lot = max_lot_by_risk
                    limit_reason = "Sesuai Manajemen Resiko (Portfolio)"
                    
            else:
                # Mode B: Determine Lot based on allocated Capital (Fixed Capital)
                # Lot = Modal Entry / Price per Lot
                max_lot = int(modal / (100 * current_price))
                limit_reason = "Sesuai Alokasi Modal Entry"
                
                # Calculate implied risk
                calculated_loss = max_lot * 100 * price_risk_per_share
                # Update risk_amount for display
                risk_amount = calculated_loss
                if max_lot == 0:
                    st.warning("Modal tidak cukup untuk membeli 1 lot.")

            total_entry_value = max_lot * 100 * current_price
            potential_loss = max_lot * 100 * (current_price - stop_loss_price)
            potential_profit = max_lot * 100 * (take_profit_price - current_price)
            
            # Persentase resiko terhadap modal entry (For Mode B context)
            if total_entry_value > 0:
                implied_risk_pct = (potential_loss / total_entry_value) * 100
            else:
                implied_risk_pct = 0

            # Display Results
            st.markdown("---")
            st.markdown(f"### 📊 Hasil Analisa: {symbol}")
            
            # Key Metrics Cards
            c1, c2, c3 = st.columns(3)
            with c1:
                
                price_label = "Harga Manual (Entry)" if use_manual_price else "Harga Realtime (Entry)"
                
                st.markdown(f"""
                <div style='background-color: rgba(37, 99, 235, 0.1); padding: 15px; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2); text-align: center;'>
                    <p style='margin:0; font-size:14px; opacity:0.8;'>{price_label}</p>
                    <h3 style='margin:5px 0 0 0; color: #3b82f6;'>{format_rupiah(current_price)}</h3>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div style='background-color: rgba(239, 68, 68, 0.1); padding: 15px; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2); text-align: center;'>
                    <p style='margin:0; font-size:14px; opacity:0.8;'>Stop Loss ({stop_loss_pct}%)</p>
                    <h3 style='margin:5px 0 0 0; color: #ef4444;'>{format_rupiah(stop_loss_price)}</h3>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div style='background-color: rgba(16, 185, 129, 0.1); padding: 15px; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2); text-align: center;'>
                    <p style='margin:0; font-size:14px; opacity:0.8;'>Take Profit (1:{rrr})</p>
                    <h3 style='margin:5px 0 0 0; color: #10b981;'>{format_rupiah(take_profit_price)}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)

            # Plan Details
            st.info(f"💡 **Dasar Perhitungan:** {limit_reason}")
            
            col_det1, col_det2 = st.columns(2)
            with col_det1:
                st.markdown("#### 📋 Rincian Entry")
                st.write(f"**Jumlah Lot:** {max_lot} Lot")
                st.write(f"**Total Nilai Entry:** {format_rupiah(total_entry_value)}")
                if calc_mode == "Hitung Lot dari Resiko (Money Management)":
                    st.write(f"**Risk Limit:** {risk_per_trade_pct}% dari Portfolio ({format_rupiah(risk_amount)})")
            
            with col_det2:
                st.markdown("#### 💰 Proyeksi PnL")
                st.markdown(f"**Potensi Profit:** <span style='color:#10b981; font-weight:bold;'>{format_rupiah(potential_profit)}</span> (+{stop_loss_pct * rrr:.2f}%)", unsafe_allow_html=True)
                st.markdown(f"**Potensi Loss:** <span style='color:#ef4444; font-weight:bold;'>{format_rupiah(potential_loss)}</span> (-{stop_loss_pct}%)", unsafe_allow_html=True)
            
            # --- PROFESSIONAL METRICS SECTION ---
            st.markdown("---")
            st.markdown("#### 🧠 Professional Insight")
            
            # --- PROFESSIONAL METRICS SECTION ---
            st.markdown("---")
            st.markdown("#### 🧠 Professional Insight")
            
            # Calculate Breakeven Win Rate
            be_winrate = (1 / (1 + rrr)) * 100
            
            # SNIPER MODE: Probability Score Calculation
            # Logic: 
            # 1. R:R > 2 (+20%)
            # 2. Risk per Trade < 2% of Capital (+20%)
            # 3. Stop Loss is tight (< 5%) (+20%)
            # 4. Winrate required < 40% (+20%)
            # 5. Modal Cukup (+20%)
            
            prob_score = 0
            sc_details = []
            
            if rrr >= 2.0:
                prob_score += 20
                sc_details.append("✅ Risk Reward Sehat (>1:2)")
            else:
                sc_details.append("⚠️ Risk Reward Kecil")
                
            if stop_loss_pct <= 5.0:
                prob_score += 20
                sc_details.append("✅ SL Ketat (<5%)")
            else:
                 sc_details.append("⚠️ SL Lebar (>5%)")
            
            if be_winrate < 40:
                prob_score += 20
                sc_details.append("✅ Beban Winrate Rendah")
            else:
                sc_details.append("⚠️ Beban Winrate Tinggi")

            if calc_mode == "Hitung Lot dari Resiko (Money Management)":
                 if risk_per_trade_pct <= 2.0:
                     prob_score += 20
                     sc_details.append("✅ Resiko Portfolio Aman (<2%)")
                 else:
                     sc_details.append("⚠️ Resiko Portfolio Agresif")
                 if capital_required <= modal:
                     prob_score += 20
                     sc_details.append("✅ Modal Cukup")
                 else:
                     sc_details.append("❌ Modal Kurang")
            else:
                 # Mode Fixed Capital
                 if implied_risk_pct <= 5.0:
                     prob_score += 20
                     sc_details.append("✅ Resiko per Entry Aman (<5%)")
                 else:
                     sc_details.append("⚠️ Resiko per Entry Besar")
                 prob_score += 20 # Bonus for simplicity
            
            # Badge Color
            if prob_score >= 80:
                score_color = "#10b981"
                score_title = "💎 SNIPER SETUP (High Probability)"
            elif prob_score >= 60:
                score_color = "#f59e0b"
                score_title = "⚖️ STANDARD SETUP"
            else:
                score_color = "#ef4444"
                score_title = "💀 HIGH RISK GAMBLE"

            col_pro1, col_pro2, col_pro3 = st.columns(3)
            with col_pro1:
                st.markdown(f"""
                <div style='background-color: var(--secondary-background-color); padding: 12px; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2); height: 100%;'>
                    <div style='font-size: 0.8rem; font-weight: 600; opacity: 0.9; margin-bottom: 4px;'>🎯 Win Rate Wajib (BE)</div>
                    <div style='font-size: 1.4rem; font-weight: 700; color: #f59e0b;'>{be_winrate:.1f}%</div>
                    <div style='font-size: 0.7rem; opacity: 0.7; margin-top: 4px;'>
                        Hanya butuh menang {be_winrate:.1f}% kali untuk impas.
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_pro2:
                st.markdown(f"""
                <div style='background-color: var(--secondary-background-color); padding: 12px; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2); height: 100%;'>
                    <div style='font-size: 0.8rem; font-weight: 600; opacity: 0.9; margin-bottom: 4px;'>📊 Trade Quality Score</div>
                    <div style='font-size: 1.4rem; font-weight: 700; color: {score_color};'>{prob_score}/100</div>
                    <div style='font-size: 0.7rem; opacity: 0.7; margin-top: 4px;'>
                        {score_title}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_pro3:
                sc_html = "".join([f"<li style='margin-bottom:2px;'>{d}</li>" for d in sc_details])
                st.markdown(f"""
                <div style='background-color: var(--secondary-background-color); padding: 12px; border-radius: 8px; border: 1px solid rgba(128,128,128,0.2); height: 100%; font-size: 0.75rem;'>
                    <ul style='padding-left: 15px; margin: 0;'>
                        {sc_html}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
        else:
            st.toast(f"🚨 Harga realtime {symbol} tidak ditemukan!", icon="🚨")
            st.error(f"Gagal mengambil data harga untuk {symbol}. Pastikan kode saham benar.")

