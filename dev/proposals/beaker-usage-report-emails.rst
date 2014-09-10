.. _proposal-beaker-usage-report-emails:

Beaker Usage Report Emails
==========================

:Author: Nick Coghlan, Matt Jia
:Status: Implemented
:Release: `0.18 <https://beaker-project.org/docs/whats-new/release-0.18.html#usage-reminder-emails>`__


Abstract
--------

Currently, the Beaker usage reminder system sends users a separate email
for every system they have reserved. This can get very spammy
for heavy users, and may make instance admins reluctant to
enable the feature.

This proposal redesigns the current Beaker usage reminder system, allowing
it to be user based.

(See also: :issue:`994325`)


Beaker usage report emails
--------------------------

The existing usage alert email mechanism will be redesigned to send at
most one email per user, per day. An alert email will be the sent to users
under the following conditions:

* Expiring Reservations

  * they have a recipe running /distribution/reservesys or in "Reserved"
    status and the associated watchdog timer will expire within 24 hours.

* Reservations for In Demand Systems

  * they have had a system reserved for at least 3 days, at least 1 recipe
    is waiting for that system.

* Delayed Jobs

  * they have a job which is more than 14 days old but still contains Queued
    recipes

The given limits would all be server configuration options, with these
values as the defaults.

As long as a user triggers one of the alerts, then once a day they would get
an email with the subject line::

    [Beaker] Usage report for <name> (<date>)

The usage report would contain up to three sections, corresponding to the
different alert conditions:

* Expiring Reservations
* Open Loans & Reservations for In Demand Systems
* Delayed Jobs

For expiring reservations, the time of expiration would be given along with
the FQDN of the system.

For in demand systems, the duration of the current loan or reservation would
be given, the number of recipes currently waiting, and then the FQDN of the
system. Loans and reservations will be shown separately.

For purposes of the usage report, waiting recipes would be those that:

* are at least 1 hour old (filtering out transient noise due to new jobs being
  processed and scheduled)
* would be able to run on this system if it was in Automated mode and neither
  loaned to this user nor reserved by them.

For delayed jobs, the time since the job was submitted would be given, along
with a link to the job details page.

An example report would look like this::

    =========
    [Beaker] Usage report for <name> (<date>)
    =========
    Hi <name>,

    Your reservations of the following systems in <Beaker instance FQDN> are
    going to expire within 24 hours. If you wish to ensure you retain the
    contents of these systems, please extend your reservation.

    Expiry Date                   FQDN
    2014-05-15 05:18:01 +10:00    host.beakerlab.example.com

    The following systems have been allocated to you in <Beaker instance FQDN>
    for more than <X> days and have other recipes queued for execution.Please
    return them if you are no longer using them.

    Duration    Waiting     FQDN
    7 days      1 recipe    host2.beakerlab.example.com

    The following jobs you submitted to <Beaker instance FQDN> have been queued
    for more than <X> days. Please cancel them if they are no longer relevant,
    or perhaps arrange a loan of an appropriate system or systems

    Start time                   Delayed Job
    2014-05-15 05:18:01 +10:00   https://<Beaker instance FQDN>/jobs/4594

    =========

Deferred features
-----------------

* The usage e-mail covers outstanding reservations, but it does not currently
  include information about outstanding loans. This is because Beaker does not 
  track the start date of loans apart from in the system history, which cannot 
  be efficiently queried for generating the usage e-mail. 

* In future, when Beaker supports loan expiry, the usage e-mails could be
  updated to include loans expiring soon (in addition to reservations expiring 
  soon).

* In future, it would be possible to build a dashboard page that displays users' systems
  and jobs. Then we can use it in the email template to give users an overview of their
  Beaker usage.
