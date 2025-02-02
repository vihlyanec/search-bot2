import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ChatMember

# Данные бота
BOT_TOKEN = "8073491952:AAGYuMf5Cat7pDjNkm_cNYqU7WHqDD84ZRQ"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def get_bot_channels():
    bot_info = await bot.get_me()
    channels = set()
    try:
        dialogs = await bot.get_updates()
        for update in dialogs:
            if update.my_chat_member:
                chat = update.my_chat_member.chat
                if chat.type == "channel":
                    admins = await bot.get_chat_administrators(chat.id)
                    for admin in admins:
                        if admin.user.id == bot_info.id:
                            channels.add(chat.id)
    except Exception as e:
        print(f"Ошибка при получении каналов: {e}")
    return list(channels)

async def check_user_in_channels(user_id, channels):
    for channel_id in channels:
        try:
            chat_member = await bot.get_chat_member(channel_id, user_id)
            if chat_member.status in ["member", "administrator", "creator"]:
                user = chat_member.user
                return {
                    "channel_id": channel_id,
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
        except Exception:
            continue
    return None

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("👋 Отправь Telegram ID, и я проверю, подписан ли пользователь на каналы, в которых я админ.")

@dp.message()
async def search_user(message: types.Message):
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer("🚫 Введите корректный Telegram ID.")
        return
    
    channels = await get_bot_channels()
    if not channels:
        await message.answer("🚫 Я не администратор ни в одном канале.")
        return
    
    user_info = await check_user_in_channels(user_id, channels)
    
    if user_info:
        username_link = f"@{user_info['username']}" if user_info['username'] else "(нет юзернейма)"
        chat_link = f"tg://user?id={user_info['id']}"
        full_name = f"{user_info['first_name']} {user_info['last_name']}" if user_info['last_name'] else user_info['first_name']
        await message.answer(
            f"✅ Пользователь найден в канале (ID: {user_info['channel_id']}).\n"
            f"👤 <b>Имя:</b> {full_name}\n"
            f"📛 <b>Юзернейм:</b> {username_link}\n"
            f"🔗 <a href='{chat_link}'>Открыть диалог</a>",
            parse_mode="HTML"
        )
    else:
        await message.answer("🚫 Пользователь не найден в каналах, где я админ.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
