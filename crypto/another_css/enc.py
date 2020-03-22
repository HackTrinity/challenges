#!/usr/bin/env python
import numpy as np
import base64

class LFSR():
    def __init__(self, fpoly=[5,2], initstate='ones', verbose=False):
        if isinstance(initstate, str):
            if initstate=='ones':
                initstate = np.ones(np.max(fpoly))
            elif initstate=='random':
                initstate = np.random.randint(0,2,np.max(fpoly))
            else:
                raise Exception('Unknown initial state')

        self.initstate = initstate
        self.fpoly  = fpoly
        self.state  = initstate.astype(int)
        self.count  = 0
        self.seq    = np.array(-1)
        self.outbit = -1
        self.feedbackbit = -1
        self.verbose = verbose
        self.M = self.initstate.shape[0]
        self.expectedPeriod = 2**self.M -1
        self.fpoly.sort(reverse=True)
        feed = ' '
        for i in range(len(self.fpoly)):
            feed = feed + 'x^'+str(self.fpoly[i])+' + '
        feed = feed + '1'
        self.feedpoly = feed

    def set(self,fpoly,state='ones'):
        self.__init__(fpoly=fpoly,initstate=state)

    def reset(self):
        self.__init__(initstate=self.initstate,fpoly=self.fpoly)

    def changeFpoly(self, newfpoly, reset=False):
        newfpoly.sort(reverse=True)
        self.fpoly =newfpoly
        feed = ' '
        for i in range(len(self.fpoly)):
            feed = feed + 'x^'+str(self.fpoly[i])+' + '
        feed = feed + '1'
        self.feedpoly = feed

        self.check()
        if reset:
            self.reset()

    def next(self):
        b = np.logical_xor(self.state[self.fpoly[0]-1],self.state[self.fpoly[1]-1])
        if len(self.fpoly)>2:
            for i in range(2,len(self.fpoly)):
                b = np.logical_xor(self.state[self.fpoly[i]-1],b)

        self.state = np.roll(self.state, 1)
        self.state[0] = b*1
        self.feedbackbit = b*1
        if self.count==0:
            self.seq = self.state[-1]
        else:
            self.seq = np.append(self.seq,self.state[-1])
        self.outbit = self.state[-1]
        self.count +=1
        if self.verbose:
            print('S: ',self.state)
        return self.state[-1]

    def runFullCycle(self):
        for i in range(self.expectedPeriod):
            self.next()
        return self.seq

    def runKCycle(self,k):
        tempseq =np.ones(k)*-1
        for i in range(k):
            tempseq[i] = self.next()

        return tempseq

def main():
    print("Reading flag...")
    with open("flag.txt") as f:
        flag = f.read().strip()

    flag = f"Well done! You got the flag. The flag is {flag}".encode('ascii')

    with open("state.txt") as f:
        state1 = np.array(list(map(int, f.readline().split(','))))
        state2 = np.array(list(map(int, f.readline().split(','))))

    print(f"state 1 size: {len(state1)}")
    print(f"state 2 size: {len(state2)}")

    fpoly1 = [8,4,1]
    fpoly2 = [13,6,3]

    A = LFSR(fpoly=fpoly1, initstate =state1)
    B = LFSR(fpoly=fpoly2, initstate =state2)

    size = len(flag)
    xord_byte_array = bytearray(len(flag))

    # Flag is encrypted by xor-ing with keystream
    # Keystream = (LFSR A output + LFSR B output) % 256
    print("Encrypting flag...")
    for i in range(size):
        newbyte1=0
        newbyte2=0
        for x in range(8):
            A.next()
            B.next()
            newbyte1 += A.outbit*pow(2,x)
            newbyte2 += B.outbit*pow(2,x)

        xorbyte=(newbyte1+newbyte2)%256
        xord_byte_array[i] = flag[i] ^ xorbyte

    encoded = base64.b64encode(xord_byte_array)
    print(f"Safely encrypted flag: {encoded.decode('ascii')}")

if __name__ == '__main__':
    main()
