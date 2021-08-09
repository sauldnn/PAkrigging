def get_components():
    """
    Se construye la matriz de unos y se remplazan el primer bloque
    con la matriz de distancias, se calculan los componenetes de la ecuación
    AX=B.

    Parameters
    ----------
    U : List
        Lista de dos dimensiones [[], ..., []] que contiene el sampleo

    ubic : List
        Lista de posicion ['fecha', 0] en la cuál se va a calcular el valor del parametro.

    Returns
    -------
    matr, equ, to_mult: lists
        Componentes de la ecuación AX=B

    """
    dim = len(U)
    U.append(ubic)
    #Distances = [[torch.dist(torch.tensor(U[i]), torch.tensor(U[j]), 2).item() for i in range(dim+1)] for j in range(dim+1)]
    Distances = [[float(np.linalg.norm((U[i][0]-U[j][0],U[i][1]-U[j][1]))) for i in range(dim+1)] for j in range(dim+1)]
    S = np.array([[1.0 for i in range(dim+2)] for j in range(dim+1)])
    D = np.array(Distances)
    S[0:dim, 0:dim] = D[:dim,:dim]
    S[dim, dim] = 0.0
    S[0:dim, dim+1] = D[0:dim, dim]
    matr = S[:dim+1, :dim+1]
    equ = S[0:dim+1, dim+1]
    to_mult = S[:dim, dim+1]
    return matr, equ, to_mult
