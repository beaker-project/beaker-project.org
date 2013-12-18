.. _proposal-dynamic-virtualization:

OpenStack Based Dynamic Virtualization
======================================

:Author: Nick Coghlan
:Status: Proposed
:Target Release: TBD


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
ephemental virtual machines is a task that oVirt doesn't handle well, so
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
towards image based provisioning for Beaker (it lacks a counterpart to
the OpenStack Glance component), and the lack of a straightforward approach
to remotely capturing console log details was also problematic.


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

Beaker will translate memory and local disk requirements for x86 and x86_64
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

Instead, Beaker will provision a bootstrap image that launches the regular
Anaconda installer. This approach is based on the `OpenStack image building
proof of concept <https://github.com/redhat-openstack/image-building-poc>`__,
and involves Beaker generating bootstrap images in Glance for imported distro
trees in each lab, and then using those to launch the existing kickstart
based provisioning operations rather than relying DHCP based netbooting of
bare metal systems.


Console logging
~~~~~~~~~~~~~~~

Beaker will make use of the console APIs in OpenStack to ensure that console
logs for dynamically provisioned systems are captured correctly.


Deferred features
-----------------

The following additional features are under consideration, but have been
deliberately omitted in order to reduce the complexity of the initial
iteration of the design:

* Provisioning directly from predefined OpenStack images. While this
  feature is expected to be implemented eventually, the migration from
  Anaconda kickstarts to cloud-init is better handled as a separate follow-on
  activity (:issue:`1040245`)
