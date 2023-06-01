import sys
import os
import unittest
sys.path.append(os.path.join(os.getcwd(), '..'))
from server import *
from variables import *


class TestServer(unittest.TestCase):
    def test_process_client_message(self):
        message_test = {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
        self.assertEqual({RESPONSE: 200}, process_client_message(message_test))

    def test_no_action(self):
        message_test = {'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
        self.assertEqual({RESPONSE: 400, ERROR: 'Bad Request'}, process_client_message(message_test))

    def test_no_time(self):
        message_test = {'action': 'presence', 'user': {'account_name': 'Guest'}}
        self.assertEqual({RESPONSE: 400, ERROR: 'Bad Request'}, process_client_message(message_test))

    def test_no_user(self):
        message_test = {'action': 'presence', 'time': 1573760672.167031}
        self.assertEqual({RESPONSE: 400, ERROR: 'Bad Request'}, process_client_message(message_test))

    def test_bad_account_name(self):
        message_test = {'action': 'presence', 'time': 1573760672.167031, 'user': {'account_name': 'Guest12'}}
        self.assertEqual({RESPONSE: 400, ERROR: 'Bad Request'}, process_client_message(message_test))

    def test_bad_message(self):
        message_test = {'action': 'presenceed', 'time': 1573760672.167031, 'user': {'account_name': 'Guest'}}
        self.assertEqual({RESPONSE: 400, ERROR: 'Bad Request'}, process_client_message(message_test))


if __name__ == '__main__':
    unittest.main()
