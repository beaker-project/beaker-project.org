.. _proposal-event-driven-scheduling:

Event Driven Scheduling
=======================

:Author: Nick Coghlan
:Status: Proposed
:Target Release: 0.16 (tentative)


Abstract
--------

The current Beaker scheduler operates on a batch processing model, repeatedly
looping over the full set of submitted recipes, advancing them through the
possible states in groups. That is, it looks for recipes to move from
``new`` to ``processed``, then again for recipes to move from ``processed``
to ``queued``, and so on.

This approach leads to a number of unfortunate race conditions, including
the possibility of recipes "jumping the queue" to access a rare system
if that system becomes available while the scheduler is midway through a
pass over the currently queued recipes. More seriously, it causes problems
when scheduling multi-host recipesets that can only run on a limited number
of systems: if two recipesets need systems A and B, and one gets system A,
while the other gets system B, then the two recipesets will effectively
deadlock, both waiting for each other in a classic ABBA race condition.

This proposal describes a new, more event driven, scheduler design
which avoids these race conditions, as well as enabling other features
that cannot be supported with the current scheduler.

This proposal also covers a plan to better separate out time spent
provisioning systems from the time spent executing user submitted tasks.
(that part can, and probably will, be separated out and implemented before
the rest of the probosal)


Dependencies
------------

None.


Proposal
--------

The specific proposal is that scheduling events will now occur in two
distinct ways:

1. "New job" scheduling events will occur when a new job is submitted to
   Beaker and Beaker attempts to assign the recipes within the job to
   currently idle systems.
2. "Pending system" scheduling events will occur when a system is about
   to be marked as idle and Beaker first scans the recipe queue for a
   suitable recipe to schedule on that system.

The existing scheduling loop will be retained for its secondary role in
monitoring database consistency and correcting any discrepancies (for
example, by aborting recipes where the requested distro tree has been
removed from all registered lab controllers).

This proposal does not depend on the introduction of any new asynchronous
messaging infrastructure. Instead the current scheduling loop will be
supplemented by two additional loops, one looking for new jobs and the
other for pending systems.

This approach has the advantage of not requiring any special processing
at system startup to deal with unprocessed events left over from the
previous shutdown. However, the design also supports moving away from a
polling model if an asynchronous messaging system is adopted for internal
communication between Beaker components (specifically the web UI/service
and the background scheduling daemon) in the future.


Viable systems, idle systems and pending systems
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For the purposes of this proposal, the phrase "viable system" refers to
a system that is configured for automated use and meets the requirements
needed to run a given recipe. The full set of viable systems for a recipe
may include systems that are already allocated to another recipe, as well
as a VM dynamically allocated through the oVirt Engine integration.

The phrase "idle system" refers to a system that is configured for automated
use and is currently in the pool of systems available to handle new jobs.
Systems currently running a recipe are never considered idle.

The phrase "idle pool" refers to all currently idle systems. It also refers
to successful dynamic allocation of a VM through the oVirt Engine
integration.

The phrase "pending system" refers to a system that is configured for
automation, but is currently neither running a recipe nor part of the idle
pool. This may be because the system has just finished running a recipe,
or because it has just been configured for automated operation.


"New Job" processing
~~~~~~~~~~~~~~~~~~~~

The current recipe state machine includes the states::

    new
    processed
    queued
    scheduled
    waiting
    running
    completed

    cancelled
    aborted

With the current scheduler, all successfully completed recipes pass through
the full sequence of states from ``new`` to ``completed``. A recipe may jump
from any state other than ``completed`` directly to ``cancelled`` or
``aborted``.

Under this proposal, the following changes occur:

* The ``processed`` state is removed (along with the associated behaviour
  of caching an initial search for viable systems).
* A new state ``assigned`` is added to indicate when a recipe has been
  assigned to a particular lab controller, but not yet scheduled on a
  specific system. (alternative: reuse the existing 'processed' state
  for this purpose instead of deleting and adding a new state?).

When handling a "New job" scheduling event:

* recipe sets within the job will be processed in arbitrary order
* recipes within a recipe set will be processed in arbitrary order
  (alternative: process recipes in order from fewest viable systems
  to most viable systems?)
* all recipes in one recipe set will be processed before processing
  the next recipe set
