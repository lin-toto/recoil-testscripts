import numpy as np
import sys

file = open(sys.argv[1], 'wb')
lmbda = int(sys.argv[2])
count = int(sys.argv[3])

lst = (np.random.exponential(1/lmbda, count) * 256).astype(int).clip(0, 255).tolist()
data = bytes(lst)
file.write(data)

