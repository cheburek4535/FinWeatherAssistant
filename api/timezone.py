# import requests
# timezone_api_key = 'EVMVIQY1K2Y3'
# def get_timezone(lattitude, longitude):
#     url = f'http://api.timezonedb.com/v2.1/get-time-zone?key={timezone_api_key}&format=xml&by=position&lat={lattitude}&lng={longitude}'
#     response = requests.get(url)
#     response.raise_for_status()
#     data = response.json()

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz
from datetime import datetime

def get_local_time_by_city(city):
    geolocator = Nominatim(user_agent="myTGapp")
    location = geolocator.geocode(city)
    if not location:
        return f"не удалось найти город '{city}', проверьте правильность написания"

    lat, lon = location.latitude, location.longitude
    tf = TimezoneFinder()
    timezone_name = tf.timezone_at(lat=lat, lng=lon)
    if not timezone_name:
        return "Не удалось определить часовой пояс"

    tz = pytz.timezone(timezone_name)
    local_time = datetime.now(tz)
    return local_time.strftime("%H:%M:%S")




#print(get_local_time_by_city("Нью-Йорк"))