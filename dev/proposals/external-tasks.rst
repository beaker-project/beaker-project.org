.. _proposal-external-tasks:

External Tasks for Jobs
=======================

:Author: Bill Peck, Dan Callaghan
:Status: Implemented
:Release: `0.16 <https://beaker-project.org/docs/whats-new/release-0.16.html#external-tasks>`__

This document proposes de-coupling recipe tasks in Beaker from the task 
library. It will be possible to specify tasks in a recipe using an external URL 
without any corresponding task in Beaker's task library.

This feature requires support on the harness side for fetching and unpacking 
tasks from arbitrary URLs. This proposal does not cover updating Beah to 
support external tasks. In this initial iteration, external tasks will only be 
usable with alternative harnesses.

Background and rationale
------------------------

The ability to run tasks directly from source control or other arbitrary URLs 
has been a long-standing feature request in Beaker. It addresses the 
shortcomings of the centralized, linear, forwards-only versioning model of the 
task library, by allowing users to:

* test individual forks, feature branches, or development versions of a task
  without affecting other users of the same task
* run an exact revision of a task, for reproducing previous results or testing
  older versions
* devise their own branching strategy for their tasks (for example, maintaining
  separate branches for different distro families)

An expanded recipe-task model
-----------------------------

Currently each "recipe-task" in Beaker must have a correspondingly named entry 
in the task library. Beaker stores the recipe-task as a reference to the task 
library record.

The database schema will be altered so that:

* the relationship from recipe-task to the task library is optional
* each recipe-task stores the name of the task that is to be run
* each recipe-task can optionally store the version of the task that was run
* each recipe-task can optionally have an associated "fetch URL" where the task
  source code is fetched from

The harness API will be extended to allow harness implementations to report the 
name and version of a task back to Beaker.

Specifying name and fetch URL for recipe-tasks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is important that a recipe-task always have a sensible name, so that recipe 
results can be meaningfully displayed even before the recipe starts. This will 
also avoid backwards compatibility issues with external tools expecting every 
recipe-task to have a proper task name. Therefore, when a new recipe is 
submitted Beaker will use the following rules to determine the name of each 
recipe-task.

If the submitted XML only specifies a name for the task, the task must exist in 
Beaker's task library. The recipe-task name is set to the given name. This 
represents no change from the current Beaker behaviour and preserves 
compatibility for harness implementations.

::

    <task name="/distribution/reservesys" />

If the submitted XML specifies both a name and a fetch URL, the task need not 
exist in Beaker's task library. The recipe-task name is set to the given name, 
the fetch URL is set to the given URL, and the recipe-task is not associated 
with any task library entry (even if the name matches a task library entry). 

Beaker will treat the fetch URL as an opaque string and does not attempt to 
validate or fetch it. The details of how to fetch, unpack, and run the task are 
left up to the harness implementation.

::

    <task name="/distribution/reservesys">
      <fetch url="git://example.com/tasks/reservesys#master" />
    </task>

If a fetch URL is specified, a subdirectory may also be specified. This is for 
cases where the fetch URL points at an archive or source repository which 
contains multiple tasks. The subdirectory indicates to the harness where it 
should look to find the task to run. This is represented as a separate 
attribute in the XML, because URLs do not have a standard mechanism to express 
paths within an archive or repository.

::

    <task name="/distribution/reservesys">
      <fetch url="git://git.beaker-project.org/beaker-core-tasks#master"
             subdir="reservesys" />
    </task>

The ``name=""`` attribute may be omitted if a fetch URL is specified. In this 
case there is no associated task library entry. Initially Beaker will set the 
recipe-task name to the value of the fetch URL combined with the subdirectory, 
so that it has a distinct and meaningful value by default, but it is expected 
that the harness will later update the recipe-task name to some "prettier" 
value (for example, by extracting the name from :file:`testinfo.desc`).

::

    <task>
      <fetch url="git://git.beaker-project.org/beaker-core-tasks#master"
             subdir="reservesys" />
    </task>

Fetch URLs in recipe XML
~~~~~~~~~~~~~~~~~~~~~~~~

When a recipe-task is associated with a task library entry (no fetch URL), the 
recipe XML served by Beaker will include an ``<rpm/>`` element with the details 
of the RPM from the task library. The harness should install the named RPM 
using the system package installer. This represents no change from the current 
Beaker behaviour and preserves compatibility for harness implementations.

::

    <task name="/distribution/reservesys">
      <rpm name="beaker-core-tasks-distribution-reservesys"
           path="/mnt/tests/distribution/reservesys" />
      ...
    </task>

When a recipe-task has a fetch URL, the recipe XML served by Beaker will 
instead contain a ``<fetch/>`` element, matching the submitted job XML::

    <task name="/distribution/reservesys">
      <fetch url="git://git.beaker-project.org/beaker-core-tasks#master"
             subdir="reservesys" />
      ...
    </task>

Version for recipe-tasks
~~~~~~~~~~~~~~~~~~~~~~~~

For recipe-tasks which have an entry in the task library, Beaker will copy the 
current version from the task library to the recipe-task when the recipe is 
Scheduled (this is the point at which the task library snapshot is generated). 
This is the version of the task which should be run (if all goes well).

For recipe-tasks with a fetch URL, the version will be initially empty. Harness 
implementations can update Beaker with the version of the task which was run. 
This is particularly important when fetching from source control. For example, 
a harness implementation might set the version to ``<branch>@<sha>`` for a task 
fetched from git.

Beaker will treat the version as an opaque string. The format of the version 
string is left up to the harness implementation.

The versions will be displayed with the recipe results in Beaker's web UI and 
included in the job results XML.

Harness API
-----------

The following new HTTP resource will be available on the lab controller. 
Harness implementations can use this to update the name and version of 
a recipe-task.

.. http:patch:: /recipes/(recipe_id)/tasks/(task_id)

   Updates the recipe-task. Accepts JSON :mimetype:`application/json` or 
   :mimetype:`application/x-www-form-urlencoded` with the following 
   keys/parameters: *name*, *version*, *status*, *message*.

Deferred features
-----------------

This proposal does not provide any mechanism for fetching tasks from source 
control with the current version of Beah. If a recipe uses external tasks, it 
must also use a suitable harness implementation. In future it may be possible 
to implement task fetching in Beah itself, or to supply a shim task which can 
handle task fetching when executed by Beah.

In a future release the recipe-task schema could be extended further, to make 
a copy of the RPM name and version when the recipe's task library snapshot is 
created. This would fix two outstanding bugs caused by inconsistencies between 
the Beaker database and the task library snapshot: :issue:`1040258` and 
:issue:`1044934`.
