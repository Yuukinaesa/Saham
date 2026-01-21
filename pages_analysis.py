import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
from utils import format_rupiah, format_percent, format_large_number, get_tick_size, round_price_to_tick

# Plotly Imports
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

import requests
from bs4 import BeautifulSoup
import re
import time
import feedparser

def get_kabarbursa_news(symbol):
    """Scrape KabarBursa via Google RSS using feedparser"""
    try:
        url = f"https://news.google.com/rss/search?q={symbol}+site:kabarbursa.com&hl=id-ID&gl=ID&ceid=ID:id"
        feed = feedparser.parse(url)
        news_items = []
        for entry in feed.entries[:5]:
            try:
                news_items.append({
                    'title': entry.get('title', 'No Title'),
                    'link': entry.get('link', '#'),
                    'publisher': 'KabarBursa',
                    'providerPublishTime': 0
                })
            except:
                continue
        return news_items
    except:
        pass
    return []

def get_kontan_news(symbol):
    """Scrape Kontan via Google RSS using feedparser"""
    try:
        url = f"https://news.google.com/rss/search?q={symbol}+site:kontan.co.id&hl=id-ID&gl=ID&ceid=ID:id"
        feed = feedparser.parse(url)
        news_items = []
        for entry in feed.entries[:5]:
            try:
                news_items.append({
                    'title': entry.get('title', 'No Title'),
                    'link': entry.get('link', '#'),
                    'publisher': 'Kontan',
                    'providerPublishTime': 0
                })
            except:
                continue
        return news_items
    except:
        pass
    return []

def get_cnbc_news(symbol):
    """Scrape CNBC via Google RSS using feedparser"""
    try:
        url = f"https://news.google.com/rss/search?q={symbol}+site:cnbcindonesia.com&hl=id-ID&gl=ID&ceid=ID:id"
        feed = feedparser.parse(url)
        news_items = []
        for entry in feed.entries[:5]:
            try:
                news_items.append({
                    'title': entry.get('title', 'No Title'),
                    'link': entry.get('link', '#'),
                    'publisher': 'CNBC Indonesia',
                    'providerPublishTime': 0
                })
            except:
                continue
        return news_items
    except:
        pass
    return []

def get_google_news_rss(symbol):
    """General Google News using feedparser with multiple queries"""
    news_items = []
    seen_links = set()
    
    # Reduced search terms to avoid timeouts
    search_terms = [
        f"{symbol}+saham",
        f"{symbol}+Indonesia",
        f"PT+{symbol}",
    ]
    
    for query in search_terms:
        try:
            url = f"https://news.google.com/rss/search?q={query}&hl=id-ID&gl=ID&ceid=ID:id"
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:10]:
                try:
                    link = entry.get('link', '#')
                    if link not in seen_links:
                        seen_links.add(link)
                        news_items.append({
                            'title': entry.get('title', 'No Title'),
                            'link': link,
                            'publisher': entry.get('source', {}).get('title', 'Google News'),
                            'providerPublishTime': 0
                        })
                except:
                    continue
                    
            if len(news_items) >= 20:
                break
                
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        except:
            continue
    
    return news_items

def get_bisnis_news(symbol):
    """Scrape Bisnis.com via Google RSS"""
    try:
        url = f"https://news.google.com/rss/search?q={symbol}+site:bisnis.com&hl=id-ID&gl=ID&ceid=ID:id"
        feed = feedparser.parse(url)
        news_items = []
        for entry in feed.entries[:7]:
            try:
                news_items.append({
                    'title': entry.get('title', 'No Title'),
                    'link': entry.get('link', '#'),
                    'publisher': 'Bisnis.com',
                    'providerPublishTime': 0
                })
            except:
                continue
        return news_items
    except:
        pass
    return []

def get_detik_finance_news(symbol):
    """Scrape Detik via Google RSS"""
    try:
        url = f"https://news.google.com/rss/search?q={symbol}+site:detik.com&hl=id-ID&gl=ID&ceid=ID:id"
        feed = feedparser.parse(url)
        news_items = []
        for entry in feed.entries[:7]:
            try:
                news_items.append({
                    'title': entry.get('title', 'No Title'),
                    'link': entry.get('link', '#'),
                    'publisher': 'Detik Finance',
                    'providerPublishTime': 0
                })
            except:
                continue
        return news_items
    except:
        pass
    return []

def get_idx_channel_news(symbol):
    """Scrape IDX via Google RSS"""
    try:
        url = f"https://news.google.com/rss/search?q={symbol}+site:idx.co.id&hl=id-ID&gl=ID&ceid=ID:id"
        feed = feedparser.parse(url)
        news_items = []
        for entry in feed.entries[:5]:
            try:
                news_items.append({
                    'title': entry.get('title', 'No Title'),
                    'link': entry.get('link', '#'),
                    'publisher': 'IDX Channel',
                    'providerPublishTime': 0
                })
            except:
                continue
        return news_items
    except:
        pass
    return []

def get_investing_indonesia_news(symbol):
    """Scrape Investing.com via Google RSS"""
    try:
        url = f"https://news.google.com/rss/search?q={symbol}+site:id.investing.com&hl=id-ID&gl=ID&ceid=ID:id"
        feed = feedparser.parse(url)
        news_items = []
        for entry in feed.entries[:5]:
            try:
                news_items.append({
                    'title': entry.get('title', 'No Title'),
                    'link': entry.get('link', '#'),
                    'publisher': 'Investing.com ID',
                    'providerPublishTime': 0
                })
            except:
                continue
        return news_items
    except:
        pass
    return []


