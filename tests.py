import requests
import pymorphy2
from yandex_translate import YandexTranslate


def infinitive(text):
    w = pymorphy2.MorphAnalyzer()
    try:
        normal = w.parse(text)[0].normal_form
    except Exception as e:
        return False
    else:
        return normal


def my_lang1(text, my_lang=False):
    abc = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    lang, t = '', ''
    if text.lower()[0] in abc:
        text = infinitive(text)
        if text:
            if not my_lang:
                lang = 'ru-en'
                t = 'синонимы на английском:'
            else:
                lang = 'ru-ru'
                t = 'синонимы:'
        else:
            return False
    elif not text.lower()[0] in abc and my_lang:
        lang = 'en-en'
        t = 'синонимы:'
    elif not text.lower()[0] in abc and not my_lang:
        lang = 'en-ru'
        t = 'синонимы на русском:'
    if t and lang:
        return t, lang
    else:
        return False


def russian(text):
    abc = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    if text.lower()[0] not in abc:
        return True
    return False


def word_search(text, my_lang=False):
    api_server = 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup?'
    key = 'dict.1.1.20190423T161441Z.0dd9fab002fa5efa.5b4f442e77ee05b6d0d5aca59134cce7570126d1'
    if my_lang:
        par = my_lang1(text, True)
    else:
        par = my_lang1(text)
    if not par:
        return 'Вводи слова на русском или английском языке, а не на своем выдуманном'
    else:
        t, lang = par
    params = {"key": key, "lang": lang, "text": text}
    response = requests.get(api_server, params=params)
    try:
        return t + '\n' + '\n'.join(list(map(lambda x: x['text'], response.json()['def'][0]['tr'][0]['syn'])))
    except Exception as e:
        return 'Упс, не получилось найти синонимы'


def translate(text):
    trans = YandexTranslate('trnsl.1.1.20190421T135944Z.7292abf1150a9315.88e1b4e89ec715ff8de021cc3eaf0ef1cae0259b')
    if not russian(text):
        resp = ''.join(trans.translate(text, 'en-ru')['text'])
    else:
        resp = ''.join(trans.translate(text, 'ru-en')['text'])
    if resp:
        return resp
    return False


def give_examples(text, my_lang=False):
    api_server = 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup?'
    key = 'dict.1.1.20190423T161441Z.0dd9fab002fa5efa.5b4f442e77ee05b6d0d5aca59134cce7570126d1'
    all_text = ''
    if my_lang:
        try:
            text = translate(text)
            par = my_lang1(text)
        except Exception as e:
            return 'Упс, получилось найти примеры'
    else:
        par = my_lang1(text)
    if not par:
        return 'Вводи слова на русском или английском языке, а не на своем выдуманном'
    else:
        lang = par[1]
        t = 'примеры на ' + par[0].split()[-1]
    params = {"key": key, "lang": lang, "text": text}
    response = requests.get(api_server, params=params)
    try:
        for i in response.json()['def'][0]['tr'][0]['ex']:
            all_text += i['tr'][0]['text'] + '\n'
    except Exception as e:
        try:
            for i in response.json()['def'][1]['tr'][0]['ex']:
                all_text += i['tr'][0]['text'] + '\n'
        except Exception as e:
            return 'Упс, не получилось найти примеры'
        else:
            return t + '\n' + all_text
    else:
        return t + '\n' + all_text
