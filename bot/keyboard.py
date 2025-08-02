from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes

def get_main_keyboard():
    return ReplyKeyboardMarkup([
        ["🌤️ Получить погоду", "💵 Курс валют"],
        ["📊 История запросов", "⚙️ Настройки"]
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
        ['¥ Юань 💴', '£ Фунт стерлингов 💷']
    ], resize_keyboard=True)

def get_location_keyboard():
    keyboard = [
        [KeyboardButton(text="Отправить мой город", request_location=True)]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

