# BrixIT Platform

This is a management platform intended to run on Debian 8 (because systemd) to run webapplications written in several
languages.

Currently supported platforms:

- [x] Python 2.7
- [ ] Python 3.4
- [ ] Nodejs

Platform works by downloading git (other soon) repositories in the webinterface and creating "instances" of it. 
Platform will automatically create a new seperate environment for the webapplication (virtualenv for python for example)
and create a systemd unit to run the webapp. It also can automaticaly create a new entry in nginx to reverse proxy the
webapplications to port 80 in a subdirectory.

# Installing

Platform will ultimatly be a customised Debian iso that will do this for you. For now, install:

- nginx
- python2.7
- python3.4
- rabbitmq
- mysql-server
- git

and clone this repository to `/opt/platform`.

Please not that this install guide is not complete.

# Running

To start the management application:

```bash
$ cd /opt/platform
$ python3 runserver.py
# The server will start on port 5000
```

To start the background worker:

```bash

$ cd /opt/platform
$ celery worker -A platform_flask.celery
```

# Screenshots

//TODO: Screenshots