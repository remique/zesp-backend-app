import json
import time
import unittest
import flask_restful
from flask import Flask

from tests.test_base import TestBase


class TestInstitutions(TestBase):

    def test_get_user_route(self):
        response = self.app.get('/user', headers=self.header)

        self.assertEqual(200, response.status_code)

    def test_add_institution(self):
        institution_data = {
            "name": "Przedszkole Alfik",
            "city": "Toruń",
            "address": "Łyskowskiego 12",
            "contact_number": "123-456-789",
            "admin_email": "jakismail@jakismail.pl",
            "admin_password": "1234",
            "admin_firstname": "Krystyna",
            "admin_surname": "Janda",
            "admin_sex": 0
        }

        institution_result = self.app.post(
            '/institution',
            data=json.dumps(institution_data),
            content_type='application/json',
            headers=self.header
        )
        self.assertEqual(200, institution_result.status_code)
