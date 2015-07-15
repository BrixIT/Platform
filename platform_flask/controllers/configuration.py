import os

from flask import session, redirect, url_for, render_template, request

from platform_flask import app
from platform_flask.models import db, Configuration
from platform_flask.components.configuration import PlatformConfig
from platform_flask.components.mailrelay import MailRelay


@app.route('/configuration')
def configuration():
    all_config = Configuration.query
    config = {
        'http_repo_auth': PlatformConfig.get('http_repo_auth', {}),
        'smtp': PlatformConfig.get('smtp', {
            'host': '',
            'port': 25,
            'ssl': False,
            'auth': False,
            'username': '',
            'password': ''
        })
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


@app.route('/configuration/smtp/save', methods=["POST"])
def smtp_save():
    config = PlatformConfig.get('smtp', {
        'host': '',
        'port': 25,
        'ssl': False,
        'auth': False,
        'username': '',
        'password': ''
    })

    config['host'] = request.form['host']
    config['port'] = int(request.form['port'])
    config['ssl'] = 'tls' in request.form
    config['auth'] = 'auth' in request.form
    config['username'] = request.form['username']
    config['password'] = request.form['password']

    PlatformConfig.set('smtp', config)
    MailRelay().build_config()
    return redirect(url_for('configuration'), code=303)
