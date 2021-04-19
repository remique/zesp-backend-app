from flask import Response, request, jsonify, make_response, json
from database.models import Conversation, User, ConversationReply
from .schemas import ConversationSchema, ConversationReplySchema
from database.db import db
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from flask_restful_swagger_2 import Api, swagger, Resource, Schema
from .swagger_models import Conversation as ConversationSwaggerModel
from .swagger_models import ConversationReply as ConversationReplySwaggerModel
from sqlalchemy import and_, or_

conversation_schema = ConversationSchema()
conversations_schema = ConversationSchema(many=True)

conversation_reply_schema = ConversationReplySchema()
conversations_replies_schema = ConversationReplySchema(many=True)


class ConversationsApi(Resource):
    @swagger.doc({
        'tags': ['conversation'],
        'description': 'Returns ALL the conversations for logged user',
        'responses': {
            '200': {
                'description': 'Successfully got all the conversations for logged user',
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
        """Return ALL the conversations for logged user"""
        jwt_email = get_jwt_identity()
        current_user = User.query.filter_by(email=jwt_email).first()
        conversations = Conversation.query.filter(
            or_(Conversation.user_one == current_user.id, Conversation.user_two == current_user.id))

        replies = []

        for convo in conversations:
            last_reply = ConversationReply.query.filter_by(
                conv_id=convo.id).order_by(ConversationReply.reply_time.desc()).first()

            if last_reply is not None:
                replies.append(last_reply)

        return conversations_replies_schema.jsonify(replies)

    @swagger.doc({
        'tags': ['conversation'],
        'description': 'Adds a new conversation for current user',
        'parameters': [
            {
                'name': 'Body',
                'in': 'body',
                'schema': ConversationSwaggerModel,
                'type': 'object',
                'required': 'true'
            },
        ],
        'responses': {
            '200': {
                'description': 'Successfully added new conversation for current user',
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
        """Add a new conversation for current user"""
        jwt_email = get_jwt_identity()
        current_user = User.query.filter_by(email=jwt_email).first()

        user_one = current_user.id
        user_two = request.json['user_two']

        does_exist = Conversation.query.filter(
            or_(
                and_(Conversation.user_one == user_one,
                     Conversation.user_two == user_two),
                and_(Conversation.user_one == user_two,
                     Conversation.user_two == user_one))).first()
        if does_exist is not None:
            return jsonify({'msg': 'Conversation already exists'})

        new_conversation = Conversation(user_one, user_two)

        db.session.add(new_conversation)
        db.session.commit()

        return conversation_schema.jsonify(new_conversation)


class ConversationReplyApi(Resource):
    @swagger.doc({
        'tags': ['conversation_reply'],
        'description': 'Returns ALL the conversations replies',
        'responses': {
            '200': {
                'description': 'Successfully got all the conversations replies',
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
        """Return ALL the conversations replies"""
        all_replies = ConversationReply.query.all()
        result = conversations_replies_schema.dump(all_replies)
        return jsonify(result)

    @swagger.doc({
        'tags': ['conversation_reply'],
        'description': 'Adds a new reply to the conversation',
        'parameters': [
            {
                'name': 'Body',
                'in': 'body',
                'schema': ConversationReplySwaggerModel,
                'type': 'object',
                'required': 'true'
            },
        ],
        'responses': {
            '200': {
                'description': 'Successfully added new conversation',
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
        """Add a new conversation reply"""
        jwt_email = get_jwt_identity()
        current_user = User.query.filter_by(email=jwt_email).first()

        reply = request.json['reply']
        reply_user_id = current_user.id
        conv_id = request.json['conv_id']

        # Check if conversation exists
        conv_exists = Conversation.query.filter_by(id=conv_id).first()
        if conv_exists is None:
            return jsonify({'msg': 'Conversation does not exist'})

        # Check if given user exist in conversation
        if not (conv_exists.user_one == reply_user_id or conv_exists.user_two == reply_user_id):
            return jsonify({'msg': 'No such user in given conversation'})

        reply_time = db.func.current_timestamp()

        new_conv_reply = ConversationReply(
            reply, reply_time, reply_user_id, conv_id)

        db.session.add(new_conv_reply)
        db.session.commit()

        return conversation_reply_schema.jsonify(new_conv_reply)


class ConversationRepliesApi(Resource):
    @swagger.doc({
        'tags': ['conversation_reply'],
        'description': 'Returns all the messages in conversation',
        'parameters': [
            {
                'name': 'conv_id',
                'in': 'path',
                'type': 'integer',
                'required': 'true'
            },
        ],
        'responses': {
            '200': {
                'description': 'Successfully got all the replies in conversation',
            }
        },
        'security': [
            {
                'api_key': []
            }
        ]
    })
    @jwt_required()
    def get(self, conv_id):
        """Return ALL the replies in given conversation"""
        conversation = Conversation.query.filter_by(id=conv_id).first()
        if conversation is None:
            return jsonify({'msg': 'Conversation does not exist'})

        replies = ConversationReply.query.filter_by(
            conv_id=conv_id).order_by(ConversationReply.reply_time.desc()).all()

        return conversations_replies_schema.jsonify(replies)
