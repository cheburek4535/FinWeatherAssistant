import requests
from datetime import datetime
from Logger.my_logger import logger
import urllib.request



def get_currency_rates(base: str = 'USD', get_all=False) -> dict:
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



    if base.lower() in ["rub", "рубль", "российский рубль", "рубли"]:
        return {
            'timestamp': datetime.now().isoformat(),
            'base': 'RUB',
            'rate': 1.0,
            'previous': None,
            'name': 'Российский рубль'
        }



    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        valutes = data.get('Valute', {})

        if get_all:
            all_data = valutes

            return {
                'name': all_data['Name'],
                'rate': all_data['Value']
            }

        # if base.upper() not in valutes:
        #     logger.error(f"Валюта {base} не найдена в данных ЦБ РФ")
        #     return None
        if base.lower() in ["dol", "dollar", "бакс", "доллар", "американский доллар", "американская валюта", "ljkkfh",
                            ",frc", "долларов", "баксов", "доллара", "бакса", "курс доллара"]:
            dollar_currency = valutes['USD']
            return {
                'timestamp': datetime.now().isoformat(),
                'base': 'USD',
                'rate': dollar_currency['Value'],
                'previous': dollar_currency['Previous'],
                'name': 'Американский доллар'
            }

        if base.upper() in valutes:
            currency_data = valutes[base.upper()]

            return {
                'timestamp': datetime.now().isoformat(),
                'base': base.upper(),
                'rate': currency_data['Value'] / currency_data['Nominal'],
                'previous': currency_data['Previous'] / currency_data['Nominal'],
                'name': currency_data['Name']
            }

        base_lower = base.lower()
        candidates = []

        for code, info in valutes.items():
            if base_lower in info['Name'].lower():
                candidates.append((code, info['Name']))

        if len(candidates) == 1:
            currency_data = valutes.get(candidates[0][0])
            return {
                'timestamp': datetime.now().isoformat(),
                'base': candidates[0][0],
                'rate': currency_data['Value'] / currency_data['Nominal'],
                'previous': currency_data['Previous'] / currency_data['Nominal'],
                'name': currency_data['Name']
            }
        elif len(candidates) > 1:
            logger.error(f"Найдено несколько валют по названию '{base}': {','.join(name for name in candidates)}")
            return None
        else:
            logger.error(f"валюта '{base}' не найдена" )
            return None

    except Exception as e:
        logger.error(f"Ошибка запроса курсов валют: {e}")
        return None

# print(get_currency_rates('Евро'))
# print(get_currency_rates('EUR'))
# print(get_currency_rates('бакс'))

#print(get_currency_rates('AUD', get_all=True))

# url = "https://www.cbr-xml-daily.ru/daily_json.js"
# filename = "valute_list.json"
# with urllib.request.urlopen(url) as response:
#         content = response.read().decode("utf-8")
# with open(filename, 'w', encoding='utf-8') as f:
#         f.write(content)

