So I found this prototype router. It doesn't do much besides to connect to the
local network on a static IP (`192.168.147.1`). Makes sense given it's a
prototype. However, I suspect there might be a flag hidden inside somewhere...

I've opened it up and connected a debugger to the serial port, when you connect
to `192.168.147.2` on port `23` the debugger will release the reset line and
boot the router. If for any reason the router resets, re-connect to the debugger
and the router will back up.

The box it came in had a CD with a firmware upgrade tool and a sample firmware,
maybe they'll be of some use.

_Note: You will need to set the MTU of the OpenVPN TAP interface to `1300` for
this challenge to work correctly! If you're on Linux, OpenVPN will do this
automatically. For Windows instructions, click
[here](https://hamy.io/post/0004/openvpn-tap-adapter-mtu-in-windows/)_.
