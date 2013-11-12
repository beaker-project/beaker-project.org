#!/bin/bash

# Abort if any step fails
set -e

# root
if (( EUID != 0 )); then
   echo "You must be root to do this." 1>&2
   exit 100
fi


# This script creates a storage pool with the name
# beaker-images and then creates two volumes in this pool

# define a persistent storage pool
function def_storage_pool()
{

mkdir -p /beaker_images

( cat <<__EOF__
  <pool type="dir">
    <name>beaker_images</name>
      <target>
        <path>/beaker_images</path>
      </target>
  </pool>
__EOF__
) | virsh pool-define /dev/stdin

# start and setup for autostart
virsh pool-start beaker_images
virsh pool-autostart beaker_images
}

# define the storage volume for the server/lc
# 20 GiB
function def_server_lc_storage()
{
( cat <<__EOF__
<volume>
  <name>server-lc.img</name>
  <source>
  </source>
  <capacity>21474836480</capacity>
  <allocation>8589934592</allocation>
  <target>
    <path>/beaker_images/server-lc.img</path>
    <format type='raw'/>
  </target>
</volume>
__EOF__
) | virsh vol-create beaker_images /dev/stdin
}

# define the storage volume for a beaker test VM
# 10 GiB
function def_test_systems_storage()
{
( cat <<__EOF__
<volume>
  <name>test-system1.img</name>
  <source>
  </source>
  <capacity>10737418240</capacity>
  <allocation>10737418240</allocation>
  <target>
    <path>/beaker_images/test-system1.img</path>
    <format type='raw'/>
  </target>
</volume>
__EOF__
) | virsh vol-create beaker_images /dev/stdin
( cat <<__EOF__
<volume>
  <name>test-system2.img</name>
  <source>
  </source>
  <capacity>10737418240</capacity>
  <allocation>10737418240</allocation>
  <target>
    <path>/beaker_images/test-system2.img</path>
    <format type='raw'/>
  </target>
</volume>
__EOF__
) | virsh vol-create beaker_images /dev/stdin
( cat <<__EOF__
<volume>
  <name>test-system3.img</name>
  <source>
  </source>
  <capacity>10737418240</capacity>
  <allocation>10737418240</allocation>
  <target>
    <path>/beaker_images/test-system3.img</path>
    <format type='raw'/>
  </target>
</volume>
__EOF__
) | virsh vol-create beaker_images /dev/stdin
}

#define, start and mark the pool for autostart
def_storage_pool

# define the storage volumes
def_server_lc_storage
def_test_systems_storage
