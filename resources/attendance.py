from flask import Response, request, jsonify, make_response, json
from database.models import Attendance, User
from .schemas import AttendanceSchema
from database.db import db
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, get_jwt
)
from flask_restful_swagger_2 import Api, swagger, Resource, Schema
from .swagger_models import Attendance as AttendanceSwaggerModel
from datetime import datetime

attendance_schema = AttendanceSchema()
attendanceM_schema = AttendanceSchema(many=True)


class AttendanceMApi(Resource):
    @swagger.doc({
        'tags': ['attendance'],
        'description': 'Returns ALL the attendances in current institution_id',
        'responses': {
            '200': {
                'description': 'Successfully got all the attendances',
            }
        },
        'parameters': [
            {
                'name': 'date',
                'in': 'query',
                'type': 'string',
                'format': 'date',
                'description': '*Optional*: Filter by date'
            },
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
        """Return ALL the attendances in current institution_id"""
        claims = get_jwt()
        user_institution_id = claims['institution_id']
        current_user_id = claims['id']

        all_attendances = Attendance.query.all()

        date_query = request.args.get('date')
        only_me_query = request.args.get('only_me')

        if only_me_query == 'true' and date_query is None:
            attendances = Attendance.query.filter(
                Attendance.user_id == current_user_id).all()
            to_return = attendanceM_schema.dump(attendances)
            return jsonify(to_return)

        if date_query is not None:
            # format_date = db.func.date(date_query)
            format_date = datetime.strptime(date_query, '%Y-%m-%d').date()

            all_attendances = Attendance.query.filter(
                Attendance.date == format_date).all()

            if only_me_query == 'true':
                all_attendances = Attendance.query.filter(
                    Attendance.date == format_date).filter(Attendance.user_id == current_user_id).all()

        attendances_matching = []

        for attendance in all_attendances:
            # query user from the attendance
            att_user = User.query.filter(User.id == attendance.user_id).first()

            print(attendance.date)

            if att_user.institution_id == user_institution_id:
                attendances_matching.append(attendance)

        result = attendanceM_schema.dump(attendances_matching)
        return jsonify(result)

    @swagger.doc({
        'tags': ['attendance'],
        'description': 'Adds a new attendance',
        'parameters': [
            {
                'name': 'Body',
                'in': 'body',
                'schema': AttendanceSwaggerModel,
                'type': 'object',
                'required': 'true'
            },
        ],
        'responses': {
            '200': {
                'description': 'Successfully added new attendance',
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
        """Add a new attendance"""
        claims = get_jwt()
        user_roles = claims['roles']

        for r in user_roles:
            if(r['title'] != "Teacher" and r['title'] != "Admin"):
                return jsonify({'msg': 'Insufficient permissions'})

        current_user_id = claims['id']

        date_str = request.json['date']
        present = request.json['present']
        user_id = current_user_id

        user = User.query.get(user_id)
        if not user:
            return jsonify({'msg': 'User does not exist'})

        date = datetime.strptime(date_str, '%Y-%m-%d').date()

        does_exist = Attendance.query.filter(

            Attendance.date == date).filter(Attendance.user_id == current_user_id).first()

        if does_exist is not None:
            return jsonify({'msg': 'Attendance for this date already exists'})

        new_attendance = Attendance(date, present, user_id)

        db.session.add(new_attendance)
        db.session.commit()

        return attendance_schema.jsonify(new_attendance)


class AttendanceApi(Resource):

    # GET single attendance with given id
    def get(self, id):
        single_attendance = Attendance.query.get(id)

        if not single_attendance:
            return jsonify({'msg': 'No attendance found'})

        return attendance_schema.jsonify(single_attendance)

    @swagger.doc({
        'tags': ['attendance'],
        'description': 'Updates an attendance',
        'parameters': [
            {
                'name': 'Body',
                'in': 'body',
                'schema': AttendanceSwaggerModel,
                'type': 'object',
                'required': 'true'
            },
            {
                'name': 'id',
                'in': 'path',
                'description': 'Attendance identifier',
                'type': 'integer'
            }
        ],
        'responses': {
            '200': {
                'description': 'Successfully updated an attendance',
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
        """Update attendance"""
        claims = get_jwt()
        user_roles = claims['roles']

        for r in user_roles:
            if(r['title'] != "Teacher" and r['title'] != "Admin"):
                return jsonify({'msg': 'Insufficient permissions'})

        attendance = Attendance.query.get(id)

        date_str = request.json['date']
        present = request.json['present']
        user_id = request.json['user_id']

        user = User.query.get(user_id)
        if not user:
            return jsonify({'msg': 'User does not exist'})

        date = datetime.strptime(date_str, '%Y-%m-%d').date()

        attendance.date = date
        attendance.present = present
        attendance.user_id = user_id

        db.session.commit()
        return attendance_schema.jsonify(attendance)

    @swagger.doc({
        'tags': ['attendance'],
        'description': 'Deletes an attendance',
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
                'description': 'Successfully deleted an attendance',
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
        """Delete attendance"""
        claims = get_jwt()
        user_roles = claims['roles']

        for r in user_roles:
            if(r['title'] != "Teacher" and r['title'] != "Admin"):
                return jsonify({'msg': 'Insufficient permissions'})
        
        attendance = db.session.query(Attendance).filter(
            Attendance.id == id).first()
        db.session.delete(attendance)
        db.session.commit()

        return jsonify({'msg': 'Successfully removed attendance'})
