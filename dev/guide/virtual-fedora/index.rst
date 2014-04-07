.. _virtual-fedora:

Setting up a Beaker test bed
----------------------------

This guide will help you setup a `Beaker <http://beaker-project.org>`__
test bed using two virtual machines (VMs). To setup the VMs, we
will use `libvirt <http://libvirt.org>`__ with `qemu
<http://qemu.org>`__ driver. The host system is assumed to be running
an installation of Fedora 20 (although the instructions should also
work with any other Linux distribution with a suitably recent version
of libvirt).

.. note::

   While there are currently no known major compatibility issues running
   Beaker on Fedora 20, running the Beaker server components on
   Fedora is still considered an *experimental* configuration. Beaker's
   continuous integration system currently only tests compatibility of the
   server components with Red Hat Enterprise Linux 6.


Basics of a Beaker test bed
===========================

Four major components are required to be in place to setup a Beaker
test bed (also referred to as a Beaker instance):

- *Server*: The Beaker server hosts the web application and the job
  scheduler (and other components such as tasks and the harness
  repository). There is only one server per Beaker instance.

- *Lab controller*: The lab controller is in charge of a lab of test
  systems (described next) and is responsible for receiving and
  acting upon the job requests from the server, setting up the test
  machines (provisioning) and as a proxy between the test systems and
  the server. There can be one or more lab controllers per Beaker
  instance.

- *Test systems*: As their name implies, these are the systems on
  which the tests are actually run. Note that the current
  design of Beaker is such that a test system always starts from
  scratch. At the start of a job, the system is *powered on*, and an
  operating system as specified by the job is installed (In Beaker's
  terminology, this is referred to as *system provisioning*). A test
  system must be associated with a lab controller for Beaker to be
  able to run a job on it.

- *Lab DHCP server*: The test systems should be connected to a network
  with a DHCP server, configured appropriately to fetch the boot
  images from the TFTP server running on the lab controller(s).

For our test bed, we will setup the server and the lab controller on
the same VM and use a second VM as a test system. The lab DHCP server's
role is fulfilled by a ``dnsmasq`` instance automatically started by
``libvirt`` (see `here
<http://wiki.libvirt.org/page/VirtualNetworking#DNS_.26_DHCP>`__ for
more) and we shall configure it appropriately to allow network booting
from the TFTP server running on the lab controller VM.

.. note::

   It is worth noting that this guide *exclusively* aims at being an
   easy way to get started with Beaker - both from an user's and a
   developer's perspective. Hence, no attempt has been made to setup
   a secure and robust installation ready to be deployed for any form
   of production use. Refer to the `administration guide
   <../../../docs/admin-guide/>`__ for help on
   setting up a Beaker instance for production use.

In the next sections, we will see how we can setup Beaker. There are
Bash scripts whereever possible to make the setup easier. However, it
is encouraged that you read the guide before executing them,
since that will help you understand the different steps which may be
useful if you run into an error during the process.

Setting up libvirt
==================

I assume you have libvirt installed correctly on your *host
system*. In case you need help, this `guide
<http://fedoraproject.org/wiki/Getting_started_with_virtualization>`__
may be of help. We will create a new storage pool to store the images for the two
VMs using this script. Download the `script
<scripts/setup_storage.sh>`__ and run it as root user.

Next, we will setup the ``default`` network using this `script
<scripts/setup_network.sh>`__.

.. note::

   This script will *overwrite* your current default network config.
   If you have a customized configuration for your network,
   you should manually add the required configuration described in
   this guide to avoid overwriting the existing configuration.

Download and run the script as the root user.

.. note::

   We are using libvirt's system instance (instead of a session
   instance), and hence the scripts are required to be run as root, as
   it allows us to do away with specifying the instance in every script.

There are a number of things in the network config which is worth
noting such as the DNS and DHCP server configurations and the
configuration of the TFTP server for PXE booting.

