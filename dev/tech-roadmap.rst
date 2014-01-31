.. _technical-roadmap:

Technical roadmap
=================

Beaker is a big project, with a lot of moving parts. It's been around for
quite a while, and is used in several different ways by different groups
of people.

This technical roadmap is designed to highlight areas of currently active
development, as well as more speculative changes that may happen at some
point in the future.

If any of these projects sound particularly interesting, folks are welcome to 
:doc:`get involved <guide/index>`.

.. todo::
   Some more direct BZ references probably wouldn't go astray here...

Overview
--------

The :doc:`Handling Large Installations 
<proposals/handling-large-installations>` proposal offers a general overview
of currently planned features that will be the primary focus of the 
Beaker 1.x series and the remainder of the 0.x series (there's some overlap
with the technical road map below).

See :doc:`proposals/index` for the full list of Beaker design proposals.


Objectives for Beaker 1.0
~~~~~~~~~~~~~~~~~~~~~~~~~

Our aim is for the Beaker 1.0 milestone to mark a point where we no longer
feel any need to apologise for the state of Beaker's documentation, or the
capabilities of its regression test suite. It should also be possible for
anyone considering the use of Beaker to have a clear idea of its significance
for Red Hat, without having their own workflows overly constrained by the
specific ways Red Hat chooses to use it.

The following elements have been identified as key objectives of Beaker 1.0,
and we will continue with as many regular 0.x releases as are needed to
achieve them:

* The Effective Job Priorities design proposal (and its dependencies)
* Stable alternative harness API (with autotest support) (Done!)
* Improved integration with other testing systems (xUnit/subunit support)
* Documentation improvements, including
   * an architectural guide that at least explains all of Beaker's
     external interfaces
   * an explanation of the local watchdog hooks
   * more general advice on job design (including effectively using
     features like the job matrix)
   * a public page giving at least basic info on how Beaker is used
     at Red Hat

* Red Hat workflow independence

  * Moving any remaining hardcoded Red Hat specific settings into
    configuration files
  * Full Fedora deployment compatibility (including the test suite)
  * A harness independent reservesys mechanism
  * Self tests that exercise beah, the legacy harness API and the new 
    harness API
  * Theming support in the main web UI


The status of ``beah``
~~~~~~~~~~~~~~~~~~~~~~

In many respects, ``beah``, the native Beaker test harness, duplicates aspects
of other test frameworks like `autotest <http://autotest.github.io/>`__ and
`STAF <http://staf.sourceforge.net/>`__.

Being so heavily dependent on kickstart files and the RPM based task library,
``beah`` is also quite inflexible in terms of platform support.

The following kinds of changes will be considered for ``beah``:

* documentation improvements
* compatibility updates for supported test systems
* any changes needed for image based provisioning with OpenStack
* any changes needed for IPv6 compatibility
* reliability fixes
* equivalent capabilities for additions made to the stable harness API

Outside these areas, we consider it a poor use of resources to further
duplicate the effort going into development of other automated test
harnesses (especially ``autotest``), and hence any major feature proposals for
``beah`` will likely be rejected - we would prefer for any such efforts to
be directed towards the system changes needed to better support alternative
harnesss.

To support existing Beaker users, the ``beah`` test harness will be
maintained indefinitely, and the kinds of changes noted above will continue
to be permitted. The only way ``beah`` itself would ever be phased out is if
a simpler and more robust alternative became available and was capable of
correctly executing all of the existing Beaker tests that the core Beaker
developers have access to. The :doc:`proposals/reference-harness` design
proposal is expected to lead to the eventual creation of just such a harness.


Active development
------------------

The ideas in this section are currently under active development. Patches for 
at least some of these are likely to be found on the `Beaker Gerrit server 
<http://gerrit.beaker-project.org>`_, and in the absence of unexpected 
complications, they should show up in a Beaker release within the next few 
months. Searching `Bugzilla 
<https://bugzilla.redhat.com/buglist.cgi?product=Beaker&bug_status=__open__>`_ 
for Beaker bugs with target milestones set will often provide more detail on 
the specific proposals.


Full Fedora compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~

