from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import connect, daily_summary

def setup_scheduler(bot, timezone):
    scheduler = AsyncIOScheduler(timezone=timezone)

    async def water_reminder():
        with connect() as db:
            users = db.execute("SELECT telegram_id, water_target FROM users WHERE reminders_enabled=1").fetchall()
        for u in users:
            s = daily_summary(u["telegram_id"])
            if s["water_ml"] < (u["water_target"] or 2500) * 0.6:
                try:
                    await bot.send_message(u["telegram_id"], "💧 Воды сегодня пока мало. Добавь воду в NutriVision.")
                except Exception:
                    pass

    async def evening_summary():
        with connect() as db:
            users = db.execute("SELECT telegram_id FROM users WHERE reminders_enabled=1").fetchall()
        for u in users:
            try:
                await bot.send_message(u["telegram_id"], "🌙 Проверь дневной прогресс и запиши вес, если ещё не сделал этого.")
            except Exception:
                pass

    scheduler.add_job(water_reminder, "cron", hour=15, minute=0)
    scheduler.add_job(evening_summary, "cron", hour=20, minute=30)
    scheduler.start()
    return scheduler