The DNS configuration is as follows::

    <dns>
      <host ip='192.168.122.102'>
        <hostname>beaker-server-lc.beaker</hostname>
      </host>
      <host ip='192.168.122.103'>
        <hostname>beaker-test-vm1</hostname>
      </host>
    </dns>

The VM which will act as the server and the lab controller will be
setup with the hostname ``beaker-server-lc.beaker`` (with an IPv4 address:
192.168.122.102) and the test VM will have the hostname
``beaker-test-vm1`` (with an IPv4 address:
192.168.122.103). Setting up the DNS as above allows the VMs to communicate
with each other using their hostnames.

.. note::

   At this stage, you must also include the entry for your Beaker
   server in your host's :file:`/etc/hosts` file, so that you can
   access the Beaker instance from your host system's browser using the hostname::

       192.168.122.102 beaker-server-lc.beaker

   The rest of the guide assumes that this mapping exists.

The tftp and DHCP configuration is as follows::

    <tftp root='/var/lib/tftpboot' />
    <dhcp>
      <range start='192.168.122.2' end='192.168.122.254' />
      <host mac='52:54:00:c6:73:4f' name='beaker-server-lc.beaker' ip='192.168.122.102' />
      <host mac='52:54:00:c6:71:8e' name='beaker-test-vm1' ip='192.168.122.103' />
      <bootp file='pxelinux.0' server='192.168.122.102' />
    </dhcp>

The two ``<host>`` elements ensure that the VMs with the hardware
addresses as above *always* get the hostname and the IPv4 address as
above. The hardware addresses are set during the setup and hence this
makes sure that both the VMs get the same IP everytime they are
started.

As earlier discussed, a test system is provisioned at the start of
every job. The test system is booted using PXE booting and the element
``<bootp>`` in the above configuration specifies the filename and the
PXE server. As you can see, the IPv4 address of the TFTP server is
that of the server/lab controller VM. The tftp root directory is given by the element
``<tftp>`` in the above configuration.

Next, we will setup the first VM which will be the server and the lab
controller.

Setting up Server and Lab controller
====================================

Installing
~~~~~~~~~~
This is to be done on the *host system*. First download this
`kickstart <scripts/beaker-server-lc.ks>`__ which installs the server and lab
controller and other miscellaneous packages. Then, from the directory where
the kickstart file was downloaded, run `this script
<scripts/create_server_lc_vm.sh>`__ to create a virtual machine and
start a Fedora 20 installation using the downloaded kickstart file.

You may want to replace the Fedora download location in the Bash script and
the kickstart by one closer to your geographical location.

Setup server
~~~~~~~~~~~~

Once the installation has completed, login to the test VM as the root
user either via SSH from your host or in the VM itself (The root
password is set to ``fedora``).

We will now setup the Beaker database on the local MariaDB
server. The following steps need to be completed:

- Setup MariaDB for unicode support
- Create Beaker database (``beaker``) and give permissions to Beaker's user
- Initialize Beaker's database

Download and run this `script <scripts/setup_db.sh>`__ to perform the
above steps. The script will also ask you for the username, password
and email for creating an ``admin`` account. It is recommended to use
``admin`` as the username and a password of your choice.

Start the Apache server and the Beaker daemon (scheduler)::

    # systemctl start httpd
    # systemctl start beakerd

