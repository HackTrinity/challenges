#!/bin/sh
set -e

JOBS=$(nproc)

[ -d "linux-$KERNEL_VERSION" ] || tar Jxf "/usr/local/src/linux-$KERNEL_VERSION.tar.xz"

cp /usr/local/src/kernel_config "linux-$KERNEL_VERSION/.config"
make -C "linux-$KERNEL_VERSION" -j${JOBS} ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu-
cp "linux-$KERNEL_VERSION/arch/arm64/boot/Image.gz" kernel.gz
