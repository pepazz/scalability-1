#@title Def forcast_share_diario 0.0
import pandas as pd
import numpy as np


def forcast_share_diario(df_diario,
                          df_modelo,
                         etapas_vol,
                        qtd_semanas_media,
                         ultima_data_hist):

  out = df_modelo.copy()

  cb = list(out.columns.values)
  cb_d = list(df_diario.columns.values)

  aberturas = cb[1:cb.index('Week Origin')]

  etapas = etapas_vol
  etapas_soma = [e+"_soma" for e in etapas]
  etapas_share = [e+"_share" for e in etapas]

  col_data_week = cb[0]
  col_data_date = cb_d[0]

  df_diario[col_data_date] = pd.to_datetime(df_diario[col_data_date])
  df_diario[col_data_week] = pd.to_datetime(df_diario[col_data_week])

  cb_d_novo = cb_d[:-len(etapas)] + etapas
  df_diario = df_diario.rename(columns=dict(zip(cb_d, cb_d_novo)))

  df_diario[etapas] = df_diario[etapas].astype(float)

  out = out.groupby(aberturas, as_index=False)[cb[-1]].sum()
  out = out.drop(columns=[cb[-1]])

  weekdays = list(range(0,7))

  out['WeekDay'] = weekdays[0]

  aux = out.copy()
  lista_out = [out]
  for w in weekdays[1:]:
    aux['WeekDay'] = w
    lista_out = lista_out + [aux.copy()]
  out = pd.concat(lista_out)

  #-------------------------------------------------------------------------------------------------

  df_diario[col_data_date] = df_diario[col_data_date]
  df_diario[col_data_week] = df_diario[col_data_week]

  df_diario['WeekDay'] = df_diario[col_data_date].dt.dayofweek


  soma_semana = df_diario.groupby(aberturas+[col_data_week], as_index=False)[etapas].sum()
  soma_semana = soma_semana.rename(columns=dict(zip(etapas, etapas_soma)))

  merged = pd.merge(df_diario,soma_semana,how='left',on=aberturas+[col_data_week])

  merged[etapas_share] = merged[etapas].astype(float).values/merged[etapas_soma].astype(float).values

  merged = merged.fillna(0)

  #last_week = np.max(merged[col_data_week].values)
  last_week = ultima_data_hist
  firts_week = last_week-pd.Timedelta(qtd_semanas_media*7, unit='D')

  merged = merged.loc[merged[col_data_week] >= firts_week]

  average = merged.groupby(aberturas+['WeekDay'], as_index=False)[etapas_share].mean()

  #-------------------------------------------------------------------------------------------------

  out = pd.merge(out,average,how='left',on=aberturas+['WeekDay'])


  for e in etapas_share:
    out.loc[out[e]>0.4,[e]] = 1/7
    out.loc[out[e]<0.001,[e]] = 1/7
  out = out.fillna(1/7)

  out_soma = out.groupby(aberturas, as_index=False)[etapas_share].sum()
  out_soma = out_soma.rename(columns=dict(zip(etapas_share, etapas_soma)))


  out = pd.merge(out,out_soma,how='left',on=aberturas)
  out[etapas_share] = out[etapas_share].astype(float).values/out[etapas_soma].astype(float).values

  out = out.drop(columns=etapas_soma)

  return out,etapas_share



