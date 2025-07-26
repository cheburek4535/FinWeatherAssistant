import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
logging.basicConfig(
    'format=%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_main_keyboard():
    return ReplyKeyboardMarkup([
        ["🌤️ Получить погоду", "💵 Курс валют"],
        ["📊 История запросов", "⚙️ Настройки"]
    ], resize_keyboard=True)

def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_text(
        f"Привет, {user.first_name}!, Я твой финансово-погодный ассистент.",
        reply_markup=get_main_keyboard()
    )

def main() -> None:
    updater = Updater("8358394327:AAH6aKjwnjL16fcWyA4P4M7Bp8CyMRdAuGU")
    dispatcher = updater.dispatcher

