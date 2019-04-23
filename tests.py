import requests


def word_search(text):
    abc = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    api_server = 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup?'
    key = 'dict.1.1.20190423T161441Z.0dd9fab002fa5efa.5b4f442e77ee05b6d0d5aca59134cce7570126d1'
    if text.lower()[0] in abc:
        lang = 'ru-en'
        t = 'синонимы на английском:'
    else:
        lang = 'en-ru'
        t = 'синонимы на русском:'
    params = {"key": key, "lang": lang, "text": text}
    response = requests.get(api_server, params=params)
    try:
        return t + '\n' + '\n'.join(list(map(lambda x: x['text'], response.json()['def'][0]['tr'][0]['syn'])))
    except Exception as e:
        return 'Не матерись'
# print(word_search('handsome'))
