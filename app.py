import streamlit as st
import requests

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
if not symbol or not symbol.replace("USDT", "").replace("USD", "").isalpha():
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
    with st.spinner("Запрашиваем данные с Bybit и анализируем..."):
        try:
            # Получаем последние свечи с Bybit (публичный API)
            url = "https://api.bybit.com/v5/market/kline"
            params = {
                "category": "linear",
                "symbol": symbol,
                "interval": "60",
                "limit": 20
            }
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            
            if data.get("retCode") != 0:
                st.error("Ошибка Bybit API: " + data.get("retMsg", "Неизвестно"))
                st.stop()
            
            candles = data["result"]["list"]
            prices = [float(c[4]) for c in candles]  # закрытие
            trend = "восходящий" if prices[-1] > prices[0] else "нисходящий"
            
            # Формируем анализ (без реального Gemini API для демо)
            analysis = f"""
            🔍 **Быстрый технический анализ для {symbol}:**
            - Последняя цена: **{prices[-1]:.2f} USDT**
            - Тренд за последние 20 часов: **{trend}**
            - Изменение: **{((prices[-1] / prices[0]) - 1) * 100:.2f}%**
            
            💡 *Для полного AI-анализа через Gemini API — добавьте ваш API-ключ в код.*
            """
            st.success(analysis)
            
        except Exception as e:
            st.error(f"Ошибка: {str(e)}")