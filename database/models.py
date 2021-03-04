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
    password = db.Column(db.String(40), nullable=False)
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

    def __init__(self, email, password, firstname, surname, sex, active, created_at, updated_at):
        self.email = email
        self.password = password
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

    def __init__(self, name, city, address, contact_number):
        self.name = name
        self.city = city
        self.address = address
        self.contact_number = contact_number


# class UserRole(db.Model):
#     role_id = db.Column(db.Integer, db.ForeignKey('role.id'), primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

#     def __init__(self, role_id, user_id):
#         self.role_id = role_id
#         self.user_id = user_id


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
