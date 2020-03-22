#!/usr/bin/env python
import base64
from itertools import product
import sys

import numpy as np

from enc import LFSR
def prev(self, bit):
    """
    Using an output bit, run backwards, and return True if consistent, False otherwise
    """
    self.prev_state = self.state.copy()
    self.state = np.roll(self.state, -1)
    self.state[-1] = bit

    self.feedbackbit = self.state[0]

    if self.verbose:
        print(f'S: {self.state}, True')

    if self.feedbackbit == 2:
        # Uninitialised state - must be consistent
        return True

    b = np.logical_xor(self.state[self.fpoly[0]],self.state[self.fpoly[1]])
    if len(self.fpoly)>2:
        for i in range(2,len(self.fpoly)):
            b = np.logical_xor(self.state[self.fpoly[i]],b)

    if self.feedbackbit == b*1:
        return True

    return False
LFSR.prev = prev

def is_consistent(bitstring, lfsr):
    for b in bitstring:
        if not lfsr.prev(b):
            return False
    return True

known_bytes = f"Well done! You got the flag. The flag is ".encode('ascii')
length = len(known_bytes)

enc = base64.b64decode(sys.stdin.read().strip())

consistent_states = []
for state in product([0,1], repeat=13):
    state = list(state)

    a_keystream = bytearray(length)
    xored_enc = bytearray(length)

    fpoly1 = [8,4,1]
    fpoly2 = [13,6,3]
    state1 = np.array(state)
    state2 = np.array([2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2])

    A = LFSR(fpoly=fpoly1,initstate =state1)
    B = LFSR(fpoly=fpoly2,initstate =state2)

    for i in range(0, length):
        newbyte = 0
        for x in range(8):
            A.next()
            newbyte += A.outbit*pow(2,x)
        a_keystream[i] = newbyte

    for i in range(0, length):
        xored_enc[i] = ((known_bytes[i] ^ enc[i]) - a_keystream[i]) % 256

    binary_string = [int(c) for c in "".join([format(byte, '08b')[::-1] for byte in xored_enc])]
    binary_string.reverse()

    if is_consistent(binary_string, B):
        print("Found!!!")
        print(f"LFSR A state: {state}")
        print(f"LFSR B state: {B.state}")
        consistent_states.append((state, list(np.roll(B.state, -1))))


print(consistent_states)

xord_byte_array = bytearray(len(enc))

for a, b in consistent_states:
    A = LFSR(fpoly=fpoly1, initstate=np.array(a))
    B = LFSR(fpoly=fpoly2, initstate=np.array(b))

    for i in range(len(enc)):
        newbyte1=0
        newbyte2=0
        for x in range(8):
            A.next()
            B.next()
            newbyte1 += A.outbit*pow(2,x)
            newbyte2 += B.outbit*pow(2,x)

        xorbyte=(newbyte1+newbyte2)%256
        xord_byte_array[i] = enc[i] ^ xorbyte

    print(xord_byte_array)
