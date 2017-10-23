# cython: boundscheck=False, wraparound=False, nonecheck=False

import numpy as np
from numpy cimport ndarray
cimport numpy as np

DTYPE = np.int64
ctypedef np.int64_t DTYPE_t


cpdef inline np.ndarray fill_black_numpy(np.ndarray virt_matrix, np.ndarray coords,long color):

    virt_matrix[tuple(coords.T)] = color
    return virt_matrix


cdef inline list check_black(np.ndarray liv, tuple gen_size, np.ndarray matrix, DTYPE_t cellclr, int wid, int hei):

    cdef np.ndarray[DTYPE_t, ndim=2, mode="c"] around
    cdef np.ndarray[DTYPE_t, ndim=2, mode="c"] gener
    cdef np.ndarray[DTYPE_t, ndim=2, mode="c"] temp
    cdef np.ndarray generT
    cdef unsigned int i
    cdef np.ndarray[DTYPE_t, ndim=1, mode="c"] colored
    cdef np.ndarray[DTYPE_t, ndim=2, mode="c"] fin
    cdef np.ndarray[DTYPE_t, ndim=1, mode="c"] total

    around = np.array([[-1, 0, 1, -1, 1, -1, 0, 1],
                       [-1, -1, -1, 0, 0, 1, 1, 1]])

    gener = np.zeros(gen_size, dtype=DTYPE)
    temp = np.zeros(gen_size, dtype=DTYPE)


    for i from 0 <= i < 8:
        if gener.sum() == 0:
            gener[0] = (liv[0] + around[0][i]) % wid
            gener[1] = (liv[1] + around[1][i]) % hei
        else:
            temp[0] = (liv[0] + around[0][i]) % wid
            temp[1] = (liv[1] + around[1][i]) % hei

            gener = np.vstack((gener, temp))

    generT = np.reshape(gener.T, (gener.T.shape[0] * 8,
                               gener.T.shape[1] // 8)).T


    colored = (matrix[tuple(generT)] == cellclr).astype(int)
    fin = np.reshape(colored, (len(colored) // 8, 8))
    total = np.sum(fin, axis=1)

    return [generT, total]

cpdef inline list check_live(list live, np.ndarray matrix, np.ndarray fin_born, np.ndarray fin_dead, DTYPE_t cellclr, int wid, int hei):

    cdef np.ndarray liv = np.array(live).T
    cdef np.ndarray gener
    cdef np.ndarray born
    cdef np.ndarray[DTYPE_t, ndim=1, mode="c"] total
    cdef np.ndarray tot3
    cdef np.ndarray tot2
    cdef np.ndarray[DTYPE_t, ndim=2, mode="c"] make_dead3
    cdef np.ndarray[DTYPE_t, ndim=2, mode="c"] make_dead2
    cdef np.ndarray[DTYPE_t, ndim=2, mode="c"] make_born
    cdef np.ndarray sort_idx, sorted_data, row_mask

    cdef tuple gen_size


    if live:
        gen_size = (2,len(live))

        gener, total  = check_black(liv, gen_size, matrix, cellclr, wid, hei)

        tot3 = (total > 3)
        tot2 = (total < 2)

        make_dead3 = liv.T[tot3]
        make_dead2 = liv.T[tot2]

        fin_dead = np.concatenate((make_dead2, make_dead3))

        gen_size = (2,len(gener[0]))

        born, total = check_black(gener, gen_size, matrix, cellclr, wid, hei)
        tot3 = (total == 3)
        make_born = gener.T[tot3]
        if make_born.any():
            sort_idx = np.lexsort(make_born.T)
            sorted_data = make_born[sort_idx, :]
            row_mask = np.append([True], np.any(np.diff(sorted_data,
                                                            axis=0), 1))
            fin_born = sorted_data[row_mask]
        else:
            fin_born = make_born


    return [fin_born, fin_dead]
