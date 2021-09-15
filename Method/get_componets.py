def get_components(ubic, U):
  """
  Input:
    ubic: List
      Lista de dimensión (2,1) para el cual se va a calcular el variograma
    U: numpy.ndarray
      Arreglo que contiene los datos del muestreo necesarios para construir el variograma de ubic.
  Output:
    matr: numpy.ndarray
      Matriz de dimensión (nkrig+1, nkrig+1) que contiene los coeficientes del sistema de ecuaciones
      creado por el variograma
    equ: numpy.ndarray
      Vector de dimensión (1, nkrig+1) que contiene el RHS de la ecuación Ax=b
    to_mult: numpy.ndarray
      Vector de estimadores de dimensión (1, nkrig)

  """
  dim = len(U)
  U.append(ubic)
  Distances = distance_matrix(U, U).tolist()
  S = np.ones((dim+1, dim+2))
  D = np.array(Distances)
  S[0:dim, 0:dim] = D[:dim,:dim]
  S[dim, dim] = 0.0
  S[0:dim, dim+1] = D[0:dim, dim]
  matr = S[:dim+1, :dim+1]
  equ = S[0:dim+1, dim+1]
  to_mult = S[:dim, dim+1]
  return matr, equ, to_mult
