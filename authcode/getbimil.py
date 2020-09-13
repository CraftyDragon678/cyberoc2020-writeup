from z3 import *

key_table = [0x428A2F98, 0x71374491, 0xB5C0FBCF, 0xE9B5DBA5, 0x3956C25B, 0x59F111F1, 0x923F82A4, 0xAB1C5ED5,
    0xD807AA98, 0x12835B01, 0x243185BE, 0x550C7DC3, 0x72BE5D74, 0x80DEB1FE, 0x9BDC06A7, 0xC19BF174,
    0xE49B69C1, 0xEFBE4786, 0x0FC19DC6, 0x240CA1CC, 0x2DE92C6F, 0x4A7484AA, 0x5CB0A9DC, 0x76F988DA,
    0x983E5152, 0xA831C66D, 0xB00327C8, 0xBF597FC7, 0xC6E00BF3, 0xD5A79147, 0x06CA6351, 0x14292967,
    0x27B70A85, 0x2E1B2138, 0x4D2C6DFC, 0x53380D13, 0x650A7354, 0x766A0ABB, 0x81C2C92E, 0x92722C85,
    0xA2BFE8A1, 0xA81A664B, 0xC24B8B70, 0xC76C51A3, 0xD192E819, 0xD6990624, 0xF40E3585, 0x106AA070,
    0x19A4C116, 0x1E376C08, 0x2748774C, 0x34B0BCB5, 0x391C0CB3, 0x4ED8AA4A, 0x5B9CCA4F, 0x682E6FF3,
    0x748F82EE, 0x78A5636F, 0x84C87814, 0x8CC70208, 0x90BEFFFA, 0xA4506CEB, 0xBEF9A3F7, 0xC67178F2]

for length in range(2, 30):
    print("length:", length)
    s = Solver()

    answer = 0x1099

    key_arr2 = [BitVecVal(i, 32) for i in [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19]]
    key_arr = [BitVecVal(i, 32) for i in [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19]]
    inp = [BitVec(f"{i}", 32) for i in range(length)]

    for i in inp:
        s.add(0 <= i, i <= 0x7f)

    l = len(inp)
    inp.extend([BitVecVal(0x80, 32)])
    inp.extend([BitVecVal(0, 32) for _ in range(56-len(inp))])
    inp.extend([BitVecVal(0, 32) for _ in range(7)])
    inp.extend([BitVecVal(l * 8, 32)])

    roled = []

    for i in range(0, 64, 4):
        tmp = (inp[i+0] << 24) + (inp[i+1] << 16) + (inp[i+2] << 8) + inp[i+3]
        roled.append(tmp)

    for a in range(48):
        b = roled[a+1]
        c = roled[a+14]
        roled.append(
                roled[a] + roled[a+9]
                + (LShR(b, 3) ^ RotateRight(b, 7) ^ RotateRight(b, 18))
                + (LShR(c, 10) ^ RotateRight(c, 17) ^ RotateRight(c, 19))
            )

    for i in range(0, 64, 8):
        for j in range(8):
            tmp = (
                key_arr[7-j]
                + roled[i+j]
                + key_table[i+j]
                + (key_arr[4-j] & key_arr[5-j] ^ key_arr[6-j] & ~key_arr[4-j])
                + (RotateRight(key_arr[4-j], 6) ^ RotateRight(key_arr[4-j], 11) ^ RotateRight(key_arr[4-j], 25))
            )
            key_arr[3-j] += tmp
            t = None
            if j == 0:
                t = key_arr[0] & key_arr[1] ^ key_arr[2] & (key_arr[0] ^ key_arr[1])
            elif j == 1:
                t = key_arr[0] & key_arr[1] ^ key_arr[7] & (key_arr[0] ^ key_arr[1])
            elif j == 2:
                t = key_arr[0] & key_arr[6] ^ key_arr[7] & (key_arr[0] ^ key_arr[6])
            else:
                t = key_arr[-j] & key_arr[1-j] ^ key_arr[2-j] & (key_arr[-j] ^ key_arr[1-j])
            key_arr[7-j] = (
                tmp
                + (RotateRight(key_arr[-j], 13) ^ RotateRight(key_arr[-j], 22) ^ RotateRight(key_arr[-j], 2))
                + t
            )

    for i in range(8):
        key_arr[i] += key_arr2[i]
        key_arr[i] = RotateLeft(key_arr[i], 8) & 0xff00ff | RotateLeft(key_arr[i], 24) & 0xff00ff00

    _sum = [BitVecVal(0, 32) for _ in range(4)]
    for i in key_arr:
        _sum[0] += LShR(i, 24) & 0xff
        _sum[1] += LShR(i, 16) & 0xff
        _sum[2] += LShR(i, 8) & 0xff
        _sum[3] += i & 0xff
    s.add(sum(_sum) == answer)

    while s.check() == sat:
        print("answer")
        print(s.model())
