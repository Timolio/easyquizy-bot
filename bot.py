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

client = AsyncIOMotorClient(os.getenv('MONGO_URI'))
db = client['teleforms']
users_collection = db['users']

bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

translations = {
    "ru": {
        "start_message": "Привет, @{username}! 👋\nЯ помогу тебе быстро создать опрос и собрать ответы прямо здесь, в Telegram! 🎯",
        "button_text": "Погнали! 🚀"
    },
    "en": {
        "start_message": "Hello, @{username}! 👋\nI will help you quickly create a survey and collect responses right here in Telegram! 🎯",
        "button_text": "Let's go! 🚀"
    },
    "uk": {
        "start_message": "Привіт, @{username}! 👋\nЯ допоможу тобі швидко створити опитування та зібрати відповіді прямо тут, у Telegram! 🎯",
        "button_text": "Почнемо! 🚀"
    }
}

def get_translation(language_code: str, key: str, **kwargs):
    lang = translations.get(language_code, translations["en"])
    return lang[key].format(**kwargs)

@dp.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    language_code = message.from_user.language_code

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

    start_message = get_translation(language_code, "start_message", username=message.from_user.username)
    button_text = get_translation(language_code, "button_text")

    await message.answer(start_message, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(button_text, web_app=WebAppInfo(url="https://eesyquizy.vercel.app/"))]
    ]))

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')