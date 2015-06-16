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
    git_clone_task.delay("sabnzbd", "https://github.com/sabnzbd/sabnzbd")
    return redirect(url_for('index'))


@celery.task
def git_clone_task(label, repository):
    repo_path = "/opt/platform/repository/{}".format(label)
    if os.path.isdir(repo_path):
        os.rmdir(repo_path)
    call(["git", "clone", repository, repo_path])
    return "cloned!"
