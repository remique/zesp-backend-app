from flask import Response, request, jsonify, make_response, json, redirect, url_for, flash
from database.models import Image
from .schemas import ImageSchema
from database.db import db
from flask_restful_swagger_2 import Api, swagger, Resource, Schema
from .swagger_models import Image as ImageSwaggerModel
from werkzeug.utils import secure_filename
import os
import uuid

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
        }
    })
    def get(self):
        """Return ALL the images"""
        all_images = Image.query.all()
        result = images_schema.dump(all_images)
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
        }
    })
    def post(self):
        """Add a new image"""
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

        new_image = Image(url, created_at, updated_at)

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
        }
    })
    def get(self, id):
        """Get image by ID"""
        single_image = Image.query.get(id)

        if not single_image:
            return jsonify({'msg': 'No image found'})

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
        }
    })
    def delete(self, id):
        """Delete image"""
        image = db.session.query(Image).filter(Image.id == id).first()

        if not image:
            return jsonify({'msg': 'No image found'})

        path = image.url

        try:
            os.remove('.'+path)
        except OSError:
            pass

        db.session.delete(image)
        db.session.commit()

        return jsonify({'msg': 'Successfully removed image'})
