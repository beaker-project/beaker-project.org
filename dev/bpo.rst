Maintaining the beaker-project.org infrastructure
=================================================

This document describes the configuration and upgrade procedures for the host 
running beaker-project.org. If you just want to update the web site at 
http://beaker-project.org/ see its `README 
<http://git.beaker-project.org/cgit/beaker-project.org/tree/README>`__.

Configuration management
------------------------

The contents of ``/etc`` are tracked using `etckeeper 
<http://joeyh.name/code/etckeeper/>`_. After making config changes, run 
``etckeeper commit`` to record them.

Remote access
-------------

Remote access is by SSH key authentication only. Speak to a Beaker developer if 
you need a user account to be created.

Lighttpd
--------

Lighttpd listens on port 80 and serves all web traffic for 
\*.beaker-project.org. SSL on port 443 is disabled since we do not have any SSL 
certificates.

The base config is in the standard place (``/etc/lighttpd/lighttpd.conf``). 
Config for each name-based virtual host is included from the corresponding file 
in ``/etc/lighttpd/vhosts.d/``.

At present, a custom rebuild of the lighttpd package is installed to fix `bug 
912546 <https://bugzilla.redhat.com/show_bug.cgi?id=912546>`_. Make sure not to 
upgrade/downgrade to a version of the package which is not patched (for 
example, when upgrading to a new Fedora release).

Git daemon
----------

The git daemon serves read-only git repos on port 9418.

At present the Fedora package for git-daemon uses xinetd, but we are running it 
as a systemd service instead (defined in 
``/etc/systemd/system/git-daemon.service``).

Tomcat
------

Tomcat listens on port 8080 to serve the Gerrit application. This port is not 
open to the world, it is proxied by the gerrit.beaker-project.org vhost in 
lighttpd. Gerrit also listens on port 29418 for its fake SSH service.

Note that we are *not* using Gerrit's control script ``gerrit.sh`` and we are 
*not* running the embedded Jetty container.

There is no standard way to install or upgrade Java web apps so the following 
layout has been devised. Gerrit WARs are kept in ``/var/lib/gerrit``. Gerrit 
"site directories" are kept underneath that path. There is one site, named 
beaker. So the "site path" (as mentioned in the Gerrit docs) is 
``/var/lib/gerrit/beaker``. The ``etc`` directory for the Gerrit site is then 
symlinked to ``/etc/gerrit/beaker``, so that it is tracked by etckeeper.

Tomcat's ``/etc/tomcat/server.xml`` file defines one virtual host, 
gerrit.beaker-project.org, with applications stored in 
``/var/lib/tomcat/gerrit-webapps``. The ROOT application for that virtual host 
is then symlinked to the WAR inside the Gerrit site path.

To upgrade Gerrit, follow these steps::

    cd /var/lib/gerrit
    wget https://gerrit-releases.storage.googleapis.com/gerrit-2.6.1.war
    java -jar gerrit-2.6.1.war init -d beaker

The upgrade process first prompts for settings. You can accept all defaults -- 
the defaults are the existing configuration. Then it will perform any necessary 
schema upgrades.

Also check that the permissions and ownership of 
``/etc/gerrit/beaker/secure.config`` have not been overwritten (it must be 
owned root:tomcat with mode 0640).

Finally, force Tomcat to unpack the new WAR::

    systemctl stop tomcat.service
    rm -rf /var/lib/tomcat/gerrit-webapps/ROOT/
    systemctl start tomcat.service

SMTP
----

Postfix accepts mails for beaker-project.org on port 25 (as well as relaying 
from localhost, e.g. Gerrit notifications).

All user accounts (including root) have a mail alias in ``/etc/aliases`` 
pointing to their real address. No mail should ever be delivered to the local 
system.
