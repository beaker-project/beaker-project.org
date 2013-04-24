.. _proposal-enhanced-user-groups:

Enhanced User Groups
====================

:Authors: Dan Callaghan, Nick Coghlan
:Editors: Raymond Mancy
:Target Release: 1.0


Abstract
--------

This proposal adds additional self-management capabilities for Beaker's
user groups, as well as adding the ability for a job to be owned by a group
in addition to the submitting user.


Dependencies
------------

None.


Proposal
--------

Under Beaker's current group design, all group management is carried out
by Beaker administrators, and groups can own systems, but not jobs.

This proposal enhances the capabilities of the existing group model by:

* adding a group Description field in addition to the existing Display Name
* allowing users to manage their own groups, rather than requiring
  administrator involvement
* allowing administrators to create groups that are automatically derived
  from groups already defined in an LDAP server
* allowing jobs to be submitted on behalf of a group

A Beaker user can be in zero or more groups, and any Beaker user may
create a new group at any time.

All members of a group are able to submit jobs on behalf of that group.

Group members may also be granted the following additional permissions
on a group:

* group ownership
* group job modification


Group ownership
~~~~~~~~~~~~~~~

Group ownership permissions grant a user the ability to:

* add and remove group members
* grant and revoke group ownership permissions
* grant and revoke job modification permissions
* update the group's display name
* update the group's description

As a group may have multiple owners, "group ownership" may sometimes
be referred to as "group co-ownership".


Job modification
~~~~~~~~~~~~~~~~

When a job is submitted on behalf of a group, any members of that group
with job modification permissions will have the same level of access to
and control over the job as the original submitter.

By default, new members added to a group are granted job modification
permissions. This will be configurable on a per-user basis, allowing the
addition of automated service accounts which can submit jobs on behalf
of the group, but have no additional access to jobs that are not
submitted through the automated service.


General Use Cases
-----------------

The primary use case for the additional features is to simply improve the
scalability of Beaker usage in large organisations, by:

* removing the installation administrators as a bottleneck for group updates.
* making it possible to derive group membership directly from an LDAP
  server.
* allowing a team of submitters to share responsibility for a set of jobs,
  rather than limiting access to the specific user that carried out the
  actual submission.

In addition, this update aims to make it easy for users to set up automated
systems that submit jobs on their behalf by creating personal groups and
granting the ability to submit jobs on their behalf to the account used
for the automated service, *without* needing to give the automated service
permission to modify their jobs after submission.


Proposed User Interface
-----------------------

Self-Service User Groups
~~~~~~~~~~~~~~~~~~~~~~~~

Creating Ad Hoc Groups
^^^^^^^^^^^^^^^^^^^^^^

* I want to create a new group. (:issue:`908172`)

Through the web UI:

   Select "Hello -> My Groups" from the menu, then click "Create". Enter
   a group name, display name and description and click "Create".

Through the ``bkr`` cli::

   bkr group-create --display-name="My New Group" --description="This is my very own group. Email me@example.com if you want to be included." <mynewgroup>

A new group is created, with one member (you) who is also the group owner.
The change is recorded in the "Group Activity" log.


Creating LDAP-Derived Groups
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* I am a Beaker administrator and I want to create a new group whose
  membership is populated from LDAP. (:issue:`908173`)

Through the web UI:

   Select "Admin -> LDAP Groups" from the menu, then click "Create". Enter
   the  group name, which must correspond to the name of a group in your
   LDAP directory.

Through the ``bkr`` cli::

   bkr group-create --ldap <mygroup>

A new group is created, whose membership is populated from the LDAP
directory configured in your Beaker installation. An admin can refresh the
group from LDAP by running ``beaker-ldap-refresh --group=<groupname>``
on the server. Beaker will ship with a cron job to refresh all LDAP groups
once per day, but the administrators of a particular installation may
choose to refresh the group membership more frequently.

Note that LDAP groups cannot be updated through Beaker. They have no
owners, and all members are treated as having job modification permissions.


Viewing Group Details
^^^^^^^^^^^^^^^^^^^^^

* I want to view the details of a group. (:issue:`541282`)

Through the web UI:

   Select "Hello -> My Groups" from the menu, then click the name of the
   group you are interested in to go to its group page.

Through the ``bkr`` cli::

   bkr group-members <mygroup>


Updating Group Details
^^^^^^^^^^^^^^^^^^^^^^

* I want to update the details of a group I own (:issue:`952978`).

