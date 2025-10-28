import streamlit as st
import requests
import google.generativeai as genai
import os
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
            st.markdown(analysis)
            
        except Exception as e:
            st.error(f"❌ Ошибка: {str(e)}")
