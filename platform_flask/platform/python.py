import copy
import os
from subprocess import call
from platform_flask import celery
from platform_flask.components.systemd import SystemdUnit
from platform_flask.platform.base import create_instance_directories, clone_app_repo, finish_instance_creation, \
    run_extra_tasks


@celery.task()
def create_platform_python27(label, source_repo_path, git_ref, command, args, extra):
    return create_platform_python(label, source_repo_path, git_ref, command, args, '2.7', extra)


@celery.task()
def create_platform_python34(label, source_repo_path, git_ref, command, args, extra):
    return create_platform_python(label, source_repo_path, git_ref, command, args, '3.4', extra)


def create_platform_python(label, source_repo_path, git_ref, command, args, python_version, extra):
    app_path, repo_path, data_path = create_instance_directories(label)
    clone_app_repo(source_repo_path, repo_path, git_ref)

    venv_path = '{}/venv'.format(app_path)
    call(["virtualenv", "-p", "python{}".format(python_version), "--system-site-packages", venv_path])

    new_environment = copy.deepcopy(os.environ)
    new_environment['PATH'] = "{}/bin:{}".format(venv_path, new_environment['PATH'])
    new_environment['VIRTUAL_ENV'] = venv_path
    if "PYTHON_HOME" in new_environment:
        del new_environment['PYTHON_HOME']

    if os.path.isfile("{}/requirements.txt".format(repo_path)):
        print("Requirements file found. Installing dependencies")
        call(["{}/bin/pip".format(venv_path), "install", "-r", "{}/requirements.txt".format(repo_path)],
             env=new_environment)

    run_extra_tasks(label, extra)

    print("Creating systemd unit")
    unit = SystemdUnit()
    unit.description = "Platform application: {}".format(label)
    unit.name = label
    unit.exec = "{}/bin/python{} {}/{} {}".format(venv_path, python_version, repo_path, command, args)
    unit.environment = {
        'VIRTUAL_ENV': venv_path,
        'PATH': new_environment['PATH']
    }
    unit.save_unit("/etc/systemd/system/platform-{}.service".format(label))
    finish_instance_creation(label)
    return "OK"
