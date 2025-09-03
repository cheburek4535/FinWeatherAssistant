from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes, CallbackQueryHandler, JobQueue
from api.weather_api import get_weather, weather_api_key
from api.currency import get_currency_rates
from database.crud import save_request, show_story, save_daily_config, save_daily_mode
from bot.keyboard import get_main_keyboard, start, get_currency_keyboard, get_location_keyboard, get_help_keyboard
from api.geolocation import handle_location
from api.timezone import get_local_time_by_city
from bot.daily import button_handler, daily_handler, send_daily_job
import csv
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio

# Обработчик кнопки погода
async def weather_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Введите название города,\nили отправьте <u>геолокацию</u>:", reply_markup=get_location_keyboard(update), parse_mode=ParseMode.HTML)
    context.user_data['waiting_for'] = 'weather_city'

# обработчик кнопки курсы валют
async def currency_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Введите название валюты\nили выберите из <u>списка</u>:", reply_markup=get_currency_keyboard(update), parse_mode=ParseMode.HTML)
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

    await update.message.reply_text(response, reply_markup=get_main_keyboard(update))




async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #await update.message.reply_text('Инструкция по взаимодействию с ботом:\n1.Кнопки "Получить погоду" и "Курс валют" позволяют узнать погоду по городу который вы введете или отправите геолокацию и получить курс валют по названию')
    await update.message.reply_text("<b>Ниже</b> приведены кнопки для получения <u>инструкции</u> по взаимодейтсвию с ботом\nА также <u>список</u> всех валют, курсы которых которые можно можно запросить у бота.\n"
                                    "Если у вас возникли другие вопросы, вы можете связаться напрямую с разработчиком через кнопку <u>'Баг-репорт'</u>.", reply_markup=get_help_keyboard(), parse_mode="HTML")


async def premium_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Эта функция пока недоступна, ожидайте в ближайшем обновлении.")


async def bug_report_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != 5449932947:
        await update.message.reply_text("Пожалуйста, опишите обнаруженный вами <b>баг</b> или <b>ошибку</b>.\nСообщение отправится разработчику, и проект станет <b>лучше</b>✨.\nБудем благодарны за подробное описание!", parse_mode="HTML")
    else:
        await update.message.reply_text(
            "<b>Тима, ты заебал иди нахуй членосос, ладно без негатива, удиви меня кинь какую нибудь хуйню типа это баг репорт</b>", parse_mode="HTML")
    context.user_data['waiting_for'] = 'bug_report'

async def dev_tools_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Великий и всемогущий прекрасный разработчик!\nВведите id или никнейм юзера для сами знаете чего.")
    context.user_data['waiting_for'] = 'dev_tools_confirm_id'
    context.user_data['id_for_devtools'] = None


