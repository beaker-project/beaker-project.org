.. _proposal-access-policies:

Access Policies for Systems
===========================

:Author: Dan Callaghan, Nick Coghlan
:Status: In Development
:Initial Release: `0.15 <http://beaker-project.org/docs/whats-new/release-0.15.html>`__
:Target Final Release: TBD


Abstract
--------

This proposal replaces the existing mechanisms for controlling access to 
systems with a single unified "access policy". It also provides a way to 
optionally apply the same access policy consistently across many systems.


Access policies
---------------

Beaker's current system management design offers system owners little
flexibility in providing access to their systems. This proposal enhances
the system management capability by allowing system owners to grant
varying levels of access to different users and groups.

An access policy is a list of rules which grant any of the following 
permissions to any number of users or groups:

* edit this access policy (``edit-policy``)
* edit system details (``edit-system``)
* loan system to anyone (``loan-any``)
* loan system to self (``loan-self``)
* issue power and provisioning commands (``control-system``)
* reserve system (either through the scheduler when set to Automated, or via 
  the web UI or bkr client when set to Manual) (``reserve``)

Access policies replace the existing mechanisms for controlling access to 
systems: the Shared flag and group membership.

The system owner always has complete control over their system, which means 
that they implicitly have all of the above permissions. The system owner's 
permissions will not appear explicitly in the access policy.


Predefined access policies
--------------------------

By default, new systems have no access policy. That means no other Beaker users 
have permission to use the system.

A system owner can define a "custom access policy" for their system. This 
policy is specific to a single system. The system owner can always modify the 
custom policy. If the policy grants the ``edit-policy`` permission to other 
users, then they can edit the custom policy as well.

Alternatively, a system owner can apply an existing "predefined access policy" 
to their system, or create a new predefined policy. Predefined policies have 
a descriptive name, such as "Company-wide shared systems" or "QE team systems". 
Once a predefined policy has been created, any system owner can apply it to 
their system.

When a predefined policy is first created, its creator is granted 
``edit-policy`` permission on it automatically. They can then grant 
``edit-policy`` permission to other users or groups to share administrative 
responsibility if desired.

Note that a system owner does not automatically gain access to edit 
a predefined policy when they apply it to their system. In applying 
a predefined policy which they do not themselves control, a system owner is 
effectively delegating management of the permissions for their system to the 
user(s) responsible for the predefined policy.


Proposed user interface
-----------------------

Web UI
~~~~~~

The existing :guilabel:`Shared` check box and :guilabel:`Groups` tab on the 
system page will be removed.

A new tab on the system page, :guilabel:`Access Policy`, will show the system's 
current access policy. It will also display the effective permissions for the 
current user, to make it easier for users to interpret the policy and to 
determine "do I have access to this system?".

Access policies are displayed as a matrix of check boxes, with one row for each 
user or group in the policy, and one column for each permission. Groups are 
prefixed with :guilabel:`Group:` and users with :guilabel:`User:` to 
distinguish them. A special row, labelled :guilabel:`Everyone`, always appears 
as the first row: this defines permissions for all Beaker users.

For the system owner, this tab will also have an interface to select whether to 
apply a custom policy, apply an existing predefined policy, or create a new 
predefined policy. If the owner has applied a custom policy or a predefined 
policy which they have permission to edit, they can click a link labelled 
:guilabel:`Edit` to go to the Edit Access Policy page.

On the Edit Access Policy page, users can edit the name of the policy and its 
permissions. Permissions are displayed in a matrix, as on the system page, with 
the addition of :guilabel:`Add` and :guilabel:`Remove` buttons to add and 
remove rows from the matrix.

Command-line client
~~~~~~~~~~~~~~~~~~~

Apply a predefined access policy to a system::

    bkr system-set-policy --policy="dcallagh's systems" mybox.example.com

Grant and revoke permissions in a predefined policy::

    bkr policy-grant --policy="dcallagh's systems" \
        --permission=edit-system --user=dcallagh

    bkr policy-grant --policy="dcallagh's systems" \
        --permission=loan-self --group=beakerdevs

    bkr policy-grant --policy="dcallagh's systems" \
        --permission=reserve --everyone

    bkr policy-revoke --policy="dcallagh's systems" \
        --permission=reserve --everyone


Upgrading existing Beaker installations
---------------------------------------

As part of the upgrade, a migration step will map each system's existing Shared 
flag and group memberships to a new access policy. The mapping will be 
performed as follows:

* If the Shared flag is set and the system has no groups, the ``reserve`` 
  permission will be granted to everyone.

* For each group which has admin access to the system, all permissions will be 
  granted to the group.

* For each group which does not have admin access, if the Shared flag is set, 
  the ``reserve`` permission will be granted to the group.

In addition, the ``control-system`` permission will be granted to everyone for 
all existing systems. This matches Beaker's current behaviour, which permits 
any user to power any system. This default will not be applied to new systems.


Deferred features
-----------------

In future, it would be possible to add an extra permission for system 
visibility. This would replace the existing Secret flag with a finer-grained 
mechanism for controlling who can see systems which are covered by NDAs.