def analyze_sentiment(news_list):
    """
    Analyze sentiment from news titles using advanced keyword scoring.
    Returns detailed breakdown of positive/negative news.
    """
    if not news_list:
        return {
            "score": 0, 
            "label": "NEUTRAL", 
            "summary": "Tidak ada data berita.",
            "positive_news": [],
            "negative_news": [],
            "neutral_news": []
        }
        
    # Expanded and improved keyword lists
    pos_keywords = [
        'naik', 'melonjak', 'reli', 'menguat', 'tumbuh', 'growth', 'positif', 
        'dividen', 'buy', 'beli', 'akuisisi', 'tertinggi', 'rebound', 'proyek', 
        'kerjasama', 'profit', 'laba', 'surplus', 'bullish', 'ekspansi', 
        'berkembang', 'meningkat', 'kenaikan', 'prestasi', 'inovasi', 'cemerlang'
    ]
    
    neg_keywords = [
        'turun', 'merosot', 'anjlok', 'jatuh', 'rugi', 'loss', 'negatif', 
        'utang', 'debt', 'sell', 'jual', 'gugat', 'bangkrut', 'pkpu', 
        'suspend', 'bearish', 'deficit', 'weak', 'lemah', 'penurunan', 
        'gagal', 'kerugian', 'ambles', 'terpuruk', 'koreksi', 'nyangkut',
        'tertahan', 'tertekan', 'melemah'
    ]
    
    score = 0
    positive_news = []
    negative_news = []
    neutral_news = []
    
    for item in news_list:
        # Extract title properly from mixed format
        title = ""
        if isinstance(item, dict):
            content = item.get('content', item)
            title = content.get('title', item.get('title', ""))
            
        if not title: 
            continue
            
        title_lower = title.lower()
        
        # Calculate sentiment for this specific news
        news_sentiment = 0
        matched_pos = []
        matched_neg = []
        
        for word in pos_keywords:
            if word in title_lower:
                news_sentiment += 1
                matched_pos.append(word)
        
        for word in neg_keywords:
            if word in title_lower:
                news_sentiment -= 1
                matched_neg.append(word)
        
        # Categorize this news
        news_item_tagged = {
            'title': title,
            'link': item.get('link', '#'),
            'publisher': item.get('publisher', 'Unknown'),
            'sentiment_score': news_sentiment,
            'positive_keywords': matched_pos,
            'negative_keywords': matched_neg
        }
        
        if news_sentiment > 0:
            positive_news.append(news_item_tagged)
            score += news_sentiment
        elif news_sentiment < 0:
            negative_news.append(news_item_tagged)
            score += news_sentiment  # Already negative
        else:
            neutral_news.append(news_item_tagged)
            
    # Normalize label with stricter thresholds
    total_news = len(news_list)
    if total_news > 0:
        avg_sentiment = score / total_news
        
        if avg_sentiment > 0.5:
            label = "VERY POSITIVE"
        elif avg_sentiment > 0.1:
            label = "POSITIVE"
        elif avg_sentiment < -0.5:
            label = "VERY NEGATIVE"
        elif avg_sentiment < -0.1:
            label = "NEGATIVE"
        else:
            label = "NEUTRAL"
    else:
        label = "NEUTRAL"
    
    summary = f"""
    📊 **{label}** (Skor Total: {score})
    ✅ Berita Positif: {len(positive_news)} | ⚠️ Negatif: {len(negative_news)} | ⚪ Netral: {len(neutral_news)}
    """
    
    return {
        "score": score,
        "label": label,
        "summary": summary.strip(),
        "positive_news": positive_news,
        "negative_news": negative_news,
        "neutral_news": neutral_news
    }

def analyze_fundamental_quality(info):
    """
    Score fundamental quality based on key metrics.
    """
    if not info:
        return {"score": 0, "label": "UNKNOWN", "reason": "Data tidak tersedia"}
        
    score = 0
    reasons = []
    
    # 1. PER (Valuation)
    pe = info.get('trailingPE', 0)
    if 0 < pe < 15:
        score += 2
        reasons.append("PER Murah (<15x)")
    elif 15 <= pe < 25:
        score += 1
        reasons.append("PER Wajar")
    elif pe >= 25:
        score -= 1
        reasons.append("PER Mahal (>25x)")
    elif pe < 0:
        score -= 2
        reasons.append("Perusahaan Rugi (PER Negatif)")
        
    # 2. PBV (Valuation)
    pbv = info.get('priceToBook', 0)
    if 0 < pbv < 1:
        score += 2
        reasons.append("Undervalued (PBV < 1)")
    elif 1 <= pbv <= 3:
        score += 1
        reasons.append("PBV Wajar")
    elif pbv > 5:
        score -= 1
        reasons.append("PBV Mahal (>5x)")
        
    # 3. ROE (Profitability)
    roe = info.get('returnOnEquity', 0)
    if roe > 0.15: # 15%
        score += 2
        reasons.append("Profitabilitas Tinggi (ROE > 15%)")
    elif roe > 0.08:
        score += 1
        reasons.append("Profitabilitas Cukup")
    elif roe < 0:
        score -= 2
        reasons.append("ROE Negatif")
        
    # 4. DER (Leverage) - optional, yfinance often misses this, use DebtToEquity if avail
    der = info.get('debtToEquity', 0)
    if der and der < 100: # < 1x
        score += 1
        reasons.append("Hutang Sehat (DER < 1x)")
    elif der > 200:
        score -= 1
        reasons.append("Hutang Tinggi (DER > 2x)")

    label = "NEUTRAL"
    if score >= 4: label = "EXCELLENT"
    elif score >= 2: label = "GOOD"
    elif score <= -2: label = "POOR"
    elif score < 0: label = "WEAK"
    
    return {
        "score": score,
        "label": label,
        "reasons": reasons
    }

