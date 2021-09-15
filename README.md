## Contenidos

1. [Proceso](#readpt01)
2. [Objetivo](#readpt02)
3. [Acerca del método de interpolación de Kriging](#readpt03)
4. [Implementación](#readpt04)
6. [Optimización de la implementación a través del uso de GPU](#readpt06)
5. [Exploración de los datos](#readpt05)
7. [Evaluación del modelo](readpt07)

<a id="readpt01"></a>

## Proceso

<a id="readpt02"></a>

## Objetivo

Entender la utilidad del método. ¿Cuales son los costos de las predicciones? Determinar mejores formas de implementación. Estimar las limitaciones del método.
<a id="readpt03"></a>

## Acerca del método de interpolación de Kriging

Este método de inferencia espacial nos permite estimar los valores de una variable en lugares no muestrados. El planteamiento es muy simple y nos permite obtener el estimador lineal no sesgado con una varianza mínima.

La forma de estimar la varianza del método se expresa como

$$
  \sigma²_k = \displaystyle\sum\lambda_i\bar{\gamma}(x_i, V)-\bar{\gamma}(V, V)+\mu
$$

Las ecuaciones obtenidas para el caso del Kriging ordinario son:

$$
  \displaystyle\sum_{j=1}^{N}{\lambda_j\gamma(x_i, x_j)+\mu} = \bar{\gamma}(x_i, V) \quad i=1, 2, ..., N
$$

$$
  \displaystyle\sum_{i=1}^{N}\lambda_i =1
$$

El sistema anterior se puede expresar de manera equivalente como

$$
  \begin{bmatrix}
    \gamma_{1 1} & \gamma_{1 2} & \cdots & \gamma_{1 N} & 1 \\
    \gamma_{2 1} & \gamma_{2 2} & \cdots & \gamma_{2 N} & 1\\
    \cdots & \cdots & \cdots & \cdots & 1\\
    \gamma_{N 1} & \gamma_{N 2} & \cdots & \gamma_{N N} & 1 \\
    1 & 1 & \cdots & 1 & 0
  \end{bmatrix}
  \begin{bmatrix}
    \lambda_1\\ \lambda_2\\ \  \cdots \\ \lambda_N \\ \mu
  \end{bmatrix}=
  \begin{bmatrix}
    \gamma(x_1, V)\\ \gamma(x_2, V) \\ \cdots \\ \gamma(x_N, V) \\1
  \end{bmatrix}
$$

Entonces, el valor estimado para el punto $V$ puede ser expresado como

$$
  \hat{z_v} = \displaystyle\sum{\lambda'_iz(x_i)} \quad \textrm{ con $\lambda'_i$ como el peso asignado}
$$


<a id="readpt04"></a>

## Implementación

Dado un conjunto de N mediciones, deseamos obtener la estimación de un punto $x_0$ a través de la solución del sistema de ecuaciones $A\lambda =b$.

Para construir las variables que forman la ecuación anterior, supongamos calculada la matriz de distancias del arreglo $X$ y el vector $[\gamma(x_i, V)]$

```python:
# compute la matriz de unos de dimension (N+1, N+2) y sustituya los valores correspondientes y guarde los estimadores en la última columna.
S = np.ones((N+1, N+2))
S[0:dim, 0:dim] = Distances[:dim,:dim]
S[dim, dim] = 0.0
S[0:dim, dim+1] = Distances[0:dim, dim]
A = S[:dim+1, :dim+1]
B = S[0:dim+1, dim+1]
lambda_prime = S[:dim, dim+1]
```
Para calcular el valor estimado para el punto $x_0$ únicamente basta solucionar la ecuación $Ax=B$ y multiplicar el RHS resultante por el vector $\lambda'$.

<a id="readpt05"></a>

## Optimización de la implementación a través del uso de GPU

Una unidad de procesamiento gráfico o GPU, se ha convertido en uno de las más importantes tecnologías para el procesamiento de datos. Diseñado para procesamiento paralelo, una GPU permite optimizar el rendimiento de diferentes procesos entre los que se incluyen herramientas de álgebra lineal, de los cuales haremos uso para la escalabilidad del método.

La forma en que las unidades de procesamiento gráfico reciben los datos es a través de una serie de arreglos, la cual es conocida como tensores, un objeto matemático que puede ser utilizado como vectores cuyas entradas son matrices.

El proceso de introducir matrices como elementos de un tensor es conocido como vectorización y es un método ampliamente usado en la computación paralela.

La forma en la que el programa interactúa con la GPU es vectorizando los componentes de las ecuaciones que nos permiten obtener una estimación, es decir, si queremos calcular el valor interpolado del conjunto $\{x_1, x_2, ..., x_n\}$, entonces debemos calcular los conjuntos $\{A_1, A_2, ..., A_n\}$, $\{b_1, b_2, ..., b_n\}$ y $\{\lambda'_1, \lambda'_2, ..., \lambda'_n\}$ a través de la función *get_components* la cual obtiene estos elementos para cada elemento $x_i$ y una muestra de los datos con los que se desea interpolar todo el conjunto $x$.

```python:
As = []
Bs = []
lambdas = []
for i in range(n):
  u = np.array[x[i], 1]
  A, B, lamb = get_components(u, Datos)
  As.append(A)
  Bs.append(B)
  lambdas.append(lamb)
```
Ahora, podemos hacer uso de la arquitectura de los métodos de solución de ecuaciones en paralelo que implementan el uso de GPU.

```python:
A = torch.tensor(As)
B = torch.tensor(Bs)
sol = torch.linalg.solve(A, B)
Lambda = torch.tensor(lambdas)

resultados = [torch.dot(sol[i][:Lambda.shape[1]], Lambda[i]).item() for i in range(A.shape[0])]
```
Obteniendo un arreglo con los valores interpolados para el conjunto $x$.

<a id="readpt07"></a>

## Exploración de los datos

<a id="readpt06"></a>

## Evaluación del modelo
