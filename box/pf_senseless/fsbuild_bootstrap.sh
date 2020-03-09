#!/bin/sh
set -e

CHROOT=/alpine

mkdir -p "$CHROOT/opt/fsbuild/out"
mount -v --bind /opt/fsbuild "$CHROOT/opt/fsbuild"
mount --make-private "$CHROOT/opt/fsbuild"
mount -v --bind /opt/fsbuild/out "$CHROOT/opt/fsbuild/out"
mount --make-private "$CHROOT/opt/fsbuild/out"

alpine-chroot-install -b v3.11 -a aarch64
exec /alpine/enter-chroot "$@"
