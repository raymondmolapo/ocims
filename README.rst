=====================================
NOCIMS: Web Portal Installation Guide
=====================================

:Version: 1.0 <2016/05/11>
:Author: Derek Hohls <dhohls@csir.co.za>
:Filename: README.rst

.. contents::

.. footer::

    NOCIMS: Web Portal Installation Guide (ver 1.0)  -###Page###-


Overview
========

These notes are to guide you in setting up and configuring the NOCIMS Web Portal
on a target Ubuntu server (which is connected to the internet in an unblocked 
manner).

These instructions assume you have a working knowledge of:

* Linux
* Python
* Apache
* Docker and docker-compose
* PostgreSQL
* CKAN

Suggested reading is also:

* https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/


Prerequisites
=============

Docker Setup
------------

Please ensure you have an update-to-date version of Docker installed (version
1.11 or higher).  You can test this by running::

    docker run hello-world
    
And you should see output which will include::

    Hello from Docker.
    This message shows that your installation appears to be working correctly.

If you get this error message:

`"Cannot connect to the Docker daemon. Is 'docker -d' running on this host?"`

You need to install and run the latest version of Docker; please read the docs 
at https://docs.docker.com/installation/ubuntulinux/ which guide you through
setting up `apt` and so forth.

To run the Docker daemon::

    sudo docker service start


User and Project Setup
----------------------

The following install **assumes** that you have created a user called `ocims`, 
who has `sudo` rights, added that user as a member of the `docker` group (see
above) and that you are logged in as that user.

If you are reading this, then you are likely to have access to this project's
software repo; obtain a clone of the software if you have not already done so,
as described in **Project Preparation**.


Project Preparation
===================

Basic command line setup::

    cd ~
    apt-get install wget
    pip install --upgrade pip
    pip install virtualenvwrapper
    mkvirtualenv ocims
    pip install docker-compose
    pip install jinja2
    git clone ... ocims  # TODO!!
    cd ocims
    cp config.json.sample to config.json
    cp compose.yml.sample to compose.yml


Installation
============

The primary install is via a Python script (`setup.py`), which uses variables 
defined in a JSON-formatted configuration file (see below).

To use the script with default configuration file and parameters::

    python setup.py

This should alert you as to any errors in the setup. To display the various 
options for the setup, run::

    python setup.py --help

Configuration Variables
-----------------------

The `config.json` file is used to set up all the necessary configuration 
variables used to run all the Dockers, as well to set any values for the 
CKAN `production.ini` file.

The configuration variables are used by `setup.py` to set the values in the 
`compose.yml` template file - the result of this templating operation is to
create a `docker-compose.yml` file. This in turn is used for the Docker Compose
process (see: https://docs.docker.com/compose/).

The various Configuration Variables are described in more detail below.

general
~~~~~~~

 * `host`: the IP address of the machine on which all the Docker services will
   be running

solr
~~~~

**NOTE**: 
This install assumes you are using solr 5.3 or higher (earlier versions may
require different configurations e.g. the `solr_url` setting for CKAN).

 * `volume`: the file system location on which Solr data files will be stored
 * `backup`: the file system location on which Solr backup files will be stored
 * `port`: the port on which the Solr application will be accessible
 * `schema`: the full path the host directory for the `schema.xml` file
 * `conf_in`: the host directory in which the core config files are housed
 * `conf_out`: the container directory in which the core config files are housed
 
Note that in the `compose.yml` template file, there is an additional section:

 * `command`: used to precreate the `ckan` core; see https://hub.docker.com/_/solr
   in the section **How to use this Docker image**; and for details look at
   the *solr-precreate* section in the `docker-entrypoint.sh` file housed in
   https://github.com/docker-solr/docker-solr/blob/master/5.3/scripts/

postgresql
~~~~~~~~~~

 * `volume`: the file system location on which PostgreSQL data files will be stored
 * `backup`: the file system location on which PostgreSQL backup files will be stored
 * `port`: the port on which the PostgreSQL application will be accessible [5431]
 * `user`: the primary user for the PostgreSQL application 
 * `database`: the primary database for the PostgreSQL application 
 
If the port, user and database are not set, these will revert to the defaults
for the PostgreSQL and/or CKAN applications.

ckan
~~~~

* `settings`: contains a dictionary of values that will be used to 
  create entries/changes in various of the CKAN setup files (e.g. the
  `production.ini` file).

  The names of the settings correspond to those used in the CKAN installation
  guide; see http://docs.ckan.org/en/latest/maintaining/installing/install-from-package.html
  for reference.
  
  Note that where the settings do not contain explict values, these will be
  created implicitly in the code.


Initial Workflow
================

Assuming the steps in the **Project Preparation** section have been complete,
you should:

* edit `config.json` and change **Configuration Variables** as required
* run the `setup.py` Python script; this:

    * creates `docker-compose.yml` file
    * create `ckan/script/config.json` file
    * if necessary, downloads the CKAN .deb file to extract the `schema.xml';
      and also does a once-off startup of the solr container to extract the
      `conf` files (for solr core creation); and copies the CKAN `schema.xml'
      to that same directory
    * launches containers by calling the Docker compose application

The CKAN container contains a startup script (`config.py`) that runs when the 
container starts up. This will update the CKAN ini file (`production.ini`),
initialise the database (if needed), and restart the Apache and nGinx servers
running inside the container.


Daily Workflows
===============

In normal workflow, if the containers need to be shutdown for any reason::

    python setup.py -c down

And then started again::

    python setup.py -c up

Checking what Dockers are currently running::

    python setup.py -c ps
    
If you wanted to bring all the containers up but not, for example, CKAN, then::

    python setup.py -c up -x ckan

And to manually start just one container, use the normal Docker command::

    docker run -it --entrypoint=/bin/bash  \
    --env CKAN_POSTGRESQL_PASSWORD=$CKAN_POSTGRESQL_PASSWORD \
    -v ~/ckan/scripts/:/scripts ocims_ckan -s

Bear in mind that `build` only works for Dockerfiles (such as the one for CKAN)
and if you need to use another image (e.g. for Solr), then running `up`
(after `down`) will pull and use that new image the first time it is called.


Troubleshooting
===============

PostgreSQL
----------

* Note that if the PostgreSQL user/password are changed in the configuration
  file, they will **not** be changed in PostgreSQL  (after the first 
  initialisation) by the scripts that run here. You will need to consult the
  PostgreSQL manual for how to do this manually.

CKAN
----

The CKAN Docker has a pre-defined entry point.  To override it, and gain access
to the command line in the container::

    docker run -it --entrypoint=/bin/bash ocims_ckan -s

or, to include links to data volumes, e.g. the scripts directory::

    docker run -it --entrypoint=/bin/bash -v \
    ~/ckan/scripts/:/scripts ocims_ckan -s

If one or more of the services required by CKAN do not seem to be accessible,
start by checking the CKAN ini file in the ckan container - this is usually 
`/etc/ckan/default/production.ini`

Apache Issues
~~~~~~~~~~~~~

From inside the CKAN container::

    tail -f /var/log/apache2/ckan_default.error.log




.. NOTE: To generate a PDF of this file, use:
         rst2pdf README.rst -s tenpoint,serif,ocims_styles
