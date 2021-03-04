from flask import Response, request, jsonify, make_response, json
from database.models import Group, User, user_groups
from .schemas import GroupSchema
from database.db import db
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from flask_restful_swagger_2 import Api, swagger, Resource, Schema
from .swagger_models import Group as GroupSwaggerModel
from .swagger_models import UserGroup as UserGroupSwaggerModel

group_schema = GroupSchema()
groups_schema = GroupSchema(many=True)


class GroupsApi(Resource):
    @swagger.doc({
        'tags': ['group'],
        'description': 'Returns ALL the groups',
        'responses': {
            '200': {
                'description': 'Successfully got all the groups',
            }
        }
    })
    def get(self):
        """Return ALL the groups"""
        all_groups = Group.query.all()
        result = groups_schema.dump(all_groups)
        return jsonify(result)

    @swagger.doc({
        'tags': ['group'],
        'description': 'Adds a new group',
        'parameters': [
            {
                'name': 'Body',
                'in': 'body',
                'schema': GroupSwaggerModel,
                'type': 'object',
                'required': 'true'
            },
        ],
        'responses': {
            '200': {
                'description': 'Successfully added new group',
            }
        }
    })
    def post(self):
        """Add a new group"""
        name = request.json['name']
        created_at = db.func.current_timestamp()
        updated_at = db.func.current_timestamp()

        new_group = Group(name, created_at, updated_at)

        db.session.add(new_group)
        db.session.commit()

        return group_schema.jsonify(new_group)


class GroupApi(Resource):
    # GET single role with given id

    @swagger.doc({
        'tags': ['group'],
        'description': 'Get specific group',
        'parameters': [
            {
                'name': 'id',
                'description': 'Group identifier',
                'in': 'path',
                'type': 'integer',
            }
        ],
        'responses': {
            '200': {
                'description': 'Successfully got group'
            }
        }
    })
    def get(self, id):
        """Get group by ID"""
        single_group = Group.query.get(id)

        if not single_group:
            return jsonify({'msg': 'No group found'})

        return group_schema.jsonify(single_group)

    @swagger.doc({
        'tags': ['group'],
        'description': 'Updates a group',
        'parameters': [
            {
                'name': 'Body',
                'in': 'body',
                'schema': GroupSwaggerModel,
                'type': 'object',
                'required': 'true'
            },
            {
                'name': 'id',
                'description': 'Group identifier',
                'in': 'path',
                'type': 'integer'
            },
        ],
        'responses': {
            '200': {
                'description': 'Successfully updated group',
            }
        }
    })
    def put(self, id):
        """Update group"""
        group = Group.query.get(id)

        name = request.json['name']
        updated_at = db.func.current_timestamp()

        group.name = name
        group.updated_at = updated_at

        db.session.commit()
        return group_schema.jsonify(group)

    @swagger.doc({
        'tags': ['group'],
        'description': 'Deletes group',
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
                'description': 'Successfully deleted group',
            }
        }
    })
    def delete(self, id):
        """Delete group"""
        group = db.session.query(Group).filter(Group.id == id).first()
        db.session.delete(group)
        db.session.commit()

        return jsonify({'msg': 'Successfully removed group'})


class UserGroupsApi(Resource):
    @swagger.doc({
        'tags': ['usergroup'],
        'description': 'Returns specific user group',
        'parameters': [
            {
                'name': 'userid',
                'description': 'User identifier',
                'in': 'path',
                'type': 'integer'
            }
        ],
        'responses': {
            '200': {
                'description': 'Successfully got all the usergroups',
            }
        }
    })
    def get(self, userid):
        user = User.query.get(userid)
        if user is None:
            return jsonify({'msg': 'User doesnt exist'})

        groups = groups_schema.dump(user.groups)
        return jsonify(groups)


class UserGroupApi(Resource):
    @swagger.doc({
        'tags': ['usergroup'],
        'description': 'Gives user a group',
        'parameters': [
            {
                'name': 'Body',
                'in': 'body',
                'schema': UserGroupSwaggerModel,
                'type': 'object',
                'required': 'true'
            },
        ],
        'responses': {
            '200': {
                'description': 'Successfully added group to an user',
            }
        }
    })
    def post(self):
        """Add group to an user"""
        g_id = request.json['group_id']
        u_id = request.json['user_id']

        user = User.query.get(u_id)
        if user is None:
            return jsonify({'msg': 'User doesnt exist'})
        group = Group.query.get(g_id)
        if group is None:
            return jsonify({'msg': 'Group doesnt exist'})

        if(group in user.groups):
            return jsonify({'msg': 'User already has this group'})

        user.groups.append(group)
        db.session.commit()

        return jsonify({'msg': 'Successfully added group to the user'})

    @swagger.doc({
        'tags': ['usergroup'],
        'description': 'Removes a group from user',
        'parameters': [
            {
                'name': 'Body',
                'in': 'body',
                'schema': UserGroupSwaggerModel,
                'type': 'object',
                'required': 'true'
            },
        ],
        'responses': {
            '200': {
                'description': 'Successfully removed group from the user',
            }
        }
    })
    def delete(self):
        """Delete group from the user"""
        g_id = request.json['group_id']
        u_id = request.json['user_id']

        user = User.query.get(u_id)
        if user is None:
            return jsonify({'msg': 'User doesnt exist'})
        group = Group.query.get(g_id)
        if group is None:
            return jsonify({'msg': 'Group doesnt exist'})

        if(group in user.groups):
            result = user.groups.remove(group)
            db.session.commit()
            return jsonify({'msg': 'Group removed'})
        else:
            return jsonify({'msg': 'User doesnt have selected group'})
