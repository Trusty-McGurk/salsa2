class Salsa:
    def __init__(self, r):
        assert r >= 0
        self._r = r  # number of rounds
        self._mask = 0xffffffff  # 32-bit mask

    def __call__(self, key=[0] * 32, nonce=[0] * 8, block_counter=[0] * 8):
        # print(len(key))
        assert len(key) == 32
        assert len(nonce) == 8
        assert len(block_counter) == 8

        # init state
        k = [self._littleendian(key[4 * i:4 * i + 4]) for i in range(8)]
        n = [self._littleendian(nonce[4 * i:4 * i + 4]) for i in range(2)]
        b = [self._littleendian(block_counter[4 * i:4 * i + 4]) for i in range(2)]
        c = [0x61707865, 0x3320646e, 0x79622d32, 0x6b206574]

        s = [c[0], k[0], k[1], k[2],
             k[3], c[1], n[0], n[1],
             b[0], b[1], c[2], k[4],
             k[5], k[6], k[7], c[3]]

        # the state
        self._s = s[:]

        for i in range(self._r):
            print("State {}:".format(i))
            print_state(self._s)
            self._round()
        # j = input("")

        # add initial state to the final one
        self._s = [(self._s[i] + s[i]) & self._mask for i in range(16)]

        return self._s

    def _littleendian(self, b):
        assert len(b) == 4
        return b[0] ^ (b[1] << 8) ^ (b[2] << 16) ^ (b[3] << 24)

    def _round(self):
        # quarterround 1
        self._s[4] ^= self._rotl32((self._s[0] + self._s[12]) & self._mask, 7)
        self._s[8] ^= self._rotl32((self._s[0] + self._s[4]) & self._mask, 9)
        self._s[12] ^= self._rotl32((self._s[4] + self._s[8]) & self._mask, 13)
        self._s[0] ^= self._rotl32((self._s[8] + self._s[12]) & self._mask, 18)

        # quarterround 2
        self._s[9] ^= self._rotl32((self._s[1] + self._s[5]) & self._mask, 7)
        self._s[13] ^= self._rotl32((self._s[5] + self._s[9]) & self._mask, 9)
        self._s[1] ^= self._rotl32((self._s[9] + self._s[13]) & self._mask, 13)
        self._s[5] ^= self._rotl32((self._s[1] + self._s[13]) & self._mask, 18)

        # quarterround 3
        self._s[14] ^= self._rotl32((self._s[6] + self._s[10]) & self._mask, 7)
        self._s[2] ^= self._rotl32((self._s[10] + self._s[14]) & self._mask, 9)
        self._s[6] ^= self._rotl32((self._s[2] + self._s[14]) & self._mask, 13)
        self._s[10] ^= self._rotl32((self._s[2] + self._s[6]) & self._mask, 18)

        # quarterround 4
        self._s[3] ^= self._rotl32((self._s[11] + self._s[15]) & self._mask, 7)
        self._s[7] ^= self._rotl32((self._s[3] + self._s[15]) & self._mask, 9)
        self._s[11] ^= self._rotl32((self._s[3] + self._s[7]) & self._mask, 13)
        self._s[15] ^= self._rotl32((self._s[7] + self._s[11]) & self._mask, 18)

        # transpose
        self._s = [self._s[0], self._s[4], self._s[8], self._s[12],
                   self._s[1], self._s[5], self._s[9], self._s[13],
                   self._s[2], self._s[6], self._s[10], self._s[14],
                   self._s[3], self._s[7], self._s[11], self._s[15]]

    def _rotl32(self, w, r):
        # rotate left for 32-bits
        return (((w << r) & self._mask) | (w >> (32 - r)))


def print_state(s):
    assert len(s) == 16
    for i in range(4):
        print("{:08x} {:08x} {:08x} {:08x}".format(s[4 * i], s[4 * i + 1], s[4 * i + 2], s[4 * i + 3]))

def littleendian(b):
    assert len(b) == 4
    return b[0] ^ (b[1] << 8) ^ (b[2] << 16) ^ (b[3] << 24)

def encrypt_plaintext(ptext, s):
    bytemsg = list(map(lambda x: ord(x), list(ptext)))
    bytemsg_8 = [littleendian(bytemsg[i * 4:i * 4 + 4])for i in range(len(bytemsg)//4)]
    remainder = [0] * 4
    for i in range (len(bytemsg) % 4):
        remainder[i] = bytemsg[len(bytemsg) - (len(bytemsg) % 4) + i]
    bytemsg_8.append(littleendian(remainder))
    mark = 0
    retlist = [None] * len(bytemsg_8)
    for i in range(len(bytemsg_8)):
        retlist[i] = bytemsg_8[i] ^ s[mark]
        mark = mark + 1
        if mark == 16:
            mark = 0

    return retlist

round_num = 2
salsa20 = Salsa(round_num)
ptext = input("Enter plaintext: ")

# change to be hex values if you want a password for key
#
# s = salsa20(range(1,33), [3,1,4,1,5,9,2,6], [7,0,0,0,0,0,0,0])
key = []
for i in range(0, 32):
    key.append(0)

nonce = []
pos = []
for i in range(0, 8):
    nonce.append(2)
    pos.append(1)

s = salsa20(key, nonce, pos)
print()
print("End State of Round {}: ".format(round_num))
print_state(s)
print()
ciphertext = encrypt_plaintext(ptext, s)
print("Ciphertext:")
for i in range(len(ciphertext)):
    print("{:08x}".format(ciphertext[i]), end = " ")
print()
