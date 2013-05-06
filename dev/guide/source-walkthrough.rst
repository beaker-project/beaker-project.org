Source code walk-through
------------------------

Please see the
`README <http://git.beaker-project.org/cgit/beaker/tree/README>`_ file
in the root directory of Beaker's source tree for a detailed description
of its layout.

Lab controller
~~~~~~~~~~~~~~

The lab controller is the intermediary point of communication between
the lab machines, and the beaker server. It provides entry points for
the following processes:

-  beaker-proxy
-  beaker-watchdog
-  beaker-transfer
-  beaker-provision

These processes authenticate themselves using the credentials found in
``/etc/beaker/labcontroller.conf``.

beaker-proxy
^^^^^^^^^^^^

beaker-proxy is a process that binds to an open unprivileged port on the
lab controller. It provides an xmlrpc server that more or less forwards
calls made to it (from lab machines) onto the beaker server.

Here is a simple example of a typical controller from
``bkr.labcontroller.proxy``:

::

    def task_info(self,
                  qtask_id):
        """ accepts qualified task_id J:213 RS:1234 R:312 T:1234 etc.. Returns dict with status """
        logger.debug("task_info %s", qtask_id)
        return self.hub.taskactions.task_info(qtask_id)

This is quite straightforward. An xmlrpc call would be made to the the
lab controller onto port 8000 (the default for beaker-proxy), with the
method ``task_info`` and the ``qtask id``. The ``task_info()`` method
then calls and returns ``bkr.server.taskactions.task_info``. The ``hub``
variable is a ``HubProxy`` class from ``kobo.client``. ``HubProxy`` in
turn is merely a thin wrapper over ``xmlrpclib.ServerProxy`` that adds
session based authentication management.

beaker-transfer
^^^^^^^^^^^^^^^

When provisioning a system in beaker, Beaker transfers various log files
to the lab controller as a matter of course. Even more log files are
created when running an actual recipe. By default, these logs are
uploaded from the test machine to the lab controller.

Using the ``CACHE`` and ``ARCHIVE_*`` variables in
``labcontroller.conf``, you can specify a remote server where the log
files can be moved to. Once configured, beaker-transfer is responsible
for moving these files from the lab controller to the remote server.

beaker-watchdog
^^^^^^^^^^^^^^^

To ensure that recipes do not run on for longer than what they are
expected to, Beaker uses a watchdog process. This process keeps track of
running recipes on all test systems attached to a particular lab
controller. If a recipe is running for longer than what the server has
specified it can run for, the watchdog aborts the recipe.

Here is a breakdown of how the process works:

1) Recipe progresses up to the Scheduled stage, and a watchdog is
   created for the recipe.
2) Recipe goes into ``Waiting`` stage and (amongst others things) a
   reboot command is sent to the lab controller.
3) System is rebooted and then an RPC is made to the server to start the
   first task, and create a kill time for the watchdog.
4) For each successive task that is run in the recipe, the harness
   extends the kill time of the watchdog by the expected run time
   specified by the ``TestTime`` value in testinfo.desc.
5) If a task runs beyond it's kill time, the harness will first try and
   abort the job and continue onto the next test. If the system crashes
   or panics and the harness isn't able to recover then beaker-watchdog
   will abort the recipe (and any remaining tasks). The time between the
   harness watchdog (also known as local watchdog) and beaker-watchdog
   (also known as external watchdog) is ten minutes.

beaker-provision
^^^^^^^^^^^^^^^^

It is the responsibility of beaker-provision to handle the provisioning
of a system. Its main duties are creating boot loader images and power
cycling systems.

Here is a breakdown of how this process works:

1) Beaker server generates and serves a kickstart file.
2) Beaker server sends a command to beaker-provision with the path to
   the distro tree, kernel options, and a link to the kickstart file. It
   also sends a command to power cycle the system.
3) From these details, beaker-provision generates the relevant boot
   loader configuration file, and then power cycles the test system.
4) The system boots and starts its install.

Server
~~~~~~

The main focus of the beaker server is to maintain a distro and system
inventory, run tasks against this inventory, and display the results of
those tasks. Any interaction with this inventory must be via the server.
For further details of the design of Beaker's services, please see the
relevant
`docs <http://beaker-project.org/guide/Administration-Beaker_Architecture.html>`_.

Beaker is developed to run in Red Hat Enterprise Linux 6 (RHEL6).
Versions previous to 0.7 were designed for RHEL5. Although it may be
technically possible to run Beaker on other distributions, package
dependencies and other issues may ensue.

The Beaker server is a web application that is built upon TurboGears
(TG) 1.x. Here is a quick breakdown of TG (and its relevant sub-frameworks) and 
how Beaker utilizes them.

TurboGears 1.x
    TurboGears (TG) is a "front-to-back" web meta-framework. TurboGears 1.x is 
    no longer under active development. Documentation is still available on the 
    `TurboGears website <http://www.turbogears.org/1.0/docs/>`_.
Core TG
    These are modules which are implemented within TG itself.
identity
    does session based authentication, is used to control access to resources.
