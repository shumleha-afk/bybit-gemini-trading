import streamlit as st
import websocket
import json
import threading
import time
import google.generativeai as genai
import os

# === Настройки страницы ===
st.set_page_config(
    page_title="Bybit TradingView + Gemini AI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("📈 Bybit TradingView + 🤖 Gemini AI Анализ")
st.markdown("---")

# === Поле ввода символа ===
symbol = st.text_input("Введите символ (например: BTCUSDT, ETHUSDT)", value="BTCUSDT").strip().upper()

if not symbol or not symbol.replace("USDT", "").replace("USD", "").replace("PERP", "").isalpha():
    st.warning("Пожалуйста, введите корректный символ (например: BTCUSDT)")
    st.stop()

# === График TradingView ===
tradingview_url = f"https://s.tradingview.com/widgetembed/?frameElementId=tradingview_123&symbol=BYBIT:{symbol}.P&interval=60&theme=dark&style=1&locale=ru&toolbar_bg=%23f1f3f6&enable_publishing=false&hide_top_toolbar=false&hide_side_toolbar=true&save_image=true&studies=%5B%22STD%3BCumulative%251Volume%251Delta%22%2C%22STD%3BDEMA%22%2C%22STD%3BOpen%251Interest%22%2C%22STD%3BPivot%251Points%251Standard%22%2C%22STD%3BDivergence%251Indicator%22%5D&hide_volume=false&hide_legend=false&withdateranges=false&hotlist=false&calendar=false&details=false&watchlist=%5B%5D&compareSymbols=%5B%5D&studies_overrides=%7B%7D&overrides=%7B%22paneProperties.backgroundColor%22%3A%22%230F0F0F%22%2C%22paneProperties.gridColor%22%3A%22rgba(242%2C%20242%2C%20242%2C%200.06)%22%7D&timezone=Europe%2FMoscow"

st.components.v1.iframe(
    src=tradingview_url,
    width=1200,
    height=700,
    scrolling=False
)

# === Функция для получения свечей через WebSocket ===
def get_klines_via_websocket(symbol, interval="60", limit=20):
    url = "wss://stream.bybit.com/v5/public/linear"
    klines = []
    lock = threading.Lock()
    event = threading.Event()

    def on_message(ws, message):
        data = json.loads(message)
        if data.get("topic") == f"kline.{interval}.{symbol}":
            kline = data["data"]["kline"][-1]  # последняя завершённая свеча
            with lock:
                if len(klines) < limit:
                    klines.append(kline)
                else:
                    ws.close()
                    event.set()

    def on_error(ws, error):
        pass

    def on_close(ws, close_status_code, close_msg):
        event.set()

    def on_open(ws):
        subscribe_msg = {
            "op": "subscribe",
            "args": [f"kline.{interval}.{symbol}"]
        }
        ws.send(json.dumps(subscribe_msg))

    ws = websocket.WebSocketApp(url,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    
    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()
    
    # Ждём данные или таймаут
    if not event.wait(timeout=10):
        ws.close()
    
    return klines

# === Кнопка анализа ===
if st.button("🤖 Получить AI-анализ от Gemini"):
    with st.spinner("Подключаемся к Bybit WebSocket и анализируем..."):
        try:
            # Получаем свечи через WebSocket
         full_symbol = f"{symbol}.P"  # Добавляем .P для perpetual
klines = get_klines_via_websocket(full_symbol, interval="60", limit=10)
            
            # === Кнопка анализа ===
if st.button("🤖 Получить AI-анализ от Gemini"):
    with st.spinner("Подключаемся к Bybit WebSocket и анализируем..."):
        try:
            # Используем полный символ с .P
            full_symbol = f"{symbol}.P"
            
            # Получаем свечи через WebSocket
            klines = get_klines_via_websocket(full_symbol, interval="60", limit=10)
            
            if not klines:
                st.error("❌ Не удалось получить данные через WebSocket. Проверьте символ.")
                st.stop()
            
            # Формируем данные для Gemini
            data_str = "\n".join([
                f"Время: {k['timestamp']}, O: {k['open']}, H: {k['high']}, L: {k['low']}, C: {k['close']}"
                for k in klines
            ])
            
            # Настройка Gemini API
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                st.error("❌ Не задан GEMINI_API_KEY в Secrets.")
                st.stop()
                
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-pro")
            
            prompt = f"""
            Проанализируй последние 10 часовых свечей {symbol} на Bybit.
            Дай краткий технический анализ: тренд, возможные точки входа.
            Данные (время в Unix ms, O, H, L, C):
            {data_str}
            """
            
            response = model.generate_content(prompt)
            st.success("✅ AI-анализ от Gemini:")
            st.markdown(response.text)
            
        except Exception as e:
            st.error(f"❌ Ошибка: {str(e)}")
