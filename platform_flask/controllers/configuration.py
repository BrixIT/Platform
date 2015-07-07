import os

from flask import session, redirect, url_for, render_template

from platform_flask import app
from platform_flask.models import db, Configuration


@app.route('/configuration')
def configuration():
    all_config = Configuration.query
    return render_template('configuration.html', all_config=all_config)