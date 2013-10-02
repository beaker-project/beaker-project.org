.. _proposal-improved-reservations-and-loans:

Improved System Reservations and Loans
======================================

:Author: Nick Coghlan
:Status: Proposed
:Target Release: 0.16


Abstract
--------

This proposal redesigns the current external watchdog mechanism, allowing
it to be used even for systems that are not currently running a recipe. This
new reservation timer is then used to offer time limited manual reservations.

A similar time limiting mechanism is proposed for system loans, as well as
the ability to indicate when reserving a system in Manual mode that the
loan should be returned automatically when the reservation is returned.

To avoid surprising users when their loans and reservations are returned
automatically, the existing "alert email" mechanism will be redesigned to
focus on informing users of such upcoming events, as well as improving the
handling of existing alerts.

Finally, a command line interface will be provided for system loan
management.


Recipe independent watchdog timers
----------------------------------

A new "expiry_time" attribute will be added to reservation records.

The existing "kill_time" attribute on external watchdog records will be
replaced with a reference to the appropriate reservation.

For systems in Automated mode, very little will change. Wherever the kill
time for the watchdog would previously have been set or modified, the
expiry time on the reservation will be updated instead. The details of the
currently running task and subtask will still be recorded on the watchdog
and the ``beaker-watchdog`` daemon on the lab controller will still be
responsible for monitoring for an expired watchdog and aborting the recipe
as appropriate.

For systems in Manual mode, the web UI will be updated to allow specification
of a duration when taking the system. The default will continue to be no
time limit, but if a time limit is requested, then the default will be
24 hours (configurable as a global Beaker server setting). If a time limit
is requested, then the reservation expiry date will be set appropriately.

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

This will be stored as a new ``return_loan`` attribute on each reservation.

(also see :issue:`651477`)


Time limited loans
------------------

System loans will be separated out to be tracked explicitly (similar to
the handling of reservations, only without the "type" field). When loaning
the system, the user granting the loan will be able to specify a duration
of the loan, which will be recorded as a loan expiry time. The default will
continue to be no time limit, but if a time limit is requested, then the
default will be 7 days (configurable as a global Beaker server setting).

While a loan is active, it may be extended. However, the user extending the
loan must have ``loan-self`` (for their own loans) or ``loan-any`` (for other
users' loans) permissions on the system. This means that system loans can
be used to impose hard deadlines on reservations, as a user that is granted
a time limited loan but does not possess the ``reserve``, ``loan-self`` or
``loan-any`` on the system can only receive more time by requesting it
from a user with ``loan-any`` permissions on that system.

If a system loan has an expiry time configured, then all reservations made
by that user are automatically time limited, defaulting to the loan expiry
time or the normal default reservation time, whichever is earlier.
Attempts to extend a reservation beyond the end of the loan period will
fail.

The Beaker scheduling daemon will periodically check for expired loans
and automatically return them. For reserved systems where the reservation
is from a user that is no longer permitted to access the system once the
loan has been returned, it will also return the reservation or cancel the
recipe as appropriate.

(See also: :issue:`651479`)


Beaker usage report emails
--------------------------

The existing usage alert email mechanism will be redesigned to send at
most one email per user, per day. An alert email will be the sent to users
under the following conditions:

* they have a time limited manual reservation that will expire within 25 hours
* they have a time limited loan that will expire within 25 hours
* they have had a system reserved for at least 3 days, at least 1 recipe
  is waiting for that system and the reservation has no expiry time set
* they have had a system on loan for at least 3 days and at least 1 recipe
  is waiting for that system and the loan has no expiry time set
* they have a job which is more than 14 days old but still contains Queued
  recipes

The given limits would all be server configuration options, with these
values as the defaults.

As long as a user triggers one of the alerts, then once a day they would get
an email with the subject line::

    [Beaker] Usage report for <name> (<date>)

The usage report would contain up to three sections, corresponding to the
different alert conditions:

* Expiring Loans & Reservations
* Open Loans & Reservations for In Demand Systems
* Delayed Jobs

For expiring loans & reservations, the time of expiration would be given
along with the FQDN of the system. Loans and reservations will be shown
separately, unless the reservation is set to automatically return the loan
(in which case only the reservation is shown).

For in demand systems, the duration of the current loan or reservation would
be given, the number of recipes currently waiting, and then the FQDN of the
system. Loans and reservations will be shown separately, unless the
reservation is set to automatically return the loan (in which case only
the reservation is shown).

For purposes of the usage report, waiting recipes would be those that:

* are at least 1 hour old (filtering out transient noise due to new jobs being
  processed and scheduled)
* would be able to run on this system if it was in Automated mode and neither
  loaned to this user nor reserved by them

For delayed jobs, the time since the job was submitted would be given, along
with a link to the job details page.

(See also: :issue:`994325`)


User interface proposals
------------------------

Web UI
~~~~~~

TBD

Command line
~~~~~~~~~~~~

TBD

:issue:`734212` (CLI for system loans)


Deferred features
-----------------

* Updating the scheduled provisioning mechanism for systems in Automated
  mode to use the new harness independent mechanism rather than the
  reservesys task

* Allowing use of a new ``reservesys`` element in recipe definitions as a
  harness independent mechanism allowing reservation of the task at the end
  of the recipe. Unlike the existing harness dependent mechanism, this
  automatic reservation mechanism would allow systems to be reserved even
  if the recipe aborts (:issue:`639938`).

* Allowing the ``reservesys`` element to be specified at the recipe set level
  to reserve all systems in the recipe set whenever one or more of them
  encounters a problem.


Rejected features
-----------------

* Moving responsibility for watchdog expiry from the lab controller to the
  main server even for systems in Automated mode (as doing so would break
  the existing ability to execute watchdog script on the lab controller)

* Removing the watchdog table (as doing so would require more invasive
  changes that aren't needed to achieve the aims of this proposal)

* Allowing the ``reservesys`` element to be specified at the job level,
  since it isn't clear how that would work when recipe sets are run at
  different times.

* Having "onpass" default to false in the reservesys element. While this is
  desirable in some respects, having different defaults for one of the
  items is difficult to document clearly.


References
----------

* `Discussion thread for first draft of this proposal
  <https://lists.fedorahosted.org/pipermail/beaker-devel/2013-September/000771.html>`__
