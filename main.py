import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from scripts.order_service import order_service_handler, process_tz, process_price, process_approve, process_reject, Form as OrderForm
from scripts.ask_question import ask_question_handler, process_ask, answer_question_handler, process_answer, Form as AskForm

TOKEN = os.environ['TOKEN']
banner_url = "https://i.imgur.com/5gSZmyL.gif"
bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dp.message(Command("start"))
async def command_start(message: types.Message):
    text = """
*👋 Привет!*

Ты находишься в боте, который поможет тебе:

*• Заказать услугу программиста*

*• Задать вопрос разработчику*

*Пожалуйста, выбери одну из кнопок ниже:*
"""

    kb = InlineKeyboardMarkup(inline_keyboard=[[ 
        InlineKeyboardButton(text='💸 Заказать услугу', callback_data='order_service'), 
        InlineKeyboardButton(text='❓ Задать вопрос', callback_data='ask_question')
    ],
    [
        InlineKeyboardButton(text='📰 Отзывы', callback_data='feedback', url='https://t.me/+_cPkHKe_uaZjNzY6')
    ]])

    await bot.send_animation(
        message.chat.id,
        banner_url,
        caption=text,
        parse_mode="Markdown",
        reply_markup=kb
    )


@dp.callback_query(lambda c: c.data == 'order_service')
async def process_callback_order(callback_query: types.CallbackQuery, state):
    await order_service_handler(callback_query, state)

@dp.callback_query(lambda c: c.data == 'ask_question')
async def process_callback_ask(callback_query: types.CallbackQuery, state):
    await ask_question_handler(callback_query, state)

# Заказ услуг
dp.message(OrderForm.waiting_for_tz)(process_tz)
dp.message(OrderForm.waiting_for_price)(process_price)
dp.callback_query(lambda c: c.data.startswith('approve_'))(process_approve)
dp.callback_query(lambda c: c.data.startswith('reject_'))(process_reject)

# Ответы на вопрос
dp.message(AskForm.waiting_for_ask)(process_ask)
dp.callback_query(lambda c: c.data.startswith('answer_'))(answer_question_handler)
dp.message(AskForm.waiting_for_answer)(process_answer)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
