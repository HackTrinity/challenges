#!/bin/sh
set -e
set -o xtrace

JOBS=$(nproc)
TIMEZONE=Europe/Dublin
ALPINE_BRANCH=v3.11
BUSYBOX_VERSION=1.31.1

build_busybox() {
    dir="busybox-$1"
    archive="$dir.tar.bz2"

    apk add perl linux-headers
    wget "https://busybox.net/downloads/$archive"
    tar jxf "$archive"
    mv busybox_config "$dir/.config"

    make -j${JOBS} -C "$dir"
    cp "$dir/busybox" "$2"
}

build_initramfs() {
    cp -r initramfs_base/ "$2"
    cp "$1" "$2/bin/busybox"
}

build_rootfs() {
    packages="alpine-base dropbear dropbear-openrc haveged haveged-openrc"

    if [ "$3" == "yes" ]; then
        packages="$packages gmp"
        apk add gmp-dev
        gcc -DSIG_CHECK -o upgrade_server upgrade/sha1.c upgrade/sigcheck.c upgrade/server.c -lgmp

        ip=192.168.148.1
    else
        gcc -o upgrade_server upgrade/server.c

        ip=192.168.147.1
    fi

    ./alpine-make-rootfs \
        --branch "$ALPINE_BRANCH" \
        --packages "$packages" \
        --timezone "$TIMEZONE" \
        --script-chroot \
        "$1" \
        "./rootfs_init.sh" \
        "$ip" \
        "$4"

    apk add f2fs-tools
    truncate -s "$2" "$1.f2fs"
    mkfs.f2fs -f -l root "$1.f2fs"
    mount -v -t f2fs "$1.f2fs" /mnt
    mv "$1/"* /mnt/
    umount /mnt

    gzip "$1.f2fs"
}

[ -f out/busybox ] || build_busybox "$BUSYBOX_VERSION" out/busybox
[ -d out/initramfs ] || build_initramfs out/busybox out/initramfs

[ -f out/rootfs.f2fs.gz ] || build_rootfs out/rootfs 256M no "HackTrinity{th3_rout3r_was_che4p_0k}"
[ -f out/rootfs.signed.f2fs.gz ] || build_rootfs out/rootfs.signed 256M yes "HackTrinity{n1ntend0_wi1_sigch3ck_bad}"

[ -f out/rootfs.sample.f2fs.gz ] || build_rootfs out/rootfs.sample 256M no
[ -f out/rootfs.signed.sample.f2fs.gz ] || build_rootfs out/rootfs.signed.sample 256M yes
