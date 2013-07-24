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

The following elements have been identified as the objectives of Beaker 1.0,
and we will continue with as many regular 0.x releases as are needed to
achieve them:

* The Effective Job Priorities design proposal (and its dependencies)
* Red Hat workflow independence

  * Moving any remaining hardcoded Red Hat specific settings into
    configuration files
  * Full Fedora deployment compatibility (including the test suite)
  * A stable alternate harness API (ideally with the corresponding
    autotest patches merged on their side)
  * A harness independent reservesys mechanism
  * Self tests that exercise beah, the legacy harness API and the new 
    harness API

* Documentation improvements, including
   * an architectural guide that at least explains all of Beaker's
     external interfaces
   * an explanation of the local watchdog hooks
   * more general advice on job design (including effectively using
     features like the job matrix)
   * a public page giving at least basic info on how Beaker is used
     at Red Hat



The status of ``beah``
~~~~~~~~~~~~~~~~~~~~~~

In many respects, ``beah``, the native Beaker test harness, duplicates aspects
of other test frameworks like `autotest <http://autotest.github.io/>`__ and
`STAF <http://staf.sourceforge.net/>`__.

Being so heavily dependent on kickstart files and the RPM based task library,
``beah`` is also quite inflexible in terms of platform support.

Accordingly, we consider it a poor use of resources to further duplicate
the effort going into development of other automated test harnesses
(especially ``autotest``), and hence any major feature proposals for
``beah`` will be rejected - we would prefer for any such efforts to be
directed towards the system changes needed to better support alternative
harnesss.

However, to support existing Beaker users, the ``beah`` test harness will be
maintained indefinitely, and its documentation will continue to be improved.
The only way ``beah`` would ever be phased out is if a robust autotest based
alternative became available and was capable of correctly executing all of
the existing Beaker tests that the Beaker developers have access to.


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

Self-service user groups
~~~~~~~~~~~~~~~~~~~~~~~~

Currently, all management of user groups must be handled by Beaker
administrators. This doesn't scale to large numbers of users, so it makes
more sense to let many aspects of groups be self-administered.

This idea is covered by the :doc:`proposals/enhanced-user-groups` design 
proposal.

Group ownership of jobs
~~~~~~~~~~~~~~~~~~~~~~~

Currently, all submitted jobs must be owned by a specific user, and many
actions on the job are limited to that user. As with administrator
management of user groups, this doesn't work well for larger teams, so
the idea is to allow a job to be assigned to a user group, granting
members of that group access to commands that would otherwise be
restricted to the job owner.

One aim of this change will be to make workarounds like shared
accounts for job submission and the current "proxy_user"
setting unnecessary (although they will continue to be supported).

This idea is covered by the :doc:`proposals/enhanced-user-groups` design 
proposal.

Planned development
-------------------

The ideas in this section are firmly on the to-do list, but it is not yet
clear when they will be ready for inclusion.

Explicit system pools
~~~~~~~~~~~~~~~~~~~~~

Beaker currently includes informal notions of the "public pool" (systems
with no access restrictions) and "private pools" (systems with access
limited to particular user groups). The idea here is to make this notion
of system pools explicit in the Beaker data model and UI, making it easier
to administer large groups of machines, as well as better distributing
administration responsibilities to the owning user groups.

Adding system pools as an explicit part of the data model may also allow
additional features like making a pool accessible to all users, but only
when they explicitly request it when submitting their job, or limiting
the number of systems in a pool which may be consumed by a single user.

This idea is covered by the :doc:`proposals/system-pools` design proposal.

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

Armed with the new user group and system pool models, and the new event
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

Separate system architecture guide
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Aimed more at developers than at users or administrators, a dedicated
system architecture guide would allow new developers to more quickly
become familiar with Beaker's many moving parts, and better understand
how the all interoperate.

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

OpenStack also offers some interesting possibilities in terms of dynamically
creating isolated subnets. Integrating with that could allow Beaker to
support testing of scenarios that are currently difficult to set up due
to interference with the network of the hosting lab. For example, a full
Beaker provisioning cycle currently can't be tested easily within Beaker,
as doing so requires taking control of DHCP responses, while still retaining
access to the distro trees used for installation.

Exploration
-----------

The ideas in this section are projects that one or more of the current
developers are at least tinkering with, but they may be at wildly
divergent stages of maturity.

