import sys
import os
import unittest
from client import presence, process_ans
from variables import *
sys.path.append(os.path.join(os.getcwd(), '..'))


class TestClient(unittest.TestCase):
    """Если подадим все верные параметры результат функции должен совпасть со словарем {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}"""
    def test_ok(self):
        pres = presence()
        pres['time'] = 1.1
        self.assertEqual(pres, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_200_ans(self):
        """Если функция с параметрами response: 200 вернет строку '200 : OK', то тест пройден"""
        self.assertEqual(process_ans({RESPONSE: 200}), '200 : OK')

    def test_400_ans(self):
        """Если функция с параметрами {RESPONSE: 400, ERROR: 'Bad Request'} вернет строку '400 : Bad Request', то тест пройден"""
        self.assertEqual(process_ans({RESPONSE: 400, ERROR: 'Bad Request'}), '400 : Bad Request')

    def test_no_response(self):
        """Тест исключения без поля RESPONSE"""
        self.assertRaises(ValueError, process_ans, {ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()

