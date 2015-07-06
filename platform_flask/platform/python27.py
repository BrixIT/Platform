import copy
import os
import shutil
from subprocess import call
import requests
from platform_flask import celery
from platform_flask.components.nginx import Nginx
from platform_flask.components.systemd import SystemdUnit


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
    call(["systemctl", "enable", "platform-{}".format(label)])
    call(["systemctl", "start", "platform-{}".format(label)])
    requests.post("http://127.0.0.1:5000/callback/instance-created", {"label": label})
    Nginx.rebuild()
    call(["systemctl", "restart", "nginx"])
    return "OK"