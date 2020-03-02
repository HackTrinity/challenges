#!/usr/bin/env python3
import os
import signal
import socket

from pypacker.layer3 import icmp
from pypacker.layer3.ip import IP

class PingServer:
    def __init__(self, flag):
        self.flag = flag.encode('utf-8')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        self.sock.settimeout(0.5)

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sock.close()

    def handle(self, data):
        parsed = IP(data)
        p = parsed[IP, icmp.ICMP]
        if not p or p.type != icmp.ICMP_ECHO:
            return

        p.type = icmp.ICMP_ECHO_REPLY
        p[icmp.ICMP.Echo].body_bytes += self.flag
        self.sock.sendto(p.bin(), (socket.inet_ntoa(parsed.src), 0))

    def run(self):
        self.running = True
        while self.running:
            try:
                data = self.sock.recv(65536)
            except socket.timeout:
                continue
            self.handle(data)

    def stop(self):
        self.running = False

def main():
    flag = 'flag{dummy}'
    if os.path.exists('/run/secrets/flag.txt'):
        with open('/run/secrets/flag.txt') as f:
            flag = f.read().strip()

    with PingServer(flag) as server:
        sig_handle = lambda n, f: server.stop()
        signal.signal(signal.SIGINT, sig_handle)
        signal.signal(signal.SIGTERM, sig_handle)

        server.run()

if __name__ == '__main__':
    main()
