from platform_flask import app
from flask import Flask, session, redirect, url_for, request, flash, render_template, jsonify
from platform_flask.models import db, User, Configuration
import os
from platform_flask.systemd import Systemd, SystemdUnit
from celery.task.control import inspect


@app.route('/')
def index():
    db.create_all()
    if not os.path.isfile('/opt/platform/platform.db') or os.path.getsize('/opt/platform/platform.db') == 0:
        return redirect(url_for('setup'))

    if 'user' not in session:
        return redirect(url_for('login'))

    units = Systemd().list_all()
    return render_template('index.html', units=units)

@app.route('/ajax/get-queue')
def ajax_get_queue():
    labels = {
        'platform_flask.backend_git.git_clone_task': 'Cloning git repository'
    }
    celery_inspector = inspect()
    active = celery_inspector.active()
    if active is None:
        return jsonify(error="No celery workers active")
    response = []
    for host in active:
        for message in active[host]:
            message_id = message['id']
            name = message['name']
            label = labels[name]
            args = message['args']
            response.append({
                'id': message_id,
                'name': name,
                'args': args,
                'label': label,
                'host': host
            })
    return jsonify(response=response)


@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if not os.path.isfile('/opt/platform/platform.db') or os.path.getsize('/opt/platform/platform.db') == 0:
        if request.method == 'POST':
            db.create_all()
            user = User(request.form['firstname'], request.form['lastname'], request.form['email'],
                        request.form['password'])
            db.session.add(user)
            db.session.commit()
            flash('Set-up complete! please login with your new account.', 'success')
            return redirect(url_for('index'))
        else:
            return render_template('setup.html')
    else:
        flash('This Platform installation is already set-up! Remove the database to run setup again.', 'danger')
        return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email'].lower()).first()
        if user and user.check_password(request.form['password']):
            session['user'] = request.form['email']
            session['username'] = "{} {}".format(user.firstname, user.lastname)
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))
