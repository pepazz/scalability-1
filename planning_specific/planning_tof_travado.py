#@title def calcula_shares_historicos

# Importando bibliotecas necessárias
import pandas as pd

def calcula_shares_historicos(df_act_historico, df_parametro, nome_coluna_datas, data_piso_formatada, data_teto_formatada, lista_topos, aberturas_das_bases):
  '''
  Esta função calcula os shares das aberturas da base histórica no período 
  especificado pelo usuário.
  '''

  # Remoção de linhas com valores vazios
  #df_act_historico = df_act_historico.replace(r'^\s*$', np.nan, regex=True)
  #df_act_historico = df_act_historico.dropna()

  # Filtro do período especificado 
  df_act_historico = df_act_historico[df_act_historico[nome_coluna_datas] >= data_piso_formatada]
  df_act_historico = df_act_historico[df_act_historico[nome_coluna_datas] <= data_teto_formatada]
  
  # Remoção de valores de fluxos que não interessam nos topos de demanda
  try:
    df_act_historico.loc[(df_act_historico['fluxo'] == 'DIRECT'), ['vb']] = 0.0
    df_act_historico.loc[(df_act_historico['fluxo'] == 'VISIT'), ['os']] = 0.0
  except:
    pass

  # Inner join da base histórica com um df de parâmetro JÁ TRATADO. Desta forma
  # garante-se que as aberturas observadas no histórico sejam as mesmas do planning
  df_parametro['aux'] = 1
  df_parametro = df_parametro.groupby(aberturas_das_bases, as_index=False)['aux'].sum()
  df_parametro = df_parametro[aberturas_das_bases]
  df_act_historico = pd.merge(df_act_historico,df_parametro,how='inner',on=aberturas_das_bases)


  for topo in lista_topos:
    df_act_historico[topo] = df_act_historico[topo].astype(float)

  agrupado = df_act_historico.groupby(aberturas_das_bases, as_index=False)[lista_topos].sum()

  for topo in lista_topos:
    agrupado[f'{topo}_soma'] = agrupado[topo].sum()
    agrupado[f'share_{topo}'] = agrupado[topo]/agrupado[f'{topo}_soma']


  colunas_shares = [coluna for coluna in agrupado.columns if "share" in coluna]
  colunas_output = aberturas_das_bases+colunas_shares

  agrupado = agrupado[colunas_output]

  return agrupado
#-------------------------------------------------------------------------------



#@title def calcula_volumes_tof_diarizado
def calcula_volumes_tof_diarizado(tof_diarizado, topos_de_funil):

  group_1 = tof_diarizado.groupby(['data','building block tof'],as_index=False)[topos_de_funil].sum()

  for topo in topos_de_funil:
    group_1 = group_1.rename(columns={topo:f'soma_{topo}'})

  tof_diarizado_shares = pd.merge(tof_diarizado,group_1,how='left',on=['data','building block tof'])

  #for topo in topos_de_funil:
  #  tof_diarizado_shares[f'share_{topo}_original'] = tof_diarizado_shares[topo]/tof_diarizado_shares[f'soma_{topo}']
  
  return tof_diarizado_shares
#--------------------------------------------------------------------------------



#@title def ajusta_volumes_tof_travado_diarizado

def ajusta_volumes_tof_travado_diarizado(tof_diarizado_shares, df_shares_historicos, aberturas_das_bases, topos_de_funil):
  
  ToF_travado_diarizado = pd.merge(tof_diarizado_shares, df_shares_historicos, how='left', on=aberturas_das_bases)

  for topo in topos_de_funil:
    #ToF_travado_diarizado[f'fator_{topo}'] = ToF_travado_diarizado[f'share_{topo}_original']/ToF_travado_diarizado[f'share_{topo}']
    #ToF_travado_diarizado[topo] = ToF_travado_diarizado[topo]/ToF_travado_diarizado[f'fator_{topo}']
    ToF_travado_diarizado[topo] = tof_diarizado_shares[f'soma_{topo}']*ToF_travado_diarizado[f'share_{topo}']

  ToF_travado_diarizado = ToF_travado_diarizado.loc[:,~ToF_travado_diarizado.columns.str.contains('_')]

  ToF_travado_diarizado = ToF_travado_diarizado.fillna(0)

  n_ToF_travado_semanal = ToF_travado_diarizado.groupby(aberturas_das_bases+['building block tof', 'semana'],as_index=False)[topos_de_funil].sum()
  n_ToF_travado_semanal = n_ToF_travado_semanal.rename(columns={'semana':'data'})
  n_ToF_travado_semanal.insert(0, 'data',n_ToF_travado_semanal.pop('data'))
  n_ToF_travado_semanal['data'] = pd.to_datetime(n_ToF_travado_semanal['data'],infer_datetime_format=True)

  return ToF_travado_diarizado,n_ToF_travado_semanal
