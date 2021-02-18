# import multiprocessing
#
# def _iterate_search(t, x):
#     t.append(x)
#
#
# if __name__ == "__main__":
#     # a = multiprocessing.Array('i', [])
#
#     a = []
#
#     num_process = 8
#
#
#     ts = []
#     for j in range(1, num_process + 1):
#         t = multiprocessing.Process(target=_iterate_search, args=(a, j,))
#         t.start()
#         ts.append(t)
#
#     for t in ts:
#         t.join()
#
#     print(a)
#


import numpy as np
from numpy.linalg import *

A = np.array(
    [[19.3928, 8.3190],
     [490.6518, 78.9852]]
)

B = np.array([2.2 * 15, 2.2 * 300])


X = solve(A, B)
print(X)

print(np.dot(A, X), B)