widgets
    provides pre built templates and display functionality. Templates are 
    written in Kid. Beaker's own custom widgets are also built upon TG widgets.
CherryPy 2
    Provides resource routing, handling of request and response objects. 
    CherryPy 2 is no longer under active development.
Kid
    Provides the templating language for hand written templates, as well as TG 
    widgets. Kid is not longer under active development.
SQLAlchemy
    An ORM database interface. Used exclusively for all access to Beaker's 
    database. Note that Beaker uses some TG database modules, but these are 
    thin wrappers over SQLAlchemy.
JQuery/MochiKit
    MochiKit is bundled with TG, however JQuery is heavily used alongside it.

As a result of being built on TG, Beaker is an MVC inspired application.
Whilst it mostly follows TG conventions, Beaker does sometimes go
outside of these when it's appropriate (and advantageous) to do so.

Model
^^^^^

The ``bkr.server.model`` module primarily consists of Object Relational
Mapped (ORM) classes. Fundamentally, these are user defined python
classes associated to database tables, the objects of which are mapped
to rows in the related table. From version 0.11 ORM classes should be
defined
`declaratively <http://docs.sqlalchemy.org/en/rel_0_7/orm/extensions/declarative.html>`_.
Previous versions used `'Classical
Mapping' <http://docs.sqlalchemy.org/en/rel_0_7/orm/mapper_config.html#classical-mappings>`_.

Some basic guidelines to follow when modifying model:

-  For versions < 0.11, definitions of Tables, ORM classes, and calls to
   mapper() are segregated into three distinct sections. Tables are
   defined above ORM classes, and ORM classes above mapper functions. If
   possible define related Tables in the vicinity of each other, and
   likewise for ORM classes and mappers.
-  Commonly used queries should be contained within bound methods of the
   respective classes.
-  Enumerated types should be defined as type DeclEnum and not be
   described in a database schema. This helps avoid over normalization,
   cuts down on unnecessary calls to the database, and reduces the
   likelihood of complex joins that confuse the query optimizer. This
   only applies though if it's an enumeration that is static.
-  When writing queries, use ORM attributes over 'SQL Expression
   Language' whenever possible, and never use 'Text'.
-  Write efficient queries. Do what you can to write the most reasonably
   efficient query. For various reasons, Beaker has few options of
   removing its historical data. Thus query speed and data-set size can
   only increase over time. As Beaker's UI relies heavily on database
   calls, writing inefficient queries can quickly become a bottleneck
   and create a marked reduction in usability.
-  Beyond the basic relationship mapping, relationships should be
   defined keeping performance in mind. The sqlalchemy documentation
   provides some good
   `ideas <http://docs.sqlalchemy.org/en/rel_0_7/orm/collections.html>`_.
-  Remember to define relevant cascade options.

Controllers
^^^^^^^^^^^

A controller is called when a HTTP request is made. The URL is
translated to a particular controller. CherryPy is responsible for
handling this method look-up. For example, a call to
*http://beaker.example.com/tasks/executed* will call the
``bkr.server.tasks.executed`` method.

Generally speaking, Beaker controllers are grouped into a single module
for either one of two purposes. Either because the controller provides
various modifies and accessors for a single ORM class (e.g the
``bkr.server.system`` module contains various accessor and modifier
methods for the ``System`` class), or for the purpose of supporting a
single page view and any associated actions (e.g the
``bkr.server.preferences`` module contains all of the views and actions
needed for viewing and updating users preferences).

Sometimes a mix of these two can be found, and this is also fine (i.e
``bkr.server.tasks`` contains controllers for displaying and searching
on task details, as well as methods designed to be called remotely to
provide details of ``Task`` objects).

View
^^^^

Both Kid templates and TG widgets are used to support the 'View' of MVC.
Beaker uses TG widgets to provide re-usability of commonly rendered page
elements. A widget encapsulates the template to be rendered, as well as
any javascript and CSS files that are needed by that template. Generally
speaking, creating a widget is preferable to using a controller +
template due to the re-usability of a widget. However there is no hard
and fast rule in regards to this.

As well as standard widgets being provided by TG, Beaker also implements
many of its own widgets in the ``bkr.server.widgets`` module.

Templates are used in one of two ways; by specifying a template in an
'expose' decorator; by setting the template variable in a widget, and
then calling that widget's 'display' method. Examples of both will be
shown in the patch walk-through.

Client
~~~~~~

The beaker-client package provides shell commands that makes varied
calls to the server. The format of the calls are
``bkr <cmd> <options>``, where ``<cmd>`` corresponds to a module in the
``bkr/client/commands`` directory. The modules of the corresponding code
is a normalized version of the same name as the command, but with the
prefix *cmd\_*. For example, ``bkr job-list`` will call the ``run()``
method of the ``bkr.client.commands.cmd_job_list`` module.

This functionality is provided by the ``kobo.client.ClientCommand``
class, of which all Beaker commands inherit (indirectly or directly).
This class also provides the authentication with the Beaker server via
the same kobo classes as the `lab controller <#lab-controller>`_.
