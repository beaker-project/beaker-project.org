
.. _harness-api:

Stable Harness API
==================

:Author: Dan Callaghan
:Status: Proposed
:Target Release: TBD

Beah, the Beaker harness, currently uses XML-RPC methods exposed by 
beaker-proxy to communicate with Beaker. This API has evolved organically, in 
lock-step with Beah itself, and was derived in part from older APIs in RHTS. In 
some cases it is awkward to use. It has never been documented and is not 
considered a public or stable interface by the Beaker developers.

As a first step toward supporting alternative harnesses in Beaker, it is 
recognised that a stable, documented harness API is needed. This proposal is 
for a new harness API which covers roughly the same functionality as the 
existing XML-RPC API, but with a cleaner design. Developers who are working on 
integrating other harnesses with Beaker will be encouraged to use this new API. 
The existing XML-RPC API will remain as an internal-only implementation detail.

The existing XML-RPC API provides the following functionality to the harness:

* fetching recipe details
* fetching task details
* extending the watchdog
* marking tasks as running or completed
* recording results
* uploading logs

The new API covers the same areas. It also covers how Beaker configures the 
harness.

Environment variables
---------------------

Beaker will configure the following system-wide environment variables. When 
installed, a harness implementation must arrange to start itself on reboot and 
then configure itself according to these values.

``BEAKER_LAB_CONTROLLER_URL``
    Base URL of the Beaker lab controller. The harness communicates with Beaker 
    by accessing HTTP resources (described below) underneath this URL.

``BEAKER_LAB_CONTROLLER``
    The fully-qualified domain name of the lab controller to which this system 
    is attached. This will always match the hostname portion of 
    ``BEAKER_LAB_CONTROLLER_URL`` but is provided for convenience.
    
``BEAKER_RECIPE_ID``
    The ID of the Beaker recipe which this system is currently running. Use 
    this to fetch the recipe details from the lab controller as described 
    below.

``BEAKER_HUB_URL``
    Base URL of the Beaker server. Note that the harness should not communicate 
    with the server directly, but it may need to pass this value on to tasks.

HTTP resources
--------------

The lab controller exposes the following HTTP resources for use by the harness. 
All URL paths given below are relative to the value of the 
``BEAKER_LAB_CONTROLLER_URL`` environment variable.

When using the :http:method:`POST` method with the resources described below, 
the request body may be given as HTML form data 
(:mimetype:`application/x-www-form-urlencoded`) or encoded as a JSON object 
(:mimetype:`application/json`).

.. http:get:: /recipes/(recipe_id)/

   Returns recipe details. Response is in Beaker job results XML format, with 
   :mimetype:`application/xml` content type.

.. http:post:: /recipes/(recipe_id)/watchdog

   Extends the watchdog for a recipe.

   :form seconds: The watchdog kill time is updated to be this many seconds 
        from now.
   :status 204: The watchdog was updated.

.. http:post:: /recipes/(recipe_id)/status

   Updates the status of all tasks which are not already finished.

   :form status: The new status. Must be *Completed* or *Aborted*.
   :status 204: The task status was updated.
   :status 400: Bad parameters given.

   Typically the harness will update the status of each task individually as it 
   runs (see below). This is provided as a convenience only, for example to 
   abort all tasks in a recipe.

.. http:post:: /recipes/(recipe_id)/tasks/(task_id)/status

   Updates the status of a task.

   :form status: The new status. Must be *Running*, *Completed*, or *Aborted*.
   :status 204: The task status was updated.
   :status 400: Bad parameters given.
   :status 409: Requested state transition is invalid.

   Tasks in Beaker always start out having the *New* status. Once a task is 
   *Running*, its status may only change to *Completed*, meaning that the task 
   has completed execution, or *Aborted*, meaning that the task's execution did 
   not complete (or never began) because of some unexpected condition. Once 
   a task is *Completed* or *Aborted* its status may not be changed. Attempting 
   to change the status in a way that violates these rules will result in 
   a :http:statuscode:`409` response.

