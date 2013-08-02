Design proposals
----------------

Beaker design proposals are used for major changes that require more upfront
discussion and design than can be suitably handled in a single Bugzilla
entry or Gerrit patch review.

Each design proposal must include a rationale for making the change, and
should provide sufficient detail of the desired solution that it can be
used to gain meaningful feedback from other developers or Beaker users.

Rather than approving designs as a whole, specific elements of the design are ultimately approved through the normal review processes in Bugzilla and
Gerrit. It is expected that some of the details in design proposals may
change as implementation reveals additional aspects that were not previously considered.

Current design proposals
~~~~~~~~~~~~~~~~~~~~~~~~

These are design proposals currently under consideration for incorporation
into a future version of Beaker.

.. Rather than assigning numbers, new design proposals should just be
   created as files in this subdir and appended to this TOC.
   Proposals will be referred to by their title or URL rather than by a
   number (this is similar to Fedora feature names)

.. toctree::
   :maxdepth: 1

   handling-large-installations
   access-policies-for-systems
   system-pools
   event-driven-scheduler
   effective-job-priorities
   reference-harness
   inventory-lshw-migration

.. note::

   Not all changes require an associated design proposal. Some changes,
   (such as those for the Beaker build process and website, or Fedora
   compatibility fixes) are handled directly in Gerrit. Most other changes
   are tracked as Bugzilla entries. A design proposal is appropriate if a
   change touches several different parts of Beaker, or if it is a
   user visible piece of functionality where the overall design should
   be discussed with Beaker users *before* significant effort is expended
   on the implementation.


Completed design proposals
~~~~~~~~~~~~~~~~~~~~~~~~~~

These are design proposals that have been incorporated into a previous
version of Beaker.

.. toctree::
   :maxdepth: 1

   harness-api
   enhanced-user-groups


Rejected/withdrawn design proposals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These are design proposals that have been determined to be outside Beaker's
scope, or are otherwise considered a poor fit for the system.

* There are currently no previously rejected/withdrawn design proposals

.. toctree::
   :maxdepth: 1
