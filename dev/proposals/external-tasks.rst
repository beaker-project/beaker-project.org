.. _proposal-external-tasks:

External Tasks for Jobs
=======================

:Author: Bill Peck
:Status: Proposed
:Target Release: 0.16

Abstract
--------

This is a proposal to add support for specifying tasks that are not
registered in the beaker scheduler.  Advantages of removing the task
library from beaker are as follows:

* Tasks can be retrieved directly from a version control system
* Developers can make changes to existing tests in a test branch and verify
  those changes before affecting production runs.
* createrepo will no longer need to be run on the beaker scheduler.  This
  will greatly reduce the load.
* For tasks retrieved directly from git the sha1 can be stored.  This allows
  for running previous jobs with the exact same version of the task.  Current
  system would require you to re-submit the old version and that would affect
  all jobs, not just yours.
* When a release goes gold the tasks can be branched with that release name.
  This allows z-stream testing to use the same task version as gold.
* Moves test plan management out of beaker (excluded families)


Accepting Jobs
--------------

When specifying a task in a beaker job it is only valid to specify either a
task from the beaker library or an external task.

Example of specifying a task from the beaker libary::

        <task name="/task/from/beaker/library"/>

Example of specifying an external task that is not registered in the beaker
library::

        <task>
         <fetch url="git://server.domain.com/path/to/repo?branch#path/in/branch"/>
        </task>

Alternativly we could drop fetch and task would either have an attribute name
or url but never both.


Harness Support
----------------------

When a task is specified from the beaker library, the rpm node will be filled
in for the task::

        <task name="/task/from/beaker/library">
         <rpm name="beaker-task-1.11.noarch.rpm" path="/mnt/tests/task/from/beaker/library"/>
        </task>

The harness should install the rpm name via the system package installer. The
harness can assume that the neccasary repos are configured for this to
succeed.

When a task is specified via the external url the harness is responsible for
fetching the task. Beaker will do no verification of the url.


Reporting
---------

For the first time we will be able to support multiple task repositories.
The down side to this is that task names could be duplicated and conflict.
In order to keep task names unique the url will be used as the task name.

This presents another potential problem if the url is long.  The use of css's
overflow attribute may be one option if it can truncate from the beginnning.
There will need to be some way for the user to see the full url though.
Possibly using a hover option?

Truncate example::

        ...ernel?master#filesystems/nfs/sanity

Hover would show::

        git://git.example.com/tests/kernel?master#filesystems/nfs/sanity

The user will still be able to use wildcards in the task name search which
will make it easy to compare task results from different branches if needed.
