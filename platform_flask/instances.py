from platform_flask import app
from flask import Flask, session, redirect, url_for, request, flash, render_template
from platform_flask.models import db, User, Configuration, Repository, AppInstance
from platform_flask.systemd import Systemd, SystemdUnit
from time import sleep
import os
from subprocess import call, getoutput
from platform_flask import celery
from platform_flask.routes import get_task_status
import requests
import shutil
import copy


@app.route('/instance/new', methods=["POST"])
def instance_new():
    label = request.form['label']
    source_repo = request.form['source_repo']

    clone_source = request.form['clonesource']
    branch = request.form['branch']
    tag = request.form['tag']

    if clone_source == 'tag':
        git_ref = tag
    else:
        git_ref = branch

    platform = request.form['platform']
    entrypoint = request.form['entrypoint']
    args = request.form['args']

    port = request.form['port']
    proxy = 'proxy' in request.form
    mountpoint = request.form['mountpoint']

    source_repo = Repository.query.filter_by(label=source_repo).first()

    instance = AppInstance(label, source_repo.id)
    instance.clone_source = clone_source
    instance.tag = tag
    instance.branch = branch
    instance.platform = platform
    instance.entrypoint = entrypoint
    instance.arguments = args
    instance.port = int(port)
    instance.proxy = proxy
    instance.mountpoint = mountpoint
    instance.status = "installing"

    task = create_platform_python27.delay(label, source_repo.get_repo_path(), tag, entrypoint, args)
    instance.task = task.task_id

    db.session.add(instance)
    db.session.commit()
    return redirect(url_for('index'), code=303)


@celery.task()
def create_platform_python27(label, source_repo_path, git_ref, command, args):
    if not os.path.isdir('/opt/platform/apps'):
        os.mkdir("/opt/platform/apps")
    if os.path.isdir('/opt/platform/apps/{}'.format(label)):
        shutil.rmtree('/opt/platform/apps/{}'.format(label))
    os.mkdir("/opt/platform/apps/{}".format(label))
    os.mkdir("/opt/platform/apps/{}/data".format(label))
    repo_path = '/opt/platform/apps/{}/repo'.format(label)
    venv_path = '/opt/platform/apps/{}/venv'.format(label)

    call(["git", "clone", source_repo_path, repo_path])
    call(["git", "-C", repo_path, "checkout", git_ref])
    call(["virtualenv", "-p", "python2.7", "--system-site-packages", venv_path])

    new_environment = copy.deepcopy(os.environ)
    new_environment['PATH'] = "{}/bin:{}".format(venv_path, new_environment['PATH'])
    new_environment['VIRTUAL_ENV'] = venv_path
    if "PYTHON_HOME" in new_environment:
        del new_environment['PYTHON_HOME']

    if os.path.isfile("{}/requirements.txt".format(repo_path)):
        print("Requirements file found. Installing dependencies")
        call(["{}/bin/pip".format(venv_path), "install", "-r", "{}/requirements.txt".format(repo_path)],
             env=new_environment)

    print("Creating systemd unit")
    unit = SystemdUnit()
    unit.description = "Platform application: {}".format(label)
    unit.name = label
    unit.exec = "{}/bin/python2.7 {}/{} {}".format(venv_path, repo_path, command, args)
    unit.environment = {
        'VIRTUAL_ENV': venv_path,
        'PATH': new_environment['PATH']
    }
    unit.save_unit("/etc/systemd/system/platform-{}.service".format(label))
    print("Reloading systemd")
    call(["systemctl", "daemon-reload"])
    return "OK"
