from flask import Response, request, jsonify, make_response, json
from database.models import Activity, User, Role, Group
from .schemas import ActivitySchema
from database.db import db
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, get_jwt
)
from flask_restful_swagger_2 import Api, swagger, Resource, Schema
from .swagger_models import Activity as ActivitySwaggerModel
from .swagger_models import GroupActivityLookup

activity_schema = ActivitySchema()
activities_schema = ActivitySchema(many=True)


class ActivitiesApi(Resource):
    @swagger.doc({
        'tags': ['activity'],
        'description': 'Returns ALL the activities',
        'responses': {
            '200': {
                'description': 'Successfully got all the activities',
            }
        },
        'parameters': [
            {
                'name': 'only_me',
                'in': 'query',
                'type': 'boolean',
                'description': '*Optional*: Filter by logged in user only'
            }
        ],
        'security': [
            {
                'api_key': []
            }
        ]
    })
    @jwt_required()
    def get(self):
        """Return ALL the activities"""
        claims = get_jwt()
        current_user_id = claims['id']

        only_me_query = request.args.get('only_me')

        if only_me_query == 'true':
            user_activities = Activity.query\
                .filter(Activity.user_id == current_user_id).first()
            result = activity_schema.dump(user_activities)
            return jsonify(result)

        all_activities = Activity.query.all()
        result = activities_schema.dump(all_activities)
        return jsonify(result)


class ActivityApi(Resource):

    # GET single activity with given id
    def get(self, id):
        single_activity = Activity.query.get(id)

        if not single_activity:
            return jsonify({'msg': 'No activity found'})

        return activity_schema.jsonify(single_activity)

    @swagger.doc({
        'tags': ['activity'],
        'description': 'Updates an activity',
        'parameters': [
            {
                'name': 'Body',
                'in': 'body',
                'schema': ActivitySwaggerModel,
                'type': 'object',
                'required': 'true'
            },
            {
                'name': 'id',
                'in': 'path',
                'description': 'User identifier',
                'type': 'integer'
            }
        ],
        'responses': {
            '200': {
                'description': 'Successfully updated an activity',
            }
        }
    })
    def put(self, id):
        """Update activity"""
        activity = Activity.query.get(id)

        sleep = request.json['sleep']
        food_scale = request.json['food_scale']

        activity.sleep = sleep
        activity.food_scale = food_scale

        db.session.commit()
        return activity_schema.jsonify(activity)


class GroupActivitiesApi(Resource):
    @swagger.doc({
        'tags': ['activity'],
        'description': 'Looks for group activities within institution',
        'parameters': [
            {
                'name': 'Body',
                'in': 'body',
                'schema': GroupActivityLookup,
                'type': 'object',
                'required': 'true'
            },
        ],
        'responses': {
            '200': {
                'description': 'Found matching activities',
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
        """Search child activities by group"""

        # Get currently logged user's InstitutionId
        claims = get_jwt()
        current_user_inst_id = claims['institution_id']

        role_str = "Child"
        group_str = request.json['group']
        activity_list = []

        role = Role.query.filter(Role.title == role_str).first()
        group = Group.query.filter(Group.name == group_str).first()

        if not role:
            return jsonify({'msg': 'Child role doesnt exist'})

        if not group:
            return jsonify({'msg': 'Group doesnt exist'})

        activities = Activity.query.all()
        # Get users from user institution
        users = User.query.filter(
            User.institution_id == current_user_inst_id).all()
        # Get users with given role
        users = list(filter(lambda x: role in x.roles, users))
        # Get users with given group
        users = list(filter(lambda x: group in x.groups, users))

        # Get activities
        for u in activities:
            user = list(filter(lambda x: x.id == u.user_id, users))
            if(user):
                activity_list.append(u)

        result = activities_schema.dump(activity_list)

        if not activity_list:
            return jsonify({"msg": "No matching activities"})

        return jsonify(result)