We would like to support Fedora as a host operating system for the Beaker
server components. This work was mostly completed in Beaker 0.14 (supporting
Fedora 19+), but there are ongoing issues with upgrades of dependencies
that don't currently have solid backwards compatibility policies.

The current plan is to start running Beaker's continuous integration tests
in Fedora's `Beaker instance <http://beaker.fedoraproject.org>`__ (on Fedora),
in addition to running them on RHEL6.

We also plan to resolve the remaining packaging issues preventing inclusion
of Beaker and its dependencies directly in the main Fedora package
repositories.


Virtual-only trial environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The "Beaker-in-a-box" scripts currently require a physical machine, which
runs the main Beaker server, and then creates some KVM guests for lab
controllers and test systems.

It is more convenient for developers if the bare metal host isn't needed, and
the main server also runs inside a guest VM.

Accordingly, instructions have been added to the developer guide for an
:ref:`entirely virtual <virtual-fedora>` Fedora based local installation.
These instructions are still considered experimental until a more permanent
solution to the recurring Fedora compatibility issues is found.


Improved inventory task
~~~~~~~~~~~~~~~~~~~~~~~

The current inventory task is based on the ``smolt`` project. Replacing this
with a new version based on ``lshw`` will improve many aspects of the
system capability reporting, providing a richer set of attributes to query.

The core functionality is also being broken out as an application
(``beaker-system-scan``) that can be installed and run directly, rather
than only being usable inside a Beaker job.

This idea is covered by the :ref:`proposal-lshw-migration` design proposal.


Web UI modernisation
~~~~~~~~~~~~~~~~~~~~

The current main web UI is based on the TurboGears 1 stack (although it
uses SQLAlchemy rather than SQLObject for the database access layer). This
makes some aspects of development more awkward than they might be with a
more recent web framework.

Starting with the Beaker 0.15 release, the main web server is in the
process of being migrated to Flask, by allowing endpoints to be
implemented as either TG1 controllers or Flask handlers. We are also
aiming to replace the front end components with cleaner alternatives
based on Twitter Bootstrap.

As part of this upgrade, we also plan to allow installation-specific theming
of the main web UI. This allows Beaker installations to refer to appropriate
local resources to report issues and look up documentation, rather than
always linking directly to the site for the upstream project.


Shared access policies
~~~~~~~~~~~~~~~~~~~~~~

Beaker 0.15 implemented the first phase of the :ref:`proposal-access-policies`
design proposal, taking the previously limited permissions model for
individual systems and providing a far more fine-grained model. Remote
access through the Beaker command line client makes it possible to manage
access to large numbers of systems this way.

A future release will implement the second phase of the
:ref:`proposal-access-policies` proposal, separating out access policies as
a distinct entity in Beaker's user interface, allowing a common access policy
to be shared amongst multiple systems (system access policies are already a
distinct concept in the data model, but cannot currently be shared
across multiple systems).


Improved handling of reservations and system loans
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While systems in Beaker can currently be loaned to other users, the workflows
for doing so aren't particularly convenient. It would be helpful if
Beaker included better tools for managing System Loans, as well as a
system for automatically returning them if unused for extended periods.

This also applies to reservations, especially allowing automated
reservations without relying on the use of a particular test harness.

These ideas are covered by :ref:`proposal-time-limited-manual-reservations`
and :ref:`proposal-time-limited-system-loans`.

:issue:`734212` covers providing a command line interface to manage system
loans.


Planned development
-------------------

The ideas in this section are firmly on the to-do list, but it is not yet
clear when they will be ready for inclusion.


Explicit system pools
~~~~~~~~~~~~~~~~~~~~~

Beaker currently schedules jobs on any system the user has access to,
preferring the users own systems over group systems, over the generally
accessible system pool.

This approach isn't always desirable, since some systems have special
features that should only be used when explicitly requested, or a user may
wish to target a specific job at a particular set of machines.

Allowing systems to be grouped into pools (independent of the access policies
used to grant or deny access to the systems) will allow users to express
more abstract preferences about machines that aren't directly related to
the system itself.

This idea is covered by the :ref:`proposal-system-pools` design proposal.


Event based scheduler
~~~~~~~~~~~~~~~~~~~~~

