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


Design Proposals and Deferred Features
--------------------------------------

Each release in the 1.x series (along with any further releases in the
0.x series) will nominate a single design proposal as the release focus.
That design proposal will then describe the primary user facing change
to be included in that release.

Each such design proposal will include a "Deferred Features" section,
for components which are deliberately *not* being implemented until after
we have received feedback from users on the initial approach.

The planned cadence is for a new release to happen every 4-6 weeks. At any
given point in time, a definite focus will only be chosen for the next
release.

While a tentative focus will also be identified for subsequent releases,
it is strictly provisional, as user feedback may lead to deferred features
from earlier design proposals being given precedence, and detailed design
on the tentative features may identify a need to break them down into
smaller features implemented across multiple releases.

As there are limits to the number of developers that can effectively work
on implementing a single design proposal, the release focus is not the
*sole* change that will be made in a given release - it is merely the one
that is expected to require the most active engagement from Beaker users
in order to come up with a good design. The need for active user
engagement is also the reason for restricting each release to one major
design update - collecting and incorporating feedback takes time, and
trying to have too many such discussions at once will not lead to good
solutions.

At the very least, bug fixes and other minor enhancements will be
included in each release as needed and as time allows. Quality
improvements, external collaboration and preparatory work for subsequent
major features may also lead to the inclusion of other more significant
changes that are not directly related to the release focus.


Beaker 0.12
-----------

Release date: 5th April, 2013

Beaker 0.12 lays the foundation for the Beaker 1.0 series by making
it easier for users to switch between production and development
Beaker instances. It has three key elements:

* A new script is added to the Beaker server tools, which allows a
  system administrator to update the task library from the task
  library of another Beaker instance
* The Beaker client gains a new ``--hub`` parameter which makes it easy
  to run a command against a Beaker instance other than the one in
  the system or user configuration file.
* The Beaker client configuration architecture is adjusted to make it
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

Release for testing: 30th July, 2013
Planned release date: early August 2013

The focus of Beaker 0.14 development was the completion of
:ref:`proposal-enhanced-user-groups`, by allowing users to nominate
"submission delegates" that can submit jobs on their behalf.

See the `Beaker 0.14 Release Notes
<../../docs-release-0.14/whats-new/#beaker-0-14>`__ for details.


Beaker 0.15
-----------

Planned release date: mid September 2013

The focus of Beaker 0.15 will be a revised access policy model that makes
it easier to configure consistent access rules for large numbers of
systems.

Just as the enhanced user group model allowed groups to assume shared
management of jobs, the new access policy model will allow groups to
assume shared management of systems.


Beaker 0.16 (tentative)
-----------------------

The tentative focus for Beaker 0.16 is the scheduling related aspects of
:ref:`proposal-system-pools`.

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
