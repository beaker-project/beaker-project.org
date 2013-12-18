.. _proposal-lshw-migration:

Migrating to lshw for inventory task
====================================

:Author: Amit Saha
:Status: Proposed
:Target Release: TBD

Abstract
--------

This proposal outlines the plan of action to replace the current
:program:`smolt` based inventory task by one which uses
:program:`lshw`. 


Dependencies
------------

None.


Proposal
--------

Currently, Beaker's inventory task uses smolt (besides reading
directly from the procfs file system) to gather the details of various
hardware devices on a system. Due to the `retirement announcement
<https://fedoraproject.org/wiki/Smolt_retirement>`__  of smolt, this
will make it impossible to run the inventory task on current and
future Fedora releases and future releases of Red Hat Enterprise
Linux, unless an effort is made to maintain smolt exclusively for
Beaker's purposes. Users have also reported smolt's ineffectiveness in
certain cases (see bug report: :issue:`541294`). On the other hand, `lshw
<http://ezix.org/project/wiki/HardwareLiSter>`__ is actively
maintained and is thus a future-proof alternative for Beaker's
inventory task. For this migration to be successful without affecting
the utility of the inventory task, a number of aspects need to be
looked into. These are described in the rest of this proposal.

Implementation of the inventory task
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Currently, Beaker's inventory task performs both the functions of
retrieving the hardware data and sending it to the Beaker server. This
makes the retrieval part of the process tightly coupled to the inventory
task (running as part of a Beaker job). However, it is not necessary that
inventory will always be performed on a system as part of a job and should not be
so. 

A new utility :program:`beaker-system-scan` has been created
which is capable of retrieving and sending the retrieved hardware data
to a Beaker server. This utility was created by "extracting out" the
relevant programs from the current inventory task. Beaker's inventory
task's functionality is thus reduced to invoking beaker-system-scan.

The use of smolt in beaker-system-scan will be replaced by lshw.

Enhancing lshw and upstream contributions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It has been found that lshw retrieves incomplete
information on architectures such as IBM s390x and ARM. For example,
it lacks any support for retrieving the CPU information on IBM
s390x. Thus, existing features of lshw will need
enhancement to work correctly on such architectures. On the other
hand, lshw doesn't retrieve information such as audio codecs, which is
an example of a feature that we need to add to lshw to suit Beaker's needs.

Enhancements to lshw will first be incorporated into Beaker project's
fork of `lshw <http://git.beaker-project.org/cgit/lshw/>`__ and then
pull requests sent to the `upstream repository
<https://github.com/lyonel/lshw>`__ via GitHub. 

Maintaining a fork of lshw is motivated by two factors:

- Allow beaker-system-scan to be updated independently of the upstream
  lshw release cycle

- Allow sufficient testing of the changes and then submit requests for
  integration into upstream


Test suite development for lshw
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are absolutely no tests in lshw of any kind.
One direction (also considering how Beaker will use lshw) is to have a
test framework in place which will present a particular hardware
configuration to lshw and match it's XML output to what is expected,
thus helping prevent regressions, for one thing.

Next, we need to find a way to provide these test hardware configurations
as input to lshw. A large number of lshw's features are implemented
by directly reading information from procfs and sysfs. For at least
these features, an approach similar to :program:`lscpu` (part of `util-linux
<https://www.kernel.org/pub/linux/utils/util-linux/>`__) may be
useful. It has an option, :option:`-s` to read a system snapshot
instead of reading directly from the "live" system (see bug report:
:issue:`986157`).

Comparing the data obtained from smolt and lshw
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once lshw's features have been expanded and extended to suit Beaker's
needs, a thorough comparison of the data retrieved from smolt and lshw
is required to see if lshw is able to get all the data that
smolt would give us. If not, either lshw  should be enhanced to
retrieve those data or if the data is not important to Beaker's users,
document it as such.

Miscellaneous tasks
~~~~~~~~~~~~~~~~~~~
The current inventory task uses :command:`hal-find-by-property` and
:command:`hal-get-property` to retrieve storage controller
details. lshw will be used to retrieve these data (also, see bug
report: :issue:`896302`).
