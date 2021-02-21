import json
import time
import unittest
import flask_restful
from flask import Flask

from app import app


class Testing(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        app.config['TESTING'] = True
        # TODO: dodac obsluge bazy danych tutaj
        # w przypadku testowania trzeba korzystac z osobnej bazy
        # ktora sie czysci po kazdym uruchomieniu testow
        # zrobic to dopiero po ogarnieciu poszczegolnych konfiguracji

    def tearDown(self):
        pass

    def test_get_user_route(self):
        response = self.app.get('/user')

        self.assertEqual(200, response.status_code)

    def test_unauthorized_protected_route(self):
        response = self.app.get('/protected')
        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(data['msg'], "Missing Authorization Header")
        self.assertEqual(401, response.status_code)
