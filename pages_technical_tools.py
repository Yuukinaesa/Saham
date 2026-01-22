import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from utils import format_rupiah, format_number

def get_ohlc_data(symbol):
    try:
        ticker = yf.Ticker(f"{symbol}.JK")
        # Get data for last 2 days to ensure we have yesterday's full close
        hist = ticker.history(period="5d")
        if len(hist) < 2:
            return None
        
        # Get LAST COMPLETED day (Yesterday)
        # If today is trading day and market is open, -1 is today (incomplete), -2 is yesterday
        # But safest is just taking the last available data if user wants "Today's Pivot" based on "Yesterday"
        
        last_row = hist.iloc[-1] 
        prev_row = hist.iloc[-2]
        
        return {
            "Open": last_row['Open'],
            "High": last_row['High'],
            "Low": last_row['Low'],
            "Close": last_row['Close'],
            "Prev_High": prev_row['High'],
            "Prev_Low": prev_row['Low'],
            "Prev_Close": prev_row['Close']
        }
    except:
        return None

def calc_classic_pivot(h, l, c):
    p = (h + l + c) / 3
    r1 = 2 * p - l
    s1 = 2 * p - h
    r2 = p + (h - l)
    s2 = p - (h - l)
    r3 = h + 2 * (p - l)
    s3 = l - 2 * (h - p)
    return {"P": p, "R1": r1, "S1": s1, "R2": r2, "S2": s2, "R3": r3, "S3": s3}

def calc_woodie_pivot(h, l, c):
    # Woodie's Pivot Points usually give more weight to the Close price
    # P = (H + L + 2C) / 4
    # Note: Woodie uses the current open for some formulas, but standard var uses HLC
    p = (h + l + 2 * c) / 4
    r1 = 2 * p - l
    s1 = 2 * p - h
    r2 = p + h - l
    s2 = p - h + l
    return {"P": p, "R1": r1, "S1": s1, "R2": r2, "S2": s2}

def calc_camarilla_pivot(h, l, c):
    r = h - l
    r4 = c + r * 1.1 / 2
    s4 = c - r * 1.1 / 2
    r3 = c + r * 1.1 / 4
    s3 = c - r * 1.1 / 4
    r2 = c + r * 1.1 / 6
    s2 = c - r * 1.1 / 6
    r1 = c + r * 1.1 / 12
    s1 = c - r * 1.1 / 12
    return {"R4": r4, "S4": s4, "R3": r3, "S3": s3, "R2": r2, "S2": s2, "R1": r1, "S1": s1}

def calc_fibonacci(high, low, trend="uptrend"):
    diff = high - low
    levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]
    results = {}
    
    if trend == "uptrend":
        # Retracement from High down to Low? No, Uptrend means price moved Low to High.
        # Retracement is going DOWN from High.
        # 0% is High, 100% is Low.
        for level in levels:
            price = high - (diff * level)
            results[f"{level*100:.1f}%"] = price
    else:
        # Downtrend: Price moved High to Low.
        # Retracement is going UP from Low.
        # 0% is Low, 100% is High.
        for level in levels:
            price = low + (diff * level)
            results[f"{level*100:.1f}%"] = price
            
    return results