The current scheduler has some issues and limitations that are best resolved
by switching to a more event-driven architecture. The new design will
involve attempting to assign newly submitted recipes to an idle system
without placing the recipe in the main queue, and newly available systems
to queued recipes without placing the system in the idle pool.

This idea is covered by the :doc:`proposals/event-driven-scheduler` design
proposal.


More flexible job prioritisation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Armed with the new user group and access policy models, and the new event
driven approach to scheduling, it becomes possible to offer system owners
much greater control over which recipes are selected to run on their
systems.

This idea is covered by the :doc:`proposals/effective-job-priorities` design
proposal.


Task oriented guides for users and administrators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Beaker offers a lot of power and flexibility, but that can often come at
the price of making the right way to do certain things non-obvious. Beaker's
documentation is likely to benefit from additional sections that take a
"task-based" approach to documentation and answer questions like "How do I
limit my recipe to systems with a graphics adapter?" or "How do I require
that my recipe run directly on bare metal and not in a VM?".

This will include a general "troubleshooting guide" to help users and
administrators collaborate effectively in tracking down the more obscure
failures that can occur with the kind of integration testing Beaker
supports.


Systematic self-tests for provisioning and beah
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As a tool for better validating new Beaker releases, as well as making it
easier to check for the correct operation of new Beaker installations, a
set of self-test Beaker tasks will be made readily available. These tasks
should come with helper scripts scripts for installing them into a
Beaker installation and the appropriate job definitions to execute them
across all configured architectures and distro trees.


OpenStack based provisioning
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The current oVirt Engine integration attempts to support dynamic virtual
guests, but has some unfortunate limitations. It appears that oVirt is
simply a poor fit for the task of creating "throwaway" virtual machines for
a single recipe, as it is aimed more at providing long lived high
availability systems that never go down (even when the underlying hardware
fails or is replaced).

By contrast, OpenStack has a reputation as being excellent at quickly
providing new virtual machines, without being able to provide the stability
and long term high availability of oVirt. This suggests that OpenStack will
be a substantially better fit for Beaker's dynamic provisioning use case
than oVirt.

This idea is covered by the :doc:`proposals/dynamic-virtualization` design
proposal.



Exploration
-----------

The ideas in this section are projects that one or more of the current
developers are at least tinkering with, but they may be at wildly
divergent stages of maturity.

xUnit and subunit output support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While a Jenkins plugin to trigger Beaker jobs is available, the reporting is
currently limited as Beaker doesn't provide job results in a format that
Jenkins understands.

It would be helpful if Beaker supported exporting the results of jobs in
xUnit format. The nose `xunit plugin
<http://nose.readthedocs.org/en/latest/plugins/xunit.html>`__ may be a
useful guide to this.

A potentially related change would be to support retrieval of
`subunit results <https://pypi.python.org/pypi/python-subunit>`__ for
in-progress jobs.


Reference harness implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

At present all Beaker recipes are run with the same harness, Beah. We would 
like to develop a minimal "reference harness" implementation, so that we can 
experiment with some harness features which would be disruptive or difficult to 
implement in Beah.

This idea is covered by the :doc:`proposals/reference-harness` design proposal.

Integrated live dashboard
~~~~~~~~~~~~~~~~~~~~~~~~~

While Beaker 0.11 started sending aggregate metrics for the current system
status directly to Graphite, it doesn't provide any native dashboard
capability. It's desirable to provide an improved dashboard experience,
using either Graphite's native dashboard tools, or a richer Javascript based
charting front end (such as Rickshaw).

Test suite speed improvements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Executing the local test suite is currently rather slow, as Firefox needs
to be started for each of the Selenium tests. Migrating completely over to
the new WebDriver API, and cleaning up some tests that are currently
dependent on the comparatively slow Firefox startup time, should make it
possible to run the test suite with PhantomJS instead, making it much faster.

Job based recipe access limitations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Running recipes can currently inadvertently interfere with systems running
recipes for unrelated jobs. While it is intentional that recipes can control
systems other than the one they are running on, there should really be a
mechanism that limits this access to only those systems running other
recipes within the same recipe set.

Guided editor for job definition XML
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Currently, many Beaker users rely on automated generators to create full
Beaker job definition files from a handful of parameters. This idea is to
use the Relax-NG schema for the job XML, as well as appropriate live queries
of the Beaker database, to create a guided editor that will help users to
create job definitions directly, rather than relying on automated
generators that may expose only a fraction of Beaker's full flexibility.

