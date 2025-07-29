import requests
from datetime import datetime
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(level)s -%(message)s', level = logging.INFO)
logger = logging.getLogger(__name__)


def get_currency_rates(base: str = 'USD') -> dict:
    """
        Получаем курс указанной валюты к рублю по данным ЦБ РФ.
        :param base: Код валюты (например, 'USD', 'EUR'), базовая валюта относительно рубля.
                     Если base='RUB', то курс 1.
        :return: Словарь с ключами:
            - 'timestamp': время получения данных,
            - 'base': указанный код валюты,
            - 'rate': текущий курс валюты к рублю,
            - 'previous': предыдущий курс,
            - 'name': название валюты.
            или None при ошибке.
        """
    url = "https://www.cbr-xml-daily.ru/daily_json.js"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if base.upper() == "RUB":
            return {
                'timestamp': datetime.now().isoformat(),
                'base': 'RUB',
                'rate': 1.0,
                'previous': None,
                'name': 'Российский рубль'
            }

        valutes = data.get('Valute', {})

        if base.upper() not in valutes:
            logger.error(f"Валюта {base} не найдена в данных ЦБ РФ")
            return None

        currency_data = valutes[base.upper()]

        return {
            'timestamp': datetime.now().isoformat(),
            'base': base.upper(),
            'rate': currency_data['Value'],
            'previous': currency_data['Previous'],
            'name': currency_data['Name']
        }
    except Exception as e:
        logger.error(f"Ошибка запроса курсов валют: {e}")
        return None

print(get_currency_rates('USD'))
print(get_currency_rates('EUR'))
print(get_currency_rates('CNY'))