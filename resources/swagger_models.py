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