* a recipe will be moved directly from ``new`` to ``scheduled`` if a
  viable system is found in the idle pool. In this case, all other
  recipes in the same recipe set as the scheduled recipe will be
  moved to ``assigned``.
* recipes in ``assigned`` will be moved to ``scheduled`` if a
  suitable idle system controlled by the appropriate lab
  controller is found.
* if no recipes in a recipe set are scheduled, then every recipe in the
  recipe set will be moved to ``queued``.

While this proposal does *not* make any changes to the way a specific
system is chosen from the idle pool when multiple viable systems are
available, it does lay the groundwork for such changes in the future by
cleanly separating the "New Job" processing (where job and job owner
preferences will guide the selection) from the "Pending System"
processing (where system preferences will guide the selection).

.. _proposal-pending-systems-processing:

"Pending System" processing
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Part of this proposal is to add an explicit state machine for current
system usage, rather than continuing to rely on the implicit state machine
derived from other attributes.

The proposed set of states for the new usage state machine are as follows::

    idle
    scheduled
    waiting
    installing
    running
    pending

When the system condition is Broken, systems will always be ``idle``.

When the system condition is Manual, systems will be ``running`` when
reserved by a user, ``waiting`` and then ``installing`` when being
provisioned in response to a reservation request, but otherwise ``idle``.

When the system condition is Automated, systems will be:

* ``running`` when the associated recipe is ``running``
* ``installing`` when the associated recipe is ``installing``
* ``waiting`` when the associated recipe is ``waiting``
* ``scheduled`` when the associated recipe is ``scheduled``
* ``pending`` when a determination is needed as to whether the system
  should start running a queued recipe or be marked as ``idle``
* ``idle`` in any other case

The rationale for the duplication of states been systems and recipes is
easier tracking of both system-oriented and recipe-oriented metrics. See
:ref:`system-usage-monitoring` below.

Systems will be marked as ``pending`` (triggering a "Pending system"
scheduling event) in the following cases:

* A new system is added with its condition set to Automated
* The condition of an existing system is changed to Automated
* A system with its condition set to Automated finishes execution of a
  recipe (either because the final task completed successfully, or because
  the recipe was cancelled or aborted)

When handling a "Pending system" scheduling event

* the currently ``assigned`` recipes for the system's lab controller are
  searched for a suitable recipe. If one is found, both the system and the
  recipe will be moved to ``scheduled``.
* if the system remains ``pending``, all currently ``queued`` recipes are
  searched for a suitable recipe. If one is found, both the system and the
  recipe will be moved to ``scheduled``. All other recipes in the same
  recipe set will be moved to ``assigned``.
* if the system still remains ``pending``, it will be moved to ``idle``.

In this initial proposal, the ``assigned`` and ``queued`` recipes are still
sorted solely by overall job priority when looking for a suitable recipe.
While this is valuable in its own right (it eliminates a number of race
conditions and queue jumping that is possible in the current design), it
also creates a foundation for more sophisticated control over the system
preferences for execution of recipes (for example, see
:ref:`proposal-effective-job-priorities`).


Recipe set execution
~~~~~~~~~~~~~~~~~~~~

Regardless of the scheduling event that triggers it:

* Whenever a recipe is moved to ``scheduled``, if all other recipes in
  that recipe set are also ``scheduled``, then provisioning of the
  allocated systems and execution of tasks in those recipes will begin.

* As with the current scheduler, the bootloader configuration for guest
  recipes will be set up on the TFTP server at the same time as the
  configuration for the host recipe.

* When running a recipe, a new transient state ``installing`` (between
  ``waiting`` and ``running``) will be used to explicitly track the time
  spent at the start of the recipe provisioning the system for use.

* Whenever a recipe is moved to ``scheduled``, the associated system is
  also moved to ``scheduled``. As the recipe moves through ``waiting``,
  ``installing`` and ``running``, the associated system is moved through
  those same states.


.. _system-usage-monitoring:

System usage monitoring
~~~~~~~~~~~~~~~~~~~~~~~

To provide detailed metrics on individual systems, the current "System
Status Duration" table will be supplemented by a "System Usage" table.

Where the current table only tracks the overall condition of the system
(Broken, Manual, Automated), the new table will also track the usage within
each of those states by adding a new entry whenever the system usage or
the nominal condition change.
