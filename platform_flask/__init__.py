from flask import Flask
import pymysql

from platform_flask.components.messagequeue import make_celery

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////opt/platform/platform.db'
app.config['CELERY_BROKER_URL'] = 'amqp://guest:guest@localhost:5672//'
app.config['CELERY_RESULT_BACKEND'] = 'db+mysql://root:platform@localhost/platform'
celery = make_celery(app)


from platform_flask.models import db

db.init_app(app)
app.secret_key = 'development key'

from platform_flask.components.jinjafilters import gravatar

app.jinja_env.filters['gravatar'] = gravatar

import platform_flask.routes
import platform_flask.controllers.overview
import platform_flask.controllers.repositories
import platform_flask.controllers.instances
import platform_flask.controllers.configuration
import platform_flask.controllers.packages