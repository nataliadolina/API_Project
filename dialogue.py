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
        sessionStorage[user_id] = {'first_name': None, 'game_started': False, 'ins': False}
        return
    if not sessionStorage[user_id]['game_started']:
        if sessionStorage[user_id]['first_name'] is None:
            first_name = get_first_name(req)
            if first_name is None:
                res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
            else:
                sessionStorage[user_id]['first_name'] = first_name
                sessionStorage[user_id]['guessed_cities'] = []
                res['response'][
                    'text'] = f'Приятно познакомиться, {first_name.title()}. Я Алиса. Сыграешь со мной в игру?'
                res['response']['buttons'] = [{'title': 'Да', 'hide': True}, {'title': 'Нет', 'hide': True},
                                              {'title': 'Какая игра', 'hide': True}]
                req['session']['new'] = False
        if req['request']['original_utterance'].lower() == 'Какая игра':
            res['response']['text'] = 'Игра на развитие речи. Тебе будет дано 30 секунд, в течение которых' \
                                      ' ты будешь вводить прилагательные на английском языке.' \
                                      ' Чем больше слов, тем лучше. Итак, поехали?'
            sessionStorage[user_id]['ins'] = True
            res['response']['buttons'] = [{'title': 'Да', 'hide': True}, {'title': 'Нет', 'hide': True}, ]
        if 'да' in req['request']['original_utterance'].lower() or 'ага' in req['request'][
            'original_utterance'].lower():
            res['response']['text'] = 'Время пошло'
            sessionStorage[user_id]['game_started'] = True
        elif 'нет' in req['request']['original_utterance'].lower() or 'неа' in req['request'][
            'original_utterance'].lower():
            res['response']['text'] = 'Ну и пожалуйста'
            res['response']['buttons'] = [{'title': 'Алиса, не обижайся', 'hide': True}]

    else:
        res['response']['buttons'] = [{'title': 'Помощь', 'hide': False}, {'title': 'Стоп', 'hide': False}, ]


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
