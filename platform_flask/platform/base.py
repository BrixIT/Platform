import os
import shutil
from subprocess import call


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