def get_stock_data(symbol):
    """
    Mengambil data lengkap saham: History, Info Fundamental, News (Multi-Source), dan Analisa.
    """
    try:
        ticker_symbol = f"{symbol}.JK" if not symbol.endswith(".JK") and not symbol.startswith("^") else symbol
        
        # 1. Fetch Ticker Object
        ticker = yf.Ticker(ticker_symbol)
        
        # 2. Fetch History (5 Tahun terakhir untuk teknikal & seasonality)
        history = ticker.history(period="5y")
        
        # 3. Fetch Info (Fundamental)
        info = {}
        try:
            info = ticker.info
        except:
            info = {}
            
        # 5. Fetch Analyst Recommendations
        recommendations = None
        try:
            recommendations = ticker.recommendations
        except:
            pass

        # 4. Fetch News (Combined Sources - Maximum Coverage)
        news = []
        try:
            # Source A: yFinance (Original API)
            yf_news = ticker.news
            if yf_news:
                news.extend(yf_news)
                
            # Source B: Google News General (Multi-query)
            g_news = get_google_news_rss(symbol)
            if g_news:
                news.extend(g_news)
                
            # Source C: KabarBursa
            kb_news = get_kabarbursa_news(symbol)
            if kb_news:
                news.extend(kb_news)
                
            # Source D: Kontan
            kt_news = get_kontan_news(symbol)
            if kt_news:
                news.extend(kt_news)
                
            # Source E: CNBC Indonesia
            cnbc_news = get_cnbc_news(symbol)
            if cnbc_news:
                news.extend(cnbc_news)
                
            # Source F: Bisnis.com (NEW)
            bisnis_news = get_bisnis_news(symbol)
            if bisnis_news:
                news.extend(bisnis_news)
                
            # Source G: Detik Finance (NEW)
            detik_news = get_detik_finance_news(symbol)
            if detik_news:
                news.extend(detik_news)
                
            # Source H: IDX Channel (NEW)
            idx_news = get_idx_channel_news(symbol)
            if idx_news:
                news.extend(idx_news)
                
            # Source I: Investing.com Indonesia (NEW)
            inv_news = get_investing_indonesia_news(symbol)
            if inv_news:
                news.extend(inv_news)
                
        except Exception as e:
            pass
            
        current_price = history['Close'].iloc[-1] if not history.empty else 0
        
        # Run Automated Analysis
        sentiment = analyze_sentiment(news)
        fundamental = analyze_fundamental_quality(info)
        
        return {
            "history": history,
            "info": info,
            "news": news,
            "recommendations": recommendations,
            "current_price": current_price,
            "ticker": ticker,
            "analysis": {
                "sentiment": sentiment,
                "fundamental": fundamental
            }
        }
    except Exception as e:
        st.error(f"Error mengambil data: {e}")
        return None

def get_technical_signals(history):
    """
    Calculate ADVANCED technical signals based on history.
    Includes: RSI, MACD, EMA Trend, and Volume Analysis.
    """
    if len(history) < 50:
        return {"signal": "NEUTRAL", "reason": ["Data historis kurang cukup untuk analisa akurat."]}
    
    # Data Preparation
    close = history['Close']
    
    # 1. Moving Averages (Trend)
    ema20 = close.ewm(span=20, adjust=False).mean().iloc[-1]
    ma50 = close.rolling(window=50).mean().iloc[-1]
    ma200 = close.rolling(window=200).mean().iloc[-1]
    current = close.iloc[-1]
    
    # 2. RSI (Momentum)
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs)).iloc[-1]
    
    # 3. MACD (Trend Reversal & Momentum)
    exp12 = close.ewm(span=12, adjust=False).mean()
    exp26 = close.ewm(span=26, adjust=False).mean()
    macd = exp12 - exp26
    signal_line = macd.ewm(span=9, adjust=False).mean()
    
    macd_val = macd.iloc[-1]
    signal_val = signal_line.iloc[-1]
    
    # Scoring Logic (Weighted)
    score = 0
    reasons = []
    
    # A. Trend Filter (Long Term)
    if current < ma200:
        score -= 2
        reasons.append("Bearish Jangka Panjang (Harga < MA200)")
    else:
        score += 1
        reasons.append("Bullish Jangka Panjang (Harga > MA200)")

    # B. Trend (Short Term)
    if current > ema20:
        score += 1
        reasons.append("Bullish Jangka Pendek (Harga > EMA20)")
    else:
        score -= 1
        reasons.append("Bearish Jangka Pendek (Harga < EMA20)")
        
    # C. MACD Code
    if macd_val > signal_val:
        score += 1
        reasons.append("MACD Bullish Crossover (Momentum Positif)")
    else:
        score -= 1
        reasons.append("MACD Bearish Crossover (Momentum Negatif)")
        
    # D. RSI (Overbought/Oversold Filter)
    if rsi < 30:
        score += 2
        reasons.append(f"RSI Oversold ({rsi:.1f}) - Potensi Rebound Kuat")
    elif rsi > 70:
        score -= 2
        reasons.append(f"RSI Overbought ({rsi:.1f}) - Rawan Koreksi")
    elif 45 <= rsi <= 55:
        reasons.append(f"RSI Netral ({rsi:.1f})")
    
    # Final Decision
    # Max Score approx +5, Min approx -6
    
    if score >= 3:
        return {"signal": "STRONG BUY", "color": "green", "reason": reasons}
    elif score >= 1:
        return {"signal": "BUY", "color": "lightgreen", "reason": reasons}
    elif score <= -3:
        return {"signal": "STRONG SELL", "color": "red", "reason": reasons}
    elif score <= -1:
        return {"signal": "SELL", "color": "orange", "reason": reasons}
    else:
        return {"signal": "NEUTRAL / WAIT", "color": "gray", "reason": reasons}

