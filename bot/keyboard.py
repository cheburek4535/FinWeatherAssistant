from sqlalchemy.orm.sync import update
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from database.crud import get_daily_mode

def get_main_keyboard(update: Update):
    if update.effective_user.id != 6278046215:
        return ReplyKeyboardMarkup([
            ["🌤️ Получить погоду", "💵 Курс валют"],
            ["📔 История запросов", "📬 Рассылка"],
            ["📖 Дополнительно", "🎖️ Premium"],
            ["👾 Баг-репорт"]
        ], resize_keyboard=True)
    else:
        return ReplyKeyboardMarkup([
            ["🌤️ Получить погоду", "💵 Курс валют"],
            ["📔 История запросов", "📬 Рассылка"],
            ["📖 Дополнительно", "🎖️ Premium"],
            ["👾 Баг-репорт", "👽Dev-Tools"]
        ], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_photo(photo='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSX-mgYlbGEvb5zHDa1TikrQUqFYNafIborng&s',
       caption= f"<b>Привет, {user.first_name}! Я твой финансово-погодный ассистент.</b>",
        reply_markup=get_main_keyboard(update), parse_mode=ParseMode.HTML
    )
    dm = get_daily_mode(update.effective_user.name)
    if dm == 'ON':
        context.user_data['daily_mode'] = 'ON'
    elif dm == 'OFF':
        context.user_data['daily_mode'] = 'OFF'
    else:
        context.user_data['daily_mode'] = 'OFF'
    context.user_data['daily_valute'] = None

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


def get_help_keyboard():
    keyboard = [
        [InlineKeyboardButton("Инструкция по боту", callback_data='give_instruction')],
         [InlineKeyboardButton("Список всех валют", callback_data='give_all_valutes'),]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup