from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes, CallbackQueryHandler, JobQueue
from api.weather_api import get_weather, weather_api_key
from api.currency import get_currency_rates
from database.crud import save_request, show_story, save_daily_config, get_daily_mode, save_daily_mode
from bot.keyboard import get_main_keyboard, start, get_currency_keyboard, get_location_keyboard, get_inline_currency_keyboard, get_help_keyboard
from api.geolocation import handle_location
from api.timezone import get_local_time_by_city
from bot.daily import button_handler, daily_handler, send_daily_job
import csv
from pathlib import Path
import json
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger


# Обработчик кнопки погода
async def weather_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Введите название города,\nили отправьте геолокацию:", reply_markup=get_location_keyboard())
    context.user_data['waiting_for'] = 'weather_city'

# обработчик кнопки курсы валют
async def currency_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Введите название валюты в родительном падеже,\nили выберите из списка:", reply_markup=get_currency_keyboard())
    context.user_data['waiting_for'] = 'currency_valute'

async def story_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    story = show_story(user_id)
    if story:
        response = (

            "\n".join(story)
        )
    else:
        response = "Не удалось получить данные об истории запросов 😔."

    await update.message.reply_text(response, reply_markup=get_main_keyboard())




#async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_data = context.user_data
    get_main_keyboard()
    user_data['waiting_for'] = None

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #await update.message.reply_text('Инструкция по взаимодействию с ботом:\n1.Кнопки "Получить погоду" и "Курс валют" позволяют узнать погоду по городу который вы введете или отправите геолокацию и получить курс валют по названию')
    await update.message.reply_text("Ниже приведены кнопки для получения инструкции по взаимодейтсвию с ботом\nА также список всех валют, курсы которых которые можно можно запросить у бота.\n"
                                    "Если у вас возникли другие вопросы, вы можете связаться напрямую с разработчиком через кнопку 'Баг-репорт.'", reply_markup=get_help_keyboard())


