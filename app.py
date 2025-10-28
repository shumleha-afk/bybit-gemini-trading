import streamlit as st
import requests
import google.generativeai as genai
import os

st.set_page_config(page_title="Binance + Gemini AI", layout="wide")
st.title("📈 Binance TradingView + 🤖 Gemini AI Анализ")
st.markdown("---")

symbol = st.text_input("Введите символ (например: BTCUSDT)", value="BTCUSDT").strip().upper()

if not symbol or not symbol.replace("USDT", "").replace("USD", "").isalpha():
    st.warning("Введите корректный символ (например: BTCUSDT)")
    st.stop()

# График TradingView (Binance)
tradingview_url = f"https://s.tradingview.com/widgetembed/?symbol=BINANCE:{symbol}&interval=60"
st.components.v1.iframe(src=tradingview_url, width=1200, height=700, scrolling=False)

if st.button("🤖 Получить AI-анализ от Gemini"):
    with st.spinner("Запрашиваем данные с Binance..."):
        try:
            # Запрос к Binance API
            url = "https://api.binance.com/api/v3/klines"
            params = {"symbol": symbol, "interval": "1h", "limit": 20}
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            candles = resp.json()
            
            if not candles:
                st.error("Нет данных от Binance")
                st.stop()
            
            # Формируем данные
            data_str = "\n".join([
                f"Время: {c[0]}, O: {c[1]}, H: {c[2]}, L: {c[3]}, C: {c[4]}"
                for c in candles[-10:]
            ])
            
            # Gemini API
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                st.error("Добавьте GEMINI_API_KEY в Secrets")
                st.stop()
                
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-pro")
            prompt = f"Проанализируй последние 10 часовых свечей {symbol} на Binance:\n{data_str}"
            response = model.generate_content(prompt)
            
            st.success("✅ AI-анализ от Gemini:")
            st.markdown(response.text)
            
        except Exception as e:
          st.error(f"Ошибка: {str(e)}")
