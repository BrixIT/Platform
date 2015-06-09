from platform_flask import app
from flask import Flask, session, redirect, url_for, request
from flask.ext.mako import MakoTemplates, render_template
from platform_flask.models import db, User
import os

mako = MakoTemplates()


@app.route('/')
def index():
    if not os.path.isfile('/opt/platform/platform.db') or os.path.getsize('/opt/platform/platform.db') == 0:
        db.create_all()

    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email'].lower()).first()
        if user and user.check_password(request.form['password']):
            session['user'] = request.form['email']
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))
