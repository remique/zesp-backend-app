from flask_marshmallow import Marshmallow
from database.db import db
from database.models import (
    User, Institution, Role, Group,
    Activity, Dish, DishMenu, Conversation,
    ConversationReply
)
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy

ma = Marshmallow()


class UserSchema(ma.Schema):
    class Meta:
        model = User
        ordered = True
        fields = ("id", "email", "password", "salt", "firstname", "surname",
                  "sex", "active", "created_at", "updated_at", "roles")
        dateformat = '%Y-%m-%d %H:%M:%S%z'
    roles = ma.Nested('RoleSchema', many=True)


class InstitutionSchema(ma.Schema):
    class Meta:
        model = Institution
        ordered = True
        fields = ("id", "name", "city", "address", "contact_number")


class RoleSchema(ma.Schema):
    class Meta:
        model = Role
        ordered = True
        fields = ("id", "title", "created_at", "updated_at")


class GroupSchema(ma.Schema):
    class Meta:
        model = Role
        ordered = True
        fields = ("id", "name", "created_at", "updated_at")


class ActivitySchema(ma.Schema):
    class Meta:
        model = Activity
        ordered = True
        fields = ("id", "sleep", "food_scale", "user_id")


class DishSchema(ma.Schema):
    class Meta:
        model = Dish
        ordered = True
        fields = ("id", "name", "description", "type",
                  "institution_id", "dishMenu_id", "is_alternative")


class DishMenuSchema(ma.Schema):
    class Meta:
        model = DishMenu
        ordered = True
        fields = ("id", "date", "institution_id")


class ConversationSchema(ma.Schema):
    class Meta:
        model = Conversation
        ordered = True
        fields = ("id", "user_one", "user_two")


class ConversationReplySchema(ma.Schema):
    class Meta:
        model = ConversationReply
        ordered = True
        fields = ("id", "reply", "reply_time",
                  "reply_user", "conv_id")
    reply_user = ma.Nested('UserNestedSchema', many=False)


class UserNestedSchema(ma.Schema):
    class Meta:
        model = User
        ordered = True
        fields = ("id", "email", "firstname", "surname",
                  "sex", "active")
