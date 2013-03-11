.. _proposal-system-pools:

System Pools
============

:Author: Dan Callaghan, Nick Coghlan
:Status: Proposed
:Target Release: Beaker 1.1


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

Beaker's current system management design offers system owners little
flexibility in providing access to their systems. This proposal enhances
the system management capability by allowing system owners to add their
systems to distinct pools of machines, and using those pools to grant
varying levels of access to different user groups.

A system can be in zero or more pools. On a pool, each of the following
permissions can be granted to any number of groups:

* edit system details (``edit-system``)
* loan system to anyone (``loan-any``)
* loan system to self (``loan-self``)
* issue power and provisioning commands (``control-system``) 
* schedule recipes on the system when submitting jobs (``schedule-recipe``)
* reserve system manually (via web UI or bkr client) (``reserve-manual``)

Each pool must also have one or more "owning groups": (co-)owners of these
groups are allowed to update the pool policy.

Note that there is no "add/remove systems" permission, as the authority
to add systems to and remove them from pools always rests with the system
owners.

When running a job through the automated scheduler, the candidate systems
are taken from all pools the submitting user has access to via any of their
groups (for regular jobs), or that the owning group has access to (for jobs
submitted on behalf of a group). The submitting user may influence the
system selection through the job XML.


Proposed user interface
-----------------------

Defining ad hoc system pools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* As a Beaker user, I want to define a new pool of systems.

Through the web UI:

   Select "Systems -> Pools" from the menu, then click "Create". Enter the
   pool name, select one or more groups to own the pool, and configure the
   pool permissions as desired.

Through the ``bkr`` cli::

   bkr pool-create --owner-group=<groupname> <poolname>

A new pool is created containing no systems.


Controlling system pool membership
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* As a system owner, I want to add my system to a pool.

Through the web UI:

   On the system page, click the "Pools" tab. (This will replace the
   existing "Groups" tab.) Enter the name of the pool and click "Add".

Through the ``bkr`` cli::

   bkr system-modify --add-pool=<poolname>

The permissions defined on that pool will now apply to your system. If
your system is in multiple pools, the union of all pool permissions will
apply to your system.

* As a system owner, I want to remove my system from a pool.

Through the web UI:

   On the system page, click the "Pools" tab. (This will replace the
   existing "Groups" tab.) Click "Delete" next to the unwanted pool.

Through the ``bkr`` cli::

   bkr system-modify --remove-pool=<poolname>


Allowing all users to access a system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* I want to share my system with all Beaker users.

Add your system to the "shared" pool, which is a pool created by default
in Beaker. All users have access to this pool.

The permissions granted to systems in the shared pool are:

* ``loan-self``
* ``control-system``
* ``schedule-recipe``
* ``reserve-manual``


Allowing selected users enhanced access to a system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* As a system owner, I want to allow specific groups to edit my system's
  details, or to loan out my system, or to power-cycle my system, or to
  reserve my system via the scheduler or manually.

Through the web UI:

   First, pick a suitable pool or create a new one, and add your system
   to it. Then configure the pool to grant the desired permissions
   (see list above) to the desired groups.

Through the ``bkr`` cli::

   bkr system-modify --add-pool=<poolname>
   bkr pool-modify --grant-<permission>=<groupname> <poolname>


Restrict recipe execution to a specific system pool
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* I want to submit a job and limit it to systems in a particular pool.

Through the job XML:

   Use  ``<pool op="=" value="somepool" />`` in the
   ``<hostRequires/>`` of your job XML.

Through the ``bkr`` cli:

   Pass ``--hostrequire=pool=somepool`` to a workflow command.

This filter will select only systems which are in the given pool.


Prefer particular system pools for recipe execution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* I want to submit a job and express an ordered preference regarding
  the pools where I would like the job to run.

Through the job XML:

   Use ``<autopick/>`` in the ``<recipe/>`` section of the job XML, with a
   sequence of ``<pool/>`` elements::

       <autopick>
           <pool>somepool</pool>
           <pool>anotherpool</pool>
       </autopick>

   There is an implied "other systems" at the end, which covers all other
   systems which the user has access to (use ``<hostRequires/>`` to limit
   a job to specific system pools).

   When ``random="true"`` is set on the autopick element, the pool order
   in the XML is still used, but the specific system used is selected
   randomly from within each pool (or the implied "other systems" after
   the list of specific pools is exhausted). To select randomly from
   multiple pools without expressing a preference between them, use
   an empty ``<autopick  random="true" />`` element and several
   ``<pool/>`` selection elements grouped under a ``<or/>`` element
   in the ``<hostRequires/>`` section of the job XML.


Upgrading existing Beaker installations
---------------------------------------

All existing systems in the "shared with no groups" configuration will be
updated to be part of the shared pool.

TBD:

* Migrating systems with Groups defined with non-admin access
* Migrating systems with Groups defined with admin access

Handling this migration effectively may require bringing elements of
:ref:`proposal-implicit-system-pools` forward to the target release for
this proposal.


Deferred features
-----------------

This proposal creates the infrastructure for managing pools of systems.
There is a separate proposal covering how this infrastructure may
be integrated more seamlessly into the user groups model:
:ref:`proposal-implicit-system-pools`.

The following additional features are under consideration, but have been
deliberately omitted in order to reduce the complexity of the initial
iteration of the design:

* Adding other pools as members of a pool. The initial iteration
  does not allow pools to be members of other pools, which introduces
  potential concerns about scalability in large organisations.

  Adding this feature may also make it possible to effectively delegate
  the ability to add systems to other pools.

  See the deferred subgroups feature in :ref:`proposal-enhanced-user-groups`
  for a possible implementation strategy that could also be used for
  system subpools. However, there are additional complexities relating to
  a subpools design, as there will need to be a defined mechanism to resolve
  conflicts between pool policies.

* Pool deletion. The initial iteration does not allow pools to be deleted,
  or even hidden. This feature may actually be needed to make various other
  parts of the UI usable, in which case it will be designed and implemented
  for the target release (and the design proposal updated accordingly).

* Allowing users to specify a default pool preference to be used when there
  is no ``autopick`` section in the submitted recipe XML.
