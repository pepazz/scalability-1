#@title Def acf_pac
import statsmodels.api as sm
import numpy as np

def acf_pac(df,endogenous):
  df_diferenciado = df[endogenous].astype('float').values[1:]-df[endogenous].astype('float').values[:-1]

  try:
    pacf=sm.tsa.stattools.pacf(df_diferenciado,alpha=0.05,nlags=10)
    acf=sm.tsa.stattools.acf(df_diferenciado,fft=False,nlags=10,alpha=0.05)
  except:
    pacf=[]
    acf=[]

  if len(pacf)>0  and len(acf)>0:
    # AR
    #---------------------------------------------
    limite_superior = (2*pacf[0]-pacf[1][:,1])[1:]
    limite_inferior = (pacf[1][:,0]-2*pacf[0])[1:]

    limite_superior = np.where(limite_superior>0,0,1)
    limite_inferior = np.where(limite_inferior>0,0,1)

    limites = limite_superior*limite_inferior

    if min(limites) != 0:
      ar = 0
    else:
      c_limites = np.cumsum(limites)
      if len(np.where(c_limites==0)[0]) != 0:
        ar = max(np.where(c_limites==0)[0])+1
      else:
        ar = 0

    # MA
    #---------------------------------------------
    limite_superior = (2*acf[0]-acf[1][:,1])[1:]
    limite_inferior = (acf[1][:,0]-2*acf[0])[1:]

    limite_superior = np.where(limite_superior>0,0,1)
    limite_inferior = np.where(limite_inferior>0,0,1)

    limites = limite_superior*limite_inferior

    if min(limites) != 0:
      ma = 0
    else:
      c_limites = np.cumsum(limites)
      if len(np.where(c_limites==0)[0]) != 0:
        ma = max(np.where(c_limites==0)[0])+1
      else:
        ma = 0

  else:
    ar,ma = 0,0

  return ar,ma
