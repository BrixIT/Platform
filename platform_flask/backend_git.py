from platform_flask import app
from flask import Flask, session, redirect, url_for, request, flash, render_template
from platform_flask.models import db, User, Configuration, Repository
from time import sleep
import os
from subprocess import call
from platform_flask import celery


@app.route('/backend/git')
def backend_git():
    repo = Repository(type="git", label="sabnzbd", url="https://github.com/sabnzbd/sabnzbd")
    db.session.add(repo)
    db.session.commit()
    git_clone_task.delay("sabnzbd", "https://github.com/sabnzbd/sabnzbd")
    return redirect(url_for('index'))


@app.route('/instance/test')
def instance_test():
    git_clone_instance_task.delay("sabnzbd", "sabnzbd")
    return redirect(url_for('index'))


@app.route('/callback/repository-cloned', methods=['POST'])
def callback_repository_cloned():
    label = request.form['label']
    repo = Repository.query.filter_by(label=label).first()
    repo.cloned = True
    db.session.add(repo)
    db.session.commit()


@celery.task
def git_clone_task(label, repository):
    repo_path = "/opt/platform/repository/{}".format(label)
    if os.path.isdir(repo_path):
        os.rmdir(repo_path)
    call(["git", "clone", repository, repo_path])
    return "cloned!"


@celery.task
def git_clone_instance_task(label, source):
    source_path = "/opt/platform/repository/{}".format(source)
    target_path = "/opt/platform/apps/{}".format(label)
    if not os.path.isdir("/opt/platform/apps"):
        os.mkdir("/opt/platform/apps")
    if os.path.isdir(target_path):
        return False
    if not os.path.isdir(source_path):
        return False
    call(["git", "clone", source_path, target_path])
