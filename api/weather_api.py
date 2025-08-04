import requests
from Logger.my_logger import logger



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
            'city': data['name'],
            'temp': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'description': data['weather'][0]['description'],
            'humidity': data['main']['humidity']
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка запроса погоды: {e}")
        return None

#print(get_weather("Сочи", weather_api_key))





