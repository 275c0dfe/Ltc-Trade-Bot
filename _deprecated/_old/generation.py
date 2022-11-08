import random
import math
def randInt(min , mx):
    r= random.random() - min
    a = r * mx
    return math.floor(a) + min


def randStr(length):
    chars = "abcefghijklmnopqrstuvwxyz"
    chars += chars.upper()
    chars += "1234567890"
    s = ""
    for i in range(length):
            r = randInt(0 , len(chars))
            c = chars[r]
            s += c
    return s