import logging
import settings
import timetable_parser as p
import scheduler
import asyncio

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# Configure logging
logging.basicConfig(level=logging.INFO)


# Initialize bot and dispatcher
bot = Bot(token=settings.TG_TOKEN)
dp = Dispatcher(bot)


# Configure keyboard
button_timetable = KeyboardButton('Расписание')
timetable_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(button_timetable)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply(f"Hi!\nI'm EchoBot!\nPowered by aiogram.", reply_markup=timetable_kb)


@dp.message_handler()
async def send_timetable(message: types.Message):
    if message.text == 'Расписание':
        await message.answer(p.get_current_timetable())
    else:
        pass


async def send_notification(message):
    # TODO: добавить возможность работы с несколькими пользователями.
    #  Для этого нужно где-то хранить все id пользователей и отправлять уведомление всем сохраненным пользователям.
    await bot.send_message(859281521, f'Расписание изменилось!\n {message}')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler.scheduler())
    executor.start_polling(dp, skip_updates=True)