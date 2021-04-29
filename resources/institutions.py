from flask import Response, request, jsonify, make_response, json
from database.models import Institution, User, Role, user_roles
from .schemas import InstitutionSchema
from database.db import db
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from flask_restful_swagger_2 import Api, swagger, Resource, Schema
from .swagger_models import Institution as InstitutionSwaggerModel
from .security import generate_salt, generate_hash

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

        does_exist = Institution.query.filter_by(name=name).first()
        if does_exist is not None:
            return jsonify({'msg': 'Institution with given name already exists'})

        new_institution = Institution(name, city, address, contact_number)
        db.session.add(new_institution)

        # Create admin user for new institution
        admin_email = request.json['admin_email']
        admin_password = request.json['admin_password']
        admin_firstname = request.json['admin_firstname']
        admin_surname = request.json['admin_surname']
        admin_sex = request.json['admin_sex']
        active = 1
        admin_institution_id = new_institution.id
        created_at = db.func.current_timestamp()
        updated_at = db.func.current_timestamp()

        salt_str = generate_salt(16)
        key = generate_hash(admin_password, salt_str)

        new_user = User(admin_email, key, salt_str, admin_firstname, admin_surname, admin_institution_id, admin_sex, active,
                        created_at, updated_at)

        # Check if user with given email already exists
        does_exist = User.query.filter_by(email=admin_email).first()
        if does_exist is not None:
            db.session.delete(new_institution)
            return jsonify({'msg': 'User with given email address already exists and institution will not be created'})

        db.session.add(new_user)

        # If "Admin" role does not exist then create one
        # Assign him a role "Admin"
        role_title = "Admin"
        does_admin_role_exist = Role.query.filter(
            Role.title == role_title).first()
        if does_admin_role_exist is None:
            role_title = role_title
            new_role = Role(role_title, created_at, updated_at)
            db.session.add(new_role)
            new_user.roles.append(new_role)
        else:
            new_user.roles.append(does_admin_role_exist)

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
