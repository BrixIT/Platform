import os

from platform_flask import app
from platform_flask.models import db, User
from flask import session, redirect, url_for, request, flash, render_template, jsonify
from platform_flask.components.systemd import Systemd


@app.route('/')
def index():
    db.create_all()
    if not os.path.isfile('/opt/platform/platform.db') or os.path.getsize('/opt/platform/platform.db') == 0:
        return redirect(url_for('setup'))

    if 'user' not in session:
        return redirect(url_for('login'))

    units = Systemd().list_all()
    platform_units = Systemd().list()
    return render_template('index.html', units=units, platform_units=platform_units)
