from flask import Flask, request
import logging
import json
from tests import word_search, give_examples

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
sessionStorage = {}


@app.route('/post1', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {'session': request.json['session'], 'version': request.json['version'],
                'response': {'end_session': False}}
    handle_dialog(request.json, response)
    logging.info('Response: %r', request.json)
    return json.dumps(response)


def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        res['response']['text'] = 'Привет! как тебя зовут?'
        sessionStorage[user_id] = {'first_name': None, 'rus': False, 'eng': False,
                                   'abc': 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя', 'examples': False, 'syn': False}
        return
    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            sessionStorage[user_id]['guessed_cities'] = []
            res['response']['text'] = f'Приятно познакомиться, {first_name.title()}. Я Алиса.' \
                                      f' Хочешь расширить свой словарный запас?' \
                                      f' Тогда скорее вводи слово на русском или' \
                                      f' английском языке'
            req['session']['new'] = False
    else:
        res['response']['buttons'] = [{'title': 'Помощь', 'hide': True}]
        if req['request']['original_utterance']:
            if req['request']['command'] == 'Помощь':
                res['response']['text'] = 'Введи любое слово на русском или английском языке.' \
                                          ' Я спрошу у тебя, какую информацию об этом слове ты хочешь получить.' \
                                          ' Я умею давать примеры и синонимы к твоим' \
                                          ' словам на русском и английском языках.' \
                                          ' Просто напиши, какой язык тебе нужен!' \
                                          ' Если захочешь, чтобы я еще раз спросила у тебя настройки,' \
                                          ' жмякни на кнопку "Сменить настройки"'
                if not sessionStorage[user_id]['examples'] and not sessionStorage[user_id]['syn']:
                    res['response']['buttons'] = [{'title': 'Помощь', 'hide': True}, {'title': 'Примеры', 'hide': True},
                                                  {'title': 'Синонимы', 'hide': True},
                                                  {'title': 'Сменить настройки', 'hide': True}]
                elif not sessionStorage[user_id]['rus'] and not sessionStorage[user_id]['eng']:
                    res['response']['buttons'] = [{'title': 'Помощь', 'hide': True}, {'title': 'Русский', 'hide': True},
                                                  {'title': 'Английский', 'hide': True},
                                                  {'title': 'Сменить настройки', 'hide': True}]
            else:
                if not sessionStorage[user_id]['examples'] and not sessionStorage[user_id]['syn']:
                    res['response']['text'] = 'Ты хочешь получить примеры к данному слову или синонимы?'
                    res['response']['buttons'] = [{'title': 'Помощь', 'hide': True}, {'title': 'Примеры', 'hide': True},
                                                  {'title': 'Синонимы', 'hide': True}]
                    if req['request']['original_utterance'] == 'Примеры' or req['request'][
                        'original_utterance'] == 'Синонимы':
                        res['response']['text'] = 'На русском или на английском?'
                        if req['request']['original_utterance'] == 'Примеры':
                            sessionStorage[user_id]['examples'] = True
                            sessionStorage[user_id]['syn'] = False
                        else:
                            sessionStorage[user_id]['examples'] = False
                            sessionStorage[user_id]['syn'] = True
                        res['response']['buttons'] = [{'title': 'Помощь', 'hide': True},
                                                      {'title': 'Русский', 'hide': True},
                                                      {'title': 'Английский', 'hide': True},
                                                      {'title': 'Сменить настройки', 'hide': True}]
                    elif req['request']['original_utterance'] == 'Русский':
                        sessionStorage[user_id]['rus'] = True
                        sessionStorage[user_id]['eng'] = False
                    elif req['request']['original_utterance'] == 'Английский':
                        sessionStorage[user_id]['rus'] = False
                        sessionStorage[user_id]['eng'] = True
                else:
                    res['response']['buttons'] = [{'title': 'Помощь', 'hide': True},
                                                  {'title': 'Сменить настройки', 'hide': True}]
                    sessionStorage[user_id]['words'] = req['request']['original_utterance']
                if req['request']['original_utterance'] == 'Сменить настройки':
                    sessionStorage[user_id]['rus'] = False
                    sessionStorage[user_id]['eng'] = False
                    sessionStorage[user_id]['examples'], sessionStorage[user_id]['syn'] = False, False
                    res['response']['text'] = 'Ты хочешь получить примеры к данному слову или синонимы?'
                    res['response']['buttons'] = [{'title': 'Помощь', 'hide': True}, {'title': 'Примеры', 'hide': True},
                                                  {'title': 'Синонимы', 'hide': True}]
            if (sessionStorage[user_id]['rus'] or sessionStorage[user_id]['eng'])\
                    and (sessionStorage[user_id]['examples'] or sessionStorage[user_id]['syn']):
                if sessionStorage[user_id]['examples']:
                    logging.debug("попали в примеры")
                    if sessionStorage[user_id]['words'][0].lower() in sessionStorage[user_id]['abc']:
                        if sessionStorage[user_id]['rus']:
                            res['response']['text'] = give_examples(sessionStorage[user_id]['words'], True)
                            logging.debug("переводим с русского на русский")
                        else:
                            res['response']['text'] = give_examples(sessionStorage[user_id]['words'])
                            logging.debug("переводим с русского на английский")
                    else:
                        if sessionStorage[user_id]['eng']:
                            logging.debug("переводим с английского на русский")
                            res['response']['text'] = give_examples(sessionStorage[user_id]['words'], True)
                        else:
                            logging.debug("переводим с английского на английский")
                            res['response']['text'] = give_examples(sessionStorage[user_id]['words'])
                else:
                    logging.debug("попали в синонимы")
                    if sessionStorage[user_id]['words'][0].lower() in sessionStorage[user_id]['abc']:
                        if sessionStorage[user_id]['rus']:
                            res['response']['text'] = (sessionStorage[user_id]['words'], True)
                        else:
                            res['response']['text'] = word_search(sessionStorage[user_id]['words'])
                    else:
                        if sessionStorage[user_id]['eng']:
                            res['response']['text'] = word_search(sessionStorage[user_id]['words'], True)
                        else:
                            res['response']['text'] = word_search(sessionStorage[user_id]['words'])

app.run()