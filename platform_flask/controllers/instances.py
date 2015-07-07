import os
from subprocess import call
import shutil

from flask import redirect, url_for, request, render_template

from platform_flask import app
from platform_flask.models import db, Repository, AppInstance
from platform_flask.components.systemd import Systemd
from platform_flask.components.nginx import Nginx
from platform_flask.platform.python import create_platform_python27, create_platform_python34


@app.route('/instances')
def instances():
    apps = []
    systemd = Systemd()
    db_apps = AppInstance.query.order_by(AppInstance.repository_id)
    for a in db_apps:
        status = a.status
        if status == "installed":
            unit = systemd.load(a.label)
            unit_info = unit.get_status()
            status = unit_info['status']
        repo = Repository.query.get(a.repository_id)
        apps.append({
            'status': status,
            'label': a.label,
            'repository': repo.label,
            'platform': a.platform,
            'port': a.port,
            'mountpoint': a.mountpoint,
            'id': a.id
        })

    return render_template('instances.html', apps=apps)


@app.route('/instance/<label>')
def instance_detail(label):
    instance = AppInstance.query.filter_by(label=label).first()
    systemd = Systemd()
    unit = systemd.load(instance.label)
    journal = unit.get_journal()
    priority = {
        "0": "emerg",
        "1": "alert",
        "2": "crit",
        "3": "err",
        "4": "warning",
        "5": "notice",
        "6": "info",
        "7": "debug"
    }
    running = unit.is_running()
    resource_usage = unit.get_usage()
    return render_template('instance_detail.html', instance=instance, journal=journal, priority=priority,
                           running=running, usage=resource_usage)


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

    if platform == 'python27':
        task = create_platform_python27.delay(label, source_repo.get_repo_path(), git_ref, entrypoint, args)
    elif platform == 'python34':
        task = create_platform_python34.delay(label, source_repo.get_repo_path(), git_ref, entrypoint, args)

    instance.task = task.task_id

    db.session.add(instance)
    db.session.commit()
    return redirect(url_for('index'), code=303)


@app.route('/instance/<id>/systemd/<command>')
def instance_systemd_command(id, command):
    instance = AppInstance.query.get(id)
    label = instance.label
    unit = Systemd().load(label)
    unit.command(command)
    return redirect(url_for('instance_detail', label=label))


@app.route('/instance/<id>/destroy')
def destroy_instance(id):
    instance = AppInstance.query.get(id)
    label = instance.label
    call(['systemctl', 'stop', 'platform-{}'.format(label)])
    call(['systemctl', 'disable', 'platform-{}'.format(label)])
    if os.path.isfile('/etc/systemd/system/platform-{}.service'.format(label)):
        os.remove('/etc/systemd/system/platform-{}.service'.format(label))
    if os.path.isdir('/opt/platform/apps/{}'.format(label)):
        shutil.rmtree('/opt/platform/apps/{}'.format(label))
    db.session.delete(instance)
    db.session.commit()
    Nginx.rebuild()
    call(["systemctl", "restart", "nginx"])
    return redirect(url_for('instances'))


@app.route('/callback/instance-created', methods=["post"])
def callback_instance_new():
    label = request.form['label']
    instance = AppInstance.query.filter_by(label=label).first()
    instance.status = "installed"
    db.session.add(instance)
    db.session.commit()