def render_recommendations(rec_df, history):
    st.markdown("### ⭐ Rekomendasi & Sinyal Multi-Timeframe")
    
    # Generate Multi-Timeframe Signals
    timeframes = get_multi_timeframe_signals(history)
    
    # Display as visually rich grid
    st.markdown("#### 🤖 Sinyal Teknikal (Bot) per Horizon Waktu")
    
    # First Row (Short-Term)
    c1, c2, c3 = st.columns(3)
    cols_row1 = [c1, c2, c3]
    for i, tf in enumerate(timeframes[:3]):
        with cols_row1[i]:
            render_signal_card(tf['label'], tf['signal'], tf['color'], tf['reason'])
    
    # Second Row (Medium-Long Term)
    c4, c5, c6 = st.columns(3)
    cols_row2 = [c4, c5, c6]
    for i, tf in enumerate(timeframes[3:6]):
        with cols_row2[i]:
            render_signal_card(tf['label'], tf['signal'], tf['color'], tf['reason'])
            
    st.markdown("---")
    
    # Analyst Recommendations (Original)
    st.markdown("#### 💼 Konsensus Analis (Institutional)")
    if rec_df is not None and not rec_df.empty:
        try:
            # Clean up DataFrame
            df_display = rec_df.tail(4).copy() # Take last 4 periods
            
            # Map periods if they exist in a column or index
            # yfinance often puts period in 'period' column: '0m', '-1m', '-2m'
            
            period_map = {
                '0m': 'Bulan Ini',
                '-1m': '1 Bulan Lalu',
                '-2m': '2 Bulan Lalu',
                '-3m': '3 Bulan Lalu'
            }
            
            if 'period' in df_display.columns:
                df_display['period'] = df_display['period'].map(period_map).fillna(df_display['period'])
            
            # Rename columns
            col_map = {
                'period': 'Periode',
                'strongBuy': 'Strong Buy',
                'buy': 'Buy',
                'hold': 'Hold',
                'sell': 'Sell',
                'strongSell': 'Strong Sell'
            }
            df_display = df_display.rename(columns=col_map)
            
            # Display cleanly
            st.dataframe(
                df_display.set_index('Periode') if 'Periode' in df_display.columns else df_display, 
                use_container_width=True
            )
        except Exception as e:
            st.dataframe(rec_df.tail(5), use_container_width=True)
    else:
        st.warning("Tidak ada data rekomendasi analis institusi untuk saham ini.")

def render_signal_card(label, signal, color, reason):
    """Helper to render a single signal card."""
    color_map = {
        "green": "#10b981", "lightgreen": "#34d399", 
        "gray": "#9ca3af", "orange": "#f59e0b", "red": "#ef4444"
    }
    hex_color = color_map.get(color, "#9ca3af")
    
    st.markdown(f"""
    <div style='text-align: center; padding: 15px; background-color: {hex_color}15; border: 1px solid {hex_color}; border-radius: 10px; margin-bottom: 10px;'>
        <p style='margin:0; font-size: 12px; opacity: 0.8;'>{label}</p>
        <h3 style='color: {hex_color}; margin: 5px 0;'>{signal}</h3>
        <p style='margin:0; font-size: 11px; opacity: 0.7;'>{reason}</p>
    </div>
    """, unsafe_allow_html=True)