async def premium_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Эта функция пока недоступна, ожидайте в ближайшем обновлении.")
async def bug_report_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Пожалуйста, опишите обнаруженный вами баг или ошибку.\nСообщение отправится разработчику, и проект станет лучше✨.\nБудем благодарны за подробное описание!")
    context.user_data['waiting_for'] = 'bug_report'
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
                f"💧Влажность: {weather_data['humidity']}\n"
                f"🕒Местное время: {get_local_time_by_city(text)}"
            )
            save_request(
                user_id=update.effective_user.id,
                user_name=update.effective_user.name,
                req_type="weather",
                req_data=text,
                resp_data=response
            )
        else:
             response = "Не удалось получить данные о погоде 😔.\nПожалуйста, проверьте правильность написания названия города!"
        if text == "⬅️Назад":
            response = "Возвращено назад"
        await update.message.reply_text(response, reply_markup=get_main_keyboard())
        user_data['waiting_for'] = None


    elif user_data.get("waiting_for") == "currency_valute":
        if text == "€ Евро 💶":
            currency_data = get_currency_rates('евро')
        elif text == "$ Доллар 💵":
            currency_data = get_currency_rates('доллар')
        elif text == "£ Фунт стерлингов 💷":
            currency_data = get_currency_rates("фунт стерлингов")
        elif text == "¥ Юань 💴":
            currency_data = get_currency_rates("юань")
        else:
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
                user_name=update.effective_user.name,
                req_type='currency',
                req_data=str(text),
                resp_data=response
            )

        else:


            response = "Не удалось получить данные о курсах валют 😔.\nПожалуйста, проверьте правильность написания названия валюты!\nПравильные названия валют для запроса есть во вкладке Дополнительно->Список всех валют."

        if text == "⬅️Назад":
            response = "Возвращено назад"

        await update.message.reply_text(response, reply_markup=get_main_keyboard())
        user_data['waiting_for'] = None




    elif user_data.get("waiting_for") == "confirm_daily_city":

        file_path = Path(__file__).parent.parent / 'database' / 'city.csv'
        cities = set()
        with open(file_path, 'r', encoding='cp1251', newline='') as csvfile:

            reader = csv.DictReader(csvfile, delimiter=';')

            for row in reader:
                city_name = row['name']

                cities.add(city_name)

        user_city = text[0].upper() + text[1:]

        if user_city in cities:
            user_data["daily_city"] = user_city
            user_data["waiting_for"] = None

            if user_data['daily_type'] == 'weather':
                  daily_type_for_message = "Погода"
                  valute_for_message = "."

            elif user_data['daily_type'] == 'currency':
                    daily_type_for_message = "Курсы валют"
                    valute_for_message = f"Валюта: {user_data['daily_valute']}"
            elif user_data['daily_type'] == 'both':

                    daily_type_for_message = "Погода и валюта"
                    valute_for_message = f", Валюта: {user_data['daily_valute']}"
            else:

                    daily_type_for_message = None
                    valute_for_message = None
            save_daily_config(

                    user_id=update.effective_user.id,
                    user_name=update.effective_user.name,
                    chat_id=update.effective_chat.id,
                    daily_type=user_data['daily_type'],
                    city=user_city,
                    valute=user_data['daily_valute'] if user_data['daily_valute'] is not None else 'NULL',
                    daily_schedule=user_data['daily_schedule'],

                )

            await update.message.reply_text(
                    f'Отлично! Настройка рассылки завершена.\n Tип: "{daily_type_for_message}", город: "{user_data['daily_city']}"{valute_for_message}\n'
                    f'Теперь вы можете отменить рассылку или добавить свое время и несколько валют и городов для рассылок\n'
                    f' (доступно только премиум пользователям)', reply_markup=get_main_keyboard())
            user_data['daily_city'] = None
            user_data['daily_valute'] = None
            user_data['daily_mode'] = 'ON'
            save_daily_mode(user_name=update.effective_user.name, user_id=update.effective_user.id, daily_mode=user_data['daily_mode'])

        else:

            await update.message.reply_text("Город не найден. Проверьте правильность написания.")



    elif user_data['waiting_for'] == 'confirm_daily_valute':


        user_data['daily_valute'] = text
        if user_data['daily_type'] == 'both':

            await update.message.reply_text(
                text="Теперь напишите название города для рассылки:")


            user_data['waiting_for'] = 'confirm_daily_city'

        else:
            user_data["waiting_for"] = None
            if user_data['daily_type'] == 'weather':
                daily_type_for_message = "Погода"
            elif user_data['daily_type'] == 'currency':
                daily_type_for_message = "Курсы валют"
            elif user_data['daily_type'] == 'both':
                daily_type_for_message = "Погода и валюта"
            else:
                daily_type_for_message = None
            if user_data.get('daily_city') is not None and user_data.get('daily_city') != '':
                city = user_data['daily_city']
            else:
                city = 'NULL'

            save_daily_config(

                user_id=update.effective_user.id,
                user_name=update.effective_user.name,
                chat_id=update.effective_chat.id,
                daily_type=user_data['daily_type'],
                city=city,
                valute=text,
                daily_schedule=user_data['daily_schedule'],

            )

            await update.message.reply_text(

                f'Отлично! Настройка рассылки завершена.\n Tип: "{daily_type_for_message}", валюта: "{user_data['daily_valute']}"\n'
                f'Теперь вы можете отменить рассылку или добавить свое время и несколько валют и городов для рассылок\n'
                f' (доступно только премиум пользователям)', reply_markup=get_main_keyboard())
            user_data['daily_valute'] = None
            user_data['daily_city'] = None
            user_data['daily_mode'] = 'ON'
            save_daily_mode(user_name=update.effective_user.name, user_id=update.effective_user.id, daily_mode=user_data['daily_mode'])

    elif user_data['waiting_for'] == 'bug_report':
        user_name = update.effective_user.name
        await context.bot.send_message(chat_id=6278046215, text=f"Великий и многоуважаемый разработчик!\nВам репорт от юзера {user_name}:\n{text}")
        await update.message.reply_text("Репорт отправлен! Спасибо за участие в развитии проекта!")
        user_data['waiting_for'] = None







def init_scheduler(application):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        send_daily_job,
        trigger=CronTrigger(hour=9, minute=0),
        args=[application, 'Mon']
    )

    scheduler.add_job(
        send_daily_job,
        trigger=CronTrigger(hour=13, minute=30),
        args=[application, 'Aft']
    )

    scheduler.add_job(
        send_daily_job,
        trigger=CronTrigger(hour=18, minute=0),
        args=[application, 'Evn']
    )

    scheduler.start()
    return scheduler
#async def debug_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #print(f"Получено сообщение: {update.message.text}")
    #await update.message.reply_text(f"Вы прислали: {update.message.text}")


def main() -> None:
    application = ApplicationBuilder().token("8358394327:AAH6aKjwnjL16fcWyA4P4M7Bp8CyMRdAuGU").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_handler))

    scheduler = init_scheduler(application)

    application.add_handler(MessageHandler(filters.Regex("^🌤️ Получить погоду$"), weather_handler))
    application.add_handler(MessageHandler(filters.Regex("^💵 Курс валют$"), currency_handler))
    application.add_handler(MessageHandler(filters.Regex("^📔 История запросов$"), story_handler))
    application.add_handler(MessageHandler(filters.Regex("^📬 Рассылка$"), daily_handler))
    application.add_handler(MessageHandler(filters.Regex("^📖 Дополнительно$"), help_handler))
    application.add_handler(MessageHandler(filters.Regex("^🎖️ Premium$"), premium_handler))
    application.add_handler(MessageHandler(filters.Regex("^👾 Баг-репорт$"), bug_report_handler))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))



    application.run_polling(stop_signals=None)
    scheduler.shutdown()



if __name__ == '__main__':
    main()