Jenkins plugin to spawn systematic integration tests in Beaker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While Beaker is an excellent integration testing system, it doesn't really
have the right features to serve as a continuous integration system on its
own. However the combination of Beaker with Jenkins could be substantially
more powerful than either system on its own, as a Jenkins build bot could
be used to perform an initial "smoke test" on a small number of common
platforms, and then trigger a more comprehensive set of integration
tests across multiple platforms in Beaker if the smoke test is successful.

Autotest support
~~~~~~~~~~~~~~~~

Using Beaker's new `support for alternative harnesses 
<../docs/alternative-harnesses/>`_ it should be possible to write some glue 
code to run autotest-based tests in Beaker recipes.

This is being tracked primarily as a
`pull request <https://github.com/autotest/autotest/pull/629>`__ on the
autotest side. On the Beaker side, we're now mostly tracking this as
individual Bugzilla entries against specific problems or limitations in the
stable harness API.

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

Full Fedora compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~

The "Beaker-in-a-box" scripts currently rely on CentOS 6, as the server
components aren't fully compatible with current versions of Fedora
(provisioning Fedora on systems within Beaker works correctly).

We'd like to migrate Beaker-in-a-box over to using Fedora 18 (there are only
a few remaining problems with daemon mode operation, apparently due to the
more recent version of gevent)

Virtual-only trial environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The "Beaker-in-a-box" scripts currently require a physical machine, which
runs the main Beaker server, and then creates some KVM guests for lab
controllers and test systems.

It would be more convenient if the bare metal host wasn't needed, and the
main server also ran inside a guest VM.

Improved inventory task
~~~~~~~~~~~~~~~~~~~~~~~

The current inventory task is based on the ``smolt`` project. Replacing this
with a new version based on ``lshw`` would improve many aspects of the
system capability reporting, providing a richer set of attributes to query.

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

Support testing IPv6 only systems
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Beaker test harness currently relies on a version of Twisted which doesn't 
support IPv6. This means Beaker can't currently be used to test IPv6 only 
operation of a system, as an IPv4 connection is needed between the test harness 
and the lab controller. :issue:`810893` gives some additional background.

At least on more recent operating systems, it should be possible to use
the test harness with a newer version of Twisted. With appropriate
configuration of the lab controller and network, this should make it
possible to provision systems in Beaker with no IPv4 interfaces
configured.


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

Alternate provisioning mechanisms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provisioning is currently based directly on the Anaconda installer. VM
image based provisioning for guest recipes or the dynamic host creation
would allow Beaker to cover a wider range of testing scenarios.

Supporting tools like `os-autoinst <http://www.os-autoinst.org/>`_ or
specific image URLs for guest installs are other possibilities
potentially worth investigating.

A more flexible provisioning architecture might even be able to deploy
other distributions and operating systems that don't use Anaconda at all.

In particular, `Ansible <http://ansible.cc/discover.html>`__ may provide
a viable installer independent approach to post-boot configuration.

For image based provisioning, OpenStack's
`cloud-init tool <http://docs.openstack.org/trunk/openstack-compute/admin/content/user-data.html>`__
is also worth exploring.


Provisioning other hypervisors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Beaker provides rich "guest recipe" functionality for testing installation
and other operations within a KVM based virtual machine. Testing against
non-KVM hypervisors is possible, but more awkward, as the guest VMs must be
precreated and registered with Beaker as full systems with appropriate
custom power scripts that handle the process of starting and stopping the
underlying virtual machines. This is an unfortunate limitation.

Improved "System Loan" mechanism
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While systems in Beaker can currently be loaned to other users, the workflows
for doing so aren't particularly convenient. It might be helpful if
Beaker included better tools for requesting System Loans, as well as a
system for automatically returning them if unused for extended periods.

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

Web UI modernisation
~~~~~~~~~~~~~~~~~~~~

The current main web UI is based on the TurboGears 1 stack (although it
uses SQLAlchemy rather than SQLObject for the database access layer). This
makes some aspects of development more awkward than they might be with a
more recent web framework.

That said, TG1 is still quite usable, even if it isn't quite as capable
as the newer frameworks. Furthermore, the current direction of
development in Beaker is to push it more towards the role of being
a sophisticated inventory management and task scheduling backend (in
contrast to both other IaaS systems, which attempt to abstract away hardware
details completely, and normal identity-based orchestration systems), and
deemphasise the importance of the native Web UI.

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

- `Stable harness API <../docs/whats-new/release-0.12.html#provisional-support-for-alternative-harnesses>`_
- `Working with multiple Beaker instances <../docs/whats-new/release-0.12.html#other-enhancements>`_
