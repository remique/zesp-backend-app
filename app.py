from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_restful import Api

from database.db import db, init_db
from resources.routes import initialize_routes
from flask_jwt_extended import JWTManager

from flask_restful_swagger_2 import Api

import config

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})
app.config.from_object('config.DevelopmentConfig')

jwt = JWTManager(app)
api = Api(app, api_version='0.1',
          api_spec_url='/api/swagger',
          title='API aplikacji dla przedszkoli',
          description='Url: `localhost: 5000/api`. To jest tylko testowe API dla naszej aplikacji(v0.1). Póki co, w samej dokumentacji nie obsługujemy jeszcze autoryzacji - dodamy niedługo. ')

# Redirect to API documentation


@app.route('/api')
def index():
    return """<head>
    <meta http-equiv="refresh" content="0; url=http://petstore.swagger.io/?url=http://localhost:5000/api/swagger.json" />
    </head>"""


init_db(app)
initialize_routes(api)
