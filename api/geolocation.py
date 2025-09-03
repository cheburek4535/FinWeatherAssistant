import requests
from telegram.ext import CallbackContext
from telegram import Update
from api.weather_api import get_weather, weather_api_key
from bot.keyboard import get_main_keyboard
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
                f"🌆<i>Погода в городе {weather_data['city']}:</i>\n"
                f"🌡️Температура: {weather_data['temp']}°C\n"
                f"🤗Ощущается как: {weather_data['feels_like']}°C\n"
                f"🌥️Общее состояние: {weather_data['description']}\n"
                f"💧Влажность: {weather_data['humidity']}\n"

            )
            save_request(
                user_id=update.effective_user.id,
                user_name=update.effective_user.name,
                req_type="weather",
                req_data=user_city,
                resp_data=response
            )

            if 'дождь' in weather_data['description']:
                photo = 'https://imgs.search.brave.com/FrAZSxk-OcJL9rgq5bqWVaYwxWahT99uJueKpmBnGL0/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9tZWRp/YS5pc3RvY2twaG90/by5jb20vaWQvMTQ3/NjE4OTk4My9waG90/by9zdW1tZXItcmFp/bi1yYWluZHJvcHMt/YmFkLXdlYXRoZXIt/ZGVwcmVzc2lvbi5q/cGc_cz02MTJ4NjEy/Jnc9MCZrPTIwJmM9/SXdKWGQyYms1TzY1/YUY1WFp3b0ItV0pp/RnBDSXJtYlpsdGdi/UVRYTk5raz0'
            elif 'пасмурно' in weather_data['description'] or 'облачность' in weather_data[
                'description'] or 'облачно' in weather_data['description']:
                photo = 'https://imgs.search.brave.com/bfTijEBuXl5-ByeGFU8RyVwxFXKcA7AlIJYEkQ2zyI4/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly95Ymlz/LnJ1L3dwLWNvbnRl/bnQvdXBsb2Fkcy8y/MDIzLzA5L3Bhc211/cm5vZS1uZWJvLTEz/LndlYnA'
            elif 'ясно' in weather_data['description'] or 'солнце' in weather_data['description'] or 'солнечно' in \
                    weather_data['description']:
                photo = 'https://imgs.search.brave.com/94yUO0S20ReZBvTMh-HhW4cuYDkYHCQaCsLGZA53jDw/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9tZWRp/YS5pc3RvY2twaG90/by5jb20vaWQvMTA0/Njg1MTIzOC9ydS8l/RDElODQlRDAlQkUl/RDElODIlRDAlQkUv/JUQxJTgxJUQwJUJF/JUQwJUJCJUQwJUJE/JUQxJTg2JUQwJUI1/LSVEMSU4MSVEMCVC/MiVEMCVCNSVEMSU4/MiVEMCVCOCVEMSU4/Mi0lRDAlQkQlRDAl/QjAtJUQxJTg0JUQw/JUJFJUQwJUJEJUQw/JUI1LSVEMCVCMyVE/MCVCRSVEMCVCQiVE/MSU4MyVEMCVCMSVE/MCVCRSVEMCVCMyVE/MCVCRS0lRDAlQkQl/RDAlQjUlRDAlQjEl/RDAlQjAuanBnP2I9/MSZzPTYxMng2MTIm/dz0wJms9MjAmYz1m/RjFFSE9mMm9PcHJK/cFBUMm9EQl9iV3Nh/ZEVTYWt2elRSUzBv/V3AxZHhVPQ'
            elif 'снег' in weather_data['description'] or 'снегопад' in weather_data['description']:
                photo = 'https://imgs.search.brave.com/lrSBDeUU8sGJBhbdq-7St7FOjo_tAEHHTW2BqoIPz8c/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9zdC5k/ZXBvc2l0cGhvdG9z/LmNvbS8xMDQzMDcz/LzMwNDAvaS82MDAv/ZGVwb3NpdHBob3Rv/c18zMDQwMDMxNy1z/dG9jay1waG90by1z/bm93LmpwZw'
            else:
                photo = 'https://imgs.search.brave.com/2yaqlZEQTb8edAq9CWgvkAkyjaD5K0M_loUCkzuXHN8/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9tZWRp/YS5pc3RvY2twaG90/by5jb20vaWQvNTAz/NDk1MzUyL3J1LyVE/MSU4NCVEMCVCRSVE/MSU4MiVEMCVCRS8l/RDElODElRDAlQkYl/RDElODMlRDElODIl/RDAlQkQlRDAlQjgl/RDAlQkElRDAlQkUl/RDAlQjIlRDAlQkUl/RDAlQjUtYXJyYXkt/dmxhLmpwZz9zPTYx/Mng2MTImdz0wJms9/MjAmYz1XRDFhOEMw/Q2tUZG8tMlVGQzJy/RlVqVUFaVExER192/bUZuMmlNeV9CNkd3/PQ'

            await update.message.reply_photo(photo=photo, caption=response, reply_markup=get_main_keyboard(update),
                                             parse_mode='HTML')
            user_data['waiting_for'] = None


        else:
            await update.message.reply_text("Не удалось получить данные о погоде 😔.\nПожалуйста, попробуйте ввести город вручную", reply_markup=get_main_keyboard(update))



#print(get_weather(get_city_from_location(69, 40), weather_api_key))