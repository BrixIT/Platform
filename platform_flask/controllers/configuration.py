import os

from flask import session, redirect, url_for, render_template, request

from platform_flask import app
from platform_flask.models import db, Configuration
from platform_flask.components.configuration import PlatformConfig


@app.route('/configuration')
def configuration():
    all_config = Configuration.query
    config = {
        'http_repo_auth': PlatformConfig.get('http_repo_auth', {})
    }
    return render_template('configuration.html', all_config=all_config, config=config)


@app.route('/configuration/http_repo_auth/add', methods=["POST"])
def http_repo_auth_add():
    host = request.form['host']
    user = request.form['username']
    passwd = request.form['password']

    rows = PlatformConfig.get('http_repo_auth', {})
    rows[host] = {
        'username': user,
        'password': passwd
    }
    PlatformConfig.set('http_repo_auth', rows)
    return redirect(url_for('configuration'), code=303)
