import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes

import api.weather_api


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_main_keyboard():
    return ReplyKeyboardMarkup([
        ["🌤️ Получить погоду", "💵 Курс валют"],
        ["📊 История запросов", "⚙️ Настройки"]
    ], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! Я твой финансово-погодный ассистент. {api.weather_api.get_weather("Москва", api.weather_api.weather_api_key)}",
        reply_markup=get_main_keyboard()
    )

def main() -> None:
    application = ApplicationBuilder().token("8358394327:AAH6aKjwnjL16fcWyA4P4M7Bp8CyMRdAuGU").build()

    application.add_handler(CommandHandler("start", start))

    application.run_polling()


if __name__ == '__main__':
    main()
