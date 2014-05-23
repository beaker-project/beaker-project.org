.. _proposal-time-limited-system-loans:

Time Limited System Loans
=========================

:Author: Nick Coghlan
:Status: Deferred
:Target Release: TBD


Abstract
--------

Prompt return of system loans is currently entirely dependent on the
user with the loan remembering to return the system, or another user with
sufficient permissions on the system returning it on their behalf.

A time limiting mechanism is proposed for system loans, that automatically
returns the loan when the nominated duration expires. Unlike time limited
manual reservations (:ref:`proposal-time-limited-manual-reservations`),
users would not be able to extend their loans without appropriate permissions
on the system (either ``loan_self`` to extend only their own loans, or
``loan_any`` to extend anyone's loaning, including their own).

To avoid surprising users when their loans are returned automatically, the
"alert email" mechanism described in
:ref:`proposal-time-limited-manual-reservations` would be updated to include
notifications of expiring loans.


Proposal deferral
-----------------

Further work on this proposal is currently deferred, as the remote API
improvements in Beaker 0.15 now allow greater control of Beaker systems
from external services, and the ability to force recipe execution on
Manual systems in Beaker 0.17 will further enhance that capability.

This proposal needs to be reassessed after further experience has been gained
with the impact of those changes.


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

If a system loan has an expiry time configured, then all reservations
(whether manually or through the scheduler) made by that user are
automatically time limited, defaulting to the loan expiry time or the
normal default reservation time, whichever is earlier.
Attempts to extend the deadline of a system reservation beyond the end of
the loan period will fail.

The Beaker scheduling daemon will periodically check for expired loans
and automatically return them. For reserved systems where the reservation
is from a user that is no longer permitted to access the system once the
loan has been returned, it will also return the reservation or cancel the
recipe as appropriate.

(See also: :issue:`651479`)


Beaker usage report emails
--------------------------

The usage alert email mechanism described in
:ref:`proposal-time-limited-manual-reservations` will be updated to include
a new alert condition and section in the alert email:

* Expiring Loans

  * they have a time limited loan that will expire within 25 hours

The given limit would be a server configuration options, with this value as
the default.


User interface proposals
------------------------

Web UI
~~~~~~

TBD

Command line
~~~~~~~~~~~~

TBD

References
----------

* `Discussion thread for first draft of this proposal
  <https://lists.fedorahosted.org/pipermail/beaker-devel/2013-September/000771.html>`__