.. http:post:: /recipes/(recipe_id)/tasks/(task_id)/results/

   Records a task result. Returns a :http:statuscode:`201` response with a 
   :mailheader:`Location` header in the form 
   ``/recipes/(recipe_id)/tasks/(task_id)/results/(result_id)``.

   :form result: The result. Must be *Pass*, *Warn*, *Fail*, or *None*.
   :form path: Path of the result. Conventionally the top-level result will be 
        recorded as ``$TEST``, with sub-results as ``$TEST/suffix``, but this 
        is not required. If not specified, the default is ``/``.
   :form score: Integer score for this result. The meaning of the score is 
        defined on a per-task basis, Beaker intentionally enforces no meaning. 
        If not specified, the default is zero.
   :form message: Textual message to accompany the result. This is typically 
        short, and is expected to be displayed in one line in Beaker's web UI. 
        Use the log uploading mechanism to record test output.
   :status 201: New result recorded.
   :status 400: Bad parameters given.

.. http:put::
   /recipes/(recipe_id)/logs/(path:path)
   /recipes/(recipe_id)/tasks/(task_id)/logs/(path:path)
   /recipes/(recipe_id)/tasks/(task_id)/results/(result_id)/logs/(path:path)

   Stores a log file.

   :status 204: The log file was updated.

   Use the :mailheader:`Content-Range` header to upload part of a file.

.. http:get::
   /recipes/(recipe_id)/logs/(path:path)
   /recipes/(recipe_id)/tasks/(task_id)/logs/(path:path)
   /recipes/(recipe_id)/tasks/(task_id)/results/(result_id)/logs/(path:path)

   Returns an uploaded log file.

   Use the :mailheader:`Range` header to request part of a file.

.. http:get::
   /recipes/(recipe_id)/logs/
   /recipes/(recipe_id)/tasks/(task_id)/logs/
   /recipes/(recipe_id)/tasks/(task_id)/results/(result_id)/logs/

   Returns a listing of all uploaded logs.
   
   Possible response formats include an HTML index (:mimetype:`text/html`) or 
   an Atom feed (:mimetype:`application/atom+xml`). Use the 
   :mailheader:`Accept` header to request a particular representation. The 
   default is HTML.

Provisional period for the API
------------------------------

Before we commit to preserving a stable interface essentially forever, we need 
to have some confidence that the interface is useful and convenient for harness 
implementations to use. The best way to validate the interface is to build (or 
encourage others to build) harness implementations which use it.

Therefore, in its initial release the harness API will be considered 
"provisional" (and documented as such). In future releases we might make minor 
changes, removals, or additions in order to make the API more convenient for 
harness implementations, depending on feedback received after the initial 
release.

Once the API has been validated, it will be declared "stable" and no further 
backwards-incompatible changes will be made to it.

.. _user-defined-harness:

User-defined harness per recipe
-------------------------------

Part of the stable interface is standardizing how Beaker configures the 
harness. With this in place, we can add a simple way for users to select an 
alternative harness on a per-recipe basis.

A new kickstart metadata variable, ``harness``, will be defined. Its default 
value is ``beah``. When set to ``beah``, the existing kickstart template logic 
for configuring ``/etc/beah_beaker.conf`` and installing Beah is used. When set 
to any other value, Beah-specific parts of the template are skipped. Instead, 
the kickstart will contain a command to install the named harness.

This means the default behaviour is unchanged. If a user wants to use an 
alternate harness they can configure their job XML as desired, for example::

    <recipe ks_meta="harness=mylittleharness">
        <repos>
            <repo name="mylittleharness"
                  url="http://example.com/mylittleharness/el6/" />
        </repos>
        ...
    </recipe>

The generated kickstart for this recipe will contain the following line in 
a ``%post`` section::

    yum -y install mylittleharness

which will cause the mylittleharness package to be installed from the user's 
custom yum repo.

