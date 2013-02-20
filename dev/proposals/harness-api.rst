
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

API details
-----------

The API will consist of the following HTTP resources. All URL paths are 
relative to the base URL of the beaker-proxy service on the lab controller 
(that is, ``http://$LAB_CONTROLLER:8000/``).

.. http:get:: /recipes/(recipe_id)/

   Returns recipe details. Response is in Beaker job results XML format, with 
   :mimetype:`application/xml` content type.

.. http:post:: /recipes/(recipe_id)/watchdog

   Extend the watchdog for a recipe.

   :form seconds: The watchdog kill time is updated to be this many seconds 
        from now.
   :status 204: The watchdog was updated.

.. http:post:: /recipes/(recipe_id)/tasks/(task_id)/status

   Update the status of a task.

   :form status: The new status. Must be *running*, *completed*, or *aborted*.
   :status 204: The task status was updated.
   :status 400: Bad parameters given.
   :status 409: Requested state transition is invalid.

   Tasks in Beaker always start out having the *new* status. Once a task is 
   *running*, its status may only change to *completed*, meaning that the task 
   has completed execution, or *aborted*, meaning that an unrecoverable error 
   prevented the harness from executing the task. Once a task is *completed* or 
   *aborted* its status may not be changed. Attempting to change the status in 
   a way that violates these rules will result in a :http:statuscode:`409` 
   response.

   Note that if a task is *aborted* the entire recipe is aborted.

.. http:post:: /recipes/(recipe_id)/tasks/(task_id)/results/

   Record a task result. Returns a :http:statuscode:`201` response with a 
   :mailheader:`Location` header in the form 
   ``/recipes/(recipe_id)/tasks/(task_id)/results/(result_id)``.

   :form result: The result. Must be *pass*, *warn*, *fail*, or *none*.
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

   Upload a log file.

   :status 204: The log file was updated.

   Use the :mailheader:`Content-Range` header to upload part of a file.

.. http:post::
   /recipes/(recipe_id)/remote-logs/
   /recipes/(recipe_id)/tasks/(task_id)/remote-logs/
   /recipes/(recipe_id)/tasks/(task_id)/results/(result_id)/remote-logs/

   Similar to the above, this creates a new log record against the recipe, 
   task, or result respectively. However the log is not uploaded to Beaker 
   directly, only a URL reference to a remote log is stored in Beaker.

   :form url: URL of the remote log. For example, this might be the URL of the 
        test results which the harness has uploaded to an external test case 
        management system.
   :form label: Optional label, to be used as anchor text when this log is 
        displayed as an HTML link. If not given, the URL itself is used.
   :status 201: New remote log recorded.
   :status 400: Bad parameters given.

In addition to the above HTTP resources, the interface also specifies that 
Beaker will configure the post-install environment as follows. When installed, 
a harness implementation must arrange to start itself on reboot and then 
configure itself according to these values.

* The file ``/root/RECIPE.TXT`` will contain the ID of the recipe which this 
  system is currently running.
* The environment variable ``LAB_CONTROLLER`` will be set to the FQDN of the 
  lab controller which this system is attached to.
* The environment variable ``BEAKER`` will be set to the absolute base URL of 
  the Beaker server.

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
