import requests
from telegram.ext import MessageHandler, filters, CallbackContext
from telegram import Update
from api.weather_api import get_weather, weather_api_key
from bot.keyboard import get_main_keyboard
from Logger.my_logger import logger
from database.crud import save_request
def get_city_from_location(latitude, longitude):
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}&zoom=10&addressdetails=1"
    headers = {'User-Agent': 'FinWeatherAssistant/1.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Ошибка API: статус {response.status_code}, тело: {response.text}")
        data = response.json()
        address = data.get('address', {})
        for key in ['city', 'town', 'state', 'village', 'suburb', 'county']:
            if key in address:
                return address[key]
        return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса к API: {e}")
        return None
    except ValueError as e:
        print(f"Ошибка парсинга JSON: {e}")
        return None

async def handle_location(update: Update, context: CallbackContext) -> None:
    user_data = context.user_data
    if user_data.get('waiting_for') == 'weather_city' and update.message.location:
        latitude = update.message.location.latitude
        longitude = update.message.location.longitude
        user_city = get_city_from_location(latitude, longitude)
        weather_data = get_weather(user_city, weather_api_key)

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
                user_name=update.effective_user.name,
                req_type='weather_geo',
                req_data=str(user_city),
                resp_data=response
            )
            await update.message.reply_text(response, reply_markup=get_main_keyboard())
            user_data['waiting_for'] = None


        else:
            await update.message.reply_text("Не удалось получить данные о погоде 😔.\nПожалуйста, попробуйте ввести город вручную", reply_markup=get_main_keyboard())



#print(get_weather(get_city_from_location(69, 40), weather_api_key))