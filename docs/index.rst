.. BrixIT Platform documentation master file, created by
   sphinx-quickstart on Tue Jul 14 10:48:24 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to the documentation for BrixIT Platform
================================================

Contents:

.. toctree::
   :maxdepth: 2

   installation

Platform is a collection of components working together to make deploying (web)applications in various languages easier.
It currently supports applications written in Python 2 and Python 3 with every application running in a virtualenv, deployed
from git and behind nginx as reverse proxy.

Platform doesn't manages this al by itself. It's basically a fancy wrapper around systemd. Platform clones your git repo's,
Prepares a seperate environment for the application, Creates a systemd unit for the application and configures Nginx to proxy it.
While your application is running you can check the status on the Platform dashboard and see the logs for your application from
journald.

There are more features planned for Platform (Listed in the github `README.md`_). In the future it should also manage the databases
associated with the applications. If the application requires a mysql db it wil generate one and pass the database information
to the application. It will also support managing the application instance configuration (which are mostly .ini files) so
that most of this configuration is automatic.

.. _README.md: https://github.com/BrixIT/Platform/blob/master/README.md