import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from config import LQ45_SYMBOLS
from utils import format_rupiah, format_percent, format_large_number

@st.cache_data(ttl=600)
def fetch_market_overview():
    # Batch fetch is faster
    tickers = [f"{s}.JK" for s in LQ45_SYMBOLS]
    data_list = []
    
    # yfinance mass download
    try:
        # Download 1 day interval, last 5 days just to be safe getting prev close
        df = yf.download(tickers, period="2d", group_by='ticker', progress=False)
        
        for symbol in LQ45_SYMBOLS:
            try:
                t_sym = f"{symbol}.JK"
                # If dataframe is MultiIndex, access by ticker
                if isinstance(df.columns, pd.MultiIndex):
                     pdf = df[t_sym]
                else:
                     # Single ticker case (rare here since we passed list)
                     pdf = df
                
                if pdf.empty or len(pdf) < 1:
                    continue
                
                # Get last row
                last = pdf.iloc[-1]
                # Get prev row (if available, else difficult)
                if len(pdf) >= 2:
                    prev = pdf.iloc[-2]
                    prev_close = prev['Close']
                else:
                     # Fallback if only 1 day data
                     prev_close = last['Open'] # Approx
                
                close_price = last['Close']
                market_cap = 10000000000 # Placeholder rough weight if fetch fails
                
                # Calculate change
                change = close_price - prev_close
                change_pct = (change / prev_close) * 100 if prev_close else 0
                
                # Try simple market cap weighting:
                # Since we don't have realtime Mcap from bulk history, we use equal size 
                # OR we try to fetch info one by one (TOO SLOW).
                # BETTER APPROACH: Use Volume * Close as a proxy for "Activity Size" or just simple block
                # Let's use Volume * Close = Turnover Value for Heatmap Size
                turnover = last['Volume'] * close_price
                
                data_list.append({
                    "Symbol": symbol,
                    "Price": close_price,
                    "Change": change,
                    "Change %": change_pct,
                    "Volume": last['Volume'],
                    "Turnover": turnover,
                    "Sector": "General" # Ideally mapped
                })
            except:
                continue
                
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return []
        
    return data_list

def market_overview_page():
    st.markdown("""
    <div style='margin-bottom: 24px;'>
        <h2 style='color: var(--text-color); margin-bottom: 8px;'>🔥 Market Heatmap (LQ45)</h2>
        <p style='color: var(--text-color); opacity: 0.8; font-size: 1.1em;'>Gambaran visual performa 45 saham terlikuid (LQ45) hari ini.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Mengambil data pasar..."):
        data = fetch_market_overview()
        
    if not data:
        st.error("Gagal memuat data pasar.")
        return
        
    df = pd.DataFrame(data)
    
    # --- METRICS SUMMARY ---
    total_up = len(df[df['Change %'] > 0])
    total_down = len(df[df['Change %'] < 0])
    total_sideways = len(df[df['Change %'] == 0])
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Saham Naik", f"{total_up}", "Bullish", delta_color="normal")
    m2.metric("Saham Turun", f"{total_down}", "Bearish", delta_color="inverse")
    m3.metric("Sideways", f"{total_sideways}", "Neutral", delta_color="off")
    
    st.markdown("---")
    
    # --- HEATMAP ---
    st.markdown("### 🗺️ Peta Pergerakan Harga")
    st.caption("Ukuran Kotak = Nilai Transaksi (Turnover) | Warna = Persentase Perubahan Harga")
    
    if not df.empty:
        # Create bins for color
        fig = px.treemap(
            df, 
            path=['Symbol'], 
            values='Turnover',
            color='Change %',
            color_continuous_scale=['red', '#ffcccc', 'white', '#ccffcc', 'green'],
            color_continuous_midpoint=0,
            range_color=[-5, 5], # Cap coloring at +/- 5% for better contrast
            custom_data=['Price', 'Change %', 'Volume']
        )
        
        fig.update_traces(
            textposition='middle center',
            textfont_size=20,
            hovertemplate='<b>%{label}</b><br>Price: %{customdata[0]:,.0f}<br>Change: %{customdata[1]:.2f}%<br>Vol: %{customdata[2]:,.0f}'
        )
        
        fig.update_layout(
            margin=dict(t=0, l=0, r=0, b=0),
            height=600,
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    # --- DATA TABLES ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("#### 🚀 Top Gainers")
        top_g = df.sort_values(by="Change %", ascending=False).head(5)
        for _, row in top_g.iterrows():
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between; margin-bottom:8px; padding:8px; background-color:rgba(16,185,129,0.1); border-radius:4px;'>
                <span style='font-weight:bold;'>{row['Symbol']}</span>
                <span style='color:#10b981; font-weight:bold;'>+{row['Change %']:.2f}%</span>
            </div>
            """, unsafe_allow_html=True)
            
    with c2:
        st.markdown("#### 🔻 Top Losers")
        top_l = df.sort_values(by="Change %", ascending=True).head(5)
        for _, row in top_l.iterrows():
             st.markdown(f"""
            <div style='display:flex; justify-content:space-between; margin-bottom:8px; padding:8px; background-color:rgba(239,68,68,0.1); border-radius:4px;'>
                <span style='font-weight:bold;'>{row['Symbol']}</span>
                <span style='color:#ef4444; font-weight:bold;'>{row['Change %']:.2f}%</span>
            </div>
            """, unsafe_allow_html=True)
