import time
import requests


def translate(text):
    server = 'https://translate.yandex.net/api/v1.5/tr/getLangs'
    params = {"key": "trnsl.1.1.20190421T135944Z.7292abf1150a9315.88e1b4e89ec715ff8de021cc3eaf0ef1cae0259b",
              'text': text, 'lang': 'ru-en'}
    response = requests.post(server, params=params).json().items()['text']
    if response == text:
        return 'Не могу перевести ' + text
    else:
        return 'внесено в базу ' + '"' + response + '"'


print(translate('ты ды'))
