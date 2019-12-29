from z3 import *

# m = 0b011001111111001
# c = 0b101101011110011
# order = 5
# pls solve mask!

# first, calculate key sequence
m = 0b011001111111001
c = 0b101101011110011
k = m ^ c
k = list(map(int ,bin(k)[2:]))

# then, generate equations
order = 5
v = [BitVec('v%d'%i, 1) for i in range(order)]

s = Solver()

for i in range(5):
    Sum = 0
    for j in range(5):
        Sum ^= v[j] & k[i+j]
    s.add(k[5+i] == Sum)

print(s.check())
print(s.model())