def get_multi_timeframe_signals(history):
    """
    PROFESSIONAL-GRADE Multi-Timeframe Signal Generator.
    Based on Institutional Trading Rules:
    1. Confluence Required (Trend + Momentum + Volume must align)
    2. ADX Trend Strength Filter (No trading in sideways)
    3. Volatility Filter (ATR-based)
    4. Strict RSI zones (<25 oversold, >75 overbought)
    5. Volume Spike Confirmation
    """
    results = []
    close = history['Close']
    high = history['High']
    low = history['Low']
    volume = history['Volume']
    current = close.iloc[-1]
    n = len(close)
    
    # === HELPER FUNCTIONS ===
    def calc_rsi(series, window=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi_val = (100 - (100 / (1 + rs))).iloc[-1]
        return rsi_val if not pd.isna(rsi_val) else 50
    
    def calc_atr(high, low, close, window=14):
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=window).mean().iloc[-1]
    
    def calc_adx(high, low, close, window=14):
        # Simplified ADX
        plus_dm = high.diff()
        minus_dm = -low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        atr = tr.rolling(window=window).mean()
        plus_di = 100 * (plus_dm.rolling(window=window).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=window).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 0.0001)
        adx = dx.rolling(window=window).mean().iloc[-1]
        return adx if not pd.isna(adx) else 20

    # === PRECOMPUTE COMMON INDICATORS ===
    ema5 = close.ewm(span=5, adjust=False).mean().iloc[-1]
    ema10 = close.ewm(span=10, adjust=False).mean().iloc[-1]
    ema20 = close.ewm(span=20, adjust=False).mean().iloc[-1]
    ma50 = close.rolling(window=50).mean().iloc[-1] if n >= 50 else ema20
    ma100 = close.rolling(window=100).mean().iloc[-1] if n >= 100 else ma50
    ma200 = close.rolling(window=200).mean().iloc[-1] if n >= 200 else ma100
    
    adx = calc_adx(high, low, close, 14)
    atr = calc_atr(high, low, close, 14)
    atr_pct = (atr / current) * 100  # ATR as % of price
    
    vol_avg = volume.rolling(window=20).mean().iloc[-1]
    vol_today = volume.iloc[-1]
    vol_spike = vol_today > vol_avg * 1.3
    
    # MACD
    exp12 = close.ewm(span=12, adjust=False).mean()
    exp26 = close.ewm(span=26, adjust=False).mean()
    macd = exp12 - exp26
    signal_line = macd.ewm(span=9, adjust=False).mean()
    macd_val = macd.iloc[-1]
    signal_val = signal_line.iloc[-1]
    macd_bullish = macd_val > signal_val
    
    # === MACRO GATE (Must Pass for ANY Buy) ===
    macro_bullish = current > ma200  # Long-term uptrend
    macro_bearish = current < ma200
    trend_strong = adx > 25  # No sideways trading
    
    # === TIMEFRAME SIGNALS ===
    
    # --- 1 DAY (Scalping) ---
    rsi_7 = calc_rsi(close, 7)
    score_1d = 0
    reason_1d = []
    
    # Gate 1: Must be in trend
    if not trend_strong:
        reason_1d.append("ADX < 25 (Sideways)")
    else:
        if current > ema5:
            score_1d += 1
            reason_1d.append("Above EMA5")
        else:
            score_1d -= 1
            reason_1d.append("Below EMA5")
        
        if rsi_7 < 25:
            score_1d += 2
            reason_1d.append("RSI < 25 (Oversold)")
        elif rsi_7 > 75:
            score_1d -= 2
            reason_1d.append("RSI > 75 (Overbought)")
        
        if vol_spike:
            score_1d += 1
            reason_1d.append("Volume Spike")
            
    results.append(get_strict_signal(score_1d, "1 Hari", reason_1d, trend_strong))
    
    # --- 3 DAYS (Swing Short) ---
    rsi_10 = calc_rsi(close, 10)
    score_3d = 0
    reason_3d = []
    
    if not trend_strong:
        reason_3d.append("No Trend (ADX < 25)")
    else:
        if current > ema10: 
            score_3d += 1
            reason_3d.append("Above EMA10")
        else: 
            score_3d -= 1
            reason_3d.append("Below EMA10")
        
        if rsi_10 < 30: 
            score_3d += 1
            reason_3d.append("RSI Oversold")
        elif rsi_10 > 70: 
            score_3d -= 1
            reason_3d.append("RSI Overbought")
            
        if macd_bullish:
            score_3d += 1
            reason_3d.append("MACD Bullish")
        else:
            score_3d -= 1
            reason_3d.append("MACD Bearish")
    
    results.append(get_strict_signal(score_3d, "3 Hari", reason_3d, trend_strong))
    
    # --- 1 WEEK ---
    rsi_14 = calc_rsi(close, 14)
    score_1w = 0
    reason_1w = []
    
    if current > ema20: 
        score_1w += 1
        reason_1w.append("Above EMA20")
    else: 
        score_1w -= 1
        reason_1w.append("Below EMA20")
    
    if rsi_14 < 25: 
        score_1w += 2
        reason_1w.append("RSI Deep Oversold")
    elif rsi_14 > 75: 
        score_1w -= 2
        reason_1w.append("RSI Overbought")
    
    if macd_bullish and trend_strong:
        score_1w += 1
        reason_1w.append("MACD+ADX Confirm")
    elif not macd_bullish:
        score_1w -= 1
        reason_1w.append("MACD Bearish")
    
    results.append(get_strict_signal(score_1w, "1 Minggu", reason_1w, trend_strong))
    
    # --- 1 MONTH ---
    score_1m = 0
    reason_1m = []
    
    # Must be in primary uptrend for Buy
    if current > ma50:
        score_1m += 1
        reason_1m.append("Above MA50")
    else:
        score_1m -= 2  # Stricter penalty
        reason_1m.append("Below MA50 (No Buy)")
    
    if macd_bullish:
        score_1m += 1
        reason_1m.append("MACD Bullish")
    else:
        score_1m -= 1
        reason_1m.append("MACD Bearish")
    
    if vol_spike:
        score_1m += 1
        reason_1m.append("Vol Confirm")
    
    results.append(get_strict_signal(score_1m, "1 Bulan", reason_1m, macro_bullish))
    
    # --- 2 MONTHS ---
    score_2m = 0
    reason_2m = []
    
    if current > ma100:
        score_2m += 1
        reason_2m.append("Above MA100")
    else:
        score_2m -= 2
        reason_2m.append("Below MA100")
    
    if ma50 > ma100:
        score_2m += 1
        reason_2m.append("MA50 > MA100")
    else:
        score_2m -= 1
        reason_2m.append("MA50 < MA100")
    
    results.append(get_strict_signal(score_2m, "2 Bulan", reason_2m, macro_bullish))
    
    # --- 3 MONTHS (Investor Grade) ---
    score_3m = 0
    reason_3m = []
    
    # STRICT: Must be above MA200 to consider buy
    if current > ma200:
        score_3m += 2
        reason_3m.append("Above MA200")
    else:
        score_3m -= 3  # Very strict
        reason_3m.append("Below MA200 (No Buy Zone)")
    
    # Golden/Death Cross
    if ma50 > ma200:
        score_3m += 1
        reason_3m.append("Golden Cross Active")
    else:
        score_3m -= 2
        reason_3m.append("Death Cross Active")
    
    # RSI should not be overbought for long-term entry
    if rsi_14 > 70:
        score_3m -= 1
        reason_3m.append("RSI High (Wait)")
    
    results.append(get_strict_signal(score_3m, "3 Bulan", reason_3m, macro_bullish))
    
    return results

