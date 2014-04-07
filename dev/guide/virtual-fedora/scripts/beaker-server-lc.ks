# See http://fedoraproject.org/wiki/Anaconda/Kickstart
url --url=http://dl.fedoraproject.org/pub/fedora/linux/releases/20/Everything/x86_64/os/
repo --name=updates
repo --name=beaker-server --baseurl=http://beaker-project.org/yum/server/Fedora20


auth --useshadow --enablemd5
firstboot --disable
clearpart --all --initlabel

# auto partition
autopart 

bootloader --location=mbr
keyboard us
lang en_US
timezone America/New_York
network --hostname=beaker-server-lc.beaker
install
shutdown

# root pw: fedora
rootpw --iscrypted $1$I1lI.tL5$qOMpgkPrJIxc2vc29oHh./

# till we have a policy for beaker, disable.
selinux --disabled

%packages
beaker-server
beaker-lab-controller

# these are not tracked by beaker dependencies, so we have to manually
# install these
autofs
#MariaDB
mariadb-server
MySQL-python
tftp-server
mod_ssl

# we will need to power on the test systems from the LC, so we need
# virsh
libvirt-client

#utilities
wget

%end

%post

set -x -v
exec 1>/root/ks-post.log 2>&1

systemctl enable mysqld
systemctl enable xinetd
systemctl enable tftp

%end
