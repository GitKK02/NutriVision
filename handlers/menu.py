from aiogram import Router
from aiogram.types import Message
from keyboards.main import extended_menu, main_menu

router = Router()


@router.message(lambda m: m.text == "☰ Меню")
async def open_extended_menu(message: Message):
    await message.answer("☰ Разделы NutriVision", reply_markup=extended_menu)


@router.message(lambda m: m.text == "🏠 Главное меню")
async def open_main_menu(message: Message):
    await message.answer("🏠 Главное меню", reply_markup=main_menu)
