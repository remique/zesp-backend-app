from flask import Response, request, jsonify, make_response, json
from database.models import Institution
from .schemas import InstitutionSchema
from database.db import db
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from flask_restful_swagger_2 import Api, swagger, Resource, Schema
from .swagger_models import Institution as InstitutionSwaggerModel

institution_schema = InstitutionSchema()
institutions_schema = InstitutionSchema(many=True)


class InstitutionsApi(Resource):
    @swagger.doc({
        'tags': ['institution'],
        'description': 'Returns ALL the institutions',
        'responses': {
            '200': {
                'description': 'Successfully got all the institutions',
            }
        }
    })
    def get(self):
        """Return ALL the institutions"""
        all_institutions = Institution.query.all()
        result = institutions_schema.dump(all_institutions)
        return jsonify(result)

    @swagger.doc({
        'tags': ['institution'],
        'description': 'Adds a new institution',
        'parameters': [
            {
                'name': 'Body',
                'in': 'body',
                'schema': InstitutionSwaggerModel,
                'type': 'object',
                'required': 'true'
            },
        ],
        'responses': {
            '200': {
                'description': 'Successfully added new institution',
            }
        }
    })
    def post(self):
        """Add a new institution"""
        name = request.json['name']
        city = request.json['city']
        address = request.json['address']
        contact_number = request.json['contact_number']

        new_institution = Institution(name, city, address, contact_number)

        db.session.add(new_institution)
        db.session.commit()

        return institution_schema.jsonify(new_institution)


class InstitutionApi(Resource):

    # GET single institution with given id
    def get(self, id):
        single_institution = Institution.query.get(id)

        if not single_institution:
            return jsonify({'msg': 'No institution found'})

        return institution_schema.jsonify(single_institution)

    @swagger.doc({
        'tags': ['institution'],
        'description': 'Updates an institution',
        'parameters': [
            {
                'name': 'Body',
                'in': 'body',
                'schema': InstitutionSwaggerModel,
                'type': 'object',
                'required': 'true'
            },
            {
                'name': 'id',
                'in': 'path',
                'description': 'Institution identifier',
                'type': 'integer'
            }
        ],
        'responses': {
            '200': {
                'description': 'Successfully updated an institution',
            }
        }
    })
    def put(self, id):
        """Update institution"""
        institution = Institution.query.get(id)

        name = request.json['name']
        city = request.json['city']
        address = request.json['address']
        contact_number = request.json['contact_number']

        institution.name = name
        institution.city = city
        institution.address = address
        institution.contact_number = contact_number

        db.session.commit()
        return institution_schema.jsonify(institution)

    @swagger.doc({
        'tags': ['institution'],
        'description': 'Deletes an institution',
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
                'description': 'Successfully deleted an institution',
            }
        }
    })
    def delete(self, id):
        """Delete institution"""
        institution = db.session.query(Institution).filter(
            Institution.id == id).first()
        db.session.delete(institution)
        db.session.commit()

        return jsonify({'msg': 'Successfully removed institution'})
