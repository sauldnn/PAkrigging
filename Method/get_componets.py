def get_components():
    dim = len(U)
    U.append(ubic)
    Distances = [[math.dist(U[i],U[j]) for i in range(dim+1)] for j in range(dim+1)]
    S = np.array([[1.0 for i in range(dim+2)] for j in range(dim+1)])
    D = np.array(Distances)
    S[0:dim, 0:dim] = D[:dim,:dim]
    S[dim, dim] = 0.0
    S[0:dim, dim+1] = D[0:dim, dim]
    matr = S[:dim+1, :dim+1]
    equ = S[0:dim+1, dim+1]
    to_mult = S[0:dim, dim+1]
    return matr, equ, to_mult
