from flask import Response, request, jsonify, make_response, json, redirect, url_for, flash
from database.models import Image
from .schemas import ImageSchema
from database.db import db
from flask_restful_swagger_2 import Api, swagger, Resource, Schema
from .swagger_models import Image as ImageSwaggerModel
from werkzeug.utils import secure_filename
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, current_user, create_refresh_token, get_jwt
)
import os
import uuid
import math

image_schema = ImageSchema()
images_schema = ImageSchema(many=True)

UPLOAD_FOLDER = './static/uploaded_images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class ImagesApi(Resource):
    @swagger.doc({
        'tags': ['image'],
        'description': 'Returns ALL the images',
        'responses': {
            '200': {
                'description': 'Successfully got all the images',
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
                'description': '*Optional*: How many users to return per page'
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
        """Return ALL the images"""
        claims = get_jwt()
        user_institution_id = claims['institution_id']

        images_total = Image.query.filter(
            Image.institution_id == user_institution_id).count()

        MIN_PER_PAGE = 5
        MAX_PER_PAGE = 30

        page = request.args.get('page')
        per_page = request.args.get('per_page')

        if page is None or int(page) < 1:
            page = 1

        if per_page is None:
            per_page = 15

        if int(per_page) < MIN_PER_PAGE:
            per_page = MIN_PER_PAGE

        if int(per_page) > MAX_PER_PAGE:
            per_page = MAX_PER_PAGE

        last_page = math.ceil(int(images_total) / int(per_page))

        if int(page) >= last_page:
            page = int(last_page)

        page_offset = (int(page) - 1) * int(per_page)

        images_query = Image.query.filter(Image.institution_id == user_institution_id).order_by(
            Image.id.desc()).offset(page_offset).limit(per_page).all()
        query_result = images_schema.dump(images_query)

        result = {
            "total": images_total,
            "per_page": int(per_page),
            "current_page": int(page),
            "last_page": last_page,
            "data": query_result
        }

        return jsonify(result)

    @swagger.doc({
        'tags': ['image'],
        'description': 'Adds a new image',
        'parameters': [
            {
                'name': 'file',
                'in': 'formData',
                'type': 'file',
                'required': 'true'
            },
        ],
        'responses': {
            '200': {
                'description': 'Successfully added new image',
            },
            '403': {
                'description': 'File size limit exceeded',
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
        """Add a new image"""
        claims = get_jwt()
        user_institution_id = claims['institution_id']

        url = ''
        if 'file' not in request.files:
            return jsonify({'msg': 'No file part'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'msg': 'No selected file'})
        if file and allowed_file(file.filename):
            filename = str(uuid.uuid4()) + '.' + file.filename.split(".")[-1]

            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)

            file.save(os.path.join(UPLOAD_FOLDER, filename))
            url = url_for('static', filename="uploaded_images/"+filename)

        created_at = db.func.current_timestamp()
        updated_at = db.func.current_timestamp()
        institution_id = user_institution_id

        new_image = Image(url, created_at, updated_at, institution_id)

        db.session.add(new_image)
        db.session.commit()

        return image_schema.jsonify(new_image)


class ImageApi(Resource):
    @swagger.doc({
        'tags': ['image'],
        'description': 'Get specific image',
        'parameters': [
            {
                'name': 'id',
                'description': 'Image identifier',
                'in': 'path',
                'type': 'integer',
            }
        ],
        'responses': {
            '200': {
                'description': 'Successfully got image'
            }
        },
        'security': [
            {
                'api_key': []
            }
        ]
    })
    @jwt_required()
    def get(self, id):
        """Get image by ID"""
        claims = get_jwt()
        user_institution_id = claims['institution_id']

        single_image = Image.query.get(id)

        if single_image is None:
            return jsonify({'msg': 'Bad id provided'})

        if single_image.institution_id != user_institution_id:
            return jsonify({'msg': 'This image does not belong to current institution'})

        return image_schema.jsonify(single_image)

    @swagger.doc({
        'tags': ['image'],
        'description': 'Deletes image',
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
                'description': 'Successfully deleted image',
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
        """Delete image"""
        claims = get_jwt()
        user_institution_id = claims['institution_id']

        image = db.session.query(Image).filter(Image.id == id).first()

        if not image:
            return jsonify({'msg': 'No image found'})

        if image.institution_id != user_institution_id:
            return jsonify({'msg': 'Provided image does not belong to current institution and therefore cannot be deleted'})

        path = image.url

        try:
            os.remove('.'+path)
        except OSError:
            pass

        db.session.delete(image)
        db.session.commit()

        return jsonify({'msg': 'Successfully removed image'})
