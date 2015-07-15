.. BrixIT Platform documentation master file, created by
   sphinx-quickstart on Tue Jul 14 10:48:24 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Installation instructions
=========================

The plan is to release a custom Debian 8 iso with Platform preinstalled. Ready to be installed on your server or VM to start
running applications, but since this is a alpha development version you have to manually install it. The only supported distro
to run this in is currently Debian 8

Installation on Debian 8
------------------------

.. highlight:: bash

First install the dependencies::

   $ apt-get install git python3 python3-pip nginx mysql-server postfix

The rest of the requirements are all python modules. Set the mysql login to root:platform when asked.
Now create the mysql database used for Platform::

   $ mysql -uroot -p
   >> create database platform;
   >> quit;

Now you need to clone the Platform git repo to /opt/platform and install the dependencies::

   $ cd /opt
   $ git clone https://github.com/BrixIT/Platform.git platform
   $ cd platform
   $ pip3 install -r requirements.txt
   $ cp platformweb.service /etc/systemd/system
   $ cp platformworker.service /etc/systemd/system
   $ systemctl daemon-reload

Platform also needs RabbitMQ to communicate with the background worker service. To install RabbitMQ follow the instructions
on `the RabbitMQ website`_

The last thing you need are the dependencies for the platform you want to use.

.. _the RabbitMQ website: https://www.rabbitmq.com/install-debian.html

Installing the Python 2.7 platform
----------------------------------

The only thing needed for Python 2.7 is the python interpreter and pip::

   $ apt-get install python python-pip

Installing the Python 3.4 platform
----------------------------------

All dependencies for the Python3.4 platform are already installed since Platform itself is a Python 3 application

Starting Platform
-----------------

Platform itself is only two systemd units. Enable them and start them::

   $ systemctl enable platformweb
   $ systemctl enable platformworker
   $ systemctl start platformweb
   $ systemctl start platformworker


Basic configuration
-------------------

There are some global configuration settings that are smart to configure. The most important one is the SMTP config.

Go to the global configuration in the webinterface (Dropdown under your username in the header) and fill in the SMTP settings:

**hostname** is the name or ip of your mail relay server

**port** is the port of the relay server (defaults to 25, might be 587 or 465)

**use tls** enables SSL/TLS encryption, use only of your provider supports it. This is mostly used when your provider uses
port 465 or 587 for SMTP.

**use auth** needs to be checked when the mail relay server requires an username and password

**username** and **password** are the login settings for the mail relay

For using your Gmail account to send the emails you enter the following settings:

**hostname**: smtp.gmail.com

**port**: 587

**use tls** and **use auth** needs to be checked

**username** and **password** are the login for your Gmail account.