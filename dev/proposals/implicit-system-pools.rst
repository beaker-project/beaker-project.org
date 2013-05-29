.. _proposal-implicit-system-pools:

Implicit System Pools for User Groups
=====================================

:Author: Nick Coghlan
:Status: Proposed
:Target Release: Beaker 1.1 (tentative)


Abstract
--------

This proposal covers the automatic creation of system
pools that correspond to particular user groups. These pools allow
the system pool infrastructure to interoperate more seamlessly with the
previous group based access model for systems, while still gaining
the added flexibility and improved separation of concerns provided by
the underlying explicit system pool model.

Note: details of this design are subject to change based on feedback
received regarding the initial iteration of the system pools design.

Dependencies
------------

This proposal depends on:

* :ref:`proposal-system-pools`

Proposal
--------

Every user group in Beaker will have an associated system pool created
automatically. These associations will be recorded explicitly in the
database, but will also be visible in the naming scheme for these pools:
``implicit-pool-for-group-<groupname>``.

These implicitly created pools grant all privileges to the associated group.
Group owners are free to modify the pool policy after creation, as with
any system pool.


Miscellaneous UI concepts
~~~~~~~~~~~~~~~~~~~~~~~~~

* Implicit group pools do not appear in the regular system pool list by
  default (this may be changed through filtering options).

* Details of the group's pool are accessible through the group details
  screen.

* In addition to an Owner, systems may also be assigned to a Group. This will
  add the system to the group's implicitly associated pool.

* Limiting recipes to systems in a group's pool.

  Through the job XML:

    Use  ``<group op="=" value="somegroup" />`` in the
    ``<hostRequires/>`` of your job XML.

  Through the ``bkr`` cli:

    Pass ``--hostrequire=group=somegroup`` to a workflow command.

* Referencing a group pool when using ``<autopick/>``.

  Use ``<group/>`` elements in ``<autopick/>`` in the ``<recipe/>``
  section of the job XML, in addition to or instead of ``<pool/>``
  elements::

      <autopick>
          <group>somegroup</group>
          <pool>somepool</pool>
          <group>anothergroup</group>
      </autopick>

