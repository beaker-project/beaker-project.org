.. _proposal-time-limited-manual-reservations:

Time Limited Manual Reservations
================================

:Author: Nick Coghlan
:Status: Proposed
:Target Release: TBD


Abstract
--------

This proposal redesigns the current external watchdog mechanism, allowing
it to be used even for systems that are not currently running a recipe. This
new reservation timer is then used to offer time limited manual reservations.

To assist with voluntarily returning system loans, it is also proposed that
the ability be added to indicate when reserving a system manually that the
loan should also be returned when the reservation is returned.


Recipe independent watchdog timers
----------------------------------

A new "expiry_time" attribute will be added to reservation records.

The existing "kill_time" attribute on external watchdog records will be
replaced with a reference to the appropriate reservation.

For reservations made through the job scheduler, very little will change.
Wherever the kill time for the watchdog would previously have been set or
modified, the expiry time on the reservation will be updated instead. The
details of the currently running task and subtask will still be recorded
on the watchdog and the ``beaker-watchdog`` daemon on the lab controller
will still be responsible for monitoring for an expired watchdog and
aborting the recipe as appropriate.

For reservations made directly through the web UI, the web UI will be updated
to allow specification of a duration when taking the system. The default will
continue to be no time limit, but if a time limit is requested, then the
default will be 24 hours (configurable as a global Beaker server setting).
If a time limit is requested, then the reservation expiry date will be set
appropriately.

While a reservation is active, the reserving user may extend it through the
web UI or the ``bkr`` CLI, as well as using the ``extendtesttime.sh`` script
on the reserved system (if that script is installed, as it is by the
``/distribution/reservesys`` task).

The reserving user may also return the system early, either by cancelling the
job (for an automatic reservation), or explicitly (for a manual reservation).
The ``return2beaker.sh`` script can also be called from the reserved system
(if that script is installed, as it is by the ``/distribution/reservesys``
task).

While the ``beaker-watchdog`` daemons on the individual lab controllers will
continue to handle reservation expiry for systems executing recipes, the
Beaker scheduling daemon will periodically check for expired manual
reservations and automatically return them.


Automatically returning loans
-----------------------------

When reserving a system, a user will be able to choose to automatically
return a loan. If this option is specified, then when the reservation is
returned, the active system loan will also be returned.

As long as the reservation remains in effect, the user with the loan and
linked reservation will be able to edit this setting.

This will be stored as a new ``return_loan`` attribute on each reservation.

(also see :issue:`651477`)


User interface proposals
------------------------

Web UI
~~~~~~

TBD

Command line
~~~~~~~~~~~~

TBD


Deferred features
-----------------

* Allowing use of a new ``reservesys`` element in recipe definitions as a
  harness independent mechanism allowing reservation of the task at the end
  of the recipe. Unlike the existing harness dependent mechanism, this
  automatic reservation mechanism would allow systems to be reserved even
  if the recipe aborts (:issue:`639938`).

* Allowing the ``reservesys`` element to be specified at the recipe set level
  to reserve all systems in the recipe set whenever one or more of them
  encounters a problem.

* Updating the reserve workflow and the scheduled provisioning mechanism for
  systems in Automated mode to use the new harness independent mechanism
  rather than the reservesys task.

* Providing a page in the web UI that includes the information provided in
  the Beaker usage email.


Rejected features
-----------------

* Moving responsibility for watchdog expiry from the lab controller to the
  main server even for systems in Automated mode (as doing so would break
  the existing ability to execute watchdog script on the lab controller)

* Removing the watchdog table (as doing so would require more invasive
  changes that aren't needed to achieve the aims of this proposal)

* Allowing the now deferred ``reservesys`` element to be specified at the job
  level, since it isn't clear how that would work when recipe sets are run at
  different times.

* Having "onpass" default to false in the now deferred ``reservesys element``.
  While this is desirable in some respects, having different defaults for one
  of the items is difficult to document clearly.


References
----------

* `Discussion thread for first draft of this proposal
  <https://lists.fedorahosted.org/pipermail/beaker-devel/2013-September/000771.html>`__