def get_strict_signal(score, label, reasons, gate_passed):
    """
    STRICT Signal Converter.
    - Gate must pass for BUY signals
    - Higher thresholds required
    """
    reason_str = " | ".join(reasons[:2]) if reasons else "-"  # Show max 2 reasons
    
    # If primary gate (trend/macro) failed, cap signal at NEUTRAL
    if not gate_passed and score > 0:
        return {"label": label, "signal": "WAIT", "color": "gray", "reason": "Gate Failed: " + reason_str}
    
    # STRICT Thresholds
    if score >= 3:
        return {"label": label, "signal": "STRONG BUY", "color": "green", "reason": reason_str}
    elif score >= 2:
        return {"label": label, "signal": "BUY", "color": "lightgreen", "reason": reason_str}
    elif score <= -3:
        return {"label": label, "signal": "STRONG SELL", "color": "red", "reason": reason_str}
    elif score <= -2:
        return {"label": label, "signal": "SELL", "color": "orange", "reason": reason_str}
    elif score <= -1:
        return {"label": label, "signal": "WEAK SELL", "color": "orange", "reason": reason_str}
    elif score == 1:
        return {"label": label, "signal": "WAIT (Confirm)", "color": "gray", "reason": reason_str}
    else:
        return {"label": label, "signal": "NO TRADE", "color": "gray", "reason": reason_str}

def render_fundamental(info):
    st.markdown("### 🏢 Profil & Fundamental")
    if not info:
        st.warning("Data fundamental tidak tersedia.")
        return

    # Basic Info
    col1, col2 = st.columns([1, 2])
    with col1:
        st.info(f"**Sektor:** {info.get('sector', '-')}")
        st.info(f"**Industri:** {info.get('industry', '-')}")
    with col2:
        st.write(f"**Deskripsi:** {info.get('longBusinessSummary', info.get('description', '-'))[:300]}...")

    st.markdown("---")
    
    # Key Metrics Grid
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Market Cap", "Rp " + format_large_number(info.get('marketCap', 0)))
    with m2:
        pe = info.get('trailingPE', 0)
        st.metric("PER (Price/Earnings)", f"{pe:.2f}x" if pe else "-")
    with m3:
        pbv = info.get('priceToBook', 0)
        st.metric("PBV (Price/Book)", f"{pbv:.2f}x" if pbv else "-")
    with m4:
        roe = info.get('returnOnEquity', 0)
        st.metric("ROE", f"{roe*100:.2f}%" if roe else "-")

    m5, m6, m7, m8 = st.columns(4)
    with m5:
        dy = info.get('dividendYield', 0)
        # Handle decimal vs percent ambiguity
        if dy:
             dy_val = dy * 100 if dy < 1 else dy
             st.metric("Dividend Yield", f"{dy_val:.2f}%")
        else:
            st.metric("Dividend Yield", "-")
            
    with m6:
        st.metric("52 Week High", format_rupiah(info.get('fiftyTwoWeekHigh', 0)))
    with m7:
        st.metric("52 Week Low", format_rupiah(info.get('fiftyTwoWeekLow', 0)))
    with m8:
        vol = info.get('volume', 0)
        st.metric("Volume Terakhir", format_large_number(vol))

