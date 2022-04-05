import numpy as np

a = np.zeros((2, 4))

print(a)

b = np.arange(100, 200, 10).reshape(2, 5)

print(b)

c = np.array([[11, 22, 33], [44, 55, 66], [77, 88, 99]])

c2= np.array(c[0:3,2])
print(c2)

d = np.array([[3,6,9,12], [15,18,21,24], [17,30,33,36],[39,42,45,48], [51,54,57,60]])

d2 = np.array(d[:5:2,1:4:2])

print(d2)

