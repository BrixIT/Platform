# BrixIT Platform

This is a management platform intended to run on Debian 8 (because systemd) to run webapplications written in several
languages.

Currently planned supported platforms:

- [x] Python 2.7
- [x] Python 3.4
- [ ] Nodejs
- [ ] PHP

Platform works by downloading git (and others soon) repositories in the webinterface and creating "instances" of it. 
Platform will automatically create a new seperate environment for the webapplication (virtualenv for python for example)
and create a systemd unit to run the webapp. It also can automaticaly create a new entry in nginx to reverse proxy the
webapplications to port 80 in a subdirectory.

# Installing

The install documentation is on [platform.brixit.nl](http://platform.brixit.nl)

# Running

To start the management application:

```bash
$ systemctl start platformweb
# The server will start on port 5000
```

To start the background worker:

```bash
$ systemctl start platformworker
```

# Screenshots

The overview page:

![overview](http://brixitcdn.net/github/platform/overview.png)

The repositories page:

![repositories](http://brixitcdn.net/github/platform/repositories.png)

The instances page:

![instances](http://brixitcdn.net/github/platform/instances.png)

The page to create a new instance from a repository:

![New instance](http://brixitcdn.net/github/platform/new-instance.png)

Instance details and journal:

![Instance details](http://brixitcdn.net/github/platform/instance_detail.png)

# TODO

Not in any order:

- [ ] Implement Nodejs platform
- [ ] Write unit tests
- [ ] Support subdomain proxy instead of directory
- [ ] Implement PHP platform
- [ ] Add process tree to instance detail page
- [ ] Add config file support to instances
- [ ] Bind instance settings to config file settings (automatic port change and mountpoint config)
- [ ] Add CPU/Memory view to instances
- [ ] Add permissions for more users and instances
- [ ] Add auth support in reverse proxy
- [ ] Add support for proxying external servers
- [ ] Add support for SSL termination in proxying (maybe with mozilla's encrypt-the-web support)
- [ ] Create Debian package
- [ ] Create custom Debian iso
- [ ] Support database creation and dependencies for instances
