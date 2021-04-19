from flask import Response, request, jsonify, make_response, json
from database.models import User, Activity
from .schemas import UserSchema
from database.db import db
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, current_user
)
from flask_restful_swagger_2 import Api, swagger, Resource, Schema
from .swagger_models import User as UserSwaggerModel
from .swagger_models import Login as LoginSwaggerModel
from flask_sqlalchemy import SQLAlchemy
from .security import generate_salt, generate_hash

user_schema = UserSchema()
users_schema = UserSchema(many=True)


class UsersApi(Resource):
    # NOTE: Nizej pokazane jak wyglada autoryzacja
    # dla poszczegolnych endpointow
    @swagger.doc({
        'tags': ['user'],
        'description': 'Returns ALL the users',
        'responses': {
            '200': {
                'description': 'Successfully got all the users',
            }
        },
        'security': [
            {
                'api_key': []
            }
        ]
    })
    @jwt_required()
    def get(self):
        """Return ALL the users"""
        all_users = User.query.all()
        result = users_schema.dump(all_users)

        return jsonify(result)

    @swagger.doc({
        'tags': ['user'],
        'description': 'Adds a new user',
        'parameters': [
            {
                'name': 'Body',
                'in': 'body',
                'schema': UserSwaggerModel,
                'type': 'object',
                'required': 'true'
            },
        ],
        'responses': {
            '200': {
                'description': 'Successfully added new user',
            }
        }
    })
    def post(self):
        """Add a new user"""
        email = request.json['email']
        password = request.json['password']
        firstname = request.json['firstname']
        surname = request.json['surname']
        sex = request.json['sex']
        active = request.json['active']
        created_at = db.func.current_timestamp()
        updated_at = db.func.current_timestamp()

        salt_str = generate_salt(16)
        key = generate_hash(password, salt_str)

        new_user = User(email, key, salt_str, firstname, surname, sex, active,
                        created_at, updated_at)

        # Check if user with given email already exists
        does_exist = User.query.filter_by(email=email).first()
        if does_exist is not None:
            return jsonify({'msg': 'User with given email address already exists'})

        db.session.add(new_user)

        # Now create an empty activity for the user
        new_activity = Activity(0, 0)
        new_user.activity = new_activity

        db.session.commit()

        return user_schema.jsonify(new_user)


class UserApi(Resource):

    # GET single user with given id
    @swagger.doc({
        'tags': ['user'],
        'description': 'Returns specific user',
        'parameters': [
            {
                'name': 'id',
                'in': 'path',
                'type': 'integer',
                'required': 'true'
            },
        ],
        'responses': {
            '200': {
                'description': 'Successfully updated user',
            }
        }
    })
    def get(self, id):
        single_user = User.query.get(id)

        if not single_user:
            return jsonify({'msg': 'No user found'})

        return user_schema.jsonify(single_user)

    @swagger.doc({
        'tags': ['user'],
        'description': 'Updates an user',
        'parameters': [
            {
                'name': 'id',
                'in': 'path',
                'type': 'integer',
                'required': 'true'
            },
            {
                'name': 'Body',
                'in': 'body',
                'schema': UserSwaggerModel,
                'type': 'object',
                'required': 'true'
            },
        ],
        'responses': {
            '200': {
                'description': 'Successfully updated user',
            }
        }
    })
    def put(self, id):
        """Update user"""
        user = User.query.get(id)
        if not user:
            return jsonify({'msg': 'No user found'})

        # TODO: Maybe we can update certain user without specifying
        # all the data and provide only the thing we are about to change?
        email = request.json['email']
        password = request.json['password']
        firstname = request.json['firstname']
        surname = request.json['surname']
        sex = request.json['sex']
        active = request.json['active']
        updated_at = db.func.current_timestamp()

        salt_str = generate_salt(16)
        key = generate_hash(password, salt_str)

        user.email = email
        user.password = key
        user.salt = salt_str
        user.firstname = firstname
        user.surname = surname
        user.sex = sex
        user.active = active
        user.updated_at = updated_at

        db.session.commit()
        return user_schema.jsonify(user)

    @swagger.doc({
        'tags': ['user'],
        'description': 'Deletes an user',
        'parameters': [
            {
                'name': 'id',
                'in': 'path',
                'required': 'true',
                'type': 'integer',
                'schema': {
                    'type': 'integer'
                }
            }
        ],
        'responses': {
            '200': {
                'description': 'Successfully deleted user',
            }
        }
    })
    def delete(self, id):
        """Delete user"""
        user = db.session.query(User).filter(User.id == id).first()
        if not user:
            return jsonify({'msg': 'No user found'})
        db.session.delete(user)
        db.session.commit()

        return jsonify({"msg": "Successfully deleted user"})


class LoginApi(Resource):
    @swagger.doc({
        'tags': ['login'],
        'description': 'Logs in',
        'parameters': [
            {
                'name': 'Body',
                'in': 'body',
                'schema': LoginSwaggerModel,
                'type': 'object',
                'required': 'true'
            },
        ],
        'responses': {
            '200': {
                'description': 'Successfully logged in',
            }
        }
    })
    def post(self):
        """Endpoint to get the token"""
        email = request.json['email']
        password = request.json['password']

        if not email or not password:
            return jsonify({"msg": "Missing email or password parameter"})

        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({"msg": "No user with given email"})

        salt = user.salt
        key = generate_hash(password, salt)

        if user.password == key:
            access_token = create_access_token(identity=email)
            return jsonify({"access_token": access_token})
        else:
            return jsonify({"msg": "Wrong password!"})


class ProtectedApi(Resource):
    @swagger.doc({
        'tags': ['protected'],
        'description': 'Protected endpoint for testing only',
        'parameters': [
            {
                'name': 'Authorization',
                'in': 'header',
                'type': 'string'
            }
        ],
        'produces': [
            'application/json'
        ],
        'responses': {
            '200': {
                'description': 'Authorized',
            },
            '401': {
                'description': 'Unauthorized'
            }
        }
    })
    @jwt_required()
    def get(self):
        """Check if user is authorized"""
        current_user = get_jwt_identity()
        return jsonify({"msg": "Access granted"})
