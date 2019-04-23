from yandex_translate import YandexTranslate
from flask import Flask, request
import logging
import time
import json

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


def translate(text):
    trans = YandexTranslate('trnsl.1.1.20190421T135944Z.7292abf1150a9315.88e1b4e89ec715ff8de021cc3eaf0ef1cae0259b')
    resp = ''.join(trans.translate(text, 'en-ru')['text'])
    if resp != text:
        return resp
    else:
        return False


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        res['response']['text'] = 'Привет! как тебя зовут?'
        sessionStorage[user_id] = {'first_name': None}
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
                                      f' английском языке,я его переведу и покажу синонимы'
            res['response']['buttons'] = [{'title': 'Помощь', 'hide': False}]
            req['session']['new'] = False
    if req['request']['command'].lower() == 'Помощь':
        res['response']['text'] = 'Введи любое слово на русском языке,' \
                                  ' и Алиса даст несколько синонимов на английском.' \
                                  ' Если введешь на английском-Алиса переведет на русский.' \
                                  ' Если введешь слова на любом другом языке, Алиса будет ругаться. Не обижай Алису'
        sessionStorage[user_id]['ins'] = True
        res['response']['buttons'] = [{'title': 'Да', 'hide': True}, {'title': 'Нет', 'hide': True}, ]


def play_game(res, req, user_id):
    session = sessionStorage[user_id]
    session['current_time'] = time.clock()
    if session['current_time'] - session['start'] >= 30:
        res['response']['text'] = 'Время закончено'
        res['end_session'] = False


def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)