# Обработчик текстовых сообщений
async def handle_message(update: Update, context: CallbackContext) -> None:
    user_data = context.user_data
    text = update.message.text

    if user_data.get('waiting_for') == 'weather_city':
        # Получаем погоду для введеного города

        weather_data = get_weather(text, weather_api_key)
        if weather_data:
            response = (
                f"🌆<i>Погода в городе {weather_data['city']}:</i>\n"
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

            if 'дождь' in weather_data['description']:
                photo = 'https://imgs.search.brave.com/FrAZSxk-OcJL9rgq5bqWVaYwxWahT99uJueKpmBnGL0/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9tZWRp/YS5pc3RvY2twaG90/by5jb20vaWQvMTQ3/NjE4OTk4My9waG90/by9zdW1tZXItcmFp/bi1yYWluZHJvcHMt/YmFkLXdlYXRoZXIt/ZGVwcmVzc2lvbi5q/cGc_cz02MTJ4NjEy/Jnc9MCZrPTIwJmM9/SXdKWGQyYms1TzY1/YUY1WFp3b0ItV0pp/RnBDSXJtYlpsdGdi/UVRYTk5raz0'
            elif 'пасмурно' in weather_data['description'] or 'облачность' in weather_data['description'] or 'облачно' in weather_data['description']:
                photo = 'https://imgs.search.brave.com/bfTijEBuXl5-ByeGFU8RyVwxFXKcA7AlIJYEkQ2zyI4/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly95Ymlz/LnJ1L3dwLWNvbnRl/bnQvdXBsb2Fkcy8y/MDIzLzA5L3Bhc211/cm5vZS1uZWJvLTEz/LndlYnA'
            elif 'ясно' in weather_data['description'] or 'солнце' in weather_data['description'] or 'солнечно' in weather_data['description']:
                photo = 'https://imgs.search.brave.com/94yUO0S20ReZBvTMh-HhW4cuYDkYHCQaCsLGZA53jDw/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9tZWRp/YS5pc3RvY2twaG90/by5jb20vaWQvMTA0/Njg1MTIzOC9ydS8l/RDElODQlRDAlQkUl/RDElODIlRDAlQkUv/JUQxJTgxJUQwJUJF/JUQwJUJCJUQwJUJE/JUQxJTg2JUQwJUI1/LSVEMSU4MSVEMCVC/MiVEMCVCNSVEMSU4/MiVEMCVCOCVEMSU4/Mi0lRDAlQkQlRDAl/QjAtJUQxJTg0JUQw/JUJFJUQwJUJEJUQw/JUI1LSVEMCVCMyVE/MCVCRSVEMCVCQiVE/MSU4MyVEMCVCMSVE/MCVCRSVEMCVCMyVE/MCVCRS0lRDAlQkQl/RDAlQjUlRDAlQjEl/RDAlQjAuanBnP2I9/MSZzPTYxMng2MTIm/dz0wJms9MjAmYz1m/RjFFSE9mMm9PcHJK/cFBUMm9EQl9iV3Nh/ZEVTYWt2elRSUzBv/V3AxZHhVPQ'
            elif 'снег' in weather_data['description'] or 'снегопад' in weather_data['description']:
                photo = 'https://imgs.search.brave.com/lrSBDeUU8sGJBhbdq-7St7FOjo_tAEHHTW2BqoIPz8c/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9zdC5k/ZXBvc2l0cGhvdG9z/LmNvbS8xMDQzMDcz/LzMwNDAvaS82MDAv/ZGVwb3NpdHBob3Rv/c18zMDQwMDMxNy1z/dG9jay1waG90by1z/bm93LmpwZw'
            else:
                photo = 'https://imgs.search.brave.com/2yaqlZEQTb8edAq9CWgvkAkyjaD5K0M_loUCkzuXHN8/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9tZWRp/YS5pc3RvY2twaG90/by5jb20vaWQvNTAz/NDk1MzUyL3J1LyVE/MSU4NCVEMCVCRSVE/MSU4MiVEMCVCRS8l/RDElODElRDAlQkYl/RDElODMlRDElODIl/RDAlQkQlRDAlQjgl/RDAlQkElRDAlQkUl/RDAlQjIlRDAlQkUl/RDAlQjUtYXJyYXkt/dmxhLmpwZz9zPTYx/Mng2MTImdz0wJms9/MjAmYz1XRDFhOEMw/Q2tUZG8tMlVGQzJy/RlVqVUFaVExER192/bUZuMmlNeV9CNkd3/PQ'

            await update.message.reply_photo(photo=photo, caption=response, reply_markup=get_main_keyboard(update), parse_mode=ParseMode.HTML)
        else:
            if text != "⬅️Назад":
                response = "Не удалось получить данные о погоде 😔.\nПожалуйста, проверьте правильность написания названия города!"
                await update.message.reply_text(response, reply_markup=get_main_keyboard(update))


        if text == "⬅️Назад":
            response = "Возвращено назад"
            await update.message.reply_text(response, reply_markup=get_main_keyboard(update))


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
            await update.message.reply_photo(photo="https://memepedia.ru/wp-content/uploads/2019/06/stonks-template.png", caption=
                f"💱Курс валюты: {currency_data['name']}:\n"
                f"🕒Время: {currency_data['timestamp'][11:16]}\n"
                f"💰Текущий курс: {currency_data['rate']:.2f}₽\n"
                f"⏳Предыдущий курс: {currency_data['previous']:.2f}₽\n"
                f"📈Изменение за полдня на {(currency_data['rate'] - currency_data['previous']):.2f}₽ ({((currency_data['rate'] * 100) / currency_data['previous']) - 100:.2f}%)",
                                             reply_markup=get_main_keyboard(update)
            )

            save_request(
                user_id=update.effective_user.id,
                user_name=update.effective_user.name,
                req_type='currency',
                req_data=str(text),
                resp_data=f"💱Курс валюты: {currency_data['name']}:\n"
                f"🕒Время: {currency_data['timestamp'][11:16]}\n"
                f"💰Текущий курс: {currency_data['rate']:.2f}₽\n"
                f"⏳Предыдущий курс: {currency_data['previous']:.2f}₽\n"
                f"📈Изменение за полдня на {(currency_data['rate'] - currency_data['previous']):.2f}₽ ({((currency_data['rate'] * 100) / currency_data['previous']) - 100:.2f}%)"
            )

        else:


            response = f"Валюта {text} <b>не найдена.<b>\nВы можете посмотреть <i>список</i> всех валют с верным написанием во вкладке <b>Дополнительно->Список всех валют</b>."

        if text == "⬅️Назад":
            response = "Возвращено назад"

        if response:
            await update.message.reply_text(response, reply_markup=get_main_keyboard(update), parse_mode='HTML')
        user_data['waiting_for'] = None




    elif user_data.get("waiting_for") == "confirm_daily_city":

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(BASE_DIR, '..', 'database', 'city.csv')
        file_path = os.path.abspath(file_path)

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
                    valute=user_data.get('daily_valute') if user_data.get('daily_valute') is not None else 'NULL',
                    daily_schedule=user_data['daily_schedule'],

                )

            await update.message.reply_text(
                    f'Отлично! Настройка рассылки <b>завершена<b>.\n Tип: "{daily_type_for_message}", город: "{user_data['daily_city']}"{valute_for_message}\n'
                    f'Теперь вы можете <b>отменить рассылку или <b>добавить</b> свое время и несколько валют и городов для рассылок\n'
                    f'<i>(доступно только премиум пользователям)</i>', reply_markup=get_main_keyboard(update), parse_mode='HTML')
            user_data['daily_city'] = None
            user_data['daily_valute'] = None
            user_data['daily_mode'] = 'ON'
            save_daily_mode(user_name=update.effective_user.name, user_id=update.effective_user.id, daily_mode=user_data['daily_mode'])

        else:

            await update.message.reply_text("Город <b>не найден</b>. Проверьте правильность написания.")



    elif user_data['waiting_for'] == 'confirm_daily_valute':

        currencies = [
            "австралийский доллар", "азербайджанский манат", "алжирских динаров",
            "фунт стерлингов", "армянских драмов", "бахрейнский динар",
            "белорусский рубль", "болгарский лев", "боливиано",
            "бразильский реал", "форинтов", "донгов",
            "гонконгский доллар", "лари", "датская крона",
            "дирхам оаэ", "доллар сша", "евро",
            "египетских фунтов", "индийских рупий", "рупий",
            "иранских риалов", "тенге", "канадский доллар",
            "катарский риал", "сомов", "юань",
            "кубинских песо", "молдавских леев", "тугриков",
            "найр", "новозеландский доллар", "норвежских крон",
            "оманский риал", "злотый", "саудовский риял",
            "румынский лей", "сдр (специальные права заимствования)", "сингапурский доллар",
            "сомони", "батов", "так",
            "турецких лир", "новый туркменский манат", "узбекских сумов",
            "гривен", "чешских крон", "шведских крон",
            "швейцарский франк", "эфиопских быров", "сербских динаров",
            "рэндов", "вон", "иен",
            "кьятов"
        ]

        user_data['daily_valute'] = text.lower()
        if user_data['daily_valute'] in currencies or user_data['daily_valute'] in ["dol", "dollar", "бакс", "доллар", "американский доллар", "американская валюта", "ljkkfh",
                            ",frc", "долларов", "баксов", "доллара", "бакса", "курс доллара"]:
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

                    f'Отлично! Настройка рассылки <b>завершена<b>.\n Tип: "{daily_type_for_message}", валюта: "{user_data['daily_valute']}"\n'
                    f'Теперь вы можете <b>отменить рассылку или <b>добавить</b> свое время и несколько валют и городов для рассылок\n'
                    f'<i>(доступно только премиум пользователям)</i>', reply_markup=get_main_keyboard(update), parse_mode='HTML')
                user_data['daily_valute'] = None
                user_data['daily_city'] = None
                user_data['daily_mode'] = 'ON'
                save_daily_mode(user_name=update.effective_user.name, user_id=update.effective_user.id, daily_mode=user_data['daily_mode'])

        else:
            await update.message.reply_text(f"Валюта {text} <b>не найдена.</b>\nВы можете посмотреть <i>список</i> всех валют с верным написанием во вкладке <b>Дополнительно->Список всех валют</b>.", parse_mode='HTML')
    elif user_data['waiting_for'] == 'bug_report':
        user_name = update.effective_user.name
        await context.bot.send_message(chat_id=6278046215, text=f"Великий и многоуважаемый, мудрейший и прекраснейший разработчик!\nВам репорт от юзера {user_name}:\n\n{text}")
        if update.effective_user.id != 5449932947:
            await update.message.reply_text("Репорт отправлен! <b>Спасибо</b> за участие в развитии проекта!", parse_mode='HTML')
        else:
            await update.message.reply_text("Нет иди нахуй.")
        user_data['waiting_for'] = None


    elif user_data['waiting_for'] == 'dev_tools_confirm_id':

        await update.message.reply_text(f"Теперь введите сообщение для юзера {text}")
        user_data['id_for_devtools'] = text
        user_data['waiting_for'] = 'dev_tools_confirm_message'

    elif user_data['waiting_for'] == 'dev_tools_confirm_message':
        await context.bot.send_message(chat_id=user_data['id_for_devtools'], text=text)






def init_scheduler(application):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        send_daily_job,
        trigger=CronTrigger(hour=6, minute=0),
        args=[application, 'Mon']
    )

    scheduler.add_job(
        send_daily_job,
        trigger=CronTrigger(hour=10, minute=30),
        args=[application, 'Aft']
    )

    scheduler.add_job(
        send_daily_job,
        trigger=CronTrigger(hour=15, minute=0),
        args=[application, 'Evn']
    )

    scheduler.start()
    return scheduler
#async def debug_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #print(f"Получено сообщение: {update.message.text}")
    #await update.message.reply_text(f"Вы прислали: {update.message.text}")

async def keep_alive(context: CallbackContext):
    # Простое действие, например, логирование или отправка ping
    print("Keep-alive action to prevent sleep")


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
    application.add_handler(MessageHandler(filters.Regex("^👽Dev-Tools$"), dev_tools_handler))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))

    application.job_queue.run_repeating(keep_alive, interval=600, first=10)
    while True:
        try:
            application.run_polling(stop_signals=None)
            scheduler.shutdown()
        except Exception as e:
            print(f"Error: {e}. Reconnecting in 10 seconds...")
            asyncio.sleep(10)




if __name__ == '__main__':
     main()