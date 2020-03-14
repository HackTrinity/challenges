#!/usr/bin/env python
import base64
import sys

m = sys.argv[1]
flag = input().strip()

if m == 'encode':
    flag = base64.b64encode(flag.encode('utf-8'))
    flag = base64.b32encode(flag)
    flag = base64.b16encode(flag)
    flag = ' '.join(map(lambda b: f'{b:08b}', map(int, map(str, flag))))
elif m == 'decode':
    flag = flag.split(' ')
    f = bytearray()
    for b in flag:
        f.append(int(b, base=2))

    flag = base64.b16decode(f)
    flag = base64.b32decode(flag)
    flag = base64.b64decode(flag).decode('utf-8')
else:
    print(f'usage: {sys.argv[0]} <encode|decode>')
    sys.exit(1)

print(flag)
