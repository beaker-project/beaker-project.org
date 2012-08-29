
# Beaker is developed and tested on Red Hat Enterprise Linux 6, but any
# compatible distro should work as well.
url --url=http://mirror.centos.org/centos/6/os/x86_64/
repo --name=install --baseurl=http://mirror.centos.org/centos/6/os/x86_64/
repo --name=updates --baseurl=http://mirror.centos.org/centos/6/updates/x86_64/
repo --name=extras --baseurl=http://mirror.centos.org/centos/6/extras/x86_64/
repo --name=cr --baseurl=http://mirror.centos.org/centos/6/cr/x86_64/
repo --name=beaker-server --baseurl=http://beaker-project.org/yum/server/RedHatEnterpriseLinux6/

# If you're feeling adventurous, you could try Fedora instead. Bug reports are
# welcome.
#url --url=http://download.fedoraproject.org/pub/fedora/linux/releases/16/Fedora/x86_64/os/
#repo --name=updates --baseurl=http://download.fedoraproject.org/pub/fedora/linux/updates/16/x86_64/
#repo --name=beaker-server --baseurl=http://beaker-project.org/yum/server/Fedora16/

# The usual installation stuff. Beaker has no particular requirements here.
auth --useshadow --enablemd5
firewall --disable
firstboot --disable
clearpart --all --initlabel
part / --fstype=ext4 --size=2000 --grow
part /boot --fstype=ext4 --size=500
part swap --recommended
bootloader --location=mbr
keyboard us
lang en_US
timezone America/New_York
install
reboot

# The root password is `beaker`. You may want to change this.
rootpw --iscrypted $1$mF86/UHC$0siTuCcbOzXX5nOSdcsPG.

# For now, the Beaker server does not support running with SELinux enabled.
# Patches welcome.
selinux --disabled

# These are the basic requirements for running a Beaker server and lab.
%packages
beaker-server
beaker-lab-controller
mysql-server
MySQL-python
autofs
mod_ssl
tftp-server

# We will create some KVM guests to add to Beaker.
libvirt
virt-manager
kvm
qemu-img

# A few extra packages for convenience.
python-setuptools
python-setuptools-devel
python-devel
xorg-x11-xauth

%post
set -x -v
exec 1>/root/ks-post.log 2>&1

# Turn on some services which are needed.
chkconfig mysqld on
chkconfig httpd on
chkconfig xinetd on
chkconfig tftp on

# The real work of setting up a Beaker environment is done in these scripts.
wget -O /usr/local/sbin/beaker-setup http://beaker-project.org/in-a-box/beaker-setup
chmod 755 /usr/local/sbin/beaker-setup
wget -O /usr/local/sbin/beaker-distros http://beaker-project.org/in-a-box/beaker-distros
chmod 755 /usr/local/sbin/beaker-distros
wget -O /usr/local/sbin/beaker-virt http://beaker-project.org/in-a-box/beaker-virt
chmod 755 /usr/local/sbin/beaker-virt
cat <<EOF >>/etc/motd
Welcome to Beaker!

You need to configure a few things before you can run any jobs.

/usr/local/sbin/beaker-setup
	This will intitialize the beaker DB and setup admin account
/usr/local/sbin/beaker-distros
	This will import some common distros for use
/usr/local/sbin/beaker-virt
	This will setup some virt hosts on this box for use
EOF