def render_technical(history, symbol):
    st.markdown("### 📈 Analisa Teknikal")
    
    if history.empty:
        st.warning("Data historis tidak tersedia.")
        return

    # Tab pilihan chart
    tab_price, tab_stat = st.tabs(["Chart Harga", "Statistik Bulanan"])
    
    with tab_price:
        if PLOTLY_AVAILABLE:
            fig = go.Figure(data=[go.Candlestick(x=history.index,
                            open=history['Open'],
                            high=history['High'],
                            low=history['Low'],
                            close=history['Close'],
                            name=symbol)])
            
            fig.update_layout(
                title=f'Chart Pergerakan Harga {symbol}',
                yaxis_title='Harga Saham (IDR)',
                xaxis_title='Tanggal',
                height=500,
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.line_chart(history['Close'])
            st.info("Install 'plotly' untuk melihat Candlestick chart yang lebih detail.")

    with tab_stat:
        st.write("📊 Statistik Return Bulanan (Seasonality Real)")
        
        # Calculate Monthly Returns
        monthly_return = history['Close'].resample('M').ffill().pct_change()
        
        # Create DataFrame for Heatmap
        m_df = monthly_return.to_frame(name='Return')
        m_df['Year'] = m_df.index.year
        m_df['Month'] = m_df.index.strftime('%b') # Jan, Feb, Mar
        m_df['MonthNum'] = m_df.index.month
        
        # Pivot: Rows=Year, Cols=Month
        pivot_table = m_df.pivot_table(values='Return', index='Year', columns='MonthNum')
        
        # Map MonthNumBack to Name
        month_names = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun',
                       7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
        pivot_table = pivot_table.rename(columns=month_names)
        
        # Display as a Heatmap-like Dataframe (Styled)
        st.dataframe(
            pivot_table.style.format("{:.2%}")
            .background_gradient(cmap='RdYlGn', vmin=-0.1, vmax=0.1)
            .highlight_null(color='transparent'),
            use_container_width=True
        )
        
        # Average Seasonality Chart
        avg_seasonality = m_df.groupby('MonthNum')['Return'].mean()
        avg_seasonality.index = [month_names[i] for i in avg_seasonality.index]
        
        st.write("📈 Rata-rata Return per Bulan (Seasonality)")
        st.bar_chart(avg_seasonality)

def render_news(news, sentiment_data=None):
    """Render news with sentiment indicators"""
    st.markdown("### 📰 Berita Terkini")
    
    # Show news count
    if news and len(news) > 0:
        st.caption(f"📊 Ditemukan **{len(news)} artikel** dari berbagai sumber")
    
    if not news or len(news) == 0:
        st.info("Belum ada berita terbaru yang ditemukan oleh sistem.")
        return
    
    # If we have sentiment data, show categorized news
    if sentiment_data and isinstance(sentiment_data, dict):
        pos_news = sentiment_data.get('positive_news', [])
        neg_news = sentiment_data.get('negative_news', [])
        neu_news = sentiment_data.get('neutral_news', [])
        
        # Show tabs for different sentiments
        tab_all, tab_pos, tab_neg, tab_neu = st.tabs([
            f"📋 Semua ({len(news)})",
            f"✅ Positif ({len(pos_news)})",
            f"⚠️ Negatif ({len(neg_news)})", 
            f"⚪ Netral ({len(neu_news)})"
        ])
        
        with tab_all:
            # Combine all and show with badges
            all_tagged = pos_news + neg_news + neu_news
            for item in all_tagged[:20]:
                render_news_card(item, show_sentiment=True)
                
        with tab_pos:
            if pos_news:
                for item in pos_news[:15]:
                    render_news_card(item, show_sentiment=True)
            else:
                st.info("Tidak ada berita dengan sentimen positif")
                
        with tab_neg:
            if neg_news:
                for item in neg_news[:15]:
                    render_news_card(item, show_sentiment=True)
            else:
                st.info("Tidak ada berita dengan sentimen negatif")
                
        with tab_neu:
            if neu_news:
                for item in neu_news[:15]:
                    render_news_card(item, show_sentiment=True)
            else:
                st.info("Tidak ada berita netral")
    else:
        # Fallback: show all news without sentiment
        for item in news[:20]:
            render_news_card(item, show_sentiment=False)

def render_news_card(item, show_sentiment=False):
    """Render a single news card with optional sentiment badge"""
    title = item.get('title', 'No Title')
    link = item.get('link', '#')
    publisher = item.get('publisher', 'Unknown')
    
    # Determine sentiment badge
    badge_html = ""
    if show_sentiment:
        sentiment_score = item.get('sentiment_score', 0)
        pos_kw = item.get('positive_keywords', [])
        neg_kw = item.get('negative_keywords', [])
        
        if sentiment_score > 0:
            badge_html = f"<span style='background: #10b98120; color: #10b981; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: bold;'>✅ POSITIF ({'+' + str(sentiment_score)})</span>"
            if pos_kw:
                badge_html += f"<span style='margin-left: 5px; font-size: 9px; opacity: 0.6;'>🔍 {', '.join(pos_kw[:3])}</span>"
        elif sentiment_score < 0:
            badge_html = f"<span style='background: #ef444420; color: #ef4444; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: bold;'>⚠️ NEGATIF ({sentiment_score})</span>"
            if neg_kw:
                badge_html += f"<span style='margin-left: 5px; font-size: 9px; opacity: 0.6;'>🔍 {', '.join(neg_kw[:3])}</span>"
        else:
            badge_html = f"<span style='background: #9ca3af20; color: #9ca3af; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: bold;'>⚪ NETRAL</span>"
    
    st.markdown(f"""
    <div style='background-color: var(--secondary-background-color); padding: 12px; border-radius: 8px; margin-bottom: 10px; border: 1px solid rgba(128,128,128,0.2);'>
        <div style='margin-bottom: 5px;'>{badge_html}</div>
        <a href='{link}' target='_blank' style='text-decoration: none; color: var(--text-color); font-weight: 600; font-size: 15px;'>{title}</a>
        <div style='display: flex; justify-content: space-between; margin-top: 8px; font-size: 12px; opacity: 0.7;'>
            <span>📰 {publisher}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_trade_plan_integrated(current_price):
    st.markdown("### 🎯 Buat Trading Plan")
    st.markdown("Atur parameter trading plan Anda di bawah ini.")
    
    # Init Session State for Plan if not exists, OR update if new symbol loaded (logic handled by caller usually, but safely init here)
    if "plan_entry" not in st.session_state: st.session_state["plan_entry"] = float(current_price)
    if "plan_sl" not in st.session_state: st.session_state["plan_sl"] = 3.0
    if "plan_rrr" not in st.session_state: st.session_state["plan_rrr"] = 2.0
    if "plan_modal" not in st.session_state: st.session_state["plan_modal"] = 10000000
    
    # Input sederhana untuk plan langsung di halaman ini
    c1, c2, c3 = st.columns(3)

    with c1:
        manual_price = st.number_input("Harga Entry (Rp)", min_value=1.0, step=10.0, key="plan_entry")
    with c2:
        stop_loss_pct = st.number_input("Stop Loss (%)", min_value=0.5, step=0.5, key="plan_sl")
    with c3:
        rrr = st.number_input("Risk Reward (Ratio)", min_value=1.0, step=0.1, key="plan_rrr")

    # Kalkulasi Cepat
    try:
        sl_price = int(manual_price * (1 - stop_loss_pct/100))
        risk_per_share = manual_price - sl_price
        reward_per_share = risk_per_share * rrr
        tp_price = int(manual_price + reward_per_share)
        
        # Capital Calculator (Optional)
        st.caption("Kalkulator Posisi (Fixed Capital)")
        col_cap1, col_cap2 = st.columns(2)
        with col_cap1:
            modal_entry = st.number_input("Modal Entry (Rp)", min_value=100000, step=1000000, key="plan_modal")
        
        with col_cap2:
            # Hasil
            max_lot = int(modal_entry / (100 * manual_price))
            st.metric("Max Lot", f"{max_lot} Lot")
        
        # Summary Plan
        st.success(f"**PLAN:** Entry @{format_rupiah(manual_price)} | SL @{format_rupiah(sl_price)} (-{stop_loss_pct}%) | TP @{format_rupiah(tp_price)} (+{stop_loss_pct*rrr:.2f}%)")
    except Exception as e:
        st.error(f"Terjadi kesalahan kalkulasi: {e}")

def render_smart_summary(analysis_data, history):
    """
    Render consolidated AI Analysis summary.
    """
    st.markdown("### 🧠 AI Smart Analysis")
    
    sent = analysis_data.get('sentiment', {})
    fund = analysis_data.get('fundamental', {})
    
    # Simple Technical Summary (Short Term)
    # Re-use tech signal logic but just get 1-label summary
    tech_score = 0
    close = history['Close']
    ma50 = close.rolling(window=50).mean().iloc[-1]
    current = close.iloc[-1]
    if current > ma50: tech_score = 1
    else: tech_score = -1
    
    c1, c2, c3 = st.columns(3)
    
    # 1. Sentiment Card
    s_label = sent.get('label', 'NEUTRAL')
    s_color = "#10b981" if "POSITIVE" in s_label else "#ef4444" if "NEGATIVE" in s_label else "#9ca3af"
    with c1:
        st.markdown(f"""
        <div style='background-color: {s_color}20; padding: 15px; border-radius: 10px; border: 1px solid {s_color}; text-align: center;'>
            <h4 style='margin:0; color: {s_color};'>Sentimen Berita</h4>
            <h3 style='margin:5px 0; color: {s_color};'>{s_label}</h3>
            <p style='margin:0; font-size: 12px; opacity: 0.8;'>{sent.get('summary', '-')}</p>
        </div>
        """, unsafe_allow_html=True)
        
    # 2. Fundamental Card
    f_label = fund.get('label', 'UNKNOWN')
    f_color = "#10b981" if f_label in ["EXCELLENT", "GOOD"] else "#ef4444" if f_label in ["POOR", "WEAK"] else "#9ca3af"
    with c2:
        st.markdown(f"""
        <div style='background-color: {f_color}20; padding: 15px; border-radius: 10px; border: 1px solid {f_color}; text-align: center;'>
            <h4 style='margin:0; color: {f_color};'>Kesehatan Fundamental</h4>
            <h3 style='margin:5px 0; color: {f_color};'>{f_label}</h3>
            <p style='margin:0; font-size: 12px; opacity: 0.8;'>Skor: {fund.get('score', 0)}/5</p>
        </div>
        """, unsafe_allow_html=True)
        
    # 3. Technical Trend Card
    t_label = "Uptrend (Bullish)" if tech_score > 0 else "Downtrend (Bearish)"
    t_color = "#10b981" if tech_score > 0 else "#ef4444"
    with c3:
        st.markdown(f"""
        <div style='background-color: {t_color}20; padding: 15px; border-radius: 10px; border: 1px solid {t_color}; text-align: center;'>
            <h4 style='margin:0; color: {t_color};'>Tren Utama (Daily)</h4>
            <h3 style='margin:5px 0; color: {t_color};'>{"BULLISH" if tech_score > 0 else "BEARISH"}</h3>
            <p style='margin:0; font-size: 12px; opacity: 0.8;'>vs MA50</p>
        </div>
        """, unsafe_allow_html=True)
        
    # Fundamental Details
    with st.expander("Lihat Detail Analisa Fundamental"):
        for r in fund.get('reasons', []):
            st.write(f"• {r}")


def analysis_dashboard_page():
    st.title("🔬 Analisa Saham Lengkap")
    st.markdown("Fundamental, Teknikal, News, dan Trade Planner dalam satu tampilan.")
    
    # Input
    col_search, col_btn = st.columns([3, 1])
    with col_search:
        symbol = st.text_input("💎 Masukkan Kode Saham", value="BBRI", label_visibility="collapsed", placeholder="Contoh: BBRI").upper()
    with col_btn:
        analyze_btn = st.button("🔍 Analisa Sekarang", type="primary", use_container_width=True)
    
    # Session State Management
    if 'analysis_data' not in st.session_state:
        st.session_state['analysis_data'] = None
    if 'analysis_symbol' not in st.session_state:
        st.session_state['analysis_symbol'] = ""

    if analyze_btn:
        with st.spinner(f"Sedang membedah data {symbol}..."):
            data = get_stock_data(symbol)
            if data:
                st.session_state['analysis_data'] = data
                st.session_state['analysis_symbol'] = symbol
            else:
                st.error("Gagal mengambil data. Pastikan koneksi internet aktif dan kode saham benar.")

    # Render Content if Data Exists
    if st.session_state['analysis_data'] and st.session_state['analysis_symbol']:
        data = st.session_state['analysis_data']
        curr_symbol = st.session_state['analysis_symbol']
        
        # Display Header
        st.header(f"{curr_symbol} - Rp {format_rupiah(data['current_price'])}")
        
        # Show Smart Summary First
        if 'analysis' in data:
            render_smart_summary(data['analysis'], data['history'])
        
        st.markdown("---")
        
        # Tabs Utama
        tab_fund, tab_tech, tab_rec, tab_news, tab_plan = st.tabs(["📊 Fundamental", "📈 Teknikal", "⭐ Rekomendasi", "📰 Berita", "🎯 Trading Plan"])
        
        with tab_fund:
            render_fundamental(data['info'])
            
        with tab_tech:
            render_technical(data['history'], curr_symbol)
        
        with tab_rec:
            render_recommendations(data['recommendations'], data['history'])
            
        with tab_news:
            sentiment_data = data.get('analysis', {}).get('sentiment', None)
            render_news(data['news'], sentiment_data)
            
        with tab_plan:
            render_trade_plan_integrated(data['current_price'])

