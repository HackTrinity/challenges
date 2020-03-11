#!/bin/sh
set -e
source /etc/profile

cp /mnt/upgrade_server /mnt/advertise /usr/local/bin/

cat > /etc/init.d/fix-apk-cache <<-EOF
#!/sbin/openrc-run

description="Ensure /var/cache/apk exists so apk works"

depend() {
	need localmount
}
start() {
    if [ ! -d /var/cache/apk ]; then
        ebegin "Creating /var/cache/apk"
        mkdir /var/cache/apk
        eend $?
    fi
}
EOF
chmod +x /etc/init.d/fix-apk-cache

cat > /etc/network/interfaces <<-EOF
auto eth0
iface eth0 inet static
    address $1
    netmask 255.255.128.0
    broadcast 192.168.255.255
EOF

cat > /etc/init.d/upgrade-server <<-EOF
#!/sbin/openrc-run

description="Firmware upgrade server"
command="/usr/local/bin/upgrade_server"
command_background=true
pidfile="/var/run/\$SVCNAME"

depend() {
	need net
    after firewall
}
EOF
chmod +x /etc/init.d/upgrade-server

cat > /etc/init.d/advertise <<-EOF
#!/sbin/openrc-run

description="Router advertisement"
command="/usr/local/bin/advertise"
command_args="eth0"
command_background=true
pidfile="/var/run/\$SVCNAME"

depend() {
	need net
    after firewall
}
EOF
chmod +x /etc/init.d/advertise

# Uncomment to enable login on the serial console at boot
#echo "console::respawn:/sbin/getty -L console 115200 vt100" >> /etc/inittab

> /etc/fstab
rc-update add networking boot
rc-update add fix-apk-cache
rc-update add haveged
rc-update add dropbear
rc-update add upgrade-server
rc-update add advertise

echo "DROPBEAR_OPTS=\"-g\"" > /etc/conf.d/dropbear
mkdir -p /root/.ssh
cp /mnt/id_rsa.pub /root/.ssh/authorized_keys

if [ -n "$2" ]; then
    echo "$2" > /flag.txt
fi
