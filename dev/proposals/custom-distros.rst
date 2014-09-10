.. _custom-distros:

Handling Custom Distros
=======================

:Author: Dan Callaghan
:Status: Implemented
:Target Release: `0.18 <https://beaker-project.org/docs/whats-new/release-0.18.html#better-support-for-custom-distros>`__

This document proposes a number of backwards-compatible changes to Beaker's 
kickstart templates, to make it easier to use custom distros without modifying 
Beaker's source code. Here "custom distros" means distros which still use the 
Anaconda installer but identify themselves as something other than Fedora, Red 
Hat Enterprise Linux, or CentOS [#centos-support]_.

Background and rationale
------------------------

Beaker currently uses a separate kickstart template for each distro family 
(``RedHatEnterpriseLinux6``, ``RedHatEnterpriseLinux7``, etc).

In addition, Beaker's templates and source code contain a large number of 
conditionals which check for hardcoded distro family names to decide what the 
desired kickstart output should be. In some cases features are assumed to be 
present, and disabled for some older distro families. In other cases, features 
are conditionally enabled only for certain hardcoded distro families.

The end result is that a new distro family will effectively be treated as 
equivalent to RHEL6 unless all the relevant conditional logic in Beaker is also 
updated. Adding support for new distro families which aren't based on RHEL6 
therefore means modifying Beaker's source code --- it cannot be done by the 
Beaker administrator.

The number of "custom distros" (particularly ones built on newer technology 
like RHEL7) is expected to continue growing in the near future, therefore 
Beaker needs better mechanisms for handling them.

Proposed changes
----------------

Runtime checks inside bash scriptlets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most of the template conditionals which fall inside bash scriptlets (kickstart 
``%pre`` and ``%post`` sections) can be converted to perform an equivalent 
conditional check at runtime in the script itself.

For example, the ``rhts_post`` kickstart snippet currently has a conditional 
block which assumes that the RHEL6 readahead service only exists for the 
``RedHatEnterpriseLinux6`` family. The snippet can instead check for the 
presence of :file:`/etc/sysconfig/readahead` at runtime, so that it also takes 
effect on other RHEL6-derived distros which have the RHEL6 readahead service.

Similarly, there are a number of conditional blocks throughout the kickstart 
snippets which use wget for downloading if the family name matches RHEL3--5, 
otherwise they use curl. These conditionals can be replaced with a bash 
function which uses either wget or curl depending on which one is available at 
runtime.

Feature variables
~~~~~~~~~~~~~~~~~

Other template conditionals cannot be converted to runtime checks because they 
are related to the kickstart syntax or package selection. These conditionals 
can be converted to check for the presence or absence of a kickstart metadata 
variable instead. Beaker will populate these "feature variables" automatically, 
based on the same logic currently used in the templates.

In addition, the conditionals will all be inverted. Currently they are written 
as progressive enhancements: they assume the absence of a feature, and enable 
it for recognized distro families. This will be flipped so that Beaker always 
assumes the latest syntax and features *are* supported, and then conditionally 
disables them as necessary on older distros.

For example, the ``rhts_partitions`` snippet currently has a (quite 
complicated) conditional block which enables the ``--type`` option for the 
``autopart`` command only for RHEL7 and Fedora releases from 18 onwards. The 
snippet can instead check if the ``has_autopart_type`` variable is defined. 
Beaker will define this variable by default, unless it recognizes that the 
distro is Fedora older than 18 or RHEL/CentOS older than 7.

Default kickstart template
~~~~~~~~~~~~~~~~~~~~~~~~~~

Beaker currently expects to find a kickstart template named after the distro 
family. If none is found, Beaker cannot provision the distro. As a consequence, 
every new distro family to be supported by Beaker requires adding a new 
template (typically copied and modified from the Fedora or RHEL family on which 
it is based).

Instead, Beaker will fall back to using a ``default`` template if no other 
matching template can be found. The ``default`` template will be based on the 
existing Fedora template, modified so that it also produces the desired output 
for RHEL7 and RHEL6. The existing templates for those families will be deleted 
from Beaker's source in favour of the ``default`` template, although any 
site-specific templates for those families will continue to be used as before.

In future the kickstart templates for older RHEL families could also be 
replaced with the ``default`` template, after suitable conditionals are added 
to it to account for the missing features in those older families. However 
there is negligible benefit in doing this, since new custom distros are 
unlikely to be based on those older releases.

Advantages of the approach
--------------------------

When an unrecognised distro is imported, it will effectively be treated as the 
latest Fedora release. Beaker will fall back to using ``default`` kickstart 
template, and the aforementioned "feature variables" will be populated under 
the assumption that all features are supported.

The Beaker administrator will also have complete control over the conditional 
kickstart behaviour for each OS major, by setting kickstart metadata variables 
on the OS major in their Beaker installation. This works equally well for 
distros Beaker knows about (for example, you could set ``!has_systemd`` in the 
install options for ``RedHatEnterpriseLinux7`` to override Beaker's default 
assumption that RHEL7 has systemd) or for completely unrecognised distros.
The feature variables will be documented alongside the other kickstart metadata 
variables, to make it easier for administrators to figure out what variables 
they might need to set when using a custom distro in Beaker.

Rather than having conditionals strewn throughout Beaker's source code and 
templates, the existing rules based on hardcoded distro families (for example, 
``RedHatEnterpriseLinux7`` has systemd) will be centralized to a single method 
in Beaker's source. That will make it easier to update the logic in future as 
the distros evolve.

Backwards compatibility
-----------------------

This proposal preserves backwards compatibility for all existing custom 
snippets and templates. All existing variable names and template inheritance 
orders will be kept unchanged.

The generated kickstarts will be mostly unchanged for existing supported 
distros. To simplify the implementation, some differences across the templates 
will be regularized, but only when it has no effect on the meaning of the 
generated kickstart: the order of some commands will change, and some commands 
which have no effect (such as ``key --skip`` on RHEL6) will be dropped.

Open questions
--------------

Aside from the kickstart templates, distro names are hardcoded in some other 
parts of Beaker as well. This proposal does not attempt to address these 
issues.

* Harness repos are identified by distro family, and if a repo is not found the
  distro cannot be used in recipes. However, the Beaker administrator can 
  always create a harness repo for a custom distro, by copying from or 
  symlinking to an existing repo for a compatible distro.

* The ``beaker-import`` command uses some hardcoded product names in order to
  distinguish between different metadata formats (:issue:`1070575`).

.. rubric:: Notes

.. [#centos-support] Beaker has historically supported CentOS only on 
   a best-effort basis and not consistently. The changes in this proposal will 
   make it possible to consistently treat CentOS as equivalent to RHEL for 
   kickstart templating purposes.
