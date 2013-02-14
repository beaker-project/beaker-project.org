.. _proposal-enhanced-user-groups:

Enhanced User Groups
====================

:author: Dan Callaghan
:editors: Nick Coghlan, Raymond Mancy
:release: Beaker 1.0


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

This proposal enhances the capabilities of the group model by:

* allowing users to manage their own groups, rather than requiring
  administrator involvement
* allowing administrators to create groups that are automatically derived
  from groups already defined in an LDAP server
* allowing jobs to be submitted on behalf of a group

A Beaker user can be in zero or more groups, and any Beaker user may
create a new group at any time.

On each group, the only permission that can be granted is "group ownership".


Detailed Use Cases
------------------

Self-Service User Groups
~~~~~~~~~~~~~~~~~~~~~~~~

* I want to create a new group. (BZ#908172)

Through the web UI:

   Select "Hello -> My Groups" from the menu, then click "Create". Enter
   a group name and display name and click "Create".

Through the ``bkr`` cli::

   bkr group-create --display-name="My New Group" <mynewgroup>

A new group is created, with one member (you) who is also the group owner.
The change is recorded in the "Group Activity" log.

* I am a Beaker administrator and I want to create a new group whose
  membership is populated from LDAP. (BZ#908173)

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
once per day.

* I want to view the details of a group of which I am a member. (BZ#541282)

Through the web UI:

   Select "Hello -> My Groups" from the menu, then click the name of the
   group you are interested in to go to its group page.

Through the ``bkr`` cli::

   bkr group-members <mygroup>

* I want to add other users to a group I own. (BZ#908176)

Through the web UI:

   Go to the group page. Under the membership list, enter the user's
   username and click "Add to Group".

Through the ``bkr`` cli::

   bkr group-manage --add-member=<someusername> <mygroup>

The user is added to the group. The change is recorded in the
"Group Activity" log.

* I want to grant/revoke another member owner rights to the group. (BZ#908174)

Through the web UI:

   Go to the group page. Find the other user in the membership list,
   check/uncheck the checkbox in the "Owner" column, then click "Save".

Through the ``bkr`` cli::

   bkr group-manage --grant-owner=<someusername> <mygroup>
   bkr group-manage --revoke-owner=<someusername> <mygroup>

The user is granted owner rights, making them a co-owner of the group.
The change is recorded in the "Group Activity" log.

* I want to remove a member from a group I own. (BZ#908178)

Through the web UI:

   Go to the group page. Find the user in the membership list, and click "Remove".

Through the ``bkr`` cli::

   bkr group-manage --remove-member=<someusername> <mygroup>

The user is removed from the group. The change is recorded in the
"Group Activity" log.


Group Job Management
~~~~~~~~~~~~~~~~~~~~

* I want to submit a job for a particular group (of which I am a member).
  (BZ#908183)

Through the job XML:

  Add an optional attribute ``group="somegroup"`` to the ``<job/>`` element
  directly to the job XML.

Through the ``bkr`` cli::

  Pass the ``--job-group=somegroup`` option to a workflow command.

The job will be owned by that group and the user that submitted the job.
There can be only one "job-group" per job, thus multiple groups having ownership
of a single job is not possible. All members of the group will be able to
ack/nack, change priority, edit whiteboard, and change retention tag.  The root
password used in the job will be the group root password (if one is set),
otherwise it will be the root password set in the preferences of the submitting
user. The public SSH keys of all group members will be added
to /root/.ssh/authorized_keys.

* I want to view a list of jobs for all groups of which I am a member.
  (BZ#908185)

The default filter for the "My Jobs" page will include all jobs the user
can manage, including those the user submitted themselves, as well as
those submitted on behalf of a group of which the user is a member.

* I want to view a list jobs for a particular group (of which I am a member).

Both the "My Jobs" page and the main job list will allow filtering by
the owning group. This will permit users to display jobs owned by
particular groups (whether they are a member of those groups or not), as
well as displaying only the jobs that were not submitted on behalf of a
group at all.

* I want to set the shared root password to be used in all jobs for a particular group. (BZ#908186)

Go to the group page. Enter the root password in the "Root Password" field and click "Save". The root password may be given in hashed form (suitable for /etc/shadow) or in the clear.
Or: bkr group-manage --root-password=<thevalue>
The  given root password will be used when provisioning jobs for this group.  It will be visible on the group page to other members of the group. If  the password is given in the clear Beaker will *not* automatically hash it before storing, to make it easier to share amongst the group. (This behaviour differs from that for individual root passwords set on the Preferences page - when given in the clear, individual passwords are automatically hashed before storage) Changes to the group's root password are recorded in the "Group Activity" log  (this only records when the change occurred, and the user that made the  change - the password itself is not recorded in the activity log, even  in hashed form).



Deferred Features
-----------------

These additional features are under consideration, but have been deliberately
omitted in order to reduce the complexity of the initial iteration of the
design:

* Adding other groups as members of a group. The initial iteration
  does not allow groups to be members of other groups, which introduces
  potential concerns about scalability in large organisations. A subgroups
  model, with an implementation based on the `Closure Table`_ design, would
  address this concern. If there's time, we'll look into adding this to 1.0,
  otherwise it will be considered for inclusion in 1.1.

  The draft web UI design is the same as that for managing group members, but
  using the "Sub-group" list instead of the "Members" list. For the CLI::

     bkr group-manage --add-subgroup=<groupname> <mygroup>
     bkr group-manage --remove-subgroup=<groupname> <mygroup>
     bkr group-manage --grant-owner-subgroup=<groupname> <mygroup>
     bkr group-manage --revoke-owner-subgroup=<groupname> <mygroup>

  Beaker will not permit a group to be a member of another group if it forms
  a cycle.

  .. _Closure Table: http://stackoverflow.com/questions/192220/what-is-the-most-efficient-elegant-way-to-parse-a-flat-table-into-a-tree/192462#192462

* User-level self service to request group membership, or to remove yourself
  from groups. This capability is likely to be added in a later iteration.

* More fine-grained group permissions. The initial iteration has only two
  levels of access, ordinary group members and group (co-)owners. It may be
  desirable to separate out the following four explicit permissions in a
  future release:

  * Add/remove members (currently allowed for all co-owners)
  * Grant/revoke co-ownership (currently allowed for all co-owners)
  * Submit jobs on behalf of the group (currently allowed for all members)
  * Manage jobs on behalf of the group (currently allowed for all members)

* Group deletion. The initial iteration does not allow groups to be deleted,
  or even hidden. If subgroup management is added, and the associated UI
  includes some form of list for group selection, then it is likely that
  group owners will be granted the ability to mark a group as *hidden*, so
  it doesn't show up in such lists. Creating a useful UI for the
  :ref:`proposal-system-pools` proposal may also lead to this feature
  being implemented.
