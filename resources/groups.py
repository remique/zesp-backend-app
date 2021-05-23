from flask import Response, request, jsonify, make_response, json
from database.models import Group, User, user_groups
from .schemas import GroupSchema, UserGetSchema
from database.db import db
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, get_jwt
)
from flask_restful_swagger_2 import Api, swagger, Resource, Schema
from .swagger_models import Group as GroupSwaggerModel
from .swagger_models import UserGroup as UserGroupSwaggerModel

import math

group_schema = GroupSchema()
groups_schema = GroupSchema(many=True)

users_schema = UserGetSchema(many=True)


class GroupsApi(Resource):
    @swagger.doc({
        'tags': ['group'],
        'description': 'Returns ALL the groups',
        'responses': {
            '200': {
                'description': 'Successfully got all the groups',
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
                'description': '*Optional*: How many conversations to return per page'
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
        """Return ALL the groups"""
        current_user_jwt = get_jwt()
        current_user_institution_id = current_user_jwt['institution_id']

        total_groups = Group.query.filter(
            Group.institution_id == current_user_institution_id).count()

        MIN_PER_PAGE = 5
        MAX_PER_PAGE = 30

        # Get query parameters
        page = request.args.get('page')
        per_page = request.args.get('per_page')

        # If page is not provided, set to first page by default
        if page is None or int(page) < 1:
            page = 1

        # Default pagination
        if per_page is None:
            per_page = 15

        if int(per_page) < MIN_PER_PAGE:
            per_page = MIN_PER_PAGE

        if int(per_page) > MAX_PER_PAGE:
            per_page = MAX_PER_PAGE

        last_page = math.ceil(int(total_groups) / int(per_page))

        if int(page) >= last_page:
            page = int(last_page)

        page_offset = (int(page) - 1) * int(per_page)

        institution_groups = Group.query\
            .filter(Group.institution_id == current_user_institution_id)\
            .order_by(Group.id.desc())\
            .offset(page_offset)\
            .limit(per_page).all()

        query_result = groups_schema.dump(institution_groups)

        result = {
            "total": total_groups,
            "per_page": int(per_page),
            "current_page": int(page),
            "last_page": last_page,
            "data": query_result
        }

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
        },
        'security': [
            {
                'api_key': []
            }
        ]
    })
    @jwt_required()
    def post(self):
        """Add a new group"""
        current_user_jwt = get_jwt()
        current_user_institution_id = current_user_jwt['institution_id']
        user_roles = current_user_jwt['roles']

        for r in user_roles:
            if(r['title'] != "Admin"):
                return jsonify({'msg': 'Insufficient permissions'})

        name = request.json['name']
        institution_id = current_user_institution_id
        created_at = db.func.current_timestamp()
        updated_at = db.func.current_timestamp()

        new_group = Group(name, institution_id, created_at, updated_at)

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
        },
        'security': [
            {
                'api_key': []
            }
        ]
    })
    @jwt_required()
    def put(self, id):
        """Update group"""
        current_user_jwt = get_jwt()
        user_roles = current_user_jwt['roles']

        for r in user_roles:
            if(r['title'] != "Admin"):
                return jsonify({'msg': 'Insufficient permissions'})

        group = Group.query.get(id)

        if not group:
            return jsonify({'msg': 'No group found'})

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
        },
        'security': [
            {
                'api_key': []
            }
        ]
    })
    @jwt_required()
    def delete(self, id):
        """Delete group"""
        current_user_jwt = get_jwt()
        user_roles = current_user_jwt['roles']

        for r in user_roles:
            if(r['title'] != "Admin"):
                return jsonify({'msg': 'Insufficient permissions'})
        group = db.session.query(Group).filter(Group.id == id).first()

        if not group:
            return jsonify({'msg': 'No group found'})

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
        },
        'security': [
            {
                'api_key': []
            }
        ]
    })
    @jwt_required()
    def post(self):
        """Add group to an user"""
        current_user_jwt = get_jwt()
        user_roles = current_user_jwt['roles']

        for r in user_roles:
            if(r['title'] != "Admin"):
                return jsonify({'msg': 'Insufficient permissions'})

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
        },
        'security': [
            {
                'api_key': []
            }
        ]
    })
    @jwt_required()
    def delete(self):
        """Delete group from the user"""
        current_user_jwt = get_jwt()
        user_roles = current_user_jwt['roles']

        for r in user_roles:
            if(r['title'] != "Admin"):
                return jsonify({'msg': 'Insufficient permissions'})

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


class UserGroupFilterApi(Resource):
    @swagger.doc({
        'tags': ['usergroup'],
        'description': 'Get all the users in a group',
        'parameters': [
            {
                'name': 'group_id',
                'description': 'Group identifier',
                'in': 'path',
                'type': 'integer'
            },
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
                'description': '*Optional*: How many conversations to return per page'
            },
        ],
        'responses': {
            '200': {
                'description': 'Successfully fetch all the users',
            }
        }
    })
    def get(self, group_id):
        """Get all the users in a group"""

        total_users = User.query.filter(User.groups.any(id=group_id)).count()

        MIN_PER_PAGE = 5
        MAX_PER_PAGE = 30

        # Get query parameters
        page = request.args.get('page')
        per_page = request.args.get('per_page')

        # If page is not provided, set to first page by default
        if page is None or int(page) < 1:
            page = 1

        # Default pagination
        if per_page is None:
            per_page = 15

        if int(per_page) < MIN_PER_PAGE:
            per_page = MIN_PER_PAGE

        if int(per_page) > MAX_PER_PAGE:
            per_page = MAX_PER_PAGE

        last_page = math.ceil(int(total_users) / int(per_page))

        if int(page) >= last_page:
            page = int(last_page)

        page_offset = (int(page) - 1) * int(per_page)

        group_users = User.query\
            .filter(User.groups.any(id=group_id))\
            .offset(page_offset)\
            .limit(per_page).all()

        groups = users_schema.dump(group_users)

        result = {
            "total": total_users,
            "per_page": int(per_page),
            "current_page": int(page),
            "last_page": last_page,
            "data": groups
        }

        return jsonify(result)
