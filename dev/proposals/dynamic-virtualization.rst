.. _proposal-dynamic-virtualization:

OpenStack Based Dynamic Virtualization
======================================

:Author: Nick Coghlan
:Status: Implemented
:Release: `0.17 <https://beaker-project.org/docs/whats-new/release-0.17.html#openstack-as-dynamic-virtualization-backend>`__


Abstract
--------

While Beaker's distinguishing feature is the ability to request distinctive
hardware when provisioning systems (rather than having to name the target
system explicitly, or only getting access to a generic virtual machine),
Beaker jobs still often involve running code that doesn't need to be on
any particular hardware.

The dynamic virtualization support is designed to integrate a Beaker lab with
an external provisioning system, allowing Beaker to request access to
additional generic compute resources in order to resolve these requests.
Beaker's current dynamic virtualization support is based on oVirt Engine,
and has several limitations that make it unusable in practice.

Some of those issues are inherent in the fact that dynamic creation of
ephemeral virtual machines is a task that oVirt doesn't handle well, so
rather than fixing the problems directly, it is proposed that Beaker's
dynamic virtualization support instead be redesigned to be based on
OpenStack.


Dependencies
------------

None.


Background
----------

Beaker 0.10 added the ability to dynamically provision virtual machines
in `oVirt Engine <http://beaker-project.org/docs/admin-guide/ovirt.html>`__.
While this feature works correctly at small scale, it suffers from several
issues that prevent scaling to larger instances.

During the development of this feature, it also became clear that oVirt
simply wasn't a good fit for the problem we're trying to solve with Beaker's
dynamic virtualization. oVirt focuses on the "high availabilty" kind of
virtualization, where a virtual machine is created once, and can then be
migrated between host machines to cope with hardware failure, planned
maintenance, upgrades, etc. By contrast, Beaker needs to create dynamic,
relatively shortlived virtual machines on demand, and then throws them
away when the recipe set completes execution. This use case is a much
better fit for OpenStack than it is for OpenShift.

Furthermore, it became clear that oVirt didn't provide a clear path
towards image based provisioning for Beaker (although more recent versions
of oVirt do support integration with the OpenStack Glance image library, and
the lack of a straightforward approach to remotely capturing console log
details was also problematic (as some Beaker features, like automatic panic
detection, do not work without remote console log access, and the console
log data is also often invaluable when debugging test and system failures).


Proposal
--------

The proposal is to take the current dynamic virtualization feature, and
replace the current oVirt based provisioning components in the scheduler
with new components that use OpenStack instead. The existing support for
oVirt integration will be removed entirely.

This proposal is tracked in Bugzilla as issue :issue:`1040239`.


Minimum OpenStack version
~~~~~~~~~~~~~~~~~~~~~~~~~

Due to the significant changes to network configuration support between
OpenStack Grizzly and Havana, it is proposed that Beaker only support
OpenStack Havana and later.


Associating lab controllers with OpenStack regions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Replacing the existing association of lab controllers with specific oVirt
data centres, Beaker will allow each lab controller to optionally be
associated with an `OpenStack region
<http://docs.openstack.org/trunk/openstack-ops/content/cells_regions.html>`__.

It is expected that the associated region be in reasonably close proximity
to any physical systems associated with that lab controller, as Beaker may
provision a mixture of physical systems and dynamically created virtual
machines for a single recipe set.

Pure virtual labs that are associated with an OpenStack region, but no
physical machines *will* be supported.


Host filtering
~~~~~~~~~~~~~~

Beaker will translate memory and virtual CPU requirements for x86 and x86_64
hosts into suitable queries against the available VM "flavours" in OpenStack.
If a suitable flavour is available, and there are no other specific hardware
requirements for the recipe, then that recipe will be considered a candidate
for dynamic virtualization.

As with the existing dynamic virtualization support, Beaker will favour the
use of dynamic resources whenever the host filtering requirements allow it.


Provisioning
~~~~~~~~~~~~

The initial iteration of Beaker's OpenStack based dynamic virtualization will
not directly use image based provisioning.

Instead, Beaker will rely on a common `iPXE <http://ipxe.org/download>`__
image, which will allow Beaker to point to the appropriate kernel and
initrd URLs dynamically, and allow Anaconda to handle the installation as
usual.

This approach is preferred for the initial implementation, as many Beaker
recipes currently take advantage of Anaconda specific features (most of
the post install customisation explicitly uses kickstart specific syntax),
and Beaker itself relies on Anaconda to handle tasks like disk partitioning,
package installation and yum repo configuration.

With the assumption of Anaconda based provisioning currently pervasive in
the Beaker server code, deferring image based provisioning to a later
release should significantly reduce the amount of change needed for the
initial OpenStack integration.

This proposed approach to provisioning is very similar to that taken by
Rackspace in the design of their `boot.rackspace.com
<http://rackerlabs.github.io/boot.rackspace.com/>`__ utility scripts.


Disk configuration
~~~~~~~~~~~~~~~~~~

The initial iteration of the OpenStack integration will *not* support recipes
which request a particular disk configuration in their host requirements,
and will not support the use of persistent block storage volumes.

Instead, virtual machines will simply receive the amount of ephemeral storage
allocated for the system flavour that satisfies their memory and virtual CPU
requirements.


Network configuration
~~~~~~~~~~~~~~~~~~~~~

The initial iteration of the OpenStack integration will use a predefined
subnet that must be specified as part of the lab controller configuration in
Beaker.

Systems on this subnet must have the same level of network access as any
other systems in that Beaker lab. In particular, they must be able to access
the lab controller (to report results), the web server that hosts the
distro trees and any custom repository hosts that are supported by that
lab.


Console logging
~~~~~~~~~~~~~~~

Beaker will make use of the console APIs in OpenStack to ensure that console
logs for dynamically provisioned systems are captured correctly
(:issue:`950903`).


Deferred features
-----------------

The following additional features are under consideration, but have been
deliberately omitted in order to reduce the complexity of the initial
iteration of the design:

* Provisioning directly from predefined OpenStack images. While this
  feature is expected to be implemented eventually, adding the ability to
  support cloud-init in addition to Anaconda kickstarts is better handled as
  a separate follow-on activity (also see :issue:`1108455`).

* Using OpenStack Cinder to support alternative requested block storage
  configurations (for example, multiple disks of particular sizes).

* Using OpenStack Neutron to dynamically create individual subnets for
  each recipe set.


Rejected alternatives
---------------------

An earlier draft of this proposal suggested building `bootstrap images
<https://github.com/redhat-openstack/image-building-poc>`__ when a distro
tree was imported and uploading them to glance. Dan Callaghan suggested
using iPXE instead, which looks like it should be a much simpler alternative.
