import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(max_train_size=None, n_splits=6)
index = range(len(df))
errors = []
for train_index, test_index in tscv.split(index):
    d_train, d_test = df.iloc[train_index], df.iloc[test_index]
    d_hat = model_compilation(d_train, d_test, 24*7, 2000)
    error_i = relative_error(d_test['Valor'].tolist(), d_hat['Valor'].tolist())
    print(error_i)
    errors.append(error_i)
