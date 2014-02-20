
.. _cli-guidelines:

Command line interface guidelines
=================================

.. note::

    Much of Beaker's command line interface may not currently meet
    these guidelines, due to historical inconsistencies.
    These guidelines are for new code.

Writing in Python
=================

Scripts should always be written in Python. The 'optparse' module
should be used, as Beaker is written for Python 2.6 on Red Hat Enterprise Linux
6 and derivatives.

When adding a new command to beaker client create a new module in
``bkr.client.commands``, using an existing module as a guideline.

When writing server side scripts, a module should be created in
``bkr.server.tools`` and then added to the 'console_scripts' section
of ``Server/setup.py``. Always prepend 'beaker' to the name of the script.
The '%files server' section in ``beaker.spec`` will need to be updated as well,
see the existing entries for the correct way to do this.

The above guidelines apply for scripts written for the lab controller as
well, except the 'console_scripts' section is updated in the
``LabController/setup.py`` file and the '%files lab-controller' section of
beaker.spec needs to be modified.


Comply with POSIX standards
===========================

Endeavour to stick to the `GNU standards <http://www.gnu.org/software/libc/manual/html_node/Argument-Syntax.html>`_
unless there is a good reason not to or anything in this guide expressly goes
against it.


Output
======

The primary goal of Beaker's CLI utilities are
for interfacing with scripts for the purposes of automation.

To this end, these utilities' defaults should be geared around this.
If an operation is mutative, no output should be printed to stdout.
If an operation is selective, machine readable output should be
printed to stdout (i.e JSON).

An exit code of zero indicates success, non-zero on failure.

These utilities are also often used by humans and so human
readable output is also highly desired. If there is no default output, than
make sure that the '--verbose' option is usable, and gives sensible and
appreciable output for human consumption. If the default output is designed to
be machine readable, then make sure there is a more human friendly option for
'--format'.

In case of errors and reporting error messages, tracebacks are fine.
However, ensure that the tracebacks give user friendly error messages.
This usually means that they will need to be raised in Beaker, rather than
allowing exceptions that do not originate in Beaker to cascade up to the user.


Backwards compatibility
=======================

Beaker's CLI is considered an API. See :ref:`harness-api`
regarding Beaker's policy on changing and designing APIs.
