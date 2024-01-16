#@title Def parametros_modelo
import random
from sklearn.utils import resample
from sklearn.base import clone
import numpy as np
import pandas as pd
def parametros_modelo(modelo,X,y,pivot,erro):

  params = pd.Series(modelo.coef_[0], index=X.columns.values)

  if modelo.intercept_ != 0.0:
    intercept = pd.Series(modelo.intercept_[0], index=X.columns.values)
  else:
    intercept = [0 for x in list(params)]

  if erro:
    np.random.seed(1)
    modelo_2 = clone(modelo)
    err = np.std([modelo_2.fit(*resample(X, y)).coef_[0]
                  for i in range(100)], 0)
  else:
    err = 0


  parametros = pd.DataFrame({'slope': params,
                             'intercept': intercept,
                              'error': err})

  if pivot:
    parametros = parametros.reset_index(inplace=False)
    parametros = parametros.rename(columns={'index':'parametro'})
    parametros = pd.pivot_table(parametros, values=['slope','intercept','error'], columns='parametro')#.reset_index(inplace=False)

  return parametros
