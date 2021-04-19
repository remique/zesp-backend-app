from .db import db
import datetime
import time

# TODO: Data domyslnie jako UTC, odpowiednie strefy beda na frontendzie?

user_roles = db.Table('user_roles',
                      db.Column('role_id', db.Integer, db.ForeignKey(
                          'role.id'), primary_key=True),
                      db.Column('user_id', db.Integer, db.ForeignKey(
                          'user.id'), primary_key=True))

user_groups = db.Table('user_groups',
                       db.Column('group_id', db.Integer, db.ForeignKey(
                           'group.id'), primary_key=True),
                       db.Column('user_id', db.Integer, db.ForeignKey(
                           'user.id'), primary_key=True))


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=db.func.current_timestamp())

    def __init__(self, title, created_at, updated_at):
        self.title = title
        self.created_at = created_at
        self.updated_at = updated_at


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(40), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    salt = db.Column(db.String(16), nullable=False)
    firstname = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(40), nullable=False)
    sex = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=db.func.current_timestamp())
    roles = db.relationship('Role', secondary=user_roles,
                            backref=db.backref('users', lazy='dynamic'))
    groups = db.relationship('Group', secondary=user_groups,
                             backref=db.backref('users', lazy='dynamic'))
    activity = db.relationship(
        'Activity', backref='user', lazy=True, uselist=False)

    replies = db.relationship('ConversationReply',
                              backref='user', lazy=True)

    def __init__(self, email, password, salt, firstname, surname, sex, active, created_at, updated_at):
        self.email = email
        self.password = password
        self.salt = salt
        self.firstname = firstname
        self.surname = surname
        self.sex = sex
        self.active = active
        self.created_at = created_at
        self.updated_at = updated_at


class Institution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    city = db.Column(db.String(45), nullable=False)
    address = db.Column(db.String(128), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    dishes = db.relationship(
        'Dish', cascade="all,delete", backref='institution')
    dishMenus = db.relationship(
        'DishMenu', cascade="all,delete", backref='institution')

    def __init__(self, name, city, address, contact_number):
        self.name = name
        self.city = city
        self.address = address
        self.contact_number = contact_number


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=db.func.current_timestamp())

    def __init__(self, name, created_at, updated_at):
        self.name = name
        self.created_at = created_at
        self.updated_at = updated_at


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sleep = db.Column(db.Integer, nullable=False)
    food_scale = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, sleep, food_scale):
        self.sleep = sleep
        self.food_scale = food_scale
        # self.user_id = user_id


class DishMenu(db.Model):
    __tablename__ = 'dishmenu'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False,
                     default=db.func.current_timestamp())
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'))
    dishes = db.relationship('Dish', cascade="all,delete", backref='DishMenu')

    def __init__(self, date, institution_id):
        self.date = date
        self.institution_id = institution_id


class Dish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    description = db.Column(db.String(128), nullable=True)
    type = db.Column(db.String(45), nullable=False)
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'))
    dishMenu_id = db.Column(db.Integer, db.ForeignKey('dishmenu.id'))
    is_alternative = db.Column(db.Integer, nullable=False)

    def __init__(self, name, description, type, institution_id, dishMenu_id, is_alternative):
        self.name = name
        self.description = description
        self.type = type
        self.institution_id = institution_id
        self.dishMenu_id = dishMenu_id
        self.is_alternative = is_alternative


class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_one = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_two = db.Column(db.Integer, db.ForeignKey('user.id'))

    conversation_replies = db.relationship('ConversationReply',
                                           backref='conversation', lazy=True)

    def __init__(self, user_one, user_two):
        self.user_one = user_one
        self.user_two = user_two


class ConversationReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reply = db.Column(db.String(512), nullable=False)
    reply_time = db.Column(db.DateTime, nullable=False,
                           default=db.func.current_timestamp())
    reply_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    conv_id = db.Column(db.Integer, db.ForeignKey('conversation.id'))

    reply_user = db.relationship(
        'User', backref='conversation_reply', lazy=True, uselist=False)

    def __init__(self, reply, reply_time, reply_user_id, conv_id):
        self.reply = reply
        self.reply_time = reply_time
        self.reply_user_id = reply_user_id
        self.conv_id = conv_id
