from socket import *

"""Программа-сервер"""

import sys
import json
from message import send_message, get_message
from variables import *
import argparse
import logging
import logs.logs_config.server_logs
from decor import Log
import decor
import select
from time import time

SERVER_LOGGER = logging.getLogger('server')


@Log()
def process_client_message(message, messages_list, client):
    '''
    Обработчик сообщений от клиентов, принимает словарь -
    сообщение от клинта, проверяет корректность,
    возвращает словарь-ответ для клиента

    :param message:
    :return:
    '''
    SERVER_LOGGER.debug(f'Разбор сообщения от клиента : {message}')
    # {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        send_message(client, {RESPONSE: 200})
        return {RESPONSE: 200}
    elif ACTION in message and message[ACTION] == MESSAGE and \
            TIME in message and MESSAGE_TEXT in message:
        messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
        return
    else:
        return {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }

@Log()
def create_arg_parser():
    """
    Парсер аргументов коммандной строки
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    return parser


def main():
    parser = create_arg_parser()
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    # проверка получения корретного номера порта для работы сервера.
    if not 1023 < listen_port < 65536:
        SERVER_LOGGER.critical(f'Попытка запуска сервера с указанием неподходящего порта '
                               f'{listen_port}. Допустимы адреса с 1024 до 65535.')
        sys.exit(1)
    SERVER_LOGGER.info(f'Запущен сервер, порт для подключений: {listen_port}, '
                       f'адрес с которого принимаются подключения: {listen_address}. '
                       f'Если адрес не указан, принимаются соединения с любых адресов.')
    # Готовим сокет

    transport = socket(AF_INET, SOCK_STREAM)
    transport.bind((listen_address, listen_port))
    transport.settimeout(0.5)
    # Слушаем порт

    transport.listen(MAX_CONNECTIONS)
    clients = []
    messages = []
    transport.listen(MAX_CONNECTIONS)
    while True:
        try:

            client, client_address = transport.accept()

        except OSError:
            pass
        else:
            SERVER_LOGGER.info(f'Установлено соедение с ПК {client_address}')
            clients.append(client)
        recv_data_lst = []
        send_data_lst = []
        err_lst = []
        # Проверяем на наличие ждущих клиентов
        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            pass

        # принимаем сообщения и если там есть сообщения,
        # кладём в словарь, если ошибка, исключаем клиента.
        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    process_client_message(get_message(client_with_message),
                                           messages, client_with_message)
                except:
                    SERVER_LOGGER.info(f'Клиент {client_with_message.getpeername()} '
                                f'отключился от сервера.')
                    clients.remove(client_with_message)

        # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
        if messages and send_data_lst:
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: time(),
                MESSAGE_TEXT: messages[0][1]
            }
            del messages[0]
            for waiting_client in send_data_lst:
                try:
                    send_message(waiting_client, message)
                except:
                    SERVER_LOGGER.info(f'Клиент {waiting_client.getpeername()} отключился от сервера.')
                    clients.remove(waiting_client)



if __name__ == '__main__':
    main()
