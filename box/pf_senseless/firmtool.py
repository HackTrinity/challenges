#!/usr/bin/env python
import os
import sys
import argparse
import struct
import binascii
import socket
import time

from Crypto.PublicKey import RSA
from Crypto.Hash import SHA1
from Crypto.Signature import pkcs1_15

MAGIC = struct.pack('>I', 0x69420)
RSA_BITS = 2048
PORT = 6969

#define RES_OK          0
#define ERR_BAD_REQ     1
#define ERR_BAD_MAGIC   2
#define ERR_TOO_BIG     3
#define ERR_SIG         4
#define ERR_KERNEL      5
#define ERR_ROOTFS      6
ERRORS = {
    1: 'bad request',
    2: 'bad magic',
    3: 'kernel / rootfs too big',
    4: 'signature verification failed',
    5: 'kernel upgrade failed',
    6: 'rootfs upgrade failed'
}

def load_key(args):
    with open(args.key, 'rb') as f:
        return RSA.import_key(f.read())

def gen_key(args):
    k = RSA.generate(RSA_BITS)

    print(f'Writing {RSA_BITS} bit key to {args.key}')
    with open(args.key, 'wb') as f:
        f.write(k.export_key('PEM'))

def dump_key(args):
    k = load_key(args)
    print(f'n = 0x{k.n:x}')
    print(f'e = 0x{k.e:x}')

def _recursive_brute_sha1(h: SHA1, prev, d):
    for i in range(256):
        attempt = prev + struct.pack('B', i)

        if d == 0:
            print(f'trying {binascii.hexlify(attempt)}', end='\r')
            time.sleep(0.01)

            h2 = h.copy()
            h2.update(attempt)
            if h2.digest()[0] == 0:
                return attempt
        else:
            r = _recursive_brute_sha1(h, attempt, d-1)
            if r:
                print()
                return r
def brute_null_prefix_sha1(h: SHA1):
    d = 0
    r = None
    while not r:
        r = _recursive_brute_sha1(h, b'', d)
        d += 1

    return r

def mk_firm(args):
    padding = b''
    if args.sign or args.fakesign:
        h = SHA1.new()

        with open(args.kernel, 'rb') as k:
            while data := k.read(4096):
                h.update(data)

        with open(args.rootfs, 'rb') as r:
            while data := r.read(4096):
                h.update(data)

        if args.sign:
            key = load_key(args)
            signature = pkcs1_15.new(key).sign(h)
        else:
            padding = brute_null_prefix_sha1(h)
            h.update(padding)
            print(f'found suitable null byte padding for fakesigning: {binascii.hexlify(padding)} (new sha1 {h.hexdigest()})')

            signature = b'\0' * (RSA_BITS // 8)

    with open(args.out, 'wb') as o:
        o.write(MAGIC)

        if args.sign or args.fakesign:
            o.write(signature)

        rfs_size = os.path.getsize(args.rootfs) + len(padding)
        o.write(struct.pack('>II', os.path.getsize(args.kernel), rfs_size))

        with open(args.kernel, 'rb') as k:
            while data := k.read(4096):
                o.write(data)

        with open(args.rootfs, 'rb') as r:
            while data := r.read(4096):
                o.write(data)

        if padding:
            o.write(padding)

def send_firm(args):
    with open(args.firm, 'rb') as f:
        print(f'connecting to {args.host}:{PORT}')
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((args.host, PORT))

        print(f'sending {args.firm}...')
        conn.send(b'\0')
        conn.sendfile(f)

        r = conn.recv(1)
        conn.close()

        if not r:
            print('connection closed unexpectedly')
            return

        r = r[0]
        if r == 0:
            print('done.')
        elif r in ERRORS:
            print(f'server returned: {ERRORS[r]}')
        else:
            print(f'server returned unknown error code: {r}')

def main():
    parser = argparse.ArgumentParser('firmtool')
    parser.add_argument('-k', '--key', help='Public / private key file', default='key.pem')

    subparsers = parser.add_subparsers(required=True, dest='command')

    p_genkey = subparsers.add_parser('genkey', help='Generate RSA key')
    p_genkey.set_defaults(func=gen_key)

    p_dumpkey = subparsers.add_parser('dumpkey', help='Dump RSA pubkey components')
    p_dumpkey.set_defaults(func=dump_key)

    p_mkfirm = subparsers.add_parser('mkfirm', help='Generate firmware from kernel and rootfs')
    p_mkfirm.add_argument('-k', '--kernel', help='Path to kernel image', default='kout/kernel.gz')
    p_mkfirm.add_argument('-f', '--rootfs', help='Path to gzipped rootfs', default='fsout/rootfs.f2fs.gz')
    p_mkfirm.add_argument('-o', '--out', help='Output file', default='pf_senseless.fw')
    s_group = p_mkfirm.add_mutually_exclusive_group()
    s_group.add_argument('-s', '--sign', action='store_true', help='Sign firmware')
    s_group.add_argument('--fakesign', action='store_true', help='Fake-sign firmware')
    p_mkfirm.set_defaults(func=mk_firm)

    p_sendfirm = subparsers.add_parser('sendfirm', help='Send firmware image to server')
    p_sendfirm.add_argument('-a', '--host', help='Remote server host', default='192.168.147.1')
    p_sendfirm.add_argument('-f', '--firm', help='Path to firmware image to send', default='pf_senseless.fw')
    p_sendfirm.set_defaults(func=send_firm)

    args = parser.parse_args()
    args.func(args)

    return 0

if __name__ == '__main__':
    sys.exit(main())