Through the web UI:

   Select "Hello -> My Groups" from the menu, then click the name of the
   group you are interested in to go to its group page.

   To update the display name and/or description for the group, click
   "Edit Group", update the group details, then click "Save Changes".

Through the ``bkr`` cli::

   bkr group-modify --display-name="My Group" --description="This group is mine. Email me@example.com if you want to be included." <mynewgroup>

The group details are updated and the change is recorded in the
"Group Activity" log.


Updating Group Membership
^^^^^^^^^^^^^^^^^^^^^^^^^

* I want to add other users to a group I own. (:issue:`908176`)

Through the web UI:

   Go to the group page. Under the membership list, enter the user's
   username and click "Add to Group".

Through the ``bkr`` cli::

   bkr group-modify --add-member=<someusername> <mygroup>

The user is added to the group. The change is recorded in the
"Group Activity" log.

* I want to remove a member from a group I own. (:issue:`908178`)

Through the web UI:

   Go to the group page. Find the user in the membership list, and click "Remove".

Through the ``bkr`` cli::

   bkr group-modify --remove-member=<someusername> <mygroup>

The user is removed from the group. The change is recorded in the
"Group Activity" log.


Updating Group Permissions
^^^^^^^^^^^^^^^^^^^^^^^^^^

* I want to grant another member owner rights to the group (or revoke
  those rights). (:issue:`908174`)

Through the web UI:

   Go to the group page. Find the other user in the membership list,
   check/uncheck the checkbox in the "Owner" column, then click "Save".

Through the ``bkr`` cli::

   bkr group-modify --grant-owner=<someusername> <mygroup>
   bkr group-modify --revoke-owner=<someusername> <mygroup>

The user is granted owner rights, making them a co-owner of the group.
The change is recorded in the "Group Activity" log.

* I want to grant another member job modification rights for the group (or
  revoke those rights). (:issue:`952979`)

Through the web UI:

   Go to the group page. Find the other user in the membership list,
   check/uncheck the checkbox in the "Modify Jobs" column, then click
   "Save".

Through the ``bkr`` cli::

   bkr group-modify --grant-modify-jobs=<someusername> <mygroup>
   bkr group-modify --revoke-modify-jobs=<someusername> <mygroup>

The user is granted job modification rights, allowing them to modify jobs
submitted on behalf of the group as if they were the job submitter.
The change is recorded in the "Group Activity" log.


Group Job Management
~~~~~~~~~~~~~~~~~~~~

Submitting Shared Jobs
^^^^^^^^^^^^^^^^^^^^^^

* I want to submit a job for a particular group (of which I am a member).
  (:issue:`908183`)

Through the job XML:

  Add an optional attribute ``group="somegroup"`` to the ``<job/>`` element
  directly to the job XML.

Through the ``bkr`` cli::

  Pass the ``--job-group=somegroup`` option to a workflow command.

The job will be owned by that group and the user that submitted the job.
There can be only one "job-group" per job, thus multiple groups having ownership
of a single job is not possible. All members of the group with job modification
permissions will be able to ack/nack, change priority, edit whiteboard, and
change retention tag.  The root password used in the job will be the group
root password (if one is set), otherwise it will be the root password set in
the preferences of the submitting user. The public SSH keys of all group
members with job modification permissions will be added to
``/root/.ssh/authorized_keys``.


Viewing Shared Jobs
^^^^^^^^^^^^^^^^^^^

* I want to view a list of jobs for all groups of which I am a member.
  (:issue:`908185`)

The default filter for the "My Jobs" page will include all jobs the user
can manage, including those the user submitted themselves, as well as
those submitted on behalf of a group where the user has job modification
permissions.

* I want to view a list of jobs for a particular group. (:issue:`952980`)

Both the "My Jobs" page and the main job list will allow filtering by
the owning group. This will permit users to display jobs owned by
particular groups (whether they are a member of those groups or not), as
well as displaying only the jobs that were not submitted on behalf of a
group at all.


Root Password Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^

* I want to set the shared root password to be used in all jobs for a
  particular group. (:issue:`908186`)

Through the web UI:

  Go to the group page. Enter the root password in the "Root Password" field
  and click "Save". The root password may be given in hashed form (suitable
  for inclusion in ``/etc/shadow``) or in the clear.

Through the ``bkr`` cli::

  bkr group-modify --root-password=<thevalue>

