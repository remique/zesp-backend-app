from flask_restful_swagger_2 import Api, Schema


class User(Schema):
    type = 'object'
    description = 'Must provide these when creating new user'
    properties = {
        'email': {
            'type': 'string'
        },
        'password': {
            'type': 'string'
        },
        'firstname': {
            'type': 'string'
        },
        'surname': {
            'type': 'string'
        },
        'sex': {
            'type': 'integer',
        },
        'active': {
            'type': 'integer',
        },
    }
    required = ['email', 'password', 'firstname', 'surname', 'sex', 'active']


class Login(Schema):
    type = 'object'
    description = 'Must provide these when loggin in'
    properties = {
        'email': {
            'type': 'string'
        },
        'password': {
            'type': 'string'
        },
    }
    required = ['email', 'password']


class Institution(Schema):
    type = 'object'
    description = 'Must provide these when creating new institution'
    properties = {
        'name': {
            'type': 'string'
        },
        'city': {
            'type': 'string'
        },
        'address': {
            'type': 'string'
        },
        'contact_number': {
            'type': 'string'
        },
    }
    required = ['name', 'city', 'address', 'contact_number']


class Role(Schema):
    type = 'object'
    description = 'Must provide these when creating new role'
    properties = {
        'title': {
            'type': 'string'
        },
    }
    required = ['title']


class UserRole(Schema):
    type = 'object'
    description = 'Must provide these when adding role to an user'
    properties = {
        'role_id': {
            'type': 'integer'
        },
        'user_id': {
            'type': 'integer'
        },
    }
    required = ['role_id', 'user_id']


class Group(Schema):
    type = 'object'
    description = 'Must provide these when creating new group'
    properties = {
        'name': {
            'type': 'string'
        },
    }
    required = ['name']


class UserGroup(Schema):
    type = 'object'
    description = 'Must provide these when adding group to an user'
    properties = {
        'group_id': {
            'type': 'integer'
        },
        'user_id': {
            'type': 'integer'
        },
    }
    required = ['group_id', 'user_id']


class Activity(Schema):
    type = 'object'
    description = 'Must provide these when editing user\'s activity'
    properties = {
        'sleep': {
            'type': 'integer'
        },
        'food_scale': {
            'type': 'integer'
        },
    }
    required = ['sleep', 'food_scale']
