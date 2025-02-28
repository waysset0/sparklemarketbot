from aiogram import types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime

CHAT_ID = os.environ['CHAT_ID']

class Form(StatesGroup):
    waiting_for_ask = State()
    waiting_for_answer = State()

async def ask_question_handler(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await callback_query.bot.edit_message_text(
            text="*👋 Здравствуй!*\n\nОтлично, давай двигаться дальше. Напиши, пожалуйста, свой вопрос!",
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            parse_mode="Markdown"
        )
    except Exception as e:
        await callback_query.message.answer(
            "*👋 Здравствуй!*\n\nОтлично, давай двигаться дальше. Напиши, пожалуйста, свой вопрос!", parse_mode='markdown'
        )
    
    await state.set_state(Form.waiting_for_ask)

async def process_ask(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_username = message.from_user.username
    question_text = message.text
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    await state.update_data(question=question_text, user_id=user_id)
    
    await message.answer(
        f"*Уважаемый(ая) {user_username},*\n\n"
        "Спасибо за предоставленный вопрос. Мы внимательно его рассмотрим. Ожидайте ответа в ближайшее время.\n\n"
        "*С уважением,* \n*Sparkle Market*",
        parse_mode='Markdown'
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[[ 
        InlineKeyboardButton(text='❗ Ответить', callback_data=f'answer_{user_id}')
    ]])

    message_text = (f"*📋 Вопрос:* {question_text}\n\n"
                    f"*❓ От:* @{user_username}\n\n"
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

async def answer_question_handler(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        user_id = int(callback_query.data.split('_')[1])
        await callback_query.message.answer("Ответьте на вопрос.")
        await state.set_state(Form.waiting_for_answer)
        await state.update_data(answering_user_id=user_id)
    except Exception as e:
        await callback_query.message.answer(f"Ошибка при обработке запроса: {str(e)}")

async def process_answer(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    answering_user_id = user_data.get('answering_user_id')

    if answering_user_id:
        try:
            await message.bot.send_message(
                answering_user_id,
                f"*Пришёл ответ от разработчика на ваш вопрос:*\n\n{message.text}",
                parse_mode="Markdown"
            )
            await message.bot.send_message(
                CHAT_ID,
                f"Ответ был отправлен пользователю @{message.from_user.username}.",
                parse_mode="Markdown"
            )
        except Exception as e:
            await message.answer(f"Ошибка при отправке ответа пользователю: {str(e)}")
    else:
        await message.answer("Ошибка: Не удалось найти пользователя, которому нужно отправить ответ.")
