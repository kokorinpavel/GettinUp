import asyncio
import csv
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = "8173165112:AAG_txoWZxJF-20Hi9Y1xpMhgGI-JdvplGQ"
REQUIRED_CHANNELS_STR = "@grnwdzz, @drugazinearchives"
REQUIRED_CHANNELS = REQUIRED_CHANNELS_STR.split(', ')
PRESAVE_LINK = "https://band.link/gettingup"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

DATA_FILE = "participants.csv"


async def main():
    await dp.start_polling(bot)


def save_user(user_id, username):
    with open(DATA_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([user_id, username, datetime.now().isoformat()])


async def check_subscriptions(user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status == 'left':
                logger.info(f"User {user_id} not subscribed to {channel}")
                return False
        except Exception as e:
            logger.error(f"Error checking subscription to {channel}: {e}")
            return False
    return True


@dp.message(Command('start'))
async def start(message: types.Message):
    channels_text = "\n".join(REQUIRED_CHANNELS)
    markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Следующий шаг➡️", callback_data="check_subs")]])
    await message.answer(f'Привет! Для начала, пожалуйста, проверь подписку на следующие каналы:\n'
                         f'{channels_text}', reply_markup=markup)


@dp.callback_query(lambda c: c.data == 'check_subs')
async def process_subscription_check(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username
    is_subscribed = await check_subscriptions(user_id)

    if is_subscribed:
        save_user(user_id, username)
        markup = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Сделать пресейв 💿", url=PRESAVE_LINK)]])

        await callback_query.message.answer(
            "Спасибо за подписку! Для участия в розыгрыше нужно сделать пресейв релиза в Яндекс Музыке. Жми на кнопку и переходи по ссылке.",
            reply_markup=markup
        )
    else:
        channels_text = "\n".join(REQUIRED_CHANNELS)
        markup = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Готово ✅", callback_data="check_subs")]])
        await callback_query.message.answer(
            f"К сожалению, ты не подписан(а) на все каналы. Пожалуйста, подпишись на:\n{channels_text}\nи попробуй ещё раз.",
            reply_markup=markup
        )

    await callback_query.answer()


if __name__ == '__main__':
    asyncio.run(main())