More complex example tasks
~~~~~~~~~~~~~~~~~~~~~~~~~~

Kerberos and LDAP integration are notoriously hard features to test, and
many automated test suites simply don't bother. Beaker, however, is fully
capable of testing Kerberos and LDAP integration, along with AMQP. This
idea is to make sure the implementations of these tests for Beaker's own
testing are also used as examples of Beaker's capabilities.

Unifying ``hostRequires`` filtering and web UI search functionality
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Beaker's job processing and the web UI both allow a user to identify a
subset of interest within the full set of available systems. The user
interface for these is necessarily different, as once is based on the XML
file defining a job, while the other is defined through an interactive web
form.

However, rather than being thin wrappers around a shared internal filter
creation API, the dynamic filter creation implementations in these
components are almost completely separate. This means that capabilities
are sometimes added to the ``hostRequires`` processing and not to the web
UI, or vice-versa.

It seems like it should be possible to substantially reduce the level of
duplication between these two components, and thus make it easier to add
new filtering and sorting criteria in the future.


Speculative ideas
-----------------

The ideas in this section aren't really in development at all. Instead,
they reflect capabilities we think we'd *like* Beaker to have, or other
improvements we'd like to make, and may even have some initial design
sketches behind them. While there are no current concrete plans to do
anything about any of the ideas in this section, we're certainly open to
discussing them and reviewing any proposed patches related to them.

Most of these are at least non-trivial projects, and it's an open question
if some of them are feasible at all. Some of them may prove to be bad ideas,
regardless of feasibility.


Provisioning other hypervisors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Beaker provides rich "guest recipe" functionality for testing installation
and other operations within a KVM based virtual machine. Testing against
non-KVM hypervisors is possible, but more awkward, as the guest VMs must be
precreated and registered with Beaker as full systems with appropriate
custom power scripts that handle the process of starting and stopping the
underlying virtual machines. This is an unfortunate limitation.

Raw SQL query API
~~~~~~~~~~~~~~~~~

To further help integration with data mining tools, it may be useful to
provide the ability to query a running Beaker server for the equivalent
SQL needed to answer certain API queries.

Asynchronous message queues
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The provisioning service on the lab controllers currently receives
commands by polling a command queue stored on the main server. Similarly,
the main task scheduler polls the database to determine when new
and queued recipes can be assigned to systems.

It may be worth adopting `fedmsg <http://www.fedmsg.com>`__, or something
similar, to help get rid of these polling calls.

Alternate database backend
~~~~~~~~~~~~~~~~~~~~~~~~~~

The only currently supported database backend for the main server is MySQL
(or an equivalent, like MariaDB). There are all sorts of reasons why this
isn't good, but migrating to PostgreSQL isn't straightforward. The two main
issues to be addressed are the handling of queries where MySQL and
PostgreSQL have drastically difference performance characteristics
(and there's no solution that performs well in both), and the
challenge of actually doing a data migration for any existing
Beaker installations.

Recently implemented ideas
--------------------------

The following ideas were previously included on this roadmap, but are
now implemented in Beaker:

- `IPv6 support in the default test harness <http://beah.readthedocs.org/en/latest/admin.html#using-beah-for-ipv6-testing>`__
- `Delegating job submission <../docs/whats-new/release-0.14.html#submission-delegates>`__
- `Separate system architecture guide <../docs/whats-new/release-0.14.html#architecture-guide>`__
- `Jenkins plugin to launch Beaker jobs <https://lists.fedorahosted.org/pipermail/beaker-devel/2013-July/000657.html>`__
- `Self-service user groups <../docs/whats-new/release-0.13.html#more-flexible-user-groups>`__
- `Group ownership of jobs <../docs/whats-new/release-0.13.html#group-jobs>`__
- `autotest support for stable harness API <https://github.com/autotest/autotest/pull/629>`__
- `Stable harness API <../docs/whats-new/release-0.12.html#provisional-support-for-alternative-harnesses>`_
- `Working with multiple Beaker instances <../docs/whats-new/release-0.12.html#other-enhancements>`_
