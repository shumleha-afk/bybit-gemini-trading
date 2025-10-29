import streamlit as st
import requests
import google.generativeai as genai
import os
from datetime import datetime

st.set_page_config(page_title="CoinGecko + Gemini AI", layout="wide")
st.title("📈 Крипто-график + 🤖 AI-анализ (без блокировок)")
st.markdown("---")

# Словарь для перевода названий в ID CoinGecko
coin_map = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "ADA": "cardano",
    "DOGE": "dogecoin"
}

coin_name = st.selectbox("Выберите монету", options=list(coin_map.keys()), index=0)
vs_currency = st.selectbox("Валюта", options=["usd", "eur", "rub"], index=0)

coin_id = coin_map[coin_name]

# График TradingView (спот)
tradingview_url = f"https://s.tradingview.com/widgetembed/?symbol=COINBASE:{coin_name}USD&interval=60&theme=dark&style=1&locale=ru"
st.components.v1.iframe(src=tradingview_url, width=1200, height=700, scrolling=False)

if st.button("🤖 Получить AI-анализ от Gemini"):
    with st.spinner("Запрашиваем данные с CoinGecko..."):
        try:
            # Запрос к CoinGecko
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
            params = {"vs_currency": vs_currency, "days": "7"}  # 7 дней почасово
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            if "prices" not in data or not data["prices"]:
                st.error("Нет данных от CoinGecko")
                st.stop()
            
            # Берём последние 24 точки (~24 часа)
            prices = data["prices"][-24:]
            data_str = "\n".join([
                f"Время: {datetime.fromtimestamp(p[0]/1000).strftime('%Y-%m-%d %H:%M')}, Цена: {p[1]:.2f} {vs_currency.upper()}"
                for p in prices
            ])
            
            # Gemini API
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                st.error("Добавьте GEMINI_API_KEY в Secrets")
                st.stop()
                
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-pro")
            prompt = f"Проанализируй последние 24 часа цены {coin_name} в {vs_currency.upper()}:\n{data_str}"
            response = model.generate_content(prompt)
            
            st.success("✅ AI-анализ от Gemini:")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"Ошибка: {str(e)}")
