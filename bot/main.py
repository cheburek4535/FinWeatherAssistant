from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes

from api.weather_api import get_weather, weather_api_key
from api.currency import get_currency_rates
from database.crud import save_request


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




# Обработчик кнопки погода
async def weather_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Введите название города:")
    context.user_data['waiting_for'] = 'weather_city'

# обработчик кнопки курсы валют
async def currency_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Введите название валюты:")
    context.user_data['waiting_for'] = 'currency_valute'

async def story_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['waiting_for'] = 'story'
# Обработчик текстовых сообщений
async def handle_message(update: Update, context: CallbackContext) -> None:
    user_data = context.user_data
    text = update.message.text

    if user_data.get('waiting_for') == 'weather_city':
        # Получаем погоду для введеного города
        weather_data = get_weather(text, weather_api_key)

        if weather_data:
            response = (
                f"🌆Погода в городе {weather_data['city']}:\n"
                f"🌡️Температура: {weather_data['temp']}°C\n"
                f"🤗Ощущается как: {weather_data['feels_like']}°C\n"
                f"🌥️Общее состояние: {weather_data['description']}\n"
                f"💧Влажность: {weather_data['humidity']}%"
            )
            save_request(
                user_id=update.effective_user.id,
                req_type="weather",
                req_data=text,
                resp_data=response
            )
        else:
            response = "Не удалось получить данные о погоде 😔.\nПожалуйста, проверьте правильность написания названия города!"

        await update.message.reply_text(response, reply_markup=get_main_keyboard())
        user_data['waiting_for'] = None


    elif user_data.get("waiting_for") == "currency_valute":
        currency_data = get_currency_rates(text)

        if currency_data:
            response = (
                f"💱Курс валюты: {currency_data['name']}:\n"
                f"🕒Время: {currency_data['timestamp'][11:16]}\n"
                f"💰Текущий курс: {currency_data['rate']:.2f}₽\n"
                f"⏳Предыдущий курс: {currency_data['previous']:.2f}₽\n"
                f"📈Изменение на {(currency_data['rate'] - currency_data['previous']):.2f}₽ ({((currency_data['rate'] * 100) / currency_data['previous']) - 100:.2f}%)"
            )

            save_request(
                user_id=update.effective_user.id,
                req_type='currency',
                req_data=text,
                resp_data=response
            )
        else:
            response = "Не удалось получить данные о курсах валют 😔.\nПожалуйста, проверьте правильность написания названия валюты!"

        await update.message.reply_text(response, reply_markup=get_main_keyboard())
        user_data['waiting_for'] = None

    #elif user_data.get('waiting_for') == "srory":
       #story =



#async def debug_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #print(f"Получено сообщение: {update.message.text}")
    #await update.message.reply_text(f"Вы прислали: {update.message.text}")

def main() -> None:
    application = ApplicationBuilder().token("8358394327:AAH6aKjwnjL16fcWyA4P4M7Bp8CyMRdAuGU").build()
    application.add_handler(CommandHandler("start", start))


    application.add_handler(MessageHandler(filters.Regex("^🌤️ Получить погоду$"), weather_handler))
    application.add_handler(MessageHandler(filters.Regex("^💵 Курс валют$"), currency_handler))

    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    application.run_polling()



if __name__ == '__main__':
    main()