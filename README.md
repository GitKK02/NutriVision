# NutriVision 3.0 FIRST BETA

Готовая бета-версия Telegram-бота для теста у друзей.

## Что работает

- профиль пользователя;
- выбор цели: набор, удержание, дефицит;
- расчёт калорий и БЖУ;
- дневник питания;
- добавление питания текстом;
- анализ фото еды через OpenAI Vision;
- вода;
- ежедневный вес и история;
- прогресс с полосками;
- AI Coach;
- история дней;
- достижения;
- напоминания через APScheduler;
- главный живой экран.

## Установка

```bash
cd ~/Desktop/NutriVision_3.0_FIRST_BETA
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
python3 main.py
```

## .env

```env
BOT_TOKEN=...
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini
TIMEZONE=Europe/Moscow
```

## Быстрый тест

1. `/start`
2. Создать профиль
3. Выбрать цель
4. Добавить воду
5. Добавить вес
6. Нажать «Питание» и написать блюдо
7. Открыть «Прогресс»
8. Открыть «AI Coach»
