import sys
import logging
import logs.logs_config.client_logs
import logs.logs_config.server_logs
import traceback
import inspect

if sys.argv[0].find('client') == -1:
    # если не клиент то сервер!
    LOGGER = logging.getLogger('server')
else:
    # ну, раз не сервер, то клиент
    LOGGER = logging.getLogger('client')


class Log:
    def __call__(self, funct):
        def logger(*args, **kwargs):
            result = funct(*args, **kwargs)
            LOGGER.debug(f'Вызов функции {funct.__name__} с параметрами {args} и {kwargs}'
                         f'Вызов из модуля {funct.__module__}.'
                         f'Вызов из функции {inspect.stack()[1][3]}', stacklevel=2
                         )
            return result

        return logger