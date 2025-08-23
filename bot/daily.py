from database.crud import save_daily_config, delete_daily_config, save_daily_mode
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CallbackContext, Updater, CommandHandler, CallbackQueryHandler, ContextTypes
#from bot.keyboard import get_inline_currency_keyboard, get_main_keyboard



async def daily_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_data = context.user_data
    text = ('Вы можете включить ежедневную рассылку уведомления о погоде и курсах валют.\n'
                                    'Просто укажите время, валюту или город нажав кнопку ниже.\n'
                                    'Также вы можете узнать более подробную информацию тоже нажав на вторую кнопку ниже')
    if user_data['daily_mode'] == 'ON':
        inline_keyboard = [
            [InlineKeyboardButton("Добавить конфигурацию(Premium)", callback_data='add_daily'),
             InlineKeyboardButton("Подробнее", callback_data='daily_show_more_about')],
            [InlineKeyboardButton("Изменить рассылку", callback_data='change_daily'),
             InlineKeyboardButton("Выключить рассылку", callback_data='off_daily')],
        ]
    else:
        inline_keyboard = [
            [InlineKeyboardButton("Включить рассылку", callback_data='daily_on'),
             InlineKeyboardButton("Подробнее", callback_data='daily_show_more_about')]
        ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)



async def daily_on(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("О погоде", callback_data='daily_is_weather'),
         InlineKeyboardButton("О валюте", callback_data='daily_is_currency')],
        [InlineKeyboardButton("О погоде и валюте", callback_data='daily_is_both')],
        [InlineKeyboardButton("Назад", callback_data='back_to_daily_handler')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Давайте настроим рассылку для вас:\nО чем вы хотите получать уведомления?", reply_markup=reply_markup)



async def daily_timing_set(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Утром", callback_data='daily_in_morning'),
         InlineKeyboardButton("Днём", callback_data='daily_in_afternoon'),
         InlineKeyboardButton("Вечером", callback_data='daily_in_evening')],
        [InlineKeyboardButton("Утром и днём", callback_data='daily_in_morning_and_afternoon'),
         InlineKeyboardButton("Утром и вечером", callback_data='daily_in_morning_and_evening'),
         InlineKeyboardButton("Днём и вечером", callback_data='daily_in_afternoon_and_evening')],
        [InlineKeyboardButton("Утром Днём и вечером", callback_data='daily_in_three')],
        [InlineKeyboardButton("Назад", callback_data='back_to_daily_on')],
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
            save_daily_mode(user_name=update.effective_user.name, daily_mode=context.user_data['daily_mode'])
            context.user_data['daily_type'] = None
            context.user_data['daily_city'] = None
            context.user_data['daily_schedule'] = None
            context.user_data['daily_city'] = None
            await update.callback_query.edit_message_text("Ваша конфигурация рассылки удалена, а рассылка отменена.\nВы можете настроить рассылку заново когда захотите!")
        except Exception:
            await update.callback_query.edit_message_text("Произошла ошибка. Попробуйте позже.")



