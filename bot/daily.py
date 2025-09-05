from telegram.constants import ParseMode


from database.crud import delete_daily_config, save_daily_mode, get_daily_mode, get_daily_config, get_all_users_with_daily_mode, get_daily_config_without_time
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CallbackContext, ContextTypes
from bot.keyboard import get_help_keyboard

from api.currency import get_currency_rates
from api.weather_api import get_weather, weather_api_key
from api.timezone import get_local_time_by_city


async def daily_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_data = context.user_data
    text = ('Вы можете включить <b>ежедневную рассылку</b> уведомления о погоде и курсах валют.\n'
                                    'Просто укажите <i>время, валюту</i> и <i>город</i> нажав кнопку ниже.\n'
                                    'Также вы можете узнать более подробную информацию тоже нажав на вторую кнопку ниже')
    if get_daily_mode(update.effective_user.id) == 'ON':
        inline_keyboard = [
            [InlineKeyboardButton("➕Добавить конфиг(Premium)", callback_data='add_daily'),
             InlineKeyboardButton("📘Подробнее", callback_data='daily_show_more_about')],
            [InlineKeyboardButton("🔄Изменить рассылку", callback_data='change_daily'),
             InlineKeyboardButton("🔴Выключить рассылку", callback_data='off_daily')],
            [InlineKeyboardButton("❓Моя конфигурация рассылки", callback_data='show_config'),]
        ]
    else:
        inline_keyboard = [
            [InlineKeyboardButton("🟢Включить рассылку", callback_data='daily_on')],
             [InlineKeyboardButton("📘Подробнее", callback_data='daily_show_more_about')]
        ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)



