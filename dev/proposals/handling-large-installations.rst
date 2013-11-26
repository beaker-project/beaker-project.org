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

This is a living document that will be updated over the course of the
1.x series.

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
has an extended maintenance life cycle (through to January 2014).


Beaker 0.16
-----------

Planned release date: mid-to-late January 2014

The focus of Beaker 0.16 will be to implement
:ref:`proposal-time-limited-manual-reservations`, as well as to make
further improvements to the reliability of system provisioning.

The aim of these updates will be to improve the availablity of resources
and to minimise spurious test failures due to issues with system provisioning.


Beaker 0.17 (tentative)
-----------------------

Planned release date: late February/early March 2014

The tentative focus of Beaker 0.17 is to implement
:ref:`proposal-time-limited-system-loans`.

The aim of these updates will be to improve the availablity of resources
and reduce the overhead associated with system loan management.

With the planned inclusion of a command line interface for loan management
in one of the Beaker 0.15 maintenance releases, it is quite possible this
proposal may be postponed to a later release.


Beaker 0.18 (tentative)
-----------------------

The tentative focus of Beaker 0.18 will be completion of the "Predefined
Access Policies" portion of :ref:`proposal-access-policies`.

While the initial release of "System Access Policies" allows shared
management of systems and automation of policy updates, the Predefined
Access Policy mechanism will make it straightforward to apply a common
policy systematically to collections of systems.


Beaker 0.19 (tentative)
-----------------------

The tentative focus for Beaker 0.19 is :ref:`proposal-system-pools`.

This release should also cover the migration to
:ref:`proposal-event-driven-scheduling` (as the proposed approach to
expressing pool preferences doesn't really make sense with the
current scheduling model).


Beaker 1.0 (tentative)
----------------------

The tentative focus of Beaker 1.0 is :ref:`proposal-effective-job-priorities`

The key element of this proposal is the ability for system owners to control
the effective precedence of recipes handled by their systems (including
prioritising their own jobs, or those of their team, over jobs submitted
by other users).


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

Earlier releases in the 1.x series will include changes and additional
tools to make running multiple Beaker instances less painful, as such tools
are useful regardless of the reasons for additional instances.
