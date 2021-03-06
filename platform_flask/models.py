from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    pwdhash = db.Column(db.String(54))

    def __init__(self, firstname, lastname, email, password):
        self.firstname = firstname.title()
        self.lastname = lastname.title()
        self.email = email.lower()
        self.set_password(password)

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

    def __str__(self):
        return "{} {} <{}>".format(self.firstname, self.lastname, self.email)

    def __repr__(self):
        return "<User {}>".format(self.email)


class Configuration(db.Model):
    __tablename__ = 'configuration'
    id = db.Column(db.String(255), primary_key=True)
    value = db.Column(db.Text())

    def __init__(self, id, value):
        self.id = id
        self.value = value

    def __repr__(self):
        return "<Config {} = {}>".format(self.id, self.value)

    def __str__(self):
        return self.value


class Repository(db.Model):
    __tablename__ = 'repository'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20))
    label = db.Column(db.String(255))
    url = db.Column(db.String(255))
    extra = db.Column(db.Text())
    cloned = db.Column(db.Boolean)
    task = db.Column(db.String(36))
    instances = db.relationship("AppInstance")

    def __init__(self, type, label, url, extra=None, cloned=False, task=""):
        self.type = type
        self.label = label
        self.url = url
        if extra is None:
            extra = {}
        self.extra = json.dumps(extra)
        self.cloned = cloned
        self.task = task

    def get_extra(self):
        return json.loads(self.extra)

    def get_repo_path(self):
        return "/opt/platform/repository/{}".format(self.label)

    def __repr__(self):
        return "<Repository {} ({})>".format(self.id, self.label)


class AppInstance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(40))
    repository_id = db.Column(db.Integer, db.ForeignKey('repository.id'))
    clone_source = db.Column(db.String(5))
    tag = db.Column(db.String(100))
    branch = db.Column(db.String(120))
    platform = db.Column(db.String(50))
    entrypoint = db.Column(db.String(255))
    arguments = db.Column(db.Text)
    port = db.Column(db.Integer)
    proxy = db.Column(db.Boolean)
    mountpoint = db.Column(db.String(255))
    status = db.Column(db.String(255))
    task = db.Column(db.String(36))

    def __init__(self, label, repository_id):
        self.label = label
        self.repository_id = repository_id

    def __repr__(self):
        return "<AppInstance {} ({})>".format(self.id, self.label)
