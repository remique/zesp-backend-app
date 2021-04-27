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
    required = ['email', 'password', 'firstname',
                'surname', 'sex', 'active']


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


class DishMenu(Schema):
    type = 'object'
    description = 'Must provide these when creating dish menu'
    properties = {
        'date': {
            'type': 'string',
            'format': 'date'
        },
        'institution_id': {
            'type': 'integer'
        },
        'dish_id': {
            'type': 'integer'
        },
    }
    required = ['date', 'institution_id', 'dish_id']


class Dish(Schema):
    type = 'object'
    description = 'Must provide these when creating dish'
    properties = {
        'name': {
            'type': 'string'
        },
        'description': {
            'type': 'string'
        },
        'type': {
            'type': 'string'
        },
        'institution_id': {
            'type': 'integer'
        },
        'is_alternative': {
            'type': 'integer'
        }
    }
    required = ['name', 'type', 'institution_id', 'is_alternative']


class Conversation(Schema):
    type = 'object'
    description = 'Must provide these when creating new conversation'
    properties = {
        'user_two': {
            'type': 'integer'
        },
    }
    required = ['user_two']


class ConversationReply(Schema):
    type = 'object'
    description = 'Must provide these when creating new reply'
    properties = {
        'reply': {
            'type': 'string'
        },
        'conv_id': {
            'type': 'integer'
        },
    }
    required = ['reply', 'conv_id']


class Image(Schema):
    type = 'object'
    description = 'Must provide these when creating new image'
    properties = {
        'url': {
            'type': 'string'
        }
    }
    required = ['url']


class News(Schema):
    type = 'object'
    description = 'Must provide these when creating news'
    properties = {
        'title': {
            'type': 'string'
        },
        'details': {
            'type': 'string'
        },
        'priority': {
            'type': 'boolean'
        },
        'category_id': {
            'type': 'integer'
        },
        'institution_id': {
            'type': 'integer'
        },
        'author_id': {
            'type': 'integer'
        }
    }
    required = ['title', 'details', 'priority']


class NewsCategory(Schema):
    type = 'object'
    description = 'Must provide these when creating news category'
    properties = {
        'name': {
            'type': 'string'
        }
    }
    required = ['name']


class PasswordChange(Schema):
    type = 'object'
    description = 'Must provide these when changing password'
    properties = {
        'password': {
            'type': 'string'
        },
        'repeat_password': {
            'type': 'string'
        }
    }
    required = ['password', 'repeat_password']


class UserLookup(Schema):
    type = 'object'
    description = 'Must provide when doing user lookup'
    properties = {
        'name_like': {
            'type': 'string'
        }
    }
    required = ['name_like']
