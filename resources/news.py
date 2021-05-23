from flask import Response, request, jsonify, make_response, json
from database.models import News, Institution, Image, User
from .schemas import NewsSchema
from database.db import db
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, get_jwt
)
from flask_restful_swagger_2 import Api, swagger, Resource, Schema
from .swagger_models import News as NewsSwaggerModel
from datetime import datetime
import math

news_schema = NewsSchema()
newsM_schema = NewsSchema(many=True)


class NewsMApi(Resource):
    @swagger.doc({
        'tags': ['news'],
        'description': '''Endpoint returning all the news in an institution\
                that currently logged in user belongs to. By default it is \
                being sorted by descending date. You can optionally set \
                priority flag which will sort news by priority first, then \
                date. So all news with priority flag **true** will be on the \
                top. \n News are paginated (per_page=15 by default). You \
                need to show at least 5 news per page and up to 30 per page.''',
        'responses': {
            '200': {
                'description': 'Successfully got all the news',
            },
            '401': {
                'description': 'Unauthorized request',
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
            {
                'name': 'priority',
                'in': 'query',
                'type': 'boolean',
                'description': '*Optional*: Sort by priority'
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
        """Return ALL the news"""
        claims = get_jwt()
        user_institution_id = claims['institution_id']

        priority = request.args.get('priority')

        news_total = News.query.filter(
            News.institution_id == user_institution_id).count()

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

        last_page = math.ceil(int(news_total) / int(per_page))

        if int(page) >= last_page:
            page = int(last_page)

        page_offset = (int(page) - 1) * int(per_page)

        news_query = News.query\
            .filter(News.institution_id == user_institution_id)\
            .order_by(News.created_at.desc())\
            .offset(page_offset).limit(per_page).all()

        if priority == 'true':
            news_query = News.query\
                .filter(News.institution_id == user_institution_id)\
                .order_by(News.priority.desc(), News.created_at.desc())\
                .offset(page_offset).limit(per_page).all()

        query_result = newsM_schema.dump(news_query)

        result = {
            "total": news_total,
            "per_page": int(per_page),
            "current_page": int(page),
            "last_page": last_page,
            "data": query_result
        }

        return jsonify(result)

    @swagger.doc({
        'tags': ['news'],
        'description': 'Adds a new news',
        'parameters': [
            {
                'name': 'Body',
                'in': 'body',
                'schema': NewsSwaggerModel,
                'type': 'object',
                'required': 'true'
            },
        ],
        'responses': {
            '200': {
                'description': 'Successfully added new news',
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
    def post(self):
        """Add a new news"""
        claims = get_jwt()
        user_institution_id = claims['institution_id']
        user_roles = claims['roles']
        user_id = claims['id']

        title = request.json['title']
        details = request.json['details']
        priority = request.json['priority']
        institution_id = user_institution_id
        author_id = user_id

        for r in user_roles:
            if(r['title'] != "Teacher" and r['title'] != "Admin"):
                return jsonify({'msg': 'Insufficient permissions'})

        created_at = db.func.current_timestamp()
        updated_at = db.func.current_timestamp()

        institution = Institution.query.get(institution_id)
        if not institution:
            return jsonify({'msg': 'Institution does not exist'})

        author = User.query.get(author_id)
        if not author:
            return jsonify({'msg': 'Author/User does not exist'})

        new_news = News(title, details, priority, created_at,
                        updated_at, institution_id, author_id)

        db.session.add(new_news)
        db.session.commit()

        return news_schema.jsonify(new_news)


class NewsApi(Resource):
    @swagger.doc({
        'tags': ['news'],
        'description': '''An endpoint used to change given news. \n \
                Providing an **id** in path is required. Also please \
                note that you can only change news in an institution \
                that logged user belongs to.''',
        'parameters': [
            {
                'name': 'Body',
                'in': 'body',
                'schema': NewsSwaggerModel,
                'type': 'object',
                'required': 'true'
            },
            {
                'name': 'id',
                'in': 'path',
                'description': 'News identifier',
                'type': 'integer'
            }
        ],
        'responses': {
            '200': {
                'description': 'Successfully updated a news',
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
        """Update news by its id"""
        claims = get_jwt()
        user_institution_id = claims['institution_id']
        user_roles = claims['roles']

        for r in user_roles:
            if(r['title'] != "Teacher" and r['title'] != "Admin"):
                return jsonify({'msg': 'Insufficient permissions'})

        news = News.query.get(id)

        if not news:
            return jsonify({'msg': 'No news found'})

        if news.institution_id != user_institution_id:
            return jsonify({'msg': 'News being updated does not belong to the institution of currently logged in User'})

        title = request.json['title']
        details = request.json['details']
        priority = request.json['priority']
        updated_at = db.func.current_timestamp()

        news.title = title
        news.details = details
        news.priority = priority
        news.updated_at = updated_at

        db.session.commit()
        return news_schema.jsonify(news)

    @swagger.doc({
        'tags': ['news'],
        'description': '''An endpoint providing ability to delete news by \
                their IDs (provided in **path**). Also please note that you \
                can only delete news in an institution that logged user \
                belongs to.''',
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
                'description': 'Successfully deleted news',
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
    def delete(self, id):
        """Delete news by its id"""
        claims = get_jwt()
        user_institution_id = claims['institution_id']
        user_roles = claims['roles']

        for r in user_roles:
            if(r['title'] != "Teacher" and r['title'] != "Admin"):
                return jsonify({'msg': 'Insufficient permissions'})

        news = db.session.query(News).filter(News.id == id).first()

        if not news:
            return jsonify({'msg': 'No news found'})

        if news.institution_id != user_institution_id:
            return jsonify({'msg': 'News being deleted does not belong to the institution of currently logged in User'})

        db.session.delete(news)
        db.session.commit()

        return jsonify({"msg": "Successfully deleted news"})

