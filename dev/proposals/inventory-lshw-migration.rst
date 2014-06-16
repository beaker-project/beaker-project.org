.. _proposal-lshw-migration:

Migrating to lshw for inventory task
====================================

:Author: Amit Saha
:Status: In Progress
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
future releases of Red Hat Enterprise Linux and Fedora. Users have
also reported smolt's ineffectiveness in certain cases (see bug
report: :issue:`541294`). On the other hand, `lshw
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

The major enhancements merged to the fork so far are:

- A "chroot" based testing framework. This is described briefly in the
  next section.

- Better support for retrieving CPU information on ARM and s390x systems.

Maintaining a fork of lshw is motivated by two factors:

- Allow beaker-system-scan to be updated independently of the upstream
  lshw release cycle

- Allow sufficient testing of the changes and then submit requests for
  integration into upstream

Test suite development for lshw
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The chroot based testing framework runs lshw in a chroot so that
instead of reading files from /proc and /sys on the 
system, they read the test data files made available in the chroot.

Although this doesn't allow testing data which are retrieved by
lshw using system calls, it allows a basic level of sanity
testing to make sure regressions are caught.


Comparing the data obtained from smolt and lshw
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once lshw's features have been expanded and extended to suit Beaker's
needs, a thorough comparison of the data retrieved from smolt and lshw
is required to see if lshw is able to get all the data that
smolt would give us. If not, either lshw  should be enhanced to
retrieve those data or if the data is not important to Beaker's users,
document it as such.

Related tasks
~~~~~~~~~~~~~

beaker-system-scan currently uses :command:`hal-find-by-property` and
:command:`hal-get-property` to retrieve storage controller
details and libparted to retrieve details of disk drives. 
In both the cases, lshw will be used instead (See :issue:`896302` and
:issue:`902567` for details).
