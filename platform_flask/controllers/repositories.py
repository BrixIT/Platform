import os
from subprocess import call, getoutput
import shutil

from flask import redirect, url_for, request, render_template
import requests
import urllib.parse

from platform_flask import app
from platform_flask.models import db, Repository
from platform_flask import celery
from platform_flask.routes import get_task_status
from platform_flask.components.configuration import PlatformConfig
import yaml


@app.route('/repositories', methods=["GET", "POST"])
def repositories():
    if request.method == "POST":
        new_label = request.form["label"]
        new_url = request.form["url"]
        new_type = request.form["type"]

        parts = urllib.parse.urlparse(new_url)
        new_hostname = parts.netloc

        httpauth = PlatformConfig.get('http_repo_auth', {})
        if new_hostname in httpauth:
            parts = list(parts)
            username = httpauth[new_hostname]['username'].replace('@', '%40')
            password = httpauth[new_hostname]['password'].replace('@', '%40')
            parts[1] = "{}:{}@{}".format(username, password, parts[1])
            new_url_auth = urllib.parse.urlunparse(parts)
            task_id = git_clone_task.delay(new_label, new_url_auth).task_id
        else:
            task_id = git_clone_task.delay(new_label, new_url).task_id

        repo = Repository(type=new_type, label=new_label, url=new_url, task=task_id)
        db.session.add(repo)
        db.session.commit()
        return redirect(url_for('repositories'))

    repos = Repository.query.order_by(Repository.cloned)
    dataset = []
    for repo in repos:
        status = "<i class='glyphicon glyphicon-ok'></i> OK"
        if len(repo.task) > 0:
            status = get_task_status(repo.task)
        dataset.append({
            "status": status,
            "repo": repo
        })
    return render_template('repositories.html', repositories=dataset)


@app.route('/repositories/<id>/instance')
def create_instance(id):
    repo = Repository.query.get(id)

    tags = getoutput("git -C '{}' tag".format(repo.get_repo_path())).split("\n")
    branches_all = getoutput("git -C '{}' branch --all".format(repo.get_repo_path())).split("\n")
    branches = []
    for b in branches_all:
        if "remotes/origin/" in b and "->" not in b:
            branches.append(b.replace("remotes/origin/", "").strip())

    platform_config = {"platform": ""}
    if os.path.isfile("{}/.platform.yml".format(repo.get_repo_path())):
        platform_config = yaml.safe_load(open("{}/.platform.yml".format(repo.get_repo_path())))
    return render_template('create_instance.html', repo=repo, tags=reversed(tags), branches=branches,
                           preload=platform_config)


@app.route('/backend/git')
def backend_git():
    task_id = git_clone_task.delay("sabnzbd", "https://github.com/sabnzbd/sabnzbd").task_id
    repo = Repository(type="git", label="sabnzbd", url="https://github.com/sabnzbd/sabnzbd", task=task_id)
    db.session.add(repo)
    db.session.commit()
    return redirect(url_for('repositories'))


@app.route('/callback/git-repository-cloned', methods=['POST'])
def callback_repository_cloned():
    label = request.form['label']
    repo = Repository.query.filter_by(label=label).first()
    repo.cloned = True
    repo.task = ""
    db.session.add(repo)
    db.session.commit()
    return ""


@app.route('/repository/remove/<id>')
def remove_repository(id):
    repo = Repository.query.get(id)
    if os.path.isdir('/opt/platform/repository/{}'.format(repo.label)):
        shutil.rmtree('/opt/platform/repository/{}'.format(repo.label))
    db.session.delete(repo)
    db.session.commit()
    return redirect(url_for('repositories'))


@celery.task
def git_clone_task(label, repository):
    repo_path = "/opt/platform/repository/{}".format(label)
    if os.path.isdir(repo_path):
        os.rmdir(repo_path)
    call(["git", "clone", repository, repo_path])
    requests.post("http://127.0.0.1:5000/callback/git-repository-cloned", {"label": label})
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