async def daily_on(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🌦️О погоде", callback_data='daily_is_weather'),
         InlineKeyboardButton("💸О валюте", callback_data='daily_is_currency')],
        [InlineKeyboardButton("🌦️💸О погоде и валюте", callback_data='daily_is_both')],
        [InlineKeyboardButton("⬅️Назад", callback_data='back_to_daily_handler')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Давайте настроим рассылку для вас:\nО чем вы хотите получать уведомления?", reply_markup=reply_markup)



async def daily_timing_set(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🌅Утром", callback_data='daily_in_morning'),
         InlineKeyboardButton("🌞Днём", callback_data='daily_in_afternoon'),
         InlineKeyboardButton("🌙Вечером", callback_data='daily_in_evening')],
        [InlineKeyboardButton("⏳Утром/днём", callback_data='daily_in_morning_and_afternoon'),
         InlineKeyboardButton("⏳Утром/вечером", callback_data='daily_in_morning_and_evening'),
         InlineKeyboardButton("⏳Днём/вечером", callback_data='daily_in_afternoon_and_evening')],
        [InlineKeyboardButton("♾️Утром, днём и вечером", callback_data='daily_in_three')],
        [InlineKeyboardButton("⬅️Назад", callback_data='back_to_daily_on')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="В какое время вы хотели бы получать рассылку?", reply_markup=reply_markup)



async def daily_city_set(update: Update, context: CallbackContext):
    #await update.callback_query.edit_message_text("Напишите название города для рассылки погоды:", reply_markup=get_currency_keyboard())
    query = update.callback_query
    await query.answer()
    user_data = context.user_data
    user_data["waiting_for"] = 'confirm_daily_city'

    await query.edit_message_text("Напишите название города для рассылки погоды:")

async def daily_valute_set(update: Update, context: CallbackContext):


    user_data = context.user_data
    user_data["waiting_for"] = 'confirm_daily_valute'
    await update.callback_query.edit_message_text(
        "Напишите название валюты для рассылки курса:",
        )
    user_data['daily_valute'] = update.callback_query.data if update.callback_query.data else None

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    await query.answer()
    if data in ('daily_on', 'back_to_daily_on'):
        await daily_on(update, context)

    if data in ('daily_is_weather', 'daily_is_currency', 'daily_is_both'):
        if data == 'daily_is_weather':
            context.user_data['daily_type'] = 'weather'
        elif data == 'daily_is_currency':
            context.user_data['daily_type'] = 'currency'
        elif data == 'daily_is_both':
            context.user_data['daily_type'] = 'both'
        await daily_timing_set(update, context)

    if data == 'back_to_daily_handler':
        await daily_handler(update, context)

    if data in ('daily_in_morning', 'daily_in_afternoon', 'daily_in_evening', 'daily_in_morning_and_afternoon', 'daily_in_three', 'daily_in_afternoon_and_evening', 'daily_in_morning_and_evening'):
        schedule_map = {
            'daily_in_morning': 'Mon',
            'daily_in_afternoon': 'Aft',
            'daily_in_evening': 'Evn',
            'daily_in_morning_and_afternoon': 'MonAft',
            'daily_in_morning_and_evening': 'MonEvn',
            'daily_in_afternoon_and_evening': 'AftEvn',
            'daily_in_three': 'MonAftEvn',
        }

        context.user_data['daily_schedule'] = schedule_map.get(data, '')

        daily_type = context.user_data['daily_type']
        if daily_type == 'weather':
            await daily_city_set(update, context)
        elif daily_type == 'currency':
            await daily_valute_set(update, context)
        elif daily_type == 'both':
            context.user_data['ask_next'] = 'city'
            await daily_valute_set(update, context)

    if data in ('доллар', 'евро', 'юань', 'фунт стерлингов'):
        context.user_data['daily_valute'] = update.callback_query.data if update.callback_query.data else None


    if data == 'off_daily':
        try:
            delete_daily_config(user_name=update.effective_user.name)
            context.user_data['daily_mode'] = 'OFF'
            save_daily_mode(user_name=update.effective_user.name, user_id=update.effective_user.id, daily_mode=context.user_data['daily_mode'])
            context.user_data['daily_type'] = None
            context.user_data['daily_city'] = None
            context.user_data['daily_schedule'] = None
            context.user_data['daily_city'] = None
            await update.callback_query.edit_message_text("Ваша конфигурация рассылки удалена, а рассылка отменена.\nВы можете настроить рассылку заново когда захотите!")
        except Exception:
            await update.callback_query.edit_message_text("Произошла ошибка. Попробуйте позже.")

    if data == 'change_daily':
        try:
            delete_daily_config(user_name=update.effective_user.name)
            context.user_data['daily_mode'] = 'OFF'
            save_daily_mode(user_name=update.effective_user.name, user_id=update.effective_user.id, daily_mode=context.user_data['daily_mode'])
            context.user_data['daily_type'] = None
            context.user_data['daily_city'] = None
            context.user_data['daily_schedule'] = None
            context.user_data['daily_city'] = None
            await daily_on(update, context)
        except Exception:
            await update.callback_query.edit_message_text("Произошла ошибка. Попробуйте позже.")

    if data == 'daily_show_more_about':
        keyboard = [
            [InlineKeyboardButton('⬅️Назад', callback_data='back_to_daily_handler'),]
        ]
        await update.callback_query.edit_message_text("Вы можете настроить для себя конфигурацию для ежедневной рассылки.\n"
                                                      "Просто укажите время (утро = 9:00, день = 13:30, вечер = 18:00),\n"
                                                      "тип рассылки, город, валюту (в зависимости от типа рассылки),\n"
                                                      "и каждый день бот будет отправлять вам сообщение с вашей рассылкой.\n"
                                                      "При оформлении премиума(пока недоступен) вы сможете добавлять несколько конфигураций рассылки,\n"
                                                      "а также самостоятельно указывать нужное вам время", reply_markup=InlineKeyboardMarkup(keyboard))


    if data == 'give_all_valutes':
        currencies = [
            "Австралийский доллар", "Азербайджанский манат", "Алжирских динаров",
            "Фунт стерлингов", "Армянских драмов", "Бахрейнский динар",
            "Белорусский рубль", "Болгарский лев", "Боливиано",
            "Бразильский реал", "Форинтов", "Донгов",
            "Гонконгский доллар", "Лари", "Датская крона",
            "Дирхам ОАЭ", "Доллар США", "Евро",
            "Египетских фунтов", "Индийских рупий", "Рупий",
            "Иранских риалов", "Тенге", "Канадский доллар",
            "Катарский риал", "Сомов", "Юань",
            "Кубинских песо", "Молдавских леев", "Тугриков",
            "Найр", "Новозеландский доллар", "Норвежских крон",
            "Оманский риал", "Злотый", "Саудовский риял",
            "Румынский лей", "СДР (специальные права заимствования)", "Сингапурский доллар",
            "Сомони", "Батов", "Так",
            "Турецких лир", "Новый туркменский манат", "Узбекских сумов",
            "Гривен", "Чешских крон", "Шведских крон",
            "Швейцарский франк", "Эфиопских быров", "Сербских динаров",
            "Рэндов", "Вон", "Иен",
            "Кьятов"
        ]

        kb = [
                [InlineKeyboardButton('⬅️Назад', callback_data='back_to_help_handler'), ]
            ]
        await query.edit_message_text(
            "Вот список всех поддерживаемых валют:\n\n" +
            "\n".join([f"• {currency}" for currency in currencies]) +
            "\n\nИменно такими названиями рекомендуется указывать валюту для получения курсов.\n"
            "Обратите внимание что бот нечувствителен к регистру, и можно вводить, например так 'дОллАр', а также указывать популярную валюту через кнопки.",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    if data == 'back_to_help_handler':
        # await help_handler(update, context)
        await query.edit_message_text(
            "Ниже приведены кнопки для получения инструкции по взаимодейтсвию с ботом\nА также список всех валют, курсы которых которые можно можно запросить у бота.\n"
            "Если у вас возникли другие вопросы, вы можете связаться напрямую с разработчиком через кнопку 'Баг-репорт.'",
            reply_markup=get_help_keyboard())

    if data == 'give_instruction':
        kb = [
            [InlineKeyboardButton('⬅️Назад', callback_data='back_to_help_handler'), ]
        ]
        await query.edit_message_text("Эта функция пока не готова, ожидайте в ближайшем обновлении.",
                                      reply_markup=InlineKeyboardMarkup(kb))


    if data == 'show_config':
        kb = [
            [InlineKeyboardButton('⬅️Назад', callback_data='back_to_daily_handler')]
        ]
        config = get_daily_config_without_time(update.effective_user.id)
        schedule_map = {
            'Mon': "утром",
            'Aft': "днём",
            'Evn': "вечером",
            'MonAft': "утром и днём",
            'MonEvn': "утром и вечером",
            'AftEvn': "днём и вечером",
            'MonAftEvn': "утром, днём и вечером",
        }
        time = schedule_map.get(config[4], '')

        type_map = {
            'both' : 'о погоде и курсах валют',
            'weather': 'о погоде',
            'currency': 'о курсах валют'
        }
        dtype = type_map.get(config[0], '')

        if config[2] is not None:
            city = f", Город - {config[2]}"
        else:
            city = ''
        if config[3] is not None:
            valute = f", Валюта - {config[3]}"
        else:
            valute = ''

        await query.edit_message_text(f"Конфигурация вашей рассылки:\nРассылка {time} {dtype}{city}{valute}", reply_markup=InlineKeyboardMarkup(kb))





def send_daily_job(application, time):
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_async_send_daily(application, time))
    except Exception:
        print("Ошибка создания аппликации")
    finally:
        loop.close()


async def _async_send_daily(application, time):
    users = get_all_users_with_daily_mode()

    for user in users:
        if get_daily_mode(user) == 'ON':

             config = get_daily_config(user_id=user, time=time)
             if config[0] in ['currency', 'both']:

                 currency_data = get_currency_rates(config[3])

                 if currency_data:

                     response = (
                         f"💱Курс валюты: {currency_data['name']}:\n"
                         f"🕒Время: {currency_data['timestamp'][11:16]}\n"
                         f"💰Текущий курс: {currency_data['rate']:.2f}₽\n"
                         f"⏳Предыдущий курс: {currency_data['previous']:.2f}₽\n"
                         f"📈Изменение на {(currency_data['rate'] - currency_data['previous']):.2f}₽ ({((currency_data['rate'] * 100) / currency_data['previous']) - 100:.2f}%)"
                     )

                 else:
                     response = "Не удалось получить данные о курсах валют 😔.\nПожалуйста, проверьте правильность написания названия валюты!"
                 await application.send_message(f"Вот ваша ежедневная рассылка о валюте:")
                 await application.bot.send_message(config[1], response)


             if config[0] in ['weather','both']:

                 weather_data = get_weather(config[2], weather_api_key)
                 if weather_data:
                     response = (
                         f"🌆Погода в городе {weather_data['city']}:\n"
                         f"🌡️Температура: {weather_data['temp']}°C\n"
                         f"🤗Ощущается как: {weather_data['feels_like']}°C\n"
                         f"🌥️Общее состояние: {weather_data['description']}\n"
                         f"💧Влажность: {weather_data['humidity']}\n"
                         f"🕒Местное время: {get_local_time_by_city(config[2])}"
                     )

                 else:
                     response = "Не удалось получить данные о погоде 😔.\nПожалуйста, проверьте правильность написания названия города!"

                 await application.send_message(f"Вот ваша ежедневная рассылка о погоде:")
                 await application.bot.send_message(config[1], response)

