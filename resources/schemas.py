from flask_marshmallow import Marshmallow
from database.db import db
from database.models import (
    User, Institution, Role, Group,
    Activity, Dish, DishMenu, Conversation,
    ConversationReply, Image, News, NewsCategory
)
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy

ma = Marshmallow()


class UserSchema(ma.Schema):
    class Meta:
        model = User
        ordered = True
        fields = ("id", "email", "password", "salt", "firstname", "surname",
                  "institution_id", "sex", "active", "created_at", "updated_at", "roles")
        dateformat = '%Y-%m-%d %H:%M:%S%z'
    roles = ma.Nested('RoleSchema', many=True)


class UserGetSchema(ma.Schema):
    class Meta:
        model = User
        ordered = True
        fields = ("id", "email", "firstname", "surname",
                  "institution_id", "sex", "active", "created_at", "updated_at", "roles")
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
        fields = ("id", "name", "institution_id", "created_at", "updated_at")


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
                  "institution_id", "is_alternative")


class DishMenuSchema(ma.Schema):
    class Meta:
        model = DishMenu
        ordered = True
        fields = ("id", "date", "institution_id", "dish_id")


class ConversationSchema(ma.Schema):
    class Meta:
        model = Conversation
        ordered = True
        fields = ("id", "user_one", "user_two", "conversation_replies")
    conversation_replies = ma.Nested(
        'ConversationReplySchema', many=True)


class ConversationLastSchema(ma.Schema):
    class Meta:
        model = Conversation
        ordered = True
        fields = ("id", "user_one_obj", "user_two_obj", "conversation_replies")

    conversation_replies = ma.Nested(
        'ConversationReplyLastSchema', many=True, data_key='last_reply')

    user_two_obj = ma.Nested(
        'UserNestedSchema', many=False, data_key='user_two')


class ConversationReplyLastSchema(ma.Schema):
    class Meta:
        model = ConversationReply
        ordered = True
        fields = ("id", "reply", "reply_time",
                  "reply_user_id")
    # reply_user = ma.Nested('UserNestedSchema', many=False)


class ConversationReplySchema(ma.Schema):
    class Meta:
        model = ConversationReply
        ordered = True
        fields = ("id", "reply", "reply_time",
                  "reply_user_id", "conv_id")
    # reply_user = ma.Nested('UserNestedSchema', many=False)


class UserNestedSchema(ma.Schema):
    class Meta:
        model = User
        ordered = True
        fields = ("id", "email", "firstname", "surname",
                  "sex", "active")


class ImageSchema(ma.Schema):
    class Meta:
        model = Image
        ordered = True
        fields = ("id", "url", "created_at", "updated_at")


class NewsSchema(ma.Schema):
    class Meta:
        model = News
        ordered = True
        fields = ("title", "details", "priority", "created_at",
                  "updated_at", "category_id", "institution_id", "author_id")


class NewsCategorySchema(ma.Schema):
    class Meta:
        model = NewsCategory
        ordered = True
        fields = ("id", "name", "created_at", "updated_at")


class UserTokenSchema(ma.Schema):
    class Meta:
        model = User
        ordered = True
        fields = ("id", "email", "institution_id", "firstname", "surname",
                  "sex", "active", "roles")
    roles = ma.Nested('RoleSchema', many=True)
