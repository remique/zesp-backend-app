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
        'description': '''Return all the activities. \
                GET endpoint without any params returns all activities \
                existing in the application and is not really useful. \
                \n Parameters: \n \n \
                \n * *(Optional)* `only_me`: returns an activity for currently \
                logged in user. Note that it may show nothing if user is an \
                admin and should only be used for accounts with a role of *Child* \
                (as they are created automatically for them) \n \
                \n * *(Optional)* `only_institution`: returns all activities in \
                an institution for a current user''',
        'responses': {
            '200': {
                'description': 'Successfully got all the activities',
            },
            '401': {
                'description': 'Unauthorized request',
            }
        },
        'parameters': [
            {
                'name': 'only_me',
                'in': 'query',
                'type': 'boolean',
            },
            {
                'name': 'only_institution',
                'in': 'query',
                'type': 'boolean',
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
        current_user_institution_id = claims['institution_id']

        only_me_query = request.args.get('only_me')
        only_institution_query = request.args.get('only_institution')

        if only_institution_query == 'true' and only_me_query != 'true':
            activities = Activity.query.all()
            act_copy = []

            for activity in activities:
                user_activity = User.query\
                    .filter(User.id == activity.user_id)\
                    .first()

                if user_activity.institution_id == current_user_institution_id:
                    act_copy.append(activity)

            result = activities_schema.dump(act_copy)
            return jsonify(result)

        if only_me_query == 'true':
            user_activities = Activity.query\
                .filter(Activity.user_id == current_user_id).first()
            result = activity_schema.dump(user_activities)
            return jsonify(result)

        all_activities = Activity.query.all()
        result = activities_schema.dump(all_activities)
        return jsonify(result)


class ActivityApi(Resource):

    @swagger.doc({
        'tags': ['activity'],
        'description': '''Updates an activity. Please do note, that \
                it requires user updating an activity to be in the same \
                institution as the user being updated. \n \
                Params: \n \
                \n * (Required) `id`: User identifier''',
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
                'type': 'integer'
            }
        ],
        'responses': {
            '200': {
                'description': 'Successfully updated an activity',
            },
            '401': {
                'description': 'Unauthorized request',
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
        """Update an activity by User ID"""
        claims = get_jwt()
        user_institution_id = claims['institution_id']

        activity = Activity.query\
            .filter(Activity.user_id == id).first()

        if activity is None:
            return jsonify({'msg': 'No activity for this user'})

        activity_user = User.query\
            .filter(User.id == id).first()

        if activity_user.institution_id != user_institution_id:
            return jsonify({'msg': 'User being updated does not belong to the instution of currently logged in User'})

        sleep = request.json['sleep']
        food_scale = request.json['food_scale']

        activity.sleep = sleep
        activity.food_scale = food_scale

        db.session.commit()
        return activity_schema.jsonify(activity)


class GroupActivitiesApi(Resource):
    @swagger.doc({
        'tags': ['activity'],
        'description': '''Return all the child activities in certain group. \
                GET endpoint returns all activities for users with Child \
                role and group name passed as a parameter. \
                Params: \n \
                \n * (Required) `group`: Group name''',
        'parameters': [
            {
                'name': 'group',
                'in': 'query',
                'type': 'string'
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
    def get(self):
        """Search child activities by group"""

        # Get currently logged user's InstitutionId
        claims = get_jwt()
        current_user_inst_id = claims['institution_id']

        role_str = "Child"
        group_str = request.args.get('group')
        activity_list = []

        role = Role.query.filter(Role.title == role_str).first()
        group = Group.query.filter(Group.name == group_str)\
            .filter(Group.institution_id == current_user_inst_id).first()

        print("Searching for: ", group.name)

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

        users_clone = []

        for usr in users:
            print(usr.groups)
            # in_groups = group in usr.groups
            # print("Is group queried in usr.groups?: ", in_groups)
            # if in_groups:
            #     users_clone.append(usr)
            # for grp in usr.groups:

        print(users_clone)

        # Get users with given group
        users = list(filter(lambda x: group in x.groups, users))
        print(users)

        # Get activities
        for u in activities:
            user = list(filter(lambda x: x.id == u.user_id, users))
            if(user):
                activity_list.append(u)

        result = activities_schema.dump(activity_list)

        if not activity_list:
            return jsonify({"msg": "No matching activities"})

        return jsonify(result)
