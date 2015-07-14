The components
==============

Platform is divided in seperate components. This is a descriptions of what the seperate components do

platformweb.service
-------------------

This systemd unit starts runserver.py and hosts the whole webinterface on port 5000. The webinterface uses Sqlite as
persistance in /opt/platform/platform.db. It also connects to Mysql and RabbitMQ for the task queue managed by Celery.

platformworker.service
----------------------

This starts an instance of `celery`_ that imports the flask application as module. This communicates to the webinterface
through Mysql and RabbitMQ and runs the long running tasks like cloning a git repository and creating a new application
environment. The webinterface and worker load the same codebase but the webinterface only uses the functions that are
decorated with @app.route() and the worker uses the functions decorated with @celery.task

.. _celery: http://www.celeryproject.org/

/opt/platform/packages
----------------------

This is a repository with definitions for applications. This data is used to create an almonst "One click install" experience
when installing some popular applications. It defines almost all data required to prefill the "New instance" page in Platform,
you only need to think of a label for your instance. This directory will be split from the main Platform git repo and will
update independently with new applications. This wil also make it possible to swap the git repo path with your own fork
to provide one-click-install for your own in-house applications or you can create a pull request on the main repo to include
your own projects.