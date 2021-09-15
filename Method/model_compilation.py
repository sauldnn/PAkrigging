def model_compilation(df_train, huecos, nkrig=24*7, nbloques=200, x_axis="FechaDEC", y_axis="Valor"):
    """
    Ejecuta el modelo con el control de las dimensiones adecuadas
    de acuerdo a la capacidad de memoria RAM (nbloques = 10,000 equivale a 16gb de RAM).

    Input:
        df_train: pandas.core.frame.DataFrame
            datos de entrenamiento
        huecos: pandas.core.frame.DataFrame
            datos a interpolar
        nkrig: int
            Dimension del variograma, total de datos muestrados
            para una interpolación.
        nbloques: int
            Dimension del tensor
    Ouput: pandas.core.frame.DataFrame
        Conjunto de datos interpolados.
    """
    n_iteraciones = len(huecos)
    dim_inter = round(n_iteraciones/10) if n_iteraciones<nkrig else nkrig
    lista_diteraciones = list(range(0, n_iteraciones, nbloques))
    reemplazo = []
    print("Número de espacios",n_iteraciones)
    timex = time.time()
    for n in lista_diteraciones:
        fin = n+nbloques if n+nbloques<n_iteraciones else n_iteraciones
        print(n, "-", fin, "Tiempo:", time.time()-timex)
        timex = time.time()
        matrices = []
        equals = []
        to_multi = []
        for i in range(n, fin):
            ubic = [huecos[x_axis].iloc[i], 0]
            while True:
                U = df_train.sample(n=dim_inter, random_state=np.random.seed(i)).sort_index().values.tolist()
                matr, equ, to_mul = get_components(ubic, U)
                if np.linalg.det(matr.tolist())>0.0:
                    partial = time.time()
                    to_multi.append(to_mul.tolist())
                    matrices.append(matr.tolist())
                    equals.append(equ.tolist())
                    break
                else: pass
        torch.set_default_tensor_type("torch.cuda.FloatTensor")
        A = torch.tensor(matrices)
        torch.set_default_tensor_type("torch.cuda.FloatTensor")
        b = torch.tensor(equals)
        torch.set_default_tensor_type("torch.cuda.FloatTensor")
        soluciones = torch.linalg.solve(A, b)
        torch.set_default_tensor_type("torch.cuda.FloatTensor")
        producto = torch.tensor(to_multi)
        torch.set_default_tensor_type("torch.cuda.FloatTensor")
        reemplazo = reemplazo +
                    [[huecos[x_axis].iloc[i], torch.dot(soluciones[i][:torch.tensor(to_multi).shape[1]], producto[i]).item()] for i in range(A.shape[0])]
    return pd.DataFrame(data=reemplazo, columns=[x_axis, y_axis])
