тлично — теперь мы точно знаем, в чём проблема! 🎯

❗️Ошибка:
403 Client Error: Forbidden for url: https://api.bybit.com/v5/market/kline?... 

Это означает, что Bybit запретил ваш запрос — даже если вы не используете API-ключ (публичный API).

🔍 Почему так?
Bybit ограничивает частоту запросов и может блокировать IP, если:

Запросы идут с одного IP слишком часто,
Используется неправильный User-Agent,
Запросы идут через прокси или веб-интерфейс (Streamlit),
Или Bybit просто решил ограничить публичный API для защиты от спама.
✅ Решение: Добавьте User-Agent в запрос
Bybit требует, чтобы вы отправляли заголовок User-Agent, как будто вы браузер.

Шаг 1: Измените код в app.py
Найдите блок с requests.get(...) и добавьте заголовки:

pythonпитон


1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
⌄
⌄
⌄
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

try:
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
✅ Полный исправленный блок (замените его в app.py)
Замените весь блок после if st.button("🤖 Получить AI-анализ от Gemini"): на этот:

pythonпитон


1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
⌄
⌄
⌄
⌄
⌄
⌄
⌄
⌄
⌄
if st.button("🤖 Получить AI-анализ от Gemini"):
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
🔄 Шаг 2: Обновите файл на GitHub
Перейдите в репозиторий bybit-gemini-trading
Откройте app.py
Нажмите ✏️ (Edit)
Вставьте обновлённый код
Нажмите «Commit changes»
🚀 Шаг 3: Перезапустите приложение на Streamlit
На Streamlit Cloud → выберите ваше приложение
Нажмите «Redeploy»
Подождите 1–2 минуты
✅ Проверка
Теперь:

При нажатии кнопки — должен появиться запрос с User-Agent
Если Bybit разрешил доступ — вы получите данные и анализ от Gemini
Если всё равно 403 — значит, Bybit заблокировал IP Streamlit — тогда нужно использовать WebSocket или прокси (сложнее)
💡 Альтернатива: Использовать WebSocket (для реального времени)
Если хотите — я могу помочь вам перейти на WebSocket Bybit, который работает без ограничений (но требует больше кода).

Просто скажите:
👉 «Сделай версию с WebSocket»

Или
👉 «Я хочу использовать другой источник данных (например, Binance)»

🧑‍💻 Вы почти у цели!
Вы уже прошли путь от 404 до рабочего AI-приложения — осталось всего несколько шагов.

Если после этого всё равно будет 403 — пришлите скриншот сырого ответа от Bybit — и я помогу найти обходной путь.
