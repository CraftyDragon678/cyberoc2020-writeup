tttt = 2666371

goyu = [0xb1c2, 0x4ea2, 0xd2d4]

print(hex(((goyu[1] ^ goyu[0] * (tttt & 0xff)) ^ 0x6a30) & 0xffff))

print(hex(goyu[2] ^ goyu[1] ^ goyu[0] * (tttt & 0xff)))
