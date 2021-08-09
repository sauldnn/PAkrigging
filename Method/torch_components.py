def torch_components(ubic, U):
    dim = len(U)
    U.append(ubic)
    #Distances = [[torch.dist(torch.tensor(U[i]), torch.tensor(U[j]), 2).item() for i in range(dim+1)] for j in range(dim+1)]
    #Distances = [[float(np.linalg.norm((U[i][0]-U[j][0], U[i][1]-U[j][1]))) for i in range(dim+1)] for j in range(dim+1)]
    Distances = distance_matrix(U, U).tolist()
    torch.set_default_tensor_type("torch.cuda.FloatTensor")
    S = torch.ones(dim+1, dim+2)
    torch.set_default_tensor_type("torch.cuda.FloatTensor")
    D = torch.tensor(Distances)
    S[0:dim, 0:dim] = D[:dim,:dim]
    S[dim, dim] = 0.0
    S[0:dim, dim+1] = D[0:dim, dim]
    matr = S[:dim+1, :dim+1]
    equ = S[0:dim+1, dim+1]
    to_mult = S[:dim, dim+1]
    return matr, equ, to_mult
