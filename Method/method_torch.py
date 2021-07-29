import math
import numpy as np
import torch

def tor_method(U, ubic):
    dim = len(U)
    U.append(ubic)
    Distances = [[math.dist(U[i],U[j]) for i in range(dim+1)] for j in range(dim+1)]
    S = torch.tensor([[1.0 for i in range(dim+2)] for j in range(dim+1)])
    D = torch.tensor(Distances)
    S[0:dim, 0:dim] = D[:dim,:dim]
    S[dim, dim] = 0.0
    S[0:dim, dim+1] = D[0:dim, dim]
    a = S[:dim+1, :dim+1]
    b = S[0:dim+1, dim+1]
    Sol, _ = torch.linalg.solve(a, b)
    vect = S[0:dim, dim+1]
    result = torch.dot(Sol[:dim], experi)
    return result.item()
