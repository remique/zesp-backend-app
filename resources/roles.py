from flask import Response, request, jsonify, make_response, json
from database.models import Role, User, user_roles
from .schemas import RoleSchema, UserRoleSchema
from database.db import db
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from flask_restful_swagger_2 import Api, swagger, Resource, Schema
from .swagger_models import Role as RoleSwaggerModel
from .swagger_models import UserRole as UserRoleSwaggerModel

role_schema = RoleSchema()
roles_schema = RoleSchema(many=True)

user_role_schema = UserRoleSchema()
user_roles_schema = UserRoleSchema(many=True)

class RolesApi(Resource):
    @swagger.doc({
        'tags': ['role'],
        'description': 'Returns ALL the roles',
        'responses': {
            '200': {
                'description': 'Successfully got all the roles',
            }
        }
    })
    def get(self):
        """Return ALL the roles"""
        all_roles = Role.query.all()
        result = roles_schema.dump(all_roles)
        return jsonify(result)

    @swagger.doc({
        'tags': ['role'],
        'description': 'Adds a new role',
        'parameters': [
            {
                'name': 'Body',
                'in': 'body',
                'schema': RoleSwaggerModel,
                'type': 'object',
                'required': 'true'
            },
        ],
        'responses': {
            '200': {
                'description': 'Successfully added new role',
            }
        }
    })
    def post(self):
        """Add a new role"""
        title = request.json['title']
        created_at = db.func.current_timestamp()
        updated_at = db.func.current_timestamp()

        new_role = Role(title, created_at, updated_at)

        db.session.add(new_role)
        db.session.commit()

        return role_schema.jsonify(new_role)

class RoleApi(Resource):
    # GET single role with given id
    def get(self, id):
        single_role = Role.query.get(id)

        if not single_role:
            return jsonify({'msg': 'No role found'})

        return role_schema.jsonify(single_role)

    @swagger.doc({
        'tags': ['role'],
        'description': 'Updates a role',
        'parameters': [
            {
                'name': 'Body',
                'in': 'body',
                'schema': RoleSwaggerModel,
                'type': 'object',
                'required': 'true'
            },
        ],
        'responses': {
            '200': {
                'description': 'Successfully updated a role',
            }
        }
    })
    def put(self, id):
        """Update role"""
        role = Role.query.get(id)

        title = request.json['title']
        updated_at = db.func.current_timestamp()

        role.title = title
        role.updated_at = updated_at

        db.session.commit()
        return role_schema.jsonify(role)

    @swagger.doc({
        'tags': ['role'],
        'description': 'Deletes a role',
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
                'description': 'Successfully deleted a role',
            }
        }
    })
    def delete(self, id):
        """Delete role"""
        role = db.session.query(Role).filter(Role.id == id).first()
        db.session.delete(role)
        db.session.commit()

        return jsonify({'msg': 'Successfully removed role'})

class UserRolesApi(Resource):
    @swagger.doc({
        'tags': ['userrole'],
        'description': 'Returns ALL the user roles',
        'responses': {
            '200': {
                'description': 'Successfully got all the userroles',
            }
        }
    })
    def get(self, userid):
        user = User.query.get(userid)
        if user is None:
            return jsonify({'msg': 'User doesnt exist'})

        roles = user_roles_schema.dump(user.roles)
        return jsonify(roles)

class UserRoleApi(Resource):
    @swagger.doc({
        'tags': ['userrole'],
        'description': 'Gives user a role',
        'parameters': [
            {
                'name': 'Body',
                'in': 'body',
                'schema': UserRoleSwaggerModel,
                'type': 'object',
                'required': 'true'
            },
        ],
        'responses': {
            '200': {
                'description': 'Successfully added role to an user',
            }
        }
    })
    def post(self):
        """Add role to an user"""
        r_id = request.json['role_id']
        u_id = request.json['user_id']

        user = User.query.get(u_id)
        if user is None:
            return jsonify({'msg': 'User doesnt exist'})
        role = Role.query.get(r_id)
        if role is None:
            return jsonify({'msg': 'Role doesnt exist'})

        if(role in user.roles):
            return jsonify({'msg': 'User already has this role'})

        user.roles.append(role)
        db.session.commit()

        return jsonify({'msg': 'Successfully added role to the user'})

    @swagger.doc({
        'tags': ['userrole'],
        'description': 'Removes role from user',
        'parameters': [
            {
                'name': 'Body',
                'in': 'body',
                'schema': UserRoleSwaggerModel,
                'type': 'object',
                'required': 'true'
            },
        ],
        'responses': {
            '200': {
                'description': 'Successfully removed role from the user',
            }
        }
    })
    def delete(self):
        """Delete role from the user"""
        r_id = request.json['role_id']
        u_id = request.json['user_id']

        user = User.query.get(u_id)
        if user is None:
            return jsonify({'msg': 'User doesnt exist'})
        role = Role.query.get(r_id)
        if role is None:
            return jsonify({'msg': 'Role doesnt exist'})

        if(role in user.roles):
            result = user.roles.remove(role)
            db.session.commit()
            return jsonify({'msg': 'Role removed'})
        else:
            return jsonify({'msg': 'User doesnt have selected role'})