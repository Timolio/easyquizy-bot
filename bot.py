import asyncio
import os
import time
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

load_dotenv()

locales = {
    'welcome_message': {
        'en': '',
        'ru': '',
        'uk': ''
    },
    'launch_button' : {
        'en': '',
        'ru': '',
        'uk': ''
    }
}

client = AsyncIOMotorClient(os.getenv('MONGO_URI'))
db = client['teleforms']
users_collection = db['users']

bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id

    await users_collection.update_one(
        {'_id': user_id},
        {
            '$setOnInsert': {
                '_id': user_id,
                'created_at': int(time.time() * 1000)
            }
        },
        upsert=True 
    )

    await message.answer(f"Привет, @{message.from_user.username}! 👋\nЯ помогу тебе быстро создать опрос и собрать ответы прямо здесь, в Telegram! 🎯", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Погнали! 🚀", web_app=WebAppInfo(url="https://eesyquizy.vercel.app/"))]
    ]))

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')