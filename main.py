import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, TIMEZONE
from database import init_db
from scheduler import setup_scheduler

from handlers.start import router as start_router
from handlers.profile import router as profile_router
from handlers.goals import router as goals_router
from handlers.food import router as food_router
from handlers.water import router as water_router
from handlers.weight import router as weight_router
from handlers.progress import router as progress_router
from handlers.coach import router as coach_router
from handlers.history import router as history_router
from handlers.achievements import router as achievements_router
from handlers.reminders import router as reminders_router

async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не указан в .env")

    init_db()
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()

    for router in [
        start_router,
        profile_router,
        goals_router,
        water_router,
        weight_router,
        progress_router,
        coach_router,
        history_router,
        achievements_router,
        reminders_router,
        food_router,
    ]:
        dp.include_router(router)

    setup_scheduler(bot, TIMEZONE)

    print("NutriVision 3.0 FIRST BETA запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
