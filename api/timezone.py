import requests
timezone_api_key = 'EVMVIQY1K2Y3'
def get_timezone(lattitude, longitude):
    url = f'http://api.timezonedb.com/v2.1/get-time-zone?key={timezone_api_key}&format=xml&by=position&lat={lattitude}&lng={longitude}'
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()