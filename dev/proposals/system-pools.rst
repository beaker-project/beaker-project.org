.. _proposal-system-pools:

System Pools
============

:Author: Dan Callaghan, Nick Coghlan
:Status: Proposed
:Target Release: 0.16 (tentative)


Abstract
--------

This proposal adds the ability to mark systems as members of various
system pools. Job submitters can then express preferences and requirements for 
system pools in their jobs.


Proposal
--------

A "pool" is a named collection of systems.

Each pool has an "owning group". Users in the owning group are allowed to add 
and remove systems from the pool.

Job submitters may influence the system selection through the job XML.


Proposed user interface
-----------------------

Defining ad hoc system pools
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* As a Beaker user, I want to define a new pool of systems.

Through the web UI:

   Select "Systems -> Pools" from the menu, then click "Create". Enter the
   pool name, and select a group to own the pool.

Through the ``bkr`` cli::

   bkr pool-create --owner-group=<groupname> <poolname>

A new pool is created containing no systems.


Controlling system pool membership
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* As a pool owner, I want to add a system to my pool.

Through the web UI:

   On the system page, click the "Pools" tab. Enter the name of the pool and 
   click "Add".

Through the ``bkr`` cli::

    bkr pool-add --pool=<poolname> --system=<fqdn>

* As a pool owner, I want to remove a system from my pool.

Through the web UI:

   On the system page, click the "Pools" tab. Click "Remove" next to your pool.

Through the ``bkr`` cli::

    bkr pool-remove --pool=<poolname> --system=<fqdn>


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


Deferred features
-----------------

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
  system subpools.

* Pool deletion. The initial iteration does not allow pools to be deleted,
  or even hidden. This feature may actually be needed to make various other
  parts of the UI usable, in which case it will be designed and implemented
  for the target release (and the design proposal updated accordingly).

* Allowing users to specify a default pool preference to be used when there
  is no ``autopick`` section in the submitted recipe XML.
