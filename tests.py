import requests
import pymorphy2


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


def word_search(text, my_lang=False):
    api_server = 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup?'
    key = 'dict.1.1.20190423T161441Z.0dd9fab002fa5efa.5b4f442e77ee05b6d0d5aca59134cce7570126d1'
    lang = ''
    t = ''
    if my_lang:
        par = my_lang1(text, True)
    else:
        par = my_lang1(text)
    if not par:
        return 'Не матерись'
    else:
        t, lang = par
    params = {"key": key, "lang": lang, "text": text}
    response = requests.get(api_server, params=params)
    try:
        return t + '\n' + '\n'.join(list(map(lambda x: x['text'], response.json()['def'][0]['tr'][0]['syn'])))
    except Exception as e:
        return 'Не матерись'


def give_examples(text, my_lang=False):
    abc = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    api_server = 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup?'
    key = 'dict.1.1.20190423T161441Z.0dd9fab002fa5efa.5b4f442e77ee05b6d0d5aca59134cce7570126d1'
    lang = ''
    t = ''
    l = ''
    # text = sessionStorage[user_id]['words'][-1]
    if my_lang:
        par = my_lang1(text, True)
    else:
        par = my_lang1(text)
    if not par:
        return 'Не матерись'
    else:
        lang = par[1]
        t = 'примеры на ' + par[0].split()[-1]
    params = {"key": key, "lang": lang, "text": text}
    response = requests.get(api_server, params=params)
    print(response.json()['def'][0])
    if not my_lang:
        try:
            for i in response.json()['def'][0]['tr'][0]['ex']:
                l += i['tr'][0]['text'] + '\n'
        except Exception as e:
            try:
                for i in response.json()['def'][-2]['tr'][0]['ex']:
                    l += i['tr'][0]['text'] + '\n'
            except Exception as e:
                return 'Упс, получилось найти примеры'
            else:
                return t + '\n' + l
        else:
            return t + '\n' + l
    try:
        return t + '\n' + '\n'.join(list(map(lambda x: x['text'], response.json()['def'][0]['ex']['text'])))
    except Exception as e:
        return 'Не матерись'


print(give_examples('полный', True))
