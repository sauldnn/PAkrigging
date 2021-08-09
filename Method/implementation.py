import time
import pymysql.cursors
import mysql.connector
import pandas as pd
import math
import random
from Method import k_method
from scipy.spatial import distance_matrix
print('Inicia el programa a las ', time.strftime('%H:%M:%S', time.localtime()))

# Connect to the database
databaseName = 'PA'
username = 'root'
password = 'root'
driver = 'MySQL'
host = 'localhost'

connection = pymysql.connect(host=host,
                             user=username,
                             password=password,
                             database='PA',
                             cursorclass=pymysql.cursors.DictCursor)

base = 'presionatmosferica'
with connection.cursor() as cursor:
    cursor.execute("SELECT DISTINCT Estacion FROM {}".format(base))
    result_est = cursor.fetchall()
    cursor.execute("SELECT DISTINCT Parametro FROM {}".format(base))
    result_par = cursor.fetchall()

estaciones = pd.DataFrame(result_est)
parametros = pd.DataFrame(result_par)
QuerySerial = [
                [i, estaciones.Estacion.iloc[i],
                parametros.Parametro.iloc[j]]
                for i in range(len(estaciones))
                for j in range(len(parametros))
                ]
nkrig = 24 * 7

for k in range(len(QuerySerial)):
    ConsultaV = 'SELECT FechaDEC, Valor FROM presionatmosferica WHERE Estacion="' + QuerySerial[k][1] + '" ORDER BY FechaDEC ASC'
    with connection.cursor() as cursor:
        cursor.execute(ConsultaV)
        Valor = cursor.fetchall()
    Datos = pd.DataFrame(Valor)
    Datos['Valor'] = pd.to_numeric(Datos['Valor'], errors='coerce')
    Datos['FechaDEC'] = pd.to_numeric(Datos['FechaDEC'], errors='coerce')
    llenos = Datos.dropna()
    huecos = Datos[Datos.isnull().values]

    if len(huecos) > 0:
        print('Inicia Kriging {} a las {} con {} huecos'.format(k, time.strftime('%H:%M:%S', time.localtime()), len(huecos)))
        matrices = []
        equals = []
        to_multi = []
        timein = time.time()

        for i in range(len(huecos)):
            if i % 100 == 0:
                print('Estado: Estacion {} iteracion {} a las {}'.format(k, i, time.time()))
            ubic = [huecos.iloc[i].FechaDEC, 1]
            while True:
                # calculamos el muestreo y las matrices y vectores.
                #sampl = sample([x for x in range(0,len(llenos))], 24*7)
                #U = llenos.iloc[sampl].values.tolist()
                U = llenos.sample(n=nkrig).values.tolist()
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
        reemplazo = [torch.dot(soluciones[i][:torch.tensor(to_multi).shape[1]], torch.tensor(to_multi)[i]).item()
                    for i in range(A.shape[0])]

        for i in range(len(huecos)):
            Datos.loc[Datos[Datos.isnull().values].index[i], 'Valor'] = reemplazo[i]
        print('Fin de operacion {} a las {} '.format(k, time.time(), len(huecos)))

        mydb = mysql.connector.connect(host='localhost',
                             user='root',
                             password='root',
                             database='PA',
                             #cursorclass=pymysql.cursors.DictCursor
                              )
        mycursor = mydb.cursor()
        for j in range(len(huecos)):
            calculado = str(Datos['Valor'].iloc[huecos.iloc[i].name])
            fecha = str(Datos['Valor'].iloc[huecos.iloc[i].name])
            que = 'UPDATE presionatmosferica SET valor={} WHERE Consecutivo={}'.format(calculado, fecha)
            mycursor.execute(que)
        mydb.commit