def technical_tools_page():
    st.markdown("""
    <div style='margin-bottom: 24px;'>
        <h2 style='color: var(--text-color); margin-bottom: 8px;'>📐 Technical Tools</h2>
        <p style='color: var(--text-color); opacity: 0.8; font-size: 1.1em;'>Kalkulator Pivot Point & Fibonacci Retracement untuk menentukan Support/Resistance presisi.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create Tabs including new Confluence Scanner
    tab_pivot, tab_fibo, tab_conf = st.tabs(["🎯 Pivot Point Generator", "🔢 Fibonacci Retracement", "⚡ High Confluence Zone"])

    # --- PIVOT POINT SECTION ---
    with tab_pivot:
        col_type, col_src = st.columns([1, 1])
        with col_type:
            pivot_method = st.selectbox("Metode Pivot", ["Classic", "Woodie", "Camarilla"])
        with col_src:
            input_source = st.radio("Sumber Data", ["Auto (Hari Sebelumnya)", "Manual Input"], horizontal=True)
            
        # Initialize session state for auto data if not exists
        if 'pivot_auto_data' not in st.session_state:
            st.session_state['pivot_auto_data'] = None

        h, l, c = 0.0, 0.0, 0.0
        
        if input_source == "Auto (Hari Sebelumnya)":
            symbol = st.text_input("Kode Saham (Contoh: BBRI)", value="BBRI").upper()
            if st.button("Ambil Data Pivot"):
                 with st.spinner(f"Mengambil data {symbol}..."):
                    data = get_ohlc_data(symbol)
                    if data:
                        # Store in session state
                        st.session_state['pivot_auto_data'] = data
                        st.success("Data berhasil diambil!")
                    else:
                        st.error("Data tidak ditemukan.")
            
            # Retrieve from session state if available
            if st.session_state['pivot_auto_data']:
                data = st.session_state['pivot_auto_data']
                h = data['Prev_High']
                l = data['Prev_Low']
                c = data['Prev_Close']
                st.info(f"Menggunakan data: High={format_number(h,0)}, Low={format_number(l,0)}, Close={format_number(c,0)}")

        else:
            c1, c2, c3 = st.columns(3)
            with c1:
                h = st.number_input("High", min_value=1.0, value=1000.0, step=5.0)
            with c2:
                l = st.number_input("Low", min_value=1.0, value=900.0, step=5.0)
            with c3:
                c = st.number_input("Close", min_value=1.0, value=950.0, step=5.0)
        
        if h > 0 and l > 0 and c > 0:
            if st.button("Hitung Pivot", type="primary"):
                st.markdown("---")
                results = {}
                if pivot_method == "Classic":
                    results = calc_classic_pivot(h, l, c)
                elif pivot_method == "Woodie":
                    results = calc_woodie_pivot(h, l, c)
                elif pivot_method == "Camarilla":
                    results = calc_camarilla_pivot(h, l, c)
                
                # Store pivot results in session state for Confluence tab usage
                st.session_state['last_pivot_results'] = results

                # Display Results
                st.markdown(f"### Hasil: {pivot_method} Pivot")
                
                # S & R Cards
                col_res1, col_res2 = st.columns(2)
                
                sorted_keys = sorted(results.keys(), key=lambda x: results[x], reverse=True)
                
                with col_res1:
                    st.markdown("#### 🛡️ Resistance (Sell Area)")
                    for k in sorted_keys:
                        if "R" in k:
                            st.markdown(f"**{k}:** {format_rupiah(results[k])}")
                            
                with col_res2:
                    st.markdown("#### 🧺 Support (Buy Area)")
                    for k in sorted_keys:
                        if "S" in k:
                            st.markdown(f"**{k}:** {format_rupiah(results[k])}")
                            
                if "P" in results:
                    st.markdown(f"""
                    <div style='text-align: center; margin-top: 20px; padding: 15px; background-color: rgba(37, 99, 235, 0.1); border-radius: 8px;'>
                        <h4 style='margin:0; color: #3b82f6;'>Pivot Point (Central)</h4>
                        <h2 style='margin: 5px 0 0 0; color: #3b82f6;'>{format_rupiah(results['P'])}</h2>
                    </div>
                    """, unsafe_allow_html=True)

    # --- FIBONACCI SECTION ---
    with tab_fibo:
        st.markdown("Hitung level retracement dari swing High ke Low (downtrend) atau Low ke High (uptrend).")

        col_fib_trend, col_fib_src = st.columns([1, 1])
        with col_fib_trend:
            f_trend = st.radio("Arah Tren Utama (Swing)", ["Uptrend (Low → High)", "Downtrend (High → Low)"], horizontal=True)
            trend_code = "uptrend" if "Uptrend" in f_trend else "downtrend"
        with col_fib_src:
             fib_source = st.radio("Sumber Data Fibonacci", ["Auto (1 Bulan Terakhir)", "Manual Input"], horizontal=True)

        # Initialize session state for fibo auto data
        if 'fibo_auto_data' not in st.session_state:
            st.session_state['fibo_auto_data'] = None

        swing_low_val = 900.0
        swing_high_val = 1100.0

        if fib_source == "Auto (1 Bulan Terakhir)":
             symbol_fib = st.text_input("Kode Saham (Fibo)", value="BBRI").upper()
             if st.button("Ambil Data Swing"):
                 with st.spinner(f"Mencari Swing High/Low {symbol_fib}..."):
                     try:
                         # Fetch 1 Month Data
                         t = yf.Ticker(f"{symbol_fib}.JK")
                         h = t.history(period="1mo")
                         if not h.empty:
                             # Find Max High and Min Low in period
                             period_high = float(h['High'].max())
                             period_low = float(h['Low'].min())
                             st.session_state['fibo_auto_data'] = {'high': period_high, 'low': period_low}
                             st.success("Data Swing ditemukan!")
                         else:
                             st.error("Data history kosong.")
                     except Exception as e:
                         st.error(f"Gagal mengambil data: {e}")
            
             if st.session_state['fibo_auto_data']:
                 d = st.session_state['fibo_auto_data']
                 swing_high_val = d['high']
                 swing_low_val = d['low']
                 st.info(f"Auto Swing: Low={format_rupiah(swing_low_val)} | High={format_rupiah(swing_high_val)}")

        fc1, fc2 = st.columns(2)
        with fc1:
            swing_low = st.number_input("Swing Low Price", min_value=1.0, value=float(swing_low_val), step=5.0)
        with fc2:
            swing_high = st.number_input("Swing High Price", min_value=1.0, value=float(swing_high_val), step=5.0)
            
        if st.button("Hitung Fibonacci"):
            if swing_high <= swing_low:
                st.error("High harus lebih besar dari Low.")
            else:
                fib_res = calc_fibonacci(swing_high, swing_low, trend_code)
                
                # Store for confluence
                st.session_state['last_fibo_results'] = fib_res
                
                # --- CHART VISUALIZATION (Realtime Context) ---
                # Check if we have a symbol context from the Auto mode or Session State
                # We need to access the symbol variable. It was defined in the 'if fib_source == "Auto..."' block.
                # To make it robust, we check if 'fibo_symbol_context' exists in session state or if we can pass it.
                # Since we can't easily access local vars from previous block here without refactoring, 
                # let's assume valid symbol if we are in Auto mode.
                
                chart_drawn = False
                if fib_source == "Auto (1 Bulan Terakhir)" and 'symbol_fib' in locals():
                    st.markdown("### 📉 Realtime Chart Analysis (Multi-Indicator)")
                    with st.spinner("Menganalisa Teknikal..."):
                        try:
                            # Fetch data for chart (6 months for MA200)
                            chart_ticker = yf.Ticker(f"{symbol_fib}.JK")
                            df_chart = chart_ticker.history(period="6mo")
                            
                            if not df_chart.empty:
                                # --- TECHNICAL CALCULATION ---
                                # 1. RSI (14)
                                delta = df_chart['Close'].diff()
                                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                                rs = gain / loss
                                df_chart['RSI'] = 100 - (100 / (1 + rs))
                                current_rsi = df_chart['RSI'].iloc[-1]
                                
                                # 2. Moving Averages
                                df_chart['MA50'] = df_chart['Close'].rolling(window=50).mean()
                                df_chart['MA200'] = df_chart['Close'].rolling(window=200).mean()
                                current_close = df_chart['Close'].iloc[-1]
                                ma50_val = df_chart['MA50'].iloc[-1]
                                ma200_val = df_chart['MA200'].iloc[-1]

                                # 3. Trend Analysis
                                trend_status = "Sideways/Unknown"
                                if current_close > ma50_val and current_close > ma200_val:
                                    trend_status = "BULLISH (Strong Uptrend)"
                                elif current_close < ma50_val and current_close < ma200_val:
                                    trend_status = "BEARISH (Strong Downtrend)"
                                elif current_close > ma200_val and current_close < ma50_val:
                                    trend_status = "Correction in Uptrend"
                                elif current_close < ma200_val and current_close > ma50_val:
                                    trend_status = "Rebound in Downtrend"
                                    
                                # 4. RSI Status
                                rsi_status = "Neutral"
                                rsi_color = "white"
                                if current_rsi >= 70:
                                    rsi_status = "Overbought (Jenuh Beli)"
                                    rsi_color = "#ef4444"
                                elif current_rsi <= 30:
                                    rsi_status = "Oversold (Jenuh Jual)"
                                    rsi_color = "#10b981"
                                    
                                # --- DISPLAY TECHNICAL CARD ---
                                st.info(f"💡 **Technical Summary:** {trend_status}")
                                tc1, tc2, tc3 = st.columns(3)
                                tc1.metric("RSI (14)", f"{current_rsi:.2f}", rsi_status)
                                tc2.metric("MA 50", f"{format_number(ma50_val,0)}", f"{current_close - ma50_val:.0f} vs Price")
                                tc3.metric("MA 200", f"{format_number(ma200_val,0)}", f"{current_close - ma200_val:.0f} vs Price")
                                
                                # --- PLOTTING ---
                                from plotly.subplots import make_subplots
                                fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                                    vertical_spacing=0.05, row_heights=[0.7, 0.3])
                                
                                # Candlestick (Row 1)
                                fig.add_trace(go.Candlestick(
                                    x=df_chart.index,
                                    open=df_chart['Open'], high=df_chart['High'],
                                    low=df_chart['Low'], close=df_chart['Close'],
                                    name='Price'
                                ), row=1, col=1)
                                
                                # MA Lines (Row 1)
                                fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['MA50'], line=dict(color='cyan', width=1), name='MA 50'), row=1, col=1)
                                fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['MA200'], line=dict(color='orange', width=1), name='MA 200'), row=1, col=1)

                                # RSI (Row 2)
                                fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['RSI'], line=dict(color='purple', width=2), name='RSI'), row=2, col=1)
                                fig.add_hline(y=70, line_dash="dot", line_color="red", row=2, col=1)
                                fig.add_hline(y=30, line_dash="dot", line_color="green", row=2, col=1)
                                
                                # 2. Fibonacci Lines (Overlay on Row 1)
                                for ratio_str, price in fib_res.items():
                                    line_color = 'gray'
                                    dash_style = 'dot'
                                    width = 1
                                    
                                    if ratio_str in ['0.0%', '100.0%']:
                                        line_color = 'white'
                                        width = 1
                                        dash_style = 'solid'
                                    elif ratio_str in ['61.8%', '50.0%']:
                                        line_color = '#f59e0b'
                                        width = 2
                                        dash_style = 'solid'
                                        
                                    fig.add_hline(
                                        y=price, 
                                        line_width=width, line_dash=dash_style, line_color=line_color,
                                        annotation_text=f"Fibo {ratio_str}", annotation_position="top right",
                                        row=1, col=1
                                    )

                                # 3. Golden Pocket Update (0.618 - 0.65)
                                if '61.8%' in fib_res:
                                    gp_price_1 = fib_res['61.8%']
                                    diff = swing_high - swing_low
                                    if trend_code == "uptrend":
                                        gp_price_2 = swing_high - (diff * 0.65)
                                    else:
                                        gp_price_2 = swing_low + (diff * 0.65)
                                        
                                    fig.add_hrect(
                                        y0=gp_price_1, y1=gp_price_2,
                                        fillcolor="#f59e0b", opacity=0.15,
                                        layer="below", line_width=0,
                                        annotation_text="🏆 GOLDEN POCKET", annotation_position="left",
                                        row=1, col=1
                                    )

                                fig.update_layout(
                                    height=700,
                                    title=f"Advanced Setup: {symbol_fib} (Fibo + RSI + Trend)",
                                    yaxis_title='Harga (Rp)',
                                    xaxis_rangeslider_visible=False,
                                    template="plotly_dark",
                                    margin=dict(l=0, r=0, t=40, b=0),
                                    showlegend=True
                                )
                                fig.update_yaxes(title_text="RSI", range=[0, 100], row=2, col=1)
                                
                                st.plotly_chart(fig, use_container_width=True)
                                chart_drawn = True
                        except Exception as e:
                            st.warning(f"Gagal memuat chart: {e}")

                if not chart_drawn:
                    st.caption("ℹ️ Gunakan Mode 'Auto' dan masukkan Kode Saham untuk melihat visualisasi Chart.")

                st.markdown("### 🔢 Fibonacci Levels")
                
                # Display most important golden ratios
                golden_ratios = ['61.8%', '50.0%']
                golden_pocket = ['61.8%', '65.0%'] # Added 0.65 for Golden Pocket range
                
                # Custom order: Key levels first
                key_levels = ['61.8%', '50.0%', '38.2%', '23.6%', '78.6%']
                
                # Render Golden Pocket Special Card
                if '61.8%' in fib_res:
                    gp_low = fib_res.get('61.8%', 0)
                    # Calculate 0.65 level manually for Golden Pocket
                    diff = swing_high - swing_low
                    if trend_code == "uptrend":
                        # Retracement going down
                        p_65 = swing_high - (diff * 0.65)
                    else:
                        p_65 = swing_low + (diff * 0.65)
                    
                    st.markdown(f"""
                    <div style='background: linear-gradient(90deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.2) 100%); 
                                padding: 15px; border-radius: 8px; border-left: 5px solid #f59e0b; margin-bottom: 20px;'>
                        <h4 style='margin:0; color: #f59e0b;'>🏆 Golden Pocket Area (0.618 - 0.65)</h4>
                        <p style='margin:0; opacity:0.8; font-size:0.9rem;'>Area probabilitas pembalikan arah (reversal) tertinggi. Incar entry di zona ini.</p>
                        <div style='display:flex; gap:20px; margin-top:10px;'>
                            <div><strong>0.618:</strong> {format_rupiah(gp_low)}</div>
                            <div>- s/d -</div>
                            <div><strong>0.65:</strong> {format_rupiah(p_65)}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("#### Detail Level Lainnya")
                display_cols = st.columns(3)
                idx = 0
                for ratio, price in fib_res.items():
                    # Skip printing 0.618 and 0.65 here if we want, or just print all standardized
                    with display_cols[idx % 3]:
                        if ratio in ['61.8%', '50.0%']:
                            color = "#10b981" 
                            bg = "rgba(16, 185, 129, 0.1)"
                            extra_label = " ⭐ Key Level"
                        else:
                            color = "var(--text-color)"
                            bg = "var(--secondary-background-color)"
                            extra_label = ""
                            
                        st.markdown(f"""
                        <div style='background-color: {bg}; padding: 10px; border-radius: 6px; margin-bottom: 10px; border-left: 3px solid {color};'>
                            <div style='font-size: 0.8rem; opacity: 0.7;'>Level {ratio}{extra_label}</div>
                            <div style='font-weight: 700; font-size: 1.1rem; color: {color};'>{format_rupiah(price)}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    idx += 1
    # --- CONFLUENCE SECTION ---
    with tab_conf:
        st.markdown("#### ⚡ High Probability Confluence Zone")
        st.info("Fitur ini mencari area di mana Level Pivot dan Level Fibonacci saling berdekatan (Overlap). Area ini dianggap sebagai Support/Resistance TERKUAT.")
        
        if 'last_pivot_results' in st.session_state and 'last_fibo_results' in st.session_state:
            pivots = st.session_state['last_pivot_results']
            fibos = st.session_state['last_fibo_results']
            
            confluences = []
            threshold = 2.0 # % difference allowed to be considered "Overlap"
            
            for p_name, p_val in pivots.items():
                for f_name, f_val in fibos.items():
                    # Calculate percentage diff
                    if f_val > 0:
                        diff_pct = abs(p_val - f_val) / f_val * 100
                        if diff_pct <= threshold:
                            confluences.append({
                                'Level 1': f"Pivot {p_name}",
                                'Price 1': p_val,
                                'Level 2': f"Fibo {f_name}",
                                'Price 2': f_val,
                                'Diff': diff_pct
                            })
            
            if confluences:
                st.success(f"Ditemukan {len(confluences)} Zona Konfluensi!")
                # Sort by weakest diff (strongest match)
                confluences.sort(key=lambda x: x['Diff'])
                
                for c in confluences:
                    avg_price = (c['Price 1'] + c['Price 2']) / 2
                    st.markdown(f"""
                    <div style='background-color: rgba(37, 99, 235, 0.1); padding: 15px; border-radius: 8px; border: 1px solid #3b82f6; margin-bottom: 15px;'>
                        <h4 style='margin:0; color: #3b82f6;'>🎯 STRONG ZONE: {format_rupiah(avg_price)}</h4>
                        <p style='margin:5px 0 0 0; font-size:0.9rem;'>
                            Pertemuan antara <b>{c['Level 1']}</b> ({format_rupiah(c['Price 1'])}) dan <b>{c['Level 2']}</b> ({format_rupiah(c['Price 2'])}).
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("Belum ada area konfluensi yang kuat (jarak < 2%) ditemukan antara data Pivot dan Fibonacci saat ini.")
                
        else:
            st.warning("⚠️ Silakan hitung **Pivot Point** dan **Fibonacci** terlebih dahulu di tab sebelah kiri agar data tersedia.")
