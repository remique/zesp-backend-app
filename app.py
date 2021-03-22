from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from flask_restful import Api

from database.db import db, init_db
from scheduler import scheduler
from resources.routes import initialize_routes
from flask_jwt_extended import JWTManager

from flask_restful_swagger_2 import Api, swagger

security_definitions = {
    'api_key': {
        'type': 'apiKey',
        'name': 'Authorization',
        'in': 'header',
        'description': 'Example value **Bearer 12345**'
    }
}

description = """
Url: `localhost: 5000/api`. To jest tylko testowe API dla naszej aplikacji(v0.1). \
Domyślnie przechodząc do API wszystkie endpointy i modele są zwinięte. Jeśli chcemy, aby \
domyślnie były rozwinięte to usuwamy `docExpansion=none&`. \
\n\n **Ważne!** Autoryzujemy na endpoincie `/login` a następnie wklejamy nasz token \
do okienka **Authorize**. Po wpisaniu dobrego tokenu możemy w całości korzystać z API. 
"""


def create_app(cfg):
    app = Flask(__name__)
    CORS(app, resources={r"*": {"origins": "*"}})
    app.config.from_object(cfg)
    jwt = JWTManager(app)

    api = Api(app, api_version='0.1',
              api_spec_url='/api/swagger',
              title='API aplikacji dla przedszkoli',
              description=description,
              security_definitions=security_definitions)

    @app.route('/api')
    def index():
        return """<head>
		<meta http-equiv="refresh" content="0; url=http://petstore.swagger.io/?docExpansion=none&url=http://localhost:5000/api/swagger.json" />
		</head>"""

    init_db(app)
    initialize_routes(api)
    scheduler.init_app(app)
    scheduler.start()
    return app