The given root password will be used when provisioning jobs for this group.
It will be visible on the group page to other members of the group. If the
password is given in the clear Beaker will *not* automatically hash it
before storing, to make it easier to share amongst the group (This
behaviour deliberately differs from that for individual root passwords set
on the Preferences page - when given in the clear, individual passwords are
automatically hashed before storage).

Changes to the group's root password are recorded in the "Group Activity"
log. The activity log only records when the change occurred, and the user
that made the  change - the password itself is not recorded in the activity
log, not even in hashed form).

.. note::

   It is *strongly* recommended that group members upload their public
   SSH keys (which will be automatically added to systems provisioned
   for group jobs) rather than setting a shared root password for the
   group.


Upgrading Existing Beaker Installations
---------------------------------------

All members of existing groups in a Beaker installation will be granted
job modifications permissions for each group where they are a member.

This means that groups that already existed in a Beaker installations will
not have any designated owners after the installation is upgraded. After
upgrading, users and administrators of the Beaker installation will
need to coordinate the initial allocation of ownership privileges to
members of existing groups, as well as deciding which groups can be deleted
and replaced with LDAP group references.


Deferred Features
-----------------

These additional features are under consideration, but have been deliberately
omitted in order to reduce the complexity of the initial iteration of the
design:

* Adding other groups as members of a group (:issue:`554802`). The initial
  iteration does not allow groups to be members of other groups, which
  introduces potential concerns about scalability in large organisations. A
  subgroups model, with an implementation based on the `Closure Table`_
  design, would address this concern. If there's time, we'll look into
  adding this to 1.0, otherwise it will be considered for inclusion in 1.1.

  The draft web UI design is the same as that for managing group members, but
  using the "Sub-group" list instead of the "Members" list. For the CLI::

     bkr group-modify --add-subgroup=<groupname> <mygroup>
     bkr group-modify --remove-subgroup=<groupname> <mygroup>
     bkr group-modify --grant-owner-subgroup=<groupname> <mygroup>
     bkr group-modify --revoke-owner-subgroup=<groupname> <mygroup>
     bkr group-modify --grant-modify-jobs-subgroup=<groupname> <mygroup>
     bkr group-modify --revoke-modify-jobs-subgroup=<groupname> <mygroup>

  Beaker will not permit a group to be a member of another group if it forms
  a cycle.

  This feature will also make it possible to have an LDAP-defined group as
  part of a group that also allows manual addition of members through
  Beaker.

  .. _Closure Table: http://stackoverflow.com/questions/192220/what-is-the-most-efficient-elegant-way-to-parse-a-flat-table-into-a-tree/192462#192462

* User-level self service to request group membership (including the
  associated queue interface for group owners to approve/deny requests),
  or to remove yourself from groups. This capability is likely to be added
  in a later iteration. In the meantime, group owners may include
  information on requesting membership in the group description, and
  the list of group owners will be visible in the web UI.

* More fine-grained group permissions. The initial iteration has only three
  effective levels of access, job submission accounts, ordinary group members
  and group (co-)owners. It may be desirable to separate out the last level
  further in a future release:

  * Add/remove members (currently allowed for all co-owners)
  * Grant/revoke co-ownership (currently allowed for all co-owners)
  * Modify group display name and description (currently allowed for all co-owners)

  For ordinary members, it may also be desirable to separate out:

  * Ability to log into provisioned systems based on their SSH key (currently
    allowed for all group members with job modification privileges and a
    public SSH key registered in Beaker)
  * Ability to ack/nack job results (currently allowed for all group members
    with job modification privileges)
  * Ability to change the associated product (currently allowed for all
    group members with job modification privileges)
  * Ability to change the job retention policy (currently allowed for all
    group members with job modification privileges)

* Group deletion. The initial iteration does not allow groups to be deleted,
  or even hidden. If subgroup management is added, and the associated UI
  includes some form of list for group selection, then it is likely that
  group owners will be granted the ability to mark a group as *hidden*, so
  it doesn't show up in such lists. Creating a usable UI for the
  :ref:`proposal-system-pools` proposal may also lead to this feature
  being implemented.

* Default groups for job submission. The initial iteration always defaults to
  no group assocation for submitted jobs. It may be desirable to allow users
  to designate a "default group" for their jobs, such that members of that
  group will be granted access to their jobs if no other group is specified.

* Changing the group of a job after submission. While this is potentially
  useful in some respects, it will mean that the state of the provisioned
  systems (at least the set of authorized SSH keys and potentially the
  root password) will no longer match the nominated group. It may make more
  sense to allow additional groups to be granted edit access on the job
  

