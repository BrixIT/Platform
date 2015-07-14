Deploying applications
======================

Deploying an application is done in 2 stages. First you go to "Repositories" and use the Add repository form to clone
the git repository containing your application. If the repository requires authentication then you can enter it in the
global platform configuration (Dropdown under your username -> Platform configuration).

After you press "Fetch" the background worker will clone the HEAD revision of the default branch to the repositories folder
in Platform. After cloning is finished you can use the plus button behind the repository to create an instance.

The instance creation page is divided in three sections. In the source section you choose what branch or tag will be used
to create an instance of the application. In the Application instance section you fill in the configuration required to
deploy the application.

**Label** is only the internal name for the application instance in the admin panel

**Platform** chooses the type of platform that will be created to deploy your application in.

**Entrypoint** is the repository relative path to the main file in your application. This usually is the file that starts
a webserver and starts serving your application.

**Arguments** is the list of command line arguments passed to the file in entrypoint. You can use three substitutions here:

* {{port}} the port that your application has to bind to
* {{mountpoint}} the "subdirectory" the application will run as
* {{datadir}} the path to store instance-specific data

**Run bower install** is only visible if a bower.json file is found in the root of the repository.

The last section is Frontend. This is the Nginx configuration for the instance. If you check "Use auto assigned port" it
will use the first available port after 42000 to listen for the application. If you used {{port}} in the instance argument
it will automatically be filled with this port. It is also possible to enter another port in the Application http port box.

If you check "Proxy application to a path on \*:80" then Platform will create an entry in Nginx to reverse proxy
``http://<server-ip>/<mountpoint>`` to ``http://127.0.0.1:<application-port>/<mountpoint>``. The mountpoint is defined in the input
box below.

Press create and the background worker will deploy your application.

Python application specifics
----------------------------

If you have chosen for the Python 2.7 or Python 3.4 platform while creating an instance then Platform will create a
virtualenv for your instance. If ``requirements.txt`` exist in the root of your git repo then those dependencies will
be installed in the instance virtualenv.

The directory structure
-----------------------

Repositories are cloned to ``/opt/platform/repositories/<repo-label>`` when added from the webinterface. If you create an
instance from that repository the worker will clone the repository internally to ``/opt/platform/apps/<instance-label>/repo``
and create the empty directory ``/opt/platform/apps/<instance-label>/data``. The data directory is passed to the instance
argument template in the {{datadir}} variable.

For the Python platform the virtualenv for the instance will be created in ``/opt/platform/apps/<instance-label>/venv``