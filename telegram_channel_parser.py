import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ChatMember

# Данные бота
BOT_TOKEN = "8073491952:AAGYuMf5Cat7pDjNkm_cNYqU7WHqDD84ZRQ"
CHANNELS = [-1001941645422, -1002459000726]  # ID закрытых каналов

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def check_user_in_channels(user_id):
    """ Проверяем, есть ли пользователь в указанных каналах """
    for channel_id in CHANNELS:
        try:
            chat_member = await bot.get_chat_member(channel_id, user_id)
            if chat_member.status in ["member", "administrator", "creator"]:
                user = await bot.get_chat(user_id)
                return {
                    "channel_id": channel_id,
                    "user_id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name
                }
        except Exception:
            continue
    return None

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("👋 Отправь Telegram ID, и я проверю, подписан ли пользователь на канал.")

@dp.message()
async def search_user(message: types.Message):
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer("🚫 Введите корректный Telegram ID.")
        return

    user_info = await check_user_in_channels(user_id)
    
    if user_info:
        # Генерируем ссылку
        chat_link = f"tg://user?id={user_info['user_id']}"

        # Обрабатываем имя и фамилию
        full_name = f"{user_info['first_name']} {user_info['last_name'] or ''}".strip()
        username_display = f"@{user_info['username']}" if user_info["username"] else "(нет юзернейма)"

        # Отправляем сообщение
        await message.answer(
            f"✅ Пользователь найден в закрытом канале!\n"
            f"👤 <b>Имя:</b> {full_name}\n"
            f"📛 <b>Юзернейм:</b> {username_display}\n"
            f"🆔 <b>ID:</b> {user_info['user_id']}\n"
            f"🔗 <a href='{chat_link}'>Открыть диалог</a>",
            parse_mode="HTML"
        )
    else:
        await message.answer("🚫 Пользователь не найден в указанных закрытых каналах.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
