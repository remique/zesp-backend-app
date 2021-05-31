from flask import Response, request, jsonify, make_response, json, redirect, url_for, flash
from database.models import Album, Institution, Image, User
from .schemas import AlbumSchema, ImageSchema
from database.db import db
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, current_user, create_refresh_token, get_jwt
)
from flask_restful_swagger_2 import Api, swagger, Resource, Schema
from .swagger_models import Album as AlbumSwaggerModel
from .swagger_models import AlbumImage as AlbumImageSwaggerModel
from .swagger_models import DeleteAlbumImage as DeleteAlbumImageSwaggerModel
from datetime import datetime
import math

album_schema = AlbumSchema()
albums_schema = AlbumSchema(many=True)

images_schema = ImageSchema(many=True)


class AlbumsApi(Resource):
    @swagger.doc({
        'tags': ['album'],
        'description': 'Returns ALL the albums',
        'responses': {
            '200': {
                'description': 'Successfully got all the albums',
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
        """Return ALL the albums"""

        MIN_PER_PAGE = 5
        MAX_PER_PAGE = 30

        claims = get_jwt()
        user_institution_id = claims['institution_id']

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

        page_offset = (int(page) - 1) * int(per_page)

        albums_total = Album.query.filter(
            Album.institution_id == user_institution_id).count()

        albums_query = Album.query\
            .filter(Album.institution_id == user_institution_id)\
            .order_by(Album.id.desc())\
            .offset(page_offset)\
            .limit(per_page).all()
        query_result = albums_schema.dump(albums_query)

        result = {
            "total": albums_total,
            "per_page": int(per_page),
            "current_page": int(page),
            "last_page": math.ceil(int(albums_total) / int(per_page)),
            "data": query_result
        }

        return jsonify(result)

    @swagger.doc({
        'tags': ['album'],
        'description': 'Adds a new album',
        'parameters': [
            {
                'name': 'Body',
                'in': 'body',
                'schema': AlbumSwaggerModel,
                'type': 'object',
                'required': 'true'
            },
        ],
        'responses': {
            '200': {
                'description': 'Successfully added new album',
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
        """Add a new album"""
        claims = get_jwt()
        user_institution_id = claims['institution_id']
        user_roles = claims['roles']

        for r in user_roles:
            if(r['title'] != "Teacher" and r['title'] != "Admin"):
                return jsonify({'msg': 'Insufficient permissions'})

        name = request.json['name']
        date_str = request.json['date']
        created_at = db.func.current_timestamp()
        updated_at = db.func.current_timestamp()
        description = request.json['description']
        institution_id = user_institution_id

        institution = Institution.query.get(institution_id)
        if not institution:
            return jsonify({'msg': 'Institution does not exist'})

        date = datetime.strptime(date_str, '%Y-%m-%d').date()

        new_album = Album(name, date, created_at, updated_at,
                          description, institution_id)

        db.session.add(new_album)
        db.session.commit()

        return album_schema.jsonify(new_album)


class AlbumApi(Resource):
    @swagger.doc({
        'tags': ['album'],
        'description': 'Get specific album',
        'parameters': [
            {
                'name': 'id',
                'description': 'Album identifier',
                'in': 'path',
                'type': 'integer',
            }
        ],
        'responses': {
            '200': {
                'description': 'Successfully got album'
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
        """Get album by ID"""
        single_album = Album.query.get(id)

        if not single_album:
            return jsonify({'msg': 'No album found'})

        return album_schema.jsonify(single_album)

    @swagger.doc({
        'tags': ['album'],
        'description': 'Updates a album',
        'parameters': [
            {
                'name': 'Body',
                'in': 'body',
                'schema': AlbumSwaggerModel,
                'type': 'object',
                'required': 'true'
            },
            {
                'name': 'id',
                'description': 'Album identifier',
                'in': 'path',
                'type': 'integer'
            },
        ],
        'responses': {
            '200': {
                'description': 'Successfully updated album',
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
        """Update album"""
        album = Album.query.get(id)
        claims = get_jwt()
        user_roles = claims['roles']

        for r in user_roles:
            if(r['title'] != "Teacher" and r['title'] != "Admin"):
                return jsonify({'msg': 'Insufficient permissions'})

        if not album:
            return jsonify({'msg': 'No album found'})

        name = request.json['name']
        date_str = request.json['date']
        updated_at = db.func.current_timestamp()
        description = request.json['description']
        institution_id = request.json['institution_id']

        institution = Institution.query.get(institution_id)
        if not institution:
            return jsonify({'msg': 'Institution does not exist'})

        date = datetime.strptime(date_str, '%Y-%m-%d').date()

        album.name = name
        album.date = date
        album.updated_at = updated_at
        album.description = description
        album.institution_id = institution_id

        db.session.commit()
        return album_schema.jsonify(album)

    @swagger.doc({
        'tags': ['album'],
        'description': 'Deletes an album',
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
                'description': 'Successfully deleted album',
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
        """Delete album"""
        claims = get_jwt()
        user_roles = claims['roles']

        for r in user_roles:
            if(r['title'] != "Teacher" and r['title'] != "Admin"):
                return jsonify({'msg': 'Insufficient permissions'})

        album = Album.query.filter(Album.id == id).first()

        if not album:
            return jsonify({'msg': 'No album found'})

        images = Image.query.filter(Image.album_id == album.id).all()

        for image in images:
            db.session.delete(image)

        db.session.delete(album)
        db.session.commit()

        return jsonify({'msg': 'Successfully removed album'})


class AlbumImagesApi(Resource):
    @swagger.doc({
        'tags': ['albumimage'],
        'description': 'Returns all images within an album',
        'parameters': [
            {
                'name': 'albumid',
                'description': 'Album identifier',
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
                'description': '*Optional*: How many users to return per page'
            },
        ],
        'responses': {
            '200': {
                'description': 'Successfully got all the album images',
            }
        },
        'security': [
            {
                'api_key': []
            }
        ]
    })
    @jwt_required()
    def get(self, albumid):
        """Get contents of an album"""
        claims = get_jwt()
        user_institution_id = claims['institution_id']

        album = Album.query.get(albumid)
        if album is None:
            return jsonify({'msg': 'Album doesnt exist'})
        images_total = Image.query.filter(Image.album_id == albumid).count()

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

        # Query the image with
        images = Image.query.filter(Image.album_id == albumid)\
            .order_by(Image.id.desc())\
            .offset(page_offset)\
            .limit(per_page).all()

        images_dump = images_schema.dump(images)

        result = {
            "total": images_total,
            "per_page": int(per_page),
            "current_page": int(page),
            "last_page": last_page,
            "data": images_dump
        }

        return jsonify(result)


class AlbumImageApi(Resource):
    @swagger.doc({
        'tags': ['albumimage'],
        'description': 'Adds image to an album',
        'parameters': [
            {
                'name': 'Body',
                'in': 'body',
                'schema': AlbumImageSwaggerModel,
                'type': 'object',
                'required': 'true'
            },
        ],
        'responses': {
            '200': {
                'description': 'Successfully added image to an album',
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
        """Add image to an album"""
        i_id = request.json['image_id']
        a_id = request.json['album_id']
        claims = get_jwt()
        user_roles = claims['roles']

        for r in user_roles:
            if(r['title'] != "Teacher" and r['title'] != "Admin"):
                return jsonify({'msg': 'Insufficient permissions'})

        image = Image.query.get(i_id)
        if image is None:
            return jsonify({'msg': 'Image doesnt exist'})

        if image.album_id is not None:
            return jsonify({'msg': 'This image is already in an album'})

        album = Album.query.get(a_id)
        if album is None:
            return jsonify({'msg': 'Album doesnt exist'})

        if(image in album.images):
            return jsonify({'msg': 'Album already contains this image'})

        album.images.append(image)

        image.album_id = a_id
        album.img_count = album.img_count + 1

        db.session.commit()

        return jsonify({'msg': 'Successfully added image to an album'})


class DeleteAlbumImageApi(Resource):
    @swagger.doc({
        'tags': ['albumimage'],
        'description': 'Removes image from album',
        'parameters': [
            {
                'name': 'Body',
                'in': 'body',
                'schema': DeleteAlbumImageSwaggerModel,
                'type': 'object',
                'required': 'true'
            },
            {
                'name': 'image_id',
                'description': 'Image identifier',
                'in': 'path',
                'type': 'integer',
            }
        ],
        'responses': {
            '200': {
                'description': 'Successfully removed image from album',
            }
        },
        'security': [
            {
                'api_key': []
            }
        ]
    })
    @jwt_required()
    def delete(self, image_id):
        """Delete image from album"""
        # i_id = request.json['image_id']
        i_id = image_id
        a_id = request.json['album_id']
        claims = get_jwt()
        user_roles = claims['roles']

        for r in user_roles:
            if(r['title'] != "Teacher" and r['title'] != "Admin"):
                return jsonify({'msg': 'Insufficient permissions'})

        image = Image.query.get(i_id)
        if image is None:
            return jsonify({'msg': 'Image doesnt exist'})

        album = Album.query.get(a_id)
        if album is None:
            return jsonify({'msg': 'Album doesnt exist'})

        if image in album.images:
            result = album.images.remove(image)

            album.img_count = album.img_count - 1
            image.album_id = None

            db.session.commit()
            return jsonify({'msg': 'Album image removed'})
        else:
            return jsonify({'msg': 'Album doesnt have selected image'})
