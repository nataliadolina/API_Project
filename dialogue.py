from flask import Flask, request
import logging
import json
from tests import word_search, give_examples, russian

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
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


def language(text, user_id):
    if russian(text) and sessionStorage[user_id]['rus'] or not russian(sessionStorage[user_id]['word']) and not \
            sessionStorage[user_id]['rus']:
        return True
    return False


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        res['response']['text'] = 'Привет! как тебя зовут?'
        sessionStorage[user_id] = {'first_name': None, 'rus': False, 'eng': False,
                                   'abc': 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя', 'examples': False, 'syn': False,
                                   'word': ''}
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
            res['response']['buttons'] = [{'title': 'Помощь', 'hide': True}]
            req['session']['new'] = False
    else:
        res['response']['buttons'] = [{'title': 'Помощь', 'hide': True}]
        if req['request']['command'] == 'Сменить настройки':
            sessionStorage[user_id]['examples'], sessionStorage[user_id]['syn'] = False, False
            sessionStorage[user_id]['eng'], sessionStorage[user_id]['rus'] = False, False
        elif req['request']['original_utterance'] == 'Примеры':
            sessionStorage[user_id]['examples'], sessionStorage[user_id]['syn'] = True, False
        elif req['request']['original_utterance'] == 'Синонимы':
            sessionStorage[user_id]['examples'], sessionStorage[user_id]['syn'] = False, True
        elif req['request']['original_utterance'] == 'Русский':
            sessionStorage[user_id]['eng'], sessionStorage[user_id]['rus'] = False, True
        elif req['request']['original_utterance'] == 'Английский':
            sessionStorage[user_id]['rus'], sessionStorage[user_id]['eng'] = False, True
        else:
            sessionStorage[user_id]['word'] = req['request']['original_utterance']
        if req['request']['original_utterance'] != 'Помощь':
            if not sessionStorage[user_id]['eng'] and not sessionStorage[user_id]['rus']:
                res['response']['text'] = 'На русском или на английском?'
                res['response']['buttons'] = [{'title': 'Помощь', 'hide': True}, {'title': 'Русский', 'hide': True},
                                              {'title': 'Английский', 'hide': True},
                                              {'title': 'Сменить настройки', 'hide': True}]
            if not sessionStorage[user_id]['examples'] and not sessionStorage[user_id]['syn']:
                res['response']['text'] = 'Ты хочешь получить примеры к данному слову или синонимы?'
                res['response']['buttons'] = [{'title': 'Помощь', 'hide': True}, {'title': 'Примеры', 'hide': True},
                                              {'title': 'Синонимы', 'hide': True}]
            if sessionStorage[user_id]['eng'] or sessionStorage[user_id]['rus']:
                if sessionStorage[user_id]['word']:
                    text = sessionStorage[user_id]['word']
                    if sessionStorage[user_id]['examples']:
                        res['response']['text'] = give_examples(text, language(text, user_id))
                    else:
                        res['response']['text'] = word_search(text, language(text, user_id))
                    res['response']['buttons'] = [{'title': 'Помощь', 'hide': True},
                                                  {'title': 'Сменить настройки', 'hide': True}]
        else:
            res['response']['text'] = 'Введи любое слово на русском или английском языке.' \
                                      ' Я спрошу у тебя, какую информацию об этом слове ты хочешь получить.' \
                                      ' Я умею давать примеры и синонимы к твоим' \
                                      ' словам на русском и английском языках.' \
                                      ' Просто напиши, какой язык тебе нужен!' \
                                      ' Если захочешь, чтобы я еще раз спросила у тебя настройки,' \
                                      ' жмякни на кнопку "Сменить настройки"'
