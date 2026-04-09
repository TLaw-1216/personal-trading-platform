import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import mplfinance as mpf
import matplotlib.pyplot as plt
import pandas_ta as ta

st.set_page_config(page_title="My Personal Trading Platform", layout="wide")
st.title("🚀 My Personal Trading Platform")
st.markdown("**Sectors • News • Charts + Draw Lines** (Working on Python 3.14)")

# ================== YOUR SECTORS (edit anytime) ==================
SECTORS = {
    "Technology": ["0700.HK", "AAPL", "MSFT", "NVDA", "9988.HK"],
    "Finance": ["0005.HK", "HSBC", "JPM", "V", "9987.HK"],
    "Energy": ["883.HK", "XOM", "CVX"],
    "Property": ["0002.HK", "0016.HK"],
    "Custom Watchlist": ["BTC-USD", "TSLA"]
}

def get_data(ticker, period="1y"):
    return yf.download(ticker, period=period, progress=False)

@st.cache_data(ttl=600)
def get_news(ticker):
    try:
        return yf.Ticker(ticker).news[:8]
    except:
        return []

# ====================== SIDEBAR ======================
st.sidebar.header("Select Sector")
selected_sector = st.sidebar.selectbox("Sector", list(SECTORS.keys()))
selected_tickers = st.sidebar.multiselect("Tickers", SECTORS[selected_sector], default=SECTORS[selected_sector][:3])
period = st.sidebar.selectbox("Chart Period", ["3mo", "6mo", "1y", "2y"], index=2)

tab1, tab2 = st.tabs(["📰 Sector News", "📈 Charts + Draw Lines"])

# ------------------- News Tab -------------------
with tab1:
    st.subheader(f"{selected_sector} News & Prospects")
    st.subheader("Current Prices")
    for ticker in selected_tickers:
        try:
            info = yf.Ticker(ticker).fast_info
            price = info.last_price
            st.write(f"{ticker}: ${price:.2f}")
        except:
            st.write(f"{ticker}: N/A")
    if selected_tickers:
        cols = st.columns(min(3, len(selected_tickers)))
        for i, ticker in enumerate(selected_tickers):
            with cols[i % 3]:
                st.markdown(f"**{ticker}**")
                news_list = get_news(ticker)
                for item in news_list:
                    title = item.get("title", "")
                    signal = ""
                    if "buy" in title.lower() or "bullish" in title.lower() or "upgrade" in title.lower():
                        signal = "🟢 Buy"
                    elif "sell" in title.lower() or "bearish" in title.lower() or "downgrade" in title.lower():
                        signal = "🔴 Sell"
                    with st.expander(f"{signal} {title[:70]}..."):
                        st.caption(item.get("publisher", ""))
                        st.markdown(f"[Read →]({item.get('link', '#')})")

# ------------------- Charts Tab -------------------
with tab2:
    if selected_tickers:
        ticker = st.selectbox("Choose ticker for chart", selected_tickers)
        data = get_data(ticker, period)

        # ✅ Add this check
        if data.empty:
            st.error(f"No data found for {ticker} in period {period}")
        else:
            st.write("Preview of downloaded data:", data.head())  # shows first few rows

            # User-drawn lines
            if "lines" not in st.session_state:
                st.session_state.lines = []

            st.sidebar.subheader("✏️ Draw Support / Resistance")
            last_close = data["Close"].iloc[-1]
            if isinstance(last_close, pd.Series):
                last_close = last_close.values[0]
            price_level = st.sidebar.number_input("Price Level", value=float(last_close), step=0.01)

            line_color = st.sidebar.selectbox("Line Type", ["Support (Green)", "Resistance (Red)"])
            color = "green" if "Support" in line_color else "red"

            if st.sidebar.button("Add Line"):
                st.session_state.lines.append({"price": price_level, "color": color, "name": line_color})

            if st.sidebar.button("Clear All Lines"):
                st.session_state.lines = []

            # Plot candlestick
            # Calculate indicators
            macd = ta.macd(data['Close'])
            bb = ta.bbands(data['Close'])

            # Create addplots
            addplots = [
                mpf.make_addplot(macd['MACD'], panel=1, color='blue', ylabel='MACD'),
                mpf.make_addplot(macd['MACDh'], panel=1, type='bar', color='gray'),
                mpf.make_addplot(macd['MACDs'], panel=1, color='red'),
                mpf.make_addplot(bb['BBU'], color='green', linestyle='--'),
                mpf.make_addplot(bb['BBL'], color='red', linestyle='--'),
                mpf.make_addplot(bb['BBM'], color='blue', linestyle='--'),
            ]

            # User lines
            hlines = [line['price'] for line in st.session_state.lines]
            colors = [line['color'] for line in st.session_state.lines]

            # Plot
            fig, axlist = mpf.plot(data, type='candle', volume=True, addplot=addplots, hlines=dict(hlines=hlines, colors=colors, linestyle='--'), style='charles', returnfig=True)
            st.pyplot(fig)

            # Signals
            for line in st.session_state.lines:
                last_close = data['Close'].iloc[-1]
                if line['color'] == 'red' and last_close > line['price']:
                    st.warning(f"Price surged above resistance {line['price']}: Potential sell signal")
                elif line['color'] == 'green' and last_close < line['price']:
                    st.info(f"Price dropped below support {line['price']}: Potential buy signal")
    else:
        st.warning("Select at least one ticker")


st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Running on Python 3.14")