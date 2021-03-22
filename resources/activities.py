from flask import Response, request, jsonify, make_response, json
from database.models import Activity
from .schemas import ActivitySchema
from database.db import db
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from flask_restful_swagger_2 import Api, swagger, Resource, Schema
from .swagger_models import Activity as ActivitySwaggerModel

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
        }
    })
    def get(self):
        """Return ALL the activities"""
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
                'description': 'Activity identifier',
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
