.. _proposal-handling-large-installations:

Improved Handling of Large Beaker Installations
===============================================

:Author: Nick Coghlan
:Status: In Progress
:Release Series: 0.x, 1.x


Abstract
--------

Beaker currently uses a very simple trust model, where systems are
either "shared" (no group restrictions on use) or "private" (only
members of specified groups are able to access the system for any
purpose). Furthermore, making changes to group membership requires
action by the administrators of the Beaker installation.

The general theme of the Beaker 1.x series, and the remainder of the 0.x
series, will be to make a progressive set of smaller changes, each useful in
its own right, that combine in later releases to offer a rich policy
administration capability that allows
system owners to prioritise access to their own hardware.

The intent is that, by the time of the final 1.x series release, owners
of systems in Beaker should be comfortable making their systems available
for use by other users of the same Beaker installation, while being
confident that they remain in full control of the usage policies for those
systems, including whether or not other users are even aware of the
system's presence.

This is a living document that will be updated over the course of the 0.x
and 1.x series.

Refer to :ref:`dev-lifecycle` for more information on the Beaker development
process.


Beaker 0.12
-----------

Release date: 5th April, 2013

Beaker 0.12 laid the foundation for the Beaker 1.0 series by making
it easier for users to switch between production and development
Beaker instances. It has three key elements:

* A new script was added to the Beaker server tools, which allows a
  system administrator to update the task library from the task
  library of another Beaker instance
* The Beaker client gained a new ``--hub`` parameter which makes it easy
  to run a command against a Beaker instance other than the one in
  the system or user configuration file.
* The Beaker client configuration architecture was adjusted to make it
  easy to provide a system wide site specific configuration file, rather
  than requiring each user to define their own configuration

See the `Beaker 0.12 Release Notes <../../docs/whats-new/#beaker-0-12>`__ for
details.


Beaker 0.13
-----------

Release date: 7th June, 2013

The focus of Beaker 0.13 was :ref:`proposal-enhanced-user-groups`

The elements of the proposal implemented in this release included three key
elements:

* Administrators may delegate membership of specific groups to an
  LDAP server (to avoid maintaining membership data in two locations)
* Users may create and manage their own custom groups (to avoid overloading
  the administrators of large installations)
* Jobs may be submitted on behalf of a group, granting all members of that
  group full access to the job (to avoid the creation of shared accounts
  for collective management of jobs)

See the `Beaker 0.13 Release Notes <../../docs/whats-new/#beaker-0-13>`__ for
details.


Beaker 0.14
-----------

Release date: 2nd August, 2013

The focus of Beaker 0.14 development was the completion of
:ref:`proposal-enhanced-user-groups`, by allowing users to nominate
"submission delegates" that can submit jobs on their behalf.

See the `Beaker 0.14 Release Notes
<../../docs-release-0.14/whats-new/#beaker-0-14>`__ for details.

Due to the issues with the initial Beaker 0.15 update, Beaker 0.14
received an extended maintenance life cycle (through to December 2013).


Beaker 0.15
-----------

Release date: 22 October 2013 (for 0.15.1)

The focus of Beaker 0.15 was the per-system access policy portion of
:ref:`proposal-access-policies`.

Just as the enhanced user group model allowed groups to assume shared
management of jobs, the new access policy model allows groups to
assume shared management of systems.

See the `Beaker 0.15 Release Notes
<../../docs-release-0.15/whats-new/#beaker-0-15>`__ for details.

Note that the initial release of Beaker 0.15 including a number of critical
defects in the revised permissions model and the upgraded web interface that
rendered it effectively undeployable. The release date given above is for the
0.15.1 maintenance release that addressed these critical issues.

Due to the extended maintenance lifecycle for Beaker 0.14, Beaker 0.15 also
has an extended maintenance life cycle (through to February 2014).


Beaker 0.16
-----------

Planned release date: mid-to-late March 2014

The focus of Beaker 0.16 will be the :ref:`proposal-external-tasks` design
proposal, allowing tasks to be managed as references to external git
repositories, rather than forcing reliance on Beaker's centralised library of
task RPMs.

In addition to the significant benefits this offers in task management
itself (such as more exact reproducability of previous test runs, easier
testing of experimental versions of tasks and more flexibility in test
structure), this proposal also has the benefit of avoiding the need to
frequently regenerate yum repo metadata for a central task library that may
end up containing thousands of tasks.


Beaker 0.17 (tentative)
-----------------------

Planned release date (tentative): late April/early May 2014

The tentative focus of Beaker 0.17 is to implement an improved system
details page in the Beaker web UI, as the Beaker 0.15 release not only
highlighted many of the shortcomings of the existing interface, but also
provided greatly improved tools for dealing with them.

Refer to :ref:`proposal-system-page-improvements` for details.


Beaker 1.0
----------

The following design proposals are expected to be implemented across
several additional 0.x releases in the lead up to declaring a Beaker 1.0
release:

* :ref:`proposal-dynamic-virtualization`
* :ref:`proposal-time-limited-manual-reservations`
* :ref:`proposal-time-limited-system-loans`
* the "Predefined Access Policies" portion of :ref:`proposal-access-policies`
* :ref:`proposal-event-driven-scheduling`
* :ref:`proposal-system-pools`
* :ref:`proposal-effective-job-priorities`

With all of these proposals implemented, Beaker will provide system owners
with comprehensive and flexible control over their systems, allowing them
to make them readily available to other users, while still ensuring they
can access the system when they need to (including prioritising their own
jobs, or those of their team, over jobs submitted by other users).


Beaker 1.1 (tentative)
----------------------

Currently, clean isolation of sensitive systems, tasks and job details
requires running multiple Beaker instances, which imposes a lot of
management and maintenance overhead, as well as contributing to
inefficient use of test hardware.

The tentative focus of Beaker 1.1 is to build on the existing NDA
functionality, the enhanced user groups and the new system pool model to
provide clean isolation of sensitive systems, tasks and job details. This
feature may also require the ability to bypass the public task library for
sensitive tasks, as well as the ability to specify an alternative
archive server for sensitive log files.

Earlier releases in the 0.x and 1.x series will include changes and additional
tools to make running multiple Beaker instances less painful, as such tools
are useful regardless of the reasons for additional instances.
