
.. _cli-guidelines:

Command line interface guidelines
=================================

.. note::

    Much of Beaker's command line interface may not currently meet
    these guidelines, due to historical inconsistencies.
    These guidelines are for new code.

Writing in Python
-----------------

Scripts should always be written in Python. The :py:mod:`optparse` module
should be used, as Beaker is written for Python 2.6 on Red Hat Enterprise Linux
6 and derivatives.

When adding a new command to beaker client create a new module in the 
:py:mod:`bkr.client.commands` package, using an existing module as a guideline.

When writing server side scripts, a module should be created in the 
:py:mod:`bkr.server.tools` package and then added to the ``console_scripts`` 
key in :file:`Server/setup.py`. Always prepend ``beaker-`` to the name of the 
script. The ``%files server`` section in :file:`beaker.spec` will need to be 
updated as well, see the existing entries for the correct way to do this.

The above guidelines apply for scripts written for the lab controller as well, 
except the ``console_scripts`` key is updated in the 
:file:`LabController/setup.py` file and the ``%files lab-controller`` section 
of :file:`beaker.spec` needs to be modified.


Comply with POSIX standards
---------------------------

Endeavour to stick to the `GNU standards <http://www.gnu.org/software/libc/manual/html_node/Argument-Syntax.html>`_
unless there is a good reason not to or anything in this guide expressly goes
against it.


Output
------

The primary goal of Beaker's CLI utilities are
for interfacing with scripts for the purposes of automation.

To this end, these utilities' defaults should be geared around this.
If an operation is mutative, no output should be printed to stdout.
If an operation is selective, machine readable output should be
printed to stdout (i.e JSON).

An exit code of zero indicates success, non-zero on failure.

These utilities are also often used by humans and so human
readable output is also highly desired. If there is no default output, than
make sure that the ``--verbose`` option is usable, and gives sensible and
appreciable output for human consumption. If the default output is designed to
be machine readable, then make sure there is a more human friendly option for
``--format``.

Whenever it is practical to implement, CLI users should not see Python 
tracebacks for things that we anticipate them getting wrong, as the traceback 
is just irrelevant noise in that situation. Instead, the CLI should catch the 
relevant exception, display a clear message on stderr that explains what went 
wrong (and ideally how to fix it), and then exit with a non-zero return code.

The argument parsing library automatically takes care of this for many simpler 
user errors, and the client command framework should automatically handle it 
for authentication errors and most server side data validation and access 
control errors.

This CLI requirement also impacts the server code handling HTTP requests, as it 
usually means that an appropriate exception should be raised in Beaker itself, 
rather than allowing exceptions from library code to cascade up to the web 
framework and hence on to the CLI user. The 
:py:func:`bkr.server.flask_util.convert_internal_errors` context manager is 
provided specifically for this purpose.

However, care needs to be taken not to hide genuine programming errors by 
misreporting them as errors in the user's input.


Backwards compatibility
-----------------------

Beaker's CLI is considered an API. See :ref:`api-stability`
regarding Beaker's policy on changing and designing APIs.
