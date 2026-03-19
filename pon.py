import asyncio
import logging
import os
import g4f
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Берем токен из переменной окружения BOT_TOKEN. 
# Если её нет, используем твой текущий (но для GitHub лучше оставить только os.getenv)
TOKEN = os.getenv("BOT_TOKEN", "8405491796:AAE6HdeAuHJ93fWpGb4rPOaH-djl_BbHkOY")

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# Кнопка под сообщениями
def get_main_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="🗑️ Очистить диалог", callback_data="clear_chat")
    )
    return builder.as_markup()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(
        f"<b>Привет, {message.from_user.first_name}!</b>\n\n"
        "🤖 Бот успешно запущен в Docker-контейнере.\n"
        "Пиши вопросы, я отвечу кодом с кнопкой копирования!",
        parse_mode="HTML",
        reply_markup=get_main_kb()
    )

@dp.callback_query(F.data == "clear_chat")
async def clear_callback(callback: types.CallbackQuery):
    await callback.message.answer("✨ Контекст сброшен. Начинаем с чистого листа!")
    await callback.answer()

@dp.message()
async def chat_handler(message: types.Message):
    await bot.send_chat_action(message.chat.id, action="typing")
    try:
        # Запрос к ИИ через g4f
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.default,
            messages=[{"role": "user", "content": message.text}],
        )
        
        if response:
            # Отправляем ответ. Markdown включит те самые рамки для кода
            await message.answer(
                str(response), 
                parse_mode="Markdown", 
                reply_markup=get_main_kb()
            )
        else:
            await message.answer("⚠️ ИИ не ответил. Попробуй еще раз.")
            
    except Exception as e:
        logging.error(f"Ошибка в chat_handler: {e}")
        # Если Markdown упал (бывают кривые символы), шлем обычным текстом
        try:
            await message.answer(f"Произошла ошибка, вот ответ текстом:\n\n{str(response)}")
        except:
            await message.answer("❌ Ошибка связи с ИИ сервером.")

async def main():
    # Очистка очереди сообщений
    await bot.delete_webhook(drop_pending_updates=True)
    print("--- БОТ В СЕТИ (DOCKER) ---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("--- БОТ ВЫКЛЮЧЕН ---")
