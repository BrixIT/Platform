import os
import shutil
from subprocess import call
import requests
from platform_flask.components.nginx import Nginx


def create_instance_directories(label):
    if not os.path.isdir('/opt/platform/apps'):
        os.mkdir("/opt/platform/apps")
    if os.path.isdir('/opt/platform/apps/{}'.format(label)):
        shutil.rmtree('/opt/platform/apps/{}'.format(label))
    os.mkdir("/opt/platform/apps/{}".format(label))
    os.mkdir("/opt/platform/apps/{}/data".format(label))
    app_path = '/opt/platform/apps/{}'.format(label)
    repo_path = '{}/repo'.format(app_path)
    data_path = '{}/data'.format(app_path)
    return app_path, repo_path, data_path


def clone_app_repo(source, target, git_ref):
    call(["git", "clone", source, target])
    call(["git", "-C", target, "checkout", git_ref])


def finish_instance_creation(label):
    call(["systemctl", "daemon-reload"])
    call(["systemctl", "enable", "platform-{}".format(label)])
    call(["systemctl", "start", "platform-{}".format(label)])
    requests.post("http://127.0.0.1:5000/callback/instance-created", {"label": label})
    Nginx.rebuild()
    call(["systemctl", "restart", "nginx"])


def run_extra_tasks(label, extra):
    if 'bower' in extra and extra['bower']:
        print("Installing bower dependencies")
        call(['bower', 'install', '--allow-root'], cwd='/opt/platform/apps/{}/repo'.format(label))
