from yandex_translate import YandexTranslate
import requests


def translate(text):
    translate = YandexTranslate('trnsl.1.1.20190421T135944Z.7292abf1150a9315.88e1b4e89ec715ff8de021cc3eaf0ef1cae0259b')
    resp = ''.join(translate.translate(text, 'en-ru')['text'])
    if resp == text:
        return 'Не могу перевести ' + text
    else:
        return 'внесено в базу ' + '"' + resp + '"'
