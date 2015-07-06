import os

from flask import session, redirect, url_for, request, flash, render_template, jsonify

from platform_flask import app
from platform_flask import celery as celery_instance
from platform_flask.models import db, User
from celery.task.control import inspect


@app.route('/ajax/get-queue')
def ajax_get_queue():
    labels = {
        'platform_flask.backend_git.git_clone_task': 'Cloning git repository',
        'platform_flask.instances.create_platform_python27': 'Creating new Python 2.7 platform'
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


@app.route('/task-status/<task_id>')
def get_task_status(task_id):
    res = celery_instance.AsyncResult(task_id)
    state = res.state
    if state == "SUCCESS":
        return "<i class='glyphicon glyphicon-ok'></i> OK"
    if state == "FAILURE":
        return "<i class='glyphicon glyphicon-remove'></i> FAILURE"
    if state == "PENDING":
        return "<i class='glyphicon glyphicon-refresh spin'></i> PENDING"
    return state
