from aiogram import types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
import os

CHAT_ID = os.environ['CHAT_ID']
SUPPORT = os.environ['SUPPORT']

class Form(StatesGroup):
    waiting_for_tz = State()
    waiting_for_price = State()

async def order_service_handler(callback_query: types.CallbackQuery, state: FSMContext):
    message_text = "*Замечательно! 🎉*\n\nДля дальнейшей работы, пожалуйста, предоставьте техническое задание, которое нужно будет выполнить. Это важно для точного понимания ваших потребностей."
    
    if callback_query.message.text:
        try:
            await callback_query.bot.edit_message_text(
                text=message_text,
                chat_id=callback_query.message.chat.id,
                message_id=callback_query.message.message_id,
                parse_mode="Markdown"
            )
        except Exception as e:
            await callback_query.answer(f"Ошибка при редактировании сообщения: {str(e)}")
    else:
        await callback_query.bot.send_message(
            chat_id=callback_query.message.chat.id,
            text=message_text,
            parse_mode="Markdown"
        )
    
    await state.set_state(Form.waiting_for_tz)

async def process_tz(message: types.Message, state: FSMContext):
    await state.update_data(tz=message.text)
    await state.set_state(Form.waiting_for_price)
    await message.answer(
        ("*Спасибо за предоставленное техническое задание!*\n\n"
        "Теперь укажите, пожалуйста, цену, которую Вы готовы выделить на эту услугу. Это важно для дальнейшего обсуждения."), 
        parse_mode='markdown')

async def process_price(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tz = user_data.get('tz')
    price = message.text
    user_id = message.from_user.id

    try:
        price = int(price)
    except ValueError:
        await message.answer("*Ошибка:* Пожалуйста, введите корректное число", parse_mode='markdown')
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[[ 
        InlineKeyboardButton(text='✅ Одобрить', callback_data=f'approve_{user_id}'),
        InlineKeyboardButton(text='❌ Отклонить', callback_data=f'reject_{user_id}'),
    ]])

    message_text = (f"*📋 Техническое задание:* {tz}\n\n"
                    f"*💰 Цена:* {price}\n\n"
                    f"*❓ От:* @{message.from_user.username}\n\n"
                    f"*🕔 Дата:* {current_time}")

    try:
        await message.bot.send_message(
            chat_id=CHAT_ID,
            text=message_text,
            parse_mode="Markdown",
            reply_markup=kb
        )
    except Exception as e:
        await message.answer(f"Ошибка при отправке сообщения: {str(e)}")
        return

    await message.answer(
        (f"*Уважаемый(ая) {message.from_user.username},*\n\n"
        "Благодарим вас за ваше обращение.\n\n"
        "Ваше задание было успешно отправлено. Мы приступим к его выполнению в ближайшее время и будем держать вас в курсе всех этапов.\n\n"
        "Если у вас есть дополнительные вопросы или уточнения, не стесняйтесь обращаться.\n\n"
        "*С уважением,*\n*Sparkle Market*"),
        parse_mode='markdown')

async def process_approve(callback_query: types.CallbackQuery):
    user_id = callback_query.data.split('_')[1]

    try:
        await callback_query.bot.send_message(chat_id=user_id, text=f"*✅ Ваша заявка одобрена!*\n\nПожалуйста, свяжитесь с {SUPPORT} для дальнейших инструкций.", parse_mode='markdown')
        await callback_query.bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="✅ Заявка одобрена!",
            reply_to_message_id=callback_query.message.message_id,
            parse_mode="Markdown"
        )
    except Exception as e:
        await callback_query.answer(f"Ошибка при отправке сообщения: {str(e)}")

async def process_reject(callback_query: types.CallbackQuery):
    user_id = callback_query.data.split('_')[1]

    try:
        await callback_query.bot.send_message(chat_id=user_id, text="😞 К сожалению, ваша заявка была *отклонена*. Если вам нужна помощь или разъяснения, пишите нам!")
        await callback_query.bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="❌ Заявка отклонена!",
            reply_to_message_id=callback_query.message.message_id,
            parse_mode="Markdown"
        )
    except Exception as e:
        await callback_query.answer(f"Ошибка при отправке сообщения: {str(e)}")
