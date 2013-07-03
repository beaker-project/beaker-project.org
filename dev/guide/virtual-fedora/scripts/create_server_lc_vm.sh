#!/bin/bash

# root
if (( EUID != 0 )); then
   echo "You must be root to do this." 1>&2
   exit 100
fi

virt-install \
    --location=http://dl.fedoraproject.org/pub/fedora/linux/releases/19/Fedora/x86_64/os/\
    --initrd-inject=beaker-server-lc.ks --extra-args=ks=file:/beaker-server-lc.ks \
    --name=beaker-server-lc --network=network=default --mac=52:54:00:c6:73:4f \
    --ram=2048 --vcpus=2 \
    --disk path=/beaker_images/server-lc.img
