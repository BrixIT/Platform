from flask import Flask

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////opt/platform/platform.db'

from platform_flask.models import db

db.init_app(app)

app.secret_key = 'development key'

from platform_flask.jinjafilters import gravatar

app.jinja_env.filters['gravatar'] = gravatar

import platform_flask.routes
