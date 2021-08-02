import math
import numpy as np
def k_method(U, ubic):
        """
    Se construye la matriz de unos y se remplazan el primer bloque
    con la matriz de distancias, se calcula la solución del sistema
    de ecuaciones resultante.

    Parameters
    ----------
    U : List
        Lista de dos dimensiones [[], ..., []] que contiene las observaciones
        usadas para construir el sistema de ecuaciones

    ubic : List
        Lista de posicion ['fecha', 0] en la cuál se va a calcular el valor del parametro.

    Returns
    -------
    float
        Valor interpolado.
    """
    dim = len(U)
    U.append(ubic)
    Distances = [[math.dist(U[i],U[j]) for i in range(dim+1)] for j in range(dim+1)]
    S = np.array([[1.0 for i in range(dim+2)] for j in range(dim+1)])
    D = np.array(Distances)
    S[0:dim, 0:dim] = D[:dim,:dim]
    S[dim, dim] = 0.0
    S[0:dim, dim+1] = D[0:dim, dim]
    a = S[:dim+1, :dim+1]
    b = S[0:dim+1, dim+1]
    Sol = np.linalg.solve(a=a, b=b)
    experi = S[0:dim, dim+1]
    result = np.dot(Sol[:dim], experi)
    return result
