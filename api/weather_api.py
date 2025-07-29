import requests
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

weather_api_key = "2a27c5db9a8bd093c75fc9f50314845d"
def get_weather(city: str, api_key: str) -> dict:
    """
    Получает текущую погоду для указанного города
    :param city: Название города (например "Москва")
    :param api_key: Ваш API-ключ OpenWeatherMap
    :return: Словарь с данными о погоде
    """
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric',  # для получения в °C
        'lang': 'ru'  # русский язык ответа
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Проверка ошибок HTTP

        data = response.json()

        # Извлекаем нужные данные
        return {
            '🌆Город': data['name'],
            '🌡️Температура': data['main']['temp'],
            '🤗Ощущается как': data['main']['feels_like'],
            '🌥️Общее состояние': data['weather'][0]['description'],
            '💧Влажность': data['main']['humidity']
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка запроса погоды: {e}")
        return None

print(get_weather("Сочи", weather_api_key))


