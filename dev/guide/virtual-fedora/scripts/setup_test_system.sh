#!/bin/bash
# This script sets up the test system

# Abort if any step fails
set -e
if (( EUID != 0 )); then
   echo "You must be root to do this." 1>&2
   exit 100
fi


function setup_test_systems()
{

virsh destroy beaker-test-vm1 || true
virsh undefine beaker-test-vm1 || true
virsh destroy beaker-test-vm2 || true
virsh undefine beaker-test-vm2 || true
virsh destroy beaker-test-vm3 || true
virsh undefine beaker-test-vm3 || true

(cat <<__EOF__
<domain type='kvm'>
  <name>beaker-test-vm1</name>
  <memory unit='KiB'>2097152</memory>
  <vcpu>1</vcpu>
  <os>
    <type arch='x86_64'>hvm</type>
    <boot dev='network'/>
    <boot dev='hd'/>
    <bootmenu enable='no'/>
  </os>
  <clock offset='utc'/>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>restart</on_crash>
  <devices>
    <disk type='file' device='disk'>
      <driver name='qemu' type='raw'/>
      <source file='/beaker_images/test-system1.img'/>
      <target dev='vda' bus='virtio'/>
    </disk>
    <interface type='network'>
      <mac address='52:54:00:c6:71:8e'/>
      <source network='default'/>
      <model type='virtio'/>
    </interface>
    <memballoon model='virtio'/>
   <graphics type='vnc' port='-1' autoport='yes' keymap='en-us'/>
  </devices>
</domain>
__EOF__
) | virsh define /dev/stdin

(cat <<__EOF__
<domain type='kvm'>
  <name>beaker-test-vm2</name>
  <memory unit='KiB'>2097152</memory>
  <vcpu>1</vcpu>
  <os>
    <type arch='x86_64'>hvm</type>
    <boot dev='network'/>
    <boot dev='hd'/>
    <bootmenu enable='no'/>
  </os>
  <clock offset='utc'/>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>restart</on_crash>
  <devices>
    <disk type='file' device='disk'>
      <driver name='qemu' type='raw'/>
      <source file='/beaker_images/test-system2.img'/>
      <target dev='vda' bus='virtio'/>
    </disk>
    <interface type='network'>
      <mac address='52:54:00:c6:71:8f'/>
      <source network='default'/>
      <model type='virtio'/>
    </interface>
    <memballoon model='virtio'/>
   <graphics type='vnc' port='-1' autoport='yes' keymap='en-us'/>
  </devices>
</domain>
__EOF__
) | virsh define /dev/stdin

(cat <<__EOF__
<domain type='kvm'>
  <name>beaker-test-vm3</name>
  <memory unit='KiB'>2097152</memory>
  <vcpu>1</vcpu>
  <os>
    <type arch='x86_64'>hvm</type>
    <boot dev='network'/>
    <boot dev='hd'/>
    <bootmenu enable='no'/>
  </os>
  <clock offset='utc'/>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>restart</on_crash>
  <devices>
    <disk type='file' device='disk'>
      <driver name='qemu' type='raw'/>
      <source file='/beaker_images/test-system3.img'/>
      <target dev='vda' bus='virtio'/>
    </disk>
    <interface type='network'>
      <mac address='52:54:00:c6:71:90'/>
      <source network='default'/>
      <model type='virtio'/>
    </interface>
    <memballoon model='virtio'/>
   <graphics type='vnc' port='-1' autoport='yes' keymap='en-us'/>
  </devices>
</domain>
__EOF__
) | virsh define /dev/stdin

}

setup_test_systems