You may want to confirm that both the services are running (Use
``# systemctl status httpd`` and ``# systemctl status beakerd`` respectively).

Enable the ``httpd`` and ``beakerd`` services so that they start on system boot::

    # systemctl enable httpd beakerd

To be able to access the server web application from your host system,
add the ``http`` service to the ``default`` zone of ``firewalld`` and
reload the firewall rules::

    # firewall-cmd --permanent --add-service=http
    # firewall-cmd --reload

To test that the web application and the database has been setup
correctly, visit the URL: ``http://beaker-server-lc.beaker/bkr/`` from
your host system's browser and try to login as the admin user you created
earlier. If you are able to login, it means we are good to setup the
lab controller.

Setup lab controller
====================

We will now add a lab controller to the Beaker server. Go to
``http://beaker-server-lc.beaker/bkr/labcontrollers/new`` and add the
details for the lab controller. The FQDN should be
``beaker-server-lc.beaker`` (same as the server as earlier explained),
username should be ``host/localhost.localdomain`` and password as
``password`` and email as ``root@localhost.localdomain``. These are
default settings setup during installation in
:file:`/etc/beaker/labcontroller.conf`. Save the changes.

Restart ``xinetd`` service using ``systemctl restart xinetd``.

Add firewall rules to enable access to the TFTP server (port 69) and
``beaker-proxy`` running on port 8000::

    # firewall-cmd --permanent --add-port=69/udp
    # firewall-cmd --permanent --add-port=8000/tcp


Reload the firewall rules so that they are in effect::

   # firewall-cmd --reload

Now, start the lab controller daemons::

    # systemctl start beaker-proxy beaker-provision beaker-watchdog

To enable the daemons to start on boot::

    # systemctl enable beaker-proxy beaker-provision beaker-watchdog

You may want to check if the services are up and running::

    # systemctl status beaker-proxy beaker-watchdog beaker-provision

That completes our configuration of the lab controller.

Setup test system
=================

The script `here <scripts/setup_test_system.sh>`__ will setup the
second VM. Run this script as the root user on the *host* system.
It will create a libvirt domain with the name ``beaker-test-vm1``. The
hardware address of the test VM is setup as ``52:54:00:c6:71:8e`` and it
will use the ``default`` network.

Now that we have the test system created, add it to Beaker by going to
``http://beaker-server-lc.beaker/bkr/new`` (you will need to
be logged in). These are the fields and their values which you must
enter (or choose):

- System Name: ``beaker-test-vm1``
- Lab Controller: ``beaker-server-lc.beaker``
- Type: ``Machine``
- Mac Address: ``52:54:00:c6:71:8e``

Save the changes. The system should now be accessible at
``http://beaker-server-lc.beaker/bkr/view/beaker-test-vm1``. Add
a supported architecture to the system by going to the :guilabel:`Arch(s)` tab of the
system and add ``x86_64``.

We will now add the power configuration details for the system. This
is how the system will be powered on during provisioning. Go to the
:guilabel:`Power Config` tab on the system page (as above) and enter the following
values against the fields:

- Power Type: ``virsh``
- Power Address: ``qemu+ssh:192.168.122.1``
- Power Login: <blank>
- Power Password: <blank>
- Power Port/Plug/etc: ``beaker-test-vm1``

Click on :guilabel:`Save Power Changes` to save the configuration.

The default scripts set up two more systems to allow for `multihost testing
<http://beaker-project.org/docs/user-guide/multihost.html>`__ in the virtual
Beaker instance. Follow the same steps as above to configure
them in Beaker, changing only the system name and MAC address:

- System Name: ``beaker-test-vm2``; Mac Address: ``52:54:00:c6:71:8f``
- System Name: ``beaker-test-vm3``; Mac Address: ``52:54:00:c6:71:90``

If the host system doesn't have the capacity to run all the VMs
simultaneously, it's reasonable to skip creating or registering the
additional systems - almost all aspects of Beaker other than multihost
testing can be exercised with just a single registered system.

As you can see from the ``Power Address`` above, the Beaker lab
controller will communicate with your host's libvirtd instance
using ``ssh`` to power on/off the test VM. To make this
possible, we will have to setup passwordless login from your lab
controller (that is, the server/labcontroller VM) to your host
system. First, generate SSH keys on the VM::

    # ssh-keygen -t rsa

Then copy it to your host system::

    # ssh-copy-id root@<host-ip>

