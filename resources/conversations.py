from database.db import pusher_client
from flask import Response, request, jsonify, make_response, json
from database.models import Conversation, User, ConversationReply
from .schemas import (
    ConversationSchema, ConversationReplySchema, ConversationLastSchema,
    UserLookupSchema
)
from database.db import db
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, get_jwt
)
from flask_restful_swagger_2 import Api, swagger, Resource, Schema
from .swagger_models import Conversation as ConversationSwaggerModel
from .swagger_models import ConversationReply as ConversationReplySwaggerModel
from .swagger_models import UserLookup as UserLookupSwaggerModel
from sqlalchemy import and_, or_

import math

conversation_schema = ConversationSchema()
conversations_schema = ConversationSchema(many=True)
conversations_last_schema = ConversationLastSchema(many=True)

conversation_reply_schema = ConversationReplySchema()
conversations_replies_schema = ConversationReplySchema(many=True)

users_schema = UserLookupSchema(many=True)


class ConversationsApi(Resource):
    @swagger.doc({
        'tags': ['conversation'],
        'description': 'Returns ALL the conversations for logged user',
        'responses': {
            '200': {
                'description': 'Successfully got all the conversations for logged user',
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
                'description': '*Optional*: How many conversations to return per page'
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
        """Return ALL the conversations for logged user"""

        # TODO: Use get_jwt() instead (needed for unittesting)
        claims_jwt = get_jwt()
        jwt_email = claims_jwt['email']

        current_user = User.query.filter_by(email=jwt_email).first()

        total_conversations = Conversation.query.filter(
            or_(Conversation.user_one == current_user.id,
                Conversation.user_two == current_user.id)).count()

        MIN_PER_PAGE = 5
        MAX_PER_PAGE = 30

        # Get query parameters
        page = request.args.get('page')
        per_page = request.args.get('per_page')

        # If page is not provided, set to first page by default
        if page is None or int(page) < 1:
            page = 1

        # Default pagination
        if per_page is None:
            per_page = 15

        if int(per_page) < MIN_PER_PAGE:
            per_page = MIN_PER_PAGE

        if int(per_page) > MAX_PER_PAGE:
            per_page = MAX_PER_PAGE

        last_page = math.ceil(int(total_conversations) / int(per_page))

        if int(page) >= last_page:
            page = int(last_page)

        page_offset = (int(page) - 1) * int(per_page)

        conversations_query = Conversation.query.filter(
            or_(Conversation.user_one == current_user.id,
                Conversation.user_two == current_user.id)).order_by(Conversation.updated_at.desc()).offset(page_offset).limit(per_page).all()

        # Copying query to separate list, so we won't delete actual records
        conversations_copy = []
        for convo in conversations_query:
            conversations_copy.append(convo)

            if convo.user_two == current_user.id:
                convo.user_two = convo.user_one

        # For each conversation we clear all the replies and leave out
        # only the last one
        for convo in conversations_copy:
            last_reply = ConversationReply.query.filter_by(
                conv_id=convo.id).order_by(ConversationReply.reply_time.desc()).first()
            convo.conversation_replies.clear()

            # Don't insert None into the list
            if last_reply is not None:
                convo.conversation_replies.append(last_reply)

        conversations_query_result = conversations_last_schema.dump(
            conversations_copy)

        result = {
            "total": total_conversations,
            "per_page": int(per_page),
            "current_page": int(page),
            "last_page": last_page,
            "data": conversations_query_result
        }

        return jsonify(result)

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
        claims_jwt = get_jwt()
        jwt_email = claims_jwt['email']
        current_user = User.query.filter_by(email=jwt_email).first()

        user_one = current_user.id
        user_two = request.json['user_two']
        created_at = db.func.current_timestamp()
        updated_at = db.func.current_timestamp()

        does_exist = Conversation.query.filter(
            or_(
                and_(Conversation.user_one == user_one,
                     Conversation.user_two == user_two),
                and_(Conversation.user_one == user_two,
                     Conversation.user_two == user_one))).first()
        if does_exist is not None:
            return jsonify({'msg': 'Conversation already exists'})

        user_two_exists = User.query.filter_by(id=user_two).first()

        if not user_two_exists:
            return jsonify({'msg': 'User with given id does not exist'})

        if user_one == user_two:
            return jsonify({'msg': 'Could not make conversation with the same user'})

        new_conversation = Conversation(
            user_one, user_two, created_at, updated_at)

        db.session.add(new_conversation)
        db.session.commit()

        return conversation_schema.jsonify(new_conversation)


class ConversationReplyApi(Resource):
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
        claims_jwt = get_jwt()
        jwt_email = claims_jwt['email']
        jwt_id = claims_jwt['id']
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

        # Update conversation
        conv_exists.updated_at = db.func.current_timestamp()

        db.session.add(new_conv_reply)
        db.session.commit()

        push_message = conversation_reply_schema.dump(new_conv_reply)

        if conv_exists.user_two == jwt_id:
            user_two_channel = conv_exists.user_one
        else:
            user_two_channel = conv_exists.user_two

        usr_two_unic = str(user_two_channel)

        pusher_client.trigger(usr_two_unic, u'my-event',
                              push_message)

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
                'description': '*Optional*: How many replies to return per page'
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

        total_replies = ConversationReply.query.filter(
            ConversationReply.conv_id == conv_id).count()

        MIN_PER_PAGE = 5
        MAX_PER_PAGE = 30

        # Get query parameters
        page = request.args.get('page')
        per_page = request.args.get('per_page')

        # If page is not provided, set to first page by default
        if page is None or int(page) < 1:
            page = 1

        # Default pagination
        if per_page is None:
            per_page = 15

        if int(per_page) < MIN_PER_PAGE:
            per_page = MIN_PER_PAGE

        if int(per_page) > MAX_PER_PAGE:
            per_page = MAX_PER_PAGE

        last_page = math.ceil(int(total_replies) / int(per_page))

        if int(page) >= last_page:
            page = int(last_page)

        page_offset = (int(page) - 1) * int(per_page)

        conversation = Conversation.query.filter_by(id=conv_id).first()
        if conversation is None:
            return jsonify({'msg': 'Conversation does not exist'})

        replies_query = ConversationReply.query.filter_by(
            conv_id=conv_id).order_by(ConversationReply.reply_time.desc()).offset(page_offset).limit(per_page).all()

        replies_query_result = conversations_replies_schema.dump(replies_query)

        result = {
            "total": total_replies,
            "per_page": int(per_page),
            "current_page": int(page),
            "last_page": last_page,
            "data": replies_query_result
        }

        return jsonify(result)


class UserSearchApi(Resource):
    @swagger.doc({
        'tags': ['conversation'],
        'description': 'Looks for users matching',
        'parameters': [
            {
                'name': 'Body',
                'in': 'body',
                'schema': UserLookupSwaggerModel,
                'type': 'object',
                'required': 'true'
            },
        ],
        'responses': {
            '200': {
                'description': 'Found matching user',
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
        """Search user by his firstname and surname"""

        # Get currently logged user's InstitutionId
        claims = get_jwt()
        current_user_inst_id = claims['institution_id']

        name_like = request.json['name_like']
        user_list = []

        search_result = db.session.query(User).filter(User.institution_id == current_user_inst_id).filter(
            (User.firstname + ' ' + User.surname).like('{0}%'.format(name_like))).limit(10).all()

        for u in search_result:
            # We query user by u.id
            user_query = User.query.filter(
                User.id == u.id).filter(User.institution_id == current_user_inst_id).first()

            # Append it to the list of users
            user_list.append(user_query)

        result = users_schema.dump(user_list)

        # If we did not query any users, then there are no matching names
        if not user_list:
            return jsonify({"msg": "No matching names"})

        return jsonify(result)
