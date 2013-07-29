#!/bin/bash

# Abort if any step fails
set -e

# root
if (( EUID != 0 )); then
   echo "You must be root to do this." 1>&2
   exit 100
fi

# This script sets up the default network
function setup_network()
{

virsh net-destroy default || true
virsh net-undefine default || true

( cat <<__EOF__
 <network>
  <name>default</name>
  <forward mode='nat'/>
  <bridge name='virbr0' stp='on' delay='0' />
  <mac address='52:54:00:6B:11:87'/>
  <dns>
    <host ip='192.168.122.102'>
      <hostname>beaker-server-lc.beaker</hostname>
    </host>
    <host ip='192.168.122.103'>
      <hostname>beaker-test-vm1</hostname>
    </host>
  </dns>
   <ip address='192.168.122.1' netmask='255.255.255.0'>
    <tftp root='/var/lib/tftpboot' />
    <dhcp>
      <range start='192.168.122.2' end='192.168.122.254' />
      <host mac='52:54:00:c6:73:4f' name='beaker-server-lc.beaker' ip='192.168.122.102' />
      <host mac='52:54:00:c6:71:8e' name='beaker-test-vm1' ip='192.168.122.103' />
      <bootp file='pxelinux.0' server='192.168.122.102' />
    </dhcp>
  </ip>
</network>

__EOF__
) | virsh net-define /dev/stdin

virsh net-start default
virsh net-autostart default
}

setup_network
