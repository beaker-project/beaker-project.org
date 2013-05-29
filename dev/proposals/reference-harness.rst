Reference Harness
=================

:Author: Dan Callaghan
:Status: Proposed
:Target Release: 1.0

This proposal is for a "reference harness" implementation to be developed for 
Beaker. The purpose of the reference harness is to validate the proposed 
:ref:`harness API <harness-api>`, and to prototype some of the more radical 
harness features which have been proposed previously under the mantle of 
"Beaker Simple Harness":

* Fetching tasks directly from source control or elsewhere (bypassing the
  Beaker task library)
* No external dependencies
* Portability to older distros and non-Linux platforms
* IPv6 support (including dual-stack and IPv6-only)
* Clean, complete execution environment for tasks
* Installing task dependencies at the start of the task, instead of relying on 
  Anaconda ``%packages``

Explicit *non*-goals:

* 100% compatibility with Beah (RHTS)
* RHTS XML-RPC emulation
* Support for multi-host synchronization

As suggested by its name, the reference harness will also provide a starting 
point for others who want to develop their own harness, or want to expand the 
reference harness to meet their needs. In future the reference harness code may 
evolve into a STAF "service", a shim or wrapper layer or library for STAF and 
other harnesses, a complete replacement for Beah, or any of the above.

The reference harness will be a separate source tree from Beaker, and its 
release cycle will not (necessarily) be tied to Beaker releases. The 
user-defined harness support in Beaker will allow multiple versions of the 
reference harness to be used at any time, without interfering with Beaker 
itself.

Implementation language
-----------------------

The reference harness will be implemented in C, using mature, proven, 
cross-platform libraries where appropriate (for example, `glib`_, `libcurl`_, 
`libarchive`_).

By default the build will dynamically link against system libraries (making it 
acceptable for inclusion in Fedora), but it will also support statically 
linking against bundled versions of all dependencies except for the system 
libc. In this way it will be possible to use modern versions of utility 
libraries even on older distros and platforms, without introducing extra 
runtime dependencies.

Why not Python? Beah is written in Python, as are all known alternative harness 
implementations, and of course so is Beaker itself.

However, the harness needs to support Red Hat Enterprise Linux 3 where the 
system Python interpreter is version 2.2. Not only is it awkward to write code 
for such an old Python version, but no modern Python libraries support Python 
2.2. So the two alternatives are to ship an entire updated Python stack for 
RHEL3 (as Beah does), or to make the harness implementation compatible back to 
Python 2.2 without using any external libraries. Static linking is a good 
solution to this problem, because it lets us use modern versions of external 
libraries without introducing extra dependencies at runtime.

Static linking will also help on modern platforms, where users want to 
provision their recipe with a minimal package set and don't want the harness to 
"infect" it with additional packages which wouldn't normally be installed.

The job of the harness is also by its nature quite low-level and in some cases 
(for example, tty handling) may require calling platform libraries which are 
not exposed in Python.

Additionally, this will help to minimize the CPU, memory, and disk footprint of 
the harness.

.. _glib: http://developer.gnome.org/glib/
.. _libcurl: http://curl.haxx.se/libcurl/
.. _libarchive: http://www.libarchive.org/
