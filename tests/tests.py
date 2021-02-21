import json
import time
import unittest
import flask_restful
from flask import Flask
from app import app


class Testing(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def tearDown(self):
        pass

    def create_app(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.baseURL = "http://localhost:5000"
        pass

    def test_flask_app(self):
        rv = self.client.get('/user')
        assert rv.status_code == 200


if __name__ == '__main__':
    unittest.main()
