.. _proposal-system-pools:

System Pools
============

:author: Dan Callaghan
:editor: Nick Coghlan
:release: Beaker 1.1


Abstract
--------

This proposal adds the ability to mark systems as members of various
system pools. These pools can then be used to control usage of the assets
by assigning permissions to various user groups.


Dependencies
------------

This proposal depends on:

* :ref:`proposal-enhanced-user-groups`

Proposal
--------

A system can be in zero or more pools. On a pool, each of the following
permissions can be granted to any number of groups:

* edit system details
* loan system to anyone
* loan system to self
* control system power
* schedule recipes on the system when submitting jobs
* reserve system manually (via web UI or bkr client)

Note that there is no "add/remove systems" permissions, as the authority
to add systems to and remove them from pools always rests with the system
owners.

When running a job, the candidate systems are taken from all pools the
submitting user has access to via any of their groups (for regular  jobs),
or the owning group has access to (for group jobs)


Detailed Use Cases
------------------

* I want to add my system to a pool.

Through the web UI:

   On the system page, click the "Pools" tab. (This will replace the
   existing "Groups" tab.) Enter the name of the pool and click "Add".

Through the ``bkr`` cli::

   bkr system-modify --add-pool=<poolname>

The permissions defined on that pool will now apply to your system. If
your system is in multiple pools, the union of all pool permissions will
apply to your system.

* I want to define a new pool of systems. [GSS-R-1]

Through the web UI:

   Select "Systems -> Pools" from the menu, then click "Create". Enter the
   pool name, select one or more groups to own the pool, and configure the
   pool permissions as desired.

Through the ``bkr`` cli::

   bkr pool-create --owner-group=<groupname> <poolname>

A new pool is created containing no systems.

* I want to share my system with all Beaker users. (This replaces
  the existing "shared with no groups" configuration.)

Add your system to the "shared" pool, which is a pool created by default
in Beaker. All users have access to this pool.

* I want to allow specific groups to edit my system's details, or to loan
  out my system, or to power-cycle my system, or  to reserve my system via
  the scheduler or manually.

Through the web UI:

   First,  pick a suitable pool or create a new one, and add your system
   to it.  Then configure the pool to grant the desired permissions
   (see list above) to the desired groups.

Through the ``bkr`` cli::

   bkr system-modify --add-pool=<poolname>
   bkr pool-manage --grant-<permission>=<groupname> <poolname>

* I want to submit a job and limit it to systems in a particular pool.

Through the job XML:

   Use  ``<pool op="=" value="somepool" />`` in the
   ``<hostRequires/>`` of your job XML.

Through the ``bkr`` cli:

   Pass ``--hostrequire=pool=somepool`` to a workflow command.

This filter will select only systems which are in the given pool.

* I want to submit a job and express an ordered preference regarding
  the pools where I would like the job to run.

Through the job XML:

   Use ``<autopick/>`` in the ``<recipe/>`` section of the job XML, with a
   sequence of ``<pool/>`` elements. There is an implied "other systems"
   at the end, which covers all other systems which the user has  access
   to (use ``<hostRequires/>`` to limit a job to specific system  pools).

   When ``random="true"`` is set on the autopick element, the pool order
   in the XML is still used, but the specific system used is selected
   randomly from within each pool (or the implied "other systems" after
   the list of specific pools is exhausted). To select randomly from
   multiple pools without expressing a preference between them, use
   an empty ``<autopick  random="true" />`` element and several
   ``<pool/>`` selection elements grouped under a ``<or/>`` element
   in the ``<hostRequires/>`` section of the job XML.
