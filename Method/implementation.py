import time
import pymysql.cursors
import mysql.connector
import pandas as pd
import math
import random
import numpy as np
from Method import k_method

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

    if len(huecos) > 1:
        print('Inicia Kriging {} a las {} con {} huecos'.format(k, time.strftime('%H:%M:%S', time.localtime()), len(huecos)))

        for i in range(len(huecos)):
            if i % 100 == 0:
                print('Estado: nivel {} iteracion {} a las {}'.format(k, i, time.strftime('%H:%M:%S', time.localtime())))
            ubic = [huecos.iloc[i].FechaDEC, 1]

            while True:
                try:
                    U = [llenos.iloc[random.randrange(1, len(llenos))].tolist() for n in range(nkrig)]
                    out = k_method(U, ubic)
                    if (out > 500) and (out < 600):
                        break
                    else: pass
                except np.linalg.LinAlgError:
                    pass

            Datos.loc[huecos.iloc[i].name, 'Valor'] = out
        print('Fin de operacion {} a las {} '.format(k, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), len(huecos)))

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
