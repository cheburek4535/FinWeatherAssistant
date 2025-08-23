from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


def get_main_keyboard():
    return ReplyKeyboardMarkup([
        ["🌤️ Получить погоду", "💵 Курс валют"],
        ["📔 История запросов", "📬 Рассылка"],
        ["📖Дополнительно"]
    ], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! Я твой финансово-погодный ассистент.",
        reply_markup=get_main_keyboard()
    )

def get_currency_keyboard():
    return ReplyKeyboardMarkup([
        ['$ Доллар 💵', '€ Евро 💶'],
        ['¥ Юань 💴', '£ Фунт стерлингов 💷'],
        ['⬅️Назад']
    ], resize_keyboard=True)

def get_inline_currency_keyboard():
    keyboard = [
        [InlineKeyboardButton('$ Доллар 💵', callback_data='доллар'),
        InlineKeyboardButton('€ Евро 💶', callback_data='евро')],
        [InlineKeyboardButton('¥ Юань 💴', callback_data='юань'),
         InlineKeyboardButton('£ Фунт стерлингов 💷', callback_data='фунт стерлингов')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def get_location_keyboard():
    keyboard = [
        [KeyboardButton(text="Отправить мой город", request_location=True)],
        ['⬅️Назад']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_story_keyboard():
    return ReplyKeyboardMarkup([
        ['Получить историю запросов'],
        ['⬅️Назад']
    ], resize_keyboard=True)

def get_add_keyboard():
    return ReplyKeyboardMarkup([
        ['📊Список всех валют с курсами']
    ], resize_keyboard=True)


