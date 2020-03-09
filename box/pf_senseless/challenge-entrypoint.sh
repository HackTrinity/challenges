#!/bin/sh
set -e

ip link add name vm-bridge type bridge
ip link set vm-bridge up
ip addr add "$DEBUGGER_IP" dev vm-bridge

if [ -n "$CHALLENGE_IP" ]; then
    ip addr del "$CHALLENGE_IP" dev challenge
    ip link set challenge master vm-bridge
fi

mkdir -p /dev/net
if [ ! -c /dev/net/tun ]; then
    mknod /dev/net/tun c 10 200
fi

exec qemu-system-aarch64 \
    -nographic \
    -monitor none \
    -machine virt \
    -cpu max \
    -m 768M \
    -kernel kernel.img \
    -blockdev raw,node-name=kernel_mmc,file.driver=file,file.filename=kernel.img \
    -device sdhci-pci \
    -device sd-card,drive=kernel_mmc \
    -blockdev raw,node-name=rootfs_mmc,file.driver=file,file.filename=rootfs.img \
    -device sdhci-pci \
    -device sd-card,drive=rootfs_mmc \
    -nic tap,id=lan,downscript=no \
    -chardev socket,id=debug,server,host=0.0.0.0,port=21 \
    -serial chardev:debug
