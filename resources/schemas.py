from flask_marshmallow import Marshmallow
from database.db import db
from database.models import User, Institution
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy

ma = Marshmallow()

class UserSchema(ma.Schema):
    class Meta:
        model = User
        ordered = True
        fields = ("id", "email", "password", "firstname", "surname",
                  "sex", "active", "created_at", "updated_at")
        dateformat = '%Y-%m-%d %H:%M:%S%z'


class InstitutionSchema(ma.Schema):
    class Meta:
        model = Institution
        ordered = True
        fields = ("id", "name", "city", "address", "contact_number")