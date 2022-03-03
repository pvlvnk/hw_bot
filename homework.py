import logging
import os
import sys
import time

import requests
import telegram
from dotenv import load_dotenv

from exception import (Error500Error, ErrorNot200Error,
                       NotContainHomeworksError,
                       ResponseHomeworksNotInListError,
                       ResponseNoHomeworksError)

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


RETRY_TIME = 600
YANDEX_ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=None)
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s'
)
logger.addHandler(handler)


def send_message(bot, message):
    """
    Принимает экземлпляр класса Bot и строку с текстом сообщения.
    Отправляет сообщение.
    """
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info('Сообщение отправлено в Telegram')
    except Exception:
        logging.error('Бот не смог отправить сообщение')


def get_api_answer(current_timestamp):
    """
    Делает запрос к API яндекс практикума.
    Возвращает ответ API.
    """
    try:
        timestamp = current_timestamp or int(time.time())
        params = {'from_date': timestamp}
        response = requests.get(
            YANDEX_ENDPOINT, headers=HEADERS, params=params)
        if response.status_code == 500:
            logging.error('Эндпоинт недоступен, ошибка 500')
            raise Error500Error('Cервер не может обработать запрос к сайту')
        if response.status_code != 200:
            logging.error('Сбой при запросе к эндпоинту')
            raise ErrorNot200Error(f'Эндпоинт {YANDEX_ENDPOINT} недоступен')
        return response.json()
    except ErrorNot200Error(f'Эндпоинт {YANDEX_ENDPOINT} недоступен'):
        logging.error('Сбой при запросе к эндпоинту')
        raise ErrorNot200Error(f'Эндпоинт {YANDEX_ENDPOINT} недоступен')


def check_response(response):
    """Получает ответ API. Возвращает список домашних работ."""
    if response is None:
        logging.debug('Отсутствие новых статусов')
        raise NotContainHomeworksError('Отсутствие новых статусов')
    if response['homeworks'] is None:
        logging.error('Ответ API не содержит homeworks')
        raise ResponseNoHomeworksError('Ответ API не содержит homeworks')
    if type(response['homeworks']) is not list:
        logging.error('Под ключом homeworks пришел не список')
        raise ResponseHomeworksNotInListError(
            'Под ключом homeworks пришел не список')
    return response['homeworks']


def parse_status(homework):
    """
    Получает первый элемент из списка домашних работ.
    Возвращает строку, содержащую один из вердиктов словаря HOMEWORK_STATUSES
    """
    homework_name = homework.get('homework_name')
    if homework_name is None:
        logging.error('Отсутствует имя домашней работы')
        raise KeyError('Отсутствует имя домашней работы')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_STATUSES:
        logging.error('Неизвестный статус работы')
        raise KeyError('Неизвестный статус работы')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        return True
    logging.critical('Отсутствуют токены')
    return False


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        sys.exit(1)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            message = parse_status(homeworks[0])
            send_message(bot, message)
        except Exception as error:
            logging.error(error)
        finally:
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
