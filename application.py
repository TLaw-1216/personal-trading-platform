import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

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

@st.cache_data(ttl=300)
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
    if selected_tickers:
        cols = st.columns(min(3, len(selected_tickers)))
        for i, ticker in enumerate(selected_tickers):
            with cols[i % 3]:
                st.markdown(f"**{ticker}**")
                news_list = get_news(ticker)
                for item in news_list:
                    with st.expander(item.get("title", "News")[:70] + "..."):
                        st.caption(item.get("publisher", ""))
                        st.markdown(f"[Read →]({item.get('link', '#')})")

# ------------------- Charts Tab -------------------
with tab2:
    if selected_tickers:
        ticker = st.selectbox("Choose ticker for chart", selected_tickers)
        data = get_data(ticker, period)
        
        if not data.empty:
            # User-drawn lines
            if "lines" not in st.session_state:
                st.session_state.lines = []
            
            st.sidebar.subheader("✏️ Draw Support / Resistance")
            price_level = st.sidebar.number_input("Price Level", value=float(data["Close"].iloc[-1]), step=0.01)
            line_color = st.sidebar.selectbox("Line Type", ["Support (Green)", "Resistance (Red)"])
            color = "green" if "Support" in line_color else "red"
            
            if st.sidebar.button("Add Line"):
                st.session_state.lines.append({"price": price_level, "color": color, "name": line_color})
            
            if st.sidebar.button("Clear All Lines"):
                st.session_state.lines = []
            
            # Plot
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=data.index, open=data["Open"], high=data["High"],
                                        low=data["Low"], close=data["Close"], name="Price"))
            
            for line in st.session_state.lines:
                fig.add_hline(y=line["price"], line_dash="dash", line_color=line["color"],
                              annotation_text=line["name"])
            
            fig.update_layout(title=f"{ticker} — {period}", height=700, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("No data for this ticker")
    else:
        st.warning("Select at least one ticker")

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Running on Python 3.14")