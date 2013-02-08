.. _proposal-effective-job-priorities:

Effective Job Priorities
========================

:author: Nick Coghlan
:release: TBD


Abstract
--------

This proposal adds the ability for system owners to provide shared access
to systems, while allowing jobs submitted on behalf of particular groups to
be given precedence when the system is in high demand.


Dependencies
------------

This proposal depends on:

* :ref:`proposal-enhanced-user-groups`
* :ref:`proposal-system-pools`
* :ref:`proposal-event-driven-scheduling`


Proposal
--------

Granting access to systems in Beaker is currently "all or nothing": if you
grant another user permission to run jobs on a system you own, then the
scheduler will consider their jobs to have as much right to make use of
your systems as your own jobs do. The existing "Urgent", "High", "Normal",
"Medium", "Low" prioritisation scheme is applied globally to all recipes
currently queued whenever a system becomes available for automated use.

This proposal takes advantage of features added by the
:ref:`proposal-enhanced-user-groups`, :ref:`proposal-system-pools` and
:ref:`proposal-event-driven-scheduling` proposals to introduce the concept
of "Maximum effective priority" for the execution of jobs on a system.

The intent is to allow a system owner to, for example, leave the maximum
effective priority for jobs submitted on behalf of their own primary user
group at "Urgent", while restricting the maximum effective priority for all
other user groups to "Medium". With those settings, when the system in
question becomes "pending" (see :ref:`proposal-pending-systems-processing`)
then the queued recipes will be considered for execution in the following
precedence order, sorting first by effective priority, and then by nominal
priority::

    Urgent, Urgent (job submitted on behalf of designated group)
    High, High (job submitted on behalf of designated group)
    Normal, Normal (job submitted on behalf of designated group)
    Medium, Urgent (job NOT submitted on behalf of designated group)
    Medium, High (job NOT submitted on behalf of designated group)
    Medium, Normal (job NOT submitted on behalf of designated group)
    Medium, Medium (any job)
    Low, Low (any job)

The proposed mechanism for implementation is to change the "can submit
automated jobs" permission on system pools to record a list of
"Group, Maximum Effective Priority" pairs, rather than the simple
list of groups supported by the initial system pools design.

When the recipe queue is being sorted for a "Pending System" scheduling
event, then the effective priority for any given recipe will be
determined by looking at the associated group for the recipe's job
(defaulting to the "Everybody" group if the recipe was not submitted on
behalf of a group). The maximum effective priority for that recipe is the
*highest* maximum effective priority that group has on any of the system
pools to which the system belongs.

The actual effective priority of the recipe is then the lower of its
maximum effective priority and the nominal priority set on the job
itself.

Finally, sorting of the recipe queue is then by the
(Effective Priority, Nominal Priority) pair rather than solely by the
nominal priority:

+------------+------------+
| Effective  | Nominal    |
| Priority   | Priority   |
+============+============+
| Urgent     | Urgent     |
+------------+------------+
| High       | Urgent     |
|            +------------+
|            | High       |
+------------+------------+
| Normal     | Urgent     |
|            +------------+
|            | High       |
|            +------------+
|            | Normal     |
+------------+------------+
| Medium     | Urgent     |
|            +------------+
|            | High       |
|            +------------+
|            | Normal     |
|            +------------+
|            | Medium     |
+------------+------------+
| Low        | Urgent     |
|            +------------+
|            | High       |
|            +------------+
|            | Normal     |
|            +------------+
|            | Medium     |
|            +------------+
|            | Low        |
+------------+------------+


Open Questions
--------------

* Should we also support setting a "Minimum Priority" for groups? It's
  not clear this is necessary, and it *would* complicate the design and
  implementation. Current proposal is to leave it out of the initial
  implementation, and add it later if a compelling use case is presented
  that the current design can't address.
