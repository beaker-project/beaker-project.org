Development lifecycle
=====================

Beaker's overall development is tracked in `Bugzilla`_. Bugs which have been
accepted by the core development team as desirable features or fixes to
include in Beaker 1.0 (or an earlier minor or maintenance release) will
have an assigned target milestone. Other open Bugzilla entries are either
still under investigation, or remain under consideration for implementation
in a version following the 1.0 release.

.. _Bugzilla: https://bugzilla.redhat.com/page.cgi?id=browse.html&product=Beaker&product_version=&bug_status=open&tab=summary


Release scope and branching model
---------------------------------

The target scope of the overall 1.0 release is described in the Beaker
:ref:`technical road map <technical-roadmap>`. The number and scope of the
individual minor 0.x releases leading up to the eventual 1.0 major release
are quite fluid, as is the number of maintenance releases made for each minor
release.


Minor releases
~~~~~~~~~~~~~~

Minor releases are built around :ref:`design-proposals`. These proposals are
for relatively large chunks of functionality, which may end up being
delivered across multiple minor releases.

In general, the core development team will nominate a particular design
proposal as the current focus of development for a minor release, and the
release will not be published until a meaningful portion of the design
proposal has been completed.

Development aimed at the next minor release takes place on the ``develop``
branch in git.

For the main Beaker project, when a minor release is considered ready for
publication, an appropriate ``release-X.Y`` branch is created and a
release candidate published from the branch. If the release candidate
passes acceptance testing, then the release branch is merged to
``master`` and published as the latest version of Beaker.

Once a minor release is published, its release branch becomes the active
release branch and is used for the creation of any maintenance releases,
while the ``develop`` branch begins to be used for development of the
next minor release.

Smaller subprojects, such as the beah test harness and the
beaker-system-scan hardware scanning utility use a simpler branching
model where releases are tagged and created directly on the ``develop``
branch. Maintenance releases are never published for these subprojects -
any issues are resolved by publishing a new minor release.

The target minor release cadence for the main Beaker project is a new
release every 6-8 weeks. For other subprojects, new minor releases are
made as needed to resolve issues.


Maintenance releases
~~~~~~~~~~~~~~~~~~~~

As minor releases are based around delivering particular pieces of
functionality, their exact delivery schedule is necessarily somewhat
flexible. To ensure that fixes for hardware and installer compatibility
issues can be incorporated in a timely manner, even if a minor release
is delayed, all such changes are first included in the active release branch
and then merged forward to the ``develop`` branch rather than being
merged directly into ``develop`` in Gerrit.

Whenever the active release branch has accumulated a reasonable number of
changes and a new minor release isn't about to be published, then a new
maintenance release will be created and published from the active release
branch.

There are two major requirements for a change to be considered acceptable
for inclusion in a maintenance release (and hence included in the active
release branch rather than the ``develop`` branch):

* it must be possible to deploy it without a significant system outage (in
  particular, this means database schema changes are not permitted in
  maintenance releases)
* it must not have a broad impact on other parts of the system (for example,
  adding a new client command is acceptable in a maintenance release, as
  those are relatively independent pieces of functionality).

As only relatively small, functionally independent changes are made in
maintenance releases, these releases are published directly, without a
preceding release candidate.


.. note::

   As an exception to the normal approach, there are currently two
   active release branches: ``release-0.14`` and ``release-0.15``.
   This is due to some issues encountered in the initial 0.15 release
   which resulted in the resumption of further maintenance releases for
   0.14 while the problems with 0.15 were addressed. The current policy
   of always merging changes that would be eligible for a maintenance
   release into the active release branch is a direct result of the
   problematic 0.15 release - if this policy had been in place while 0.15
   was in development, then the initial 0.15 release would likely have
   been delayed while 0.14.2 was released instead.