The value of the ``harness`` variable will be substituted directly into the 
``yum install`` command line. Note that this means the ``harness`` variable may 
contain any valid package specification accepted by yum, including one or more 
package names or absolute package URLs.

Rejected features
-----------------

The following ideas were brought up during discussions of this proposal, but 
they will not be implemented for the reasons given.

Adding tasks to a running recipe
++++++++++++++++++++++++++++++++

There is no mechanism for the harness to add tasks to an existing recipe. 
A recipe is an immutable sequence of one or more tasks for the harness to 
execute. A cloned recipe should produce the same execution as its 
original recipe, but this would be violated if the harness has added extra 
tasks.

In addition, adding tasks to an existing recipe introduces the possibility that 
the recipe's state could go backwards, from Completed to Running. This would 
violate an invariant which is relied on by a lot of code in Beaker, and by its 
users.

The recommended way for the harness to deal with the situation where a single 
task (from Beaker's point of view) actually contains many "sub-tasks" (from the 
harness' point of view) is to report multiple results for the task, each under 
a different path.

Deferred features
-----------------

The following ideas were brought up during discussions of this proposal, but 
they will not be addressed by this first provisional version of the API.

Harness configuration per recipe
++++++++++++++++++++++++++++++++

Currently the harness is configured in two ways: Beaker passes configuration 
through system-wide environment variables, as described above; and tasks 
provide metadata to the harness, such as their expected runtime and desired 
environment (``testinfo.desc`` for RHTS-format tasks). However, there is no 
mechanism to override this configuration from the job XML.

It is desirable to allow users to pass arbitrary harness-specific configuration 
from their job XML, either globally at the recipe level, or at the individual 
task level.

One possibility is to allow the job XML to override or extend the task metadata 
for a given task, by using the same fields as in ``testinfo.desc``. However, 
it's not clear how this could be represented in XML, nor how it would extend to 
harnesses/tasks which don't use the RHTS-like ``testinfo.desc`` metadata.

Complete representations for every resource
+++++++++++++++++++++++++++++++++++++++++++

By convention, all of the HTTP resources described above should also allow GET 
requests, returning some useful representation. However, designing future-proof 
response formats for all those resources is not trivial, so they are not 
included in this proposal. The monolithic results XML (as returned by 
:http:get:`/recipes/(recipe_id)/`) may not be the most ideal format, but it 
does include all information about a recipe (except for logs) and has the 
advantage of being well-established in Beaker.

Aborting an entire recipe set or job
++++++++++++++++++++++++++++++++++++

The XML-RPC API includes methods for the harness to abort an entire recipe set 
(``recipeset_stop``) or job (``job_stop``), but there is no equivalent 
functionality defined in this API. It is not clear that this capability is 
useful or desirable. An alternative is to offer the job submitter control over 
what kinds of failures result in aborting all or parts of the job (see for 
example `Nick Coghlan's suggestions 
<http://thread.gmane.org/gmane.comp.systems.beaker.devel/451/focus=479>`_).

Harness check-in
++++++++++++++++

As harness implementations proliferate, it may be useful to encourage harnesses 
to report their name, version, and configuration to Beaker as a "harness 
check-in" step at the start of the recipe. Beaker can display this information 
to users, to make it clear which harness implementation ran their recipe.

In future a check-in step may be formalised as part of this API, but for now 
harnesses are encouraged to report these details as a recipe log with 
a consistent and obvious name (for example, ``harness-checkin.log``).

Storing results and logs in external systems
++++++++++++++++++++++++++++++++++++++++++++

The are no plans to integrate Beaker itself with any specific tool for managing 
test runs and results. But a harness implementation may choose to report its 
results to an external tool in addition to (or instead of) reporting results to 
Beaker. In this case it would be useful for the Beaker results to contain 
a reference to the corresponding results in the external tool.

One possibility is to allow "remote" logs -- that is, logs registered in Beaker 
but stored elsewhere. Beaker would record only the remote URL associated with 
the log.

Another possibility is to allow an optional URL to be associated with each 
result, which is presented as a hyperlink in Beaker's web UI.
