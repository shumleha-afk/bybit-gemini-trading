import streamlit as st
import requests
import google.generativeai as genai
import os

# === Настройки страницы ===
st.set_page_config(
    page_title="Bybit TradingView + Gemini AI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === Заголовок ===
st.title("📈 Bybit TradingView + 🤖 Gemini AI Анализ")
st.markdown("---")

# === Поле ввода символа ===
symbol = st.text_input("Введите символ (например: BTCUSDT, ETHUSDT)", value="BTCUSDT").strip().upper()

# Проверка корректности символа
if not symbol or not symbol.replace("USDT", "").replace("USD", "").replace("PERP", "").isalpha():
    st.warning("Пожалуйста, введите корректный символ (например: BTCUSDT)")
    st.stop()

# === Отображение TradingView-виджета через iframe ===
tradingview_url = f"https://s.tradingview.com/widgetembed/?frameElementId=tradingview_123&symbol=BYBIT:{symbol}.P&interval=60&theme=dark&style=1&locale=ru&toolbar_bg=%23f1f3f6&enable_publishing=false&hide_top_toolbar=false&hide_side_toolbar=true&save_image=true&studies=%5B%22STD%3BCumulative%251Volume%251Delta%22%2C%22STD%3BDEMA%22%2C%22STD%3BOpen%251Interest%22%2C%22STD%3BPivot%251Points%251Standard%22%2C%22STD%3BDivergence%251Indicator%22%5D&hide_volume=false&hide_legend=false&withdateranges=false&hotlist=false&calendar=false&details=false&watchlist=%5B%5D&compareSymbols=%5B%5D&studies_overrides=%7B%7D&overrides=%7B%22paneProperties.backgroundColor%22%3A%22%230F0F0F%22%2C%22paneProperties.gridColor%22%3A%22rgba(242%2C%20242%2C%20242%2C%200.06)%22%7D&timezone=Europe%2FMoscow"

st.components.v1.iframe(
    src=tradingview_url,
    width=1200,
    height=700,
    scrolling=False
)

# === Кнопка для AI-анализа ===
if st.button("🤖 Получить AI-анализ от Gemini"):
    # Проверяем, что symbol существует и не пустой
    if not symbol or not isinstance(symbol, str):
        st.error("❌ Символ не задан. Введите, например, BTCUSDT.")
        st.stop()
    
    with st.spinner("Запрашиваем данные с Bybit и анализируем через Gemini..."):
        try:
            # Получаем последние свечи с Bybit
            url = "https://api.bybit.com/v5/market/kline"
            params = {
                "category": "linear",
                "symbol": symbol,
                "interval": "60",
                "limit": 20
            }
            
            # 🔧 Добавляем User-Agent — имитируем браузер
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            # 🔍 Отладка: покажем URL запроса
            st.write("🔍 Запрос к Bybit API:")
            st.code(f"{url}?{requests.Request('GET', url, params=params, headers=headers).prepare().url}")
            
        resp = requests.get(url, params=params, headers=headers, timeout=10)
url = "https://api.bybit.com/v5/market/kline"
params = {
    "category": "linear",
    "symbol": symbol,
    "interval": "60",
    "limit": 20
}

# 🔧 Добавляем полные заголовки — имитируем браузер
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.bybit.com/",
    "Origin": "https://www.bybit.com",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Connection": "keep-alive"
}

try:
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()  # вызовет исключение при 4xx/5xx)
            resp.raise_for_status()  # вызовет исключение при 4xx/5xx
            
            # 🔍 Отладка: покажем сырой ответ
            st.write("📦 Сырой ответ от Bybit:")
            st.code(resp.text[:500])  # первые 500 символов
            
            data = resp.json()
            
            if data.get("retCode") != 0:
                st.error(f"❌ Bybit API ошибка: {data.get('retMsg', 'Неизвестно')}")
                st.stop()
            
            candles = data["result"]["list"]
            prices = [float(c[4]) for c in candles]  # закрытие
            
            # Формируем строку данных для Gemini
            data_str = "\n".join([
                f"Время: {c[0]}, O: {c[1]}, H: {c[2]}, L: {c[3]}, C: {c[4]}"
                for c in candles[-10:]  # последние 10 свечей для краткости
            ])
            
            # Настройка Gemini API
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                st.error("❌ Не задан GEMINI_API_KEY в Secrets. Добавьте его в Settings → Secrets на Streamlit Cloud.")
                st.stop()
                
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-pro")
            
            prompt = f"""
            Проанализируй последние 10 часовых свечей {symbol} на Bybit.
            Дай краткий технический анализ: тренд, возможные точки входа, поддержка/сопротивление.
            Данные (время в Unix ms, O, H, L, C):
            {data_str}
            """
            
            response = model.generate_content(prompt)
            analysis = response.text
            
            st.success("✅ AI-анализ от Gemini:")
            st.markdown(analysis)
            
        except Exception as e:
            st.error(f"❌ Ошибка: {str(e)}")
