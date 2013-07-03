Getting started
===============

.. highlight:: console

Beaker repository structure
---------------------------

Beaker consists of several different components. The largest and most
critical are a set of web services that manage an inventory of hardware
systems distributed across multiple labs and take care of provisioning
systems appropriately and dispatching jobs to them.

This is the software that is developed in the `main Beaker git
repository <http://git.beaker-project.org/cgit/beaker/>`_ (click link to
browse). The bulk of this developer guide focuses on this component.

However, http://git.beaker-project.org plays host to a few other
components which are also considered part of the wider "Beaker project":

-  `beaker-project.org <http://git.beaker-project.org/cgit/beaker-project.org/>`_:
   The source for the project web site (including this developer's
   guide)
-  `beah <http://git.beaker-project.org/cgit/beah/>`_: The test harness
   used to communicate between running tests and the Beaker
   infrastructure. Other test harnesses (such as autotest or STAF) are
   not yet officially supported. Unlike the Beaker web services (which
   are only officially supported on the platforms described below), the
   test harness must run on all operating systems supported for testing.
-  `rhts <http://git.beaker-project.org/cgit/rhts/>`_: The code in this
   repo isn't part of Beaker as such, it's a collection of utilities
   designed to help with writing and running Beaker test cases.

Cloning the main Beaker repo
----------------------------

Start by cloning `Beaker's git
repository <http://git.beaker-project.org/cgit/beaker/>`_::

    git clone git://git.beaker-project.org/beaker

For the purposes of development, Beaker should be run on the ``develop``
branch::

    git checkout develop

This branch will become the next Beaker release. If you want to test
against the latest released version, you can use the ``master`` branch.
For older releases, use the relevant git tag.

Cloning the other repos is similar to the above, but they all develop
directly on master (as they don't have a concept of "hot fix" releases
that only include bug fixes - any release may include a combination of
both new features and bug fixes)

Running Beaker
--------------

Beaker currently only supports MySQL with InnoDB as the database backend
(it does use SQL Alchemy internally though, so porting it to an
alternate backend shouldn't be too difficult). On RHEL and Fedora
systems, MySQL can easily be installed with::

    yum install mysql

For Beaker development, the following settings should be added to
``/etc/my.cnf`` in the ``[mysqld]`` section before starting the MySQL
daemon::

    default-storage-engine=INNODB
    max_allowed_packet=50M
    character-set-server=utf8

Once these settings are in place, start the database daemon::

    service mysqld start

Before running the development server for the first time, you must
create and populate its database (your working directory should be the
``Server`` subdirectory of your local clone of the main beaker project)::

    mysql -uroot <<"EOF"
    CREATE DATABASE beaker;
    GRANT ALL ON beaker.* TO 'beaker'@'localhost' IDENTIFIED BY 'beaker';
    EOF
    PYTHONPATH=../Common:. python bkr/server/tools/init.py \
        --user=admin \
        --password=adminpassword \
        --email=me@example.com

By default this uses the ``beaker`` database on localhost. This can be
changed by editing ``dev.cfg`` and updating the above configuration
commands appropriately.

You can then start a development server using the ``start-server.py``
script, with ``PYTHONPATH`` adjusted for the git checkout::

    cd Server/
    PYTHONPATH=../Common:. ./start-server.py

The Beaker team uses `RHEL
6 <http://www.redhat.com/products/enterprise-linux/server/>`_ for
development, testing, and deployment, therefore it is recommended to use
RHEL 6 when writing your patch. Beaker should also work on Fedora 16 or
higher, although this configuration is not well tested.

If you want to set up a complete Beaker testing environment (including a
lab controller) with the ability to provision systems and run jobs,
refer to :ref:`virtual-fedora`, or the more detailed `installation
instructions <../../docs/admin-guide/installation.html>`_.

Running Lab Controller processes in a development environment is
currently not well tested.