(If you are wondering why do we need to setup passwordless login for
the root user, that is because the ``beaker-provision`` service which
handles the test system provisioning runs as the root user and we are
using the ``system://`` instance of libvirt in this guide).

If everything has completed successfully, you should be able to power
on the test system from Beaker's web UI. Let's try that. Go the
:guilabel:`commands` tab of the system at
``http://beaker-server-lc.beaker/bkr/view/beaker-test-vm1`` and
click on :guilabel:`Power On System`. After sometime you should see
the test VM powered on and the PXE boot menu should appear signalling a
successul PXE boot. Force off the test VM for now.

Setup server to run jobs
========================

Initialize the harness repo using (on the server VM as the root user)::

   # beaker-repo-update

We will now add a few task RPMs to ensure we can run jobs (including those
with guest recipes) as well as inventory systems and reserve them through
the scheduler. Use ``wget`` (or an equivalent command) to retrieve the
latest versions of the standard task RPMs (this is best done on the host
system rather than the Beaker server VM)::

    $ wget -r -np -nc https://beaker-project.org/tasks/

Add the tasks manually via ``http://beaker-server-lc.beaker/bkr/tasks/new``
or by using the :manpage:`bkr-task-add(1)` command (in the directory where
the scripts were downloaded, using the admin account configured when
first installing Beaker)::

    $ for f in `ls *.rpm`
    > do
    >    bkr task-add --hub=http://beaker-server-lc.beaker/bkr \
    >        --username=<USER> --password=<PASSWORD> $f
    > done

Once the tasks have been added, they will be visible at the URL:
``http://beaker-server-lc.beaker/bkr/tasks/``. At the very least, the
following tasks should be present:

* ``/distribution/install``
* ``/distribution/inventory``
* ``/distribution/reservesys``
* ``/distribution/virt/install``
* ``/distribution/virt/start``

To learn more about these tasks, see
`here <../../../docs/user-guide/beaker-provided-tasks.html>`__.

Next you will have to import distributions into Beaker. These are the
distributions that you can run your job on. So, depending on your
needs, these will vary. For example, to import a Fedora 19 mirror, run
the ``beaker-import`` program on your server VM as follows::

   # beaker-import http://dl.fedoraproject.org/pub/fedora/linux/releases/20/Fedora/x86_64/os/

.. note::

   It is a good idea to import a mirror closer to your geographical location,
   as the given location will be used to install the operating system when
   provisioning test systems.

Now, go to the URL: ``http://beaker-server-lc.beaker/bkr/distros/`` and
check if the distro(s) have been imported.

Run a job
=========

Okay, now we are all set to run the first job. The easiest way to do
this is provision the test system with a distro. Go to the
:guilabel:`Provision` tab of the system page (test system page as
earlier), select a distro and click on :guilabel:`Schedule
provision`. You can see the job status by going to
``http://beaker-server-lc.beaker/bkr/jobs/`` and also keep track of the
progress in the test VM itself.

If all goes well, you should see the distro you selected being
installed. Once the installation is  complete, the test system will
reboot and after sometime, the ``/distribution/install`` task's status should show as
``Pass`` and the ``/distribution/reservesys`` task should be running,
which means now you can login to your test system using the default
root password `beaker` either via SSH or directly in the test VM.

Troubleshooting
===============

If you see that the test system is not being powered on, or there is
something unexpected going on, look for any hints in the
``beaker-provision`` logs (accessible using ``journalctl -u
beaker-provision``) in the server VM. Log messages from the scheduler
are accessible via ``journalctl -u beakerd`` and similarly for the other
services (``beaker-watchdog`` and ``beaker-proxy``). The Beaker web
application logs are accessible via ``journalctl SYSLOG_IDENTIFIER=beaker-server``. 

If you see something is going wrong with the web application, useful
information may be found in the Apache error logs.

Resources
=========

- `Beaker user guide <../../../docs/user-guide/index.html>`__
- `Beaker administrator's guide <../../../docs/admin-guide/>`__
- `Beaker documentation home <../../../docs/>`__
