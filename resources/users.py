from flask import Response, request, jsonify, make_response, json
from database.models import User, Activity
from .schemas import UserGetSchema, UserTokenSchema
from database.db import db
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, current_user, create_refresh_token, get_jwt
)
from flask_restful_swagger_2 import Api, swagger, Resource, Schema
from .swagger_models import User as UserSwaggerModel
from .swagger_models import Login as LoginSwaggerModel
from flask_sqlalchemy import SQLAlchemy
from .security import generate_salt, generate_hash

import math

user_schema = UserGetSchema()
users_schema = UserGetSchema(many=True)

user_token_schema = UserTokenSchema()


class UsersApi(Resource):
    # NOTE: Nizej pokazane jak wyglada autoryzacja
    # dla poszczegolnych endpointow
    @swagger.doc({
        'tags': ['user'],
        'description': '''Paginate users and display all pagination info and Users inside \
                          the *data* field. If there is no **page** provided, then it will \
                          set automatically to page 1. Also, it will display up to 15 users \
                          per page, unless provided otherwise in optional **per_page** argument.''',
        'responses': {
            '200': {
                'description': 'Successfully got all the users',
            }
        },
        'parameters': [
            {
                'name': 'page',
                'in': 'query',
                'type': 'integer',
                'description': '*Optional*: Which page to return'
            },
            {
                'name': 'per_page',
                'in': 'query',
                'type': 'integer',
                'description': '*Optional*: How many users to return per page *(default=15)*'
            },
        ],
        'security': [
            {
                'api_key': []
            }
        ]
    })
    @jwt_required()
    def get(self):
        """Return ALL the users in Institution of current user"""

        # Get currently logged user's InstitutionId
        claims = get_jwt()
        user_institution_id = claims['institution_id']

        # Get query parameters
        page = request.args.get('page')
        per_page = request.args.get('per_page')

        # If page is not provided, set to first page by default
        if page is None:
            page = 1

        # Default pagination
        if per_page is None:
            per_page = 15

        page_offset = (int(page) - 1) * int(per_page)

        users_total = User.query.filter(
            User.institution_id == user_institution_id).count()

        users_query = User.query.filter(User.institution_id == user_institution_id).offset(
            page_offset).limit(per_page).all()
        query_result = users_schema.dump(users_query)

        result = {
            "total": users_total,
            "per_page": int(per_page),
            "current_page": int(page),
            "last_page": math.ceil(int(users_total) / int(per_page)),
            "data": query_result
        }

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
        institution_id = request.json['institution_id']
        created_at = db.func.current_timestamp()
        updated_at = db.func.current_timestamp()

        salt_str = generate_salt(16)
        key = generate_hash(password, salt_str)

        new_user = User(email, key, salt_str, firstname, surname, institution_id, sex, active,
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
            user_claims = user_token_schema.dump(user)

            access_token = create_access_token(
                identity=email, additional_claims=user_claims)
            refresh_token = create_refresh_token(
                identity=email, additional_claims=user_claims)
            return jsonify({"access_token": access_token, "refresh_token": refresh_token})
        else:
            return jsonify({"msg": "Wrong password!"})


class RefreshTokenApi(Resource):

    @swagger.doc({
        'tags': ['login'],
        'description': 'Refresh expiring token',
        'parameters': [
            {
                'name': 'Authorization',
                'in': 'header',
                'type': 'string'
            }
        ],
        'responses': {
            '200': {
                'description': 'Successfully refreshed token',
            }
        },
    })
    @jwt_required(refresh=True)
    def post(self):
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity, fresh=False)

        return jsonify(access_token=access_token)


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

        # claims = get_jwt()
        # return jsonify({"msg": claims})
        return jsonify({"msg": "Access granted"})
