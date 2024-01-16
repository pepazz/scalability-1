#@title Def projeta_por_media
import numpy as np
# o df tem que estar ordenado por data com a mais antiga no topo
def projeta_por_media(df,endogenous,qtd_semanas_projetadas,qtd_semanas_media):
  serie = df[endogenous].astype('float').values


  if len(serie) >= qtd_semanas_media:
    serie = serie[-qtd_semanas_media:]

  avg = np.mean(serie)
  forecast = np.zeros(shape=(int(qtd_semanas_projetadas)))
  forecast[:] = avg

  return forecast
