# cython: boundscheck=False, wraparound=False, nonecheck=False

cpdef inline list fill_black(list virt_matrix, list coords, int virt_color):
    cdef long x
    cdef long y
    cdef unsigned int N = len(coords)
    cdef unsigned int i
    for i from 0 <= i < N:
        x, y = coords[i]
        virt_matrix[x][y] = virt_color

    return virt_matrix


cdef inline int check_black(int x, int y, int color, list matrix, int wid, int hei):
    cdef int total = 8
    cdef int i
    cdef list around
    cdef long  xi
    cdef long  yi

    around = [(-1, -1),(0, -1),(1, -1), (-1, 0), (1, 0),(-1, 1),(0, 1), (1, 1)]

    for i from 0 <= i < total:
        xi, yi = around[i]
        xi = (x + xi) % wid
        yi = (y + yi) % hei

        if matrix[xi][yi] == color:
            total -= 1
        if total < 2:
            return total

    return total


cpdef inline list check_live(list live, int N, list born, list dead, list matrix, int wid, int hei):

    cdef int i
    cdef int j
    cdef int cell_num

    cdef dead_app
    cdef born_app
    cdef black

    cdef list around
    cdef int ind
    cdef long xy0
    cdef long xy1
    cdef int xtemp
    cdef int ytemp
    cdef int total

    dead_app = dead.append
    born_app = born.append


    black = check_black
    for cell_num from 0 <= cell_num < N:
        i, j = live[cell_num]

        total = black(i, j, 0, matrix, wid, hei)

        if total < 2 or total > 3:
            dead_app((i, j))

        around = [(i - 1, j - 1), (i, j - 1),
                  (i + 1, j - 1), (i - 1, j),
                  (i + 1, j), (i - 1, j + 1),
                  (i, j + 1), (i + 1, j + 1)]

        for ind from 0 <= ind < 8:

            xy0, xy1 = around[ind]

            xtemp = xy0 % wid
            ytemp = xy1 % hei
            if matrix[xtemp][ytemp] == 1:
                continue
            total = black(xy0, xy1, 0, matrix, wid, hei)

            if total == 3:
                xy0 = xy0 % wid
                xy1 = xy1 % hei
                born_app((xy0, xy1))

    return [born, dead]
