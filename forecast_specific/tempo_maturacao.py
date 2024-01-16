#@title Def tempo_maturacao
impport numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta

def tempo_maturacao(historico_df,        # DataFrame historico filtrado na abertura e etapa
                    max_origin,          # int com a cohort máxima
                    col_data,
                    data_corte,
                    qtd_semanas_media):  # int com a quantidade de semanas do historico a serem consideradas na média

  # Define o cabeçalho da base historica
  cb = list(historico_df.columns.values)
  conversoes = cb[cb.index('Volume')+1:cb.index('Coincident')]


  # Seleciona da base historica apenas as colunas que importam
  base = historico_df[[col_data]+conversoes]
  base[conversoes] = base[conversoes].astype(float)

  # Caso a base esteja toda zerada, vamos retornar a max_origin.
  # Caso contrário prosseguimos com os cálculos:
  if np.sum(base[conversoes].values) == 0:
    return max_origin
  else:



    # Definimos a data máxima e mínima a ser considerada na maturação
    base[col_data] = pd.to_datetime(base[col_data], infer_datetime_format=True)
    data_max = data_corte-pd.Timedelta(max_origin*7, unit='D')
    data_min = data_max-pd.Timedelta(qtd_semanas_media*7, unit='D')

    # Define o nome das colunas que receberam os dados da soma cumulativa das conversões cohort
    maturacao = list(range(max_origin+1))
    soma_cumulativa = list(range(max_origin+1))
    for i in range(max_origin+1):
      maturacao[i] = str(maturacao[i])+'_m'
      soma_cumulativa[i] = str(soma_cumulativa[i])+'_s'


    # Define a base com a soma cumulativa das conversões
    cumsum = base[conversoes[1:]]
    cumsum = cumsum.cumsum(axis=1)
    base[soma_cumulativa] = cumsum.values

    # Definimos o grau da maturação das cohorts dividindo a soma cumulativa das mesmas pela cohort aberta
    base[maturacao] = base[soma_cumulativa].div(base['Volume Aberta']+0.000001, axis=0)

    # Selecionamos apenas as colunas que importam
    base = base[[col_data]+maturacao]

    # Transformamos a base transferindo as colunas de convesões para as linhas
    base = pd.melt(base, id_vars=[col_data], value_vars=maturacao)


    # Selecionamos apenas as conversões que estão >=99% maturadas
    base = base.loc[base['value'] >= 0.99]
    # Selecionamos apenas as semanas que já maturaram em teoria
    base = base.loc[base[col_data] <= data_max]
    # Selecionamos as semanas consideradas na média:
    base = base.loc[base[col_data] >= data_min]



    # Descartamos a coluna de valores
    base = base[[col_data]+['variable']]

    # Transformamos em inteiro as linhas da coluna que contém o índice das cohorts de maturação
    base['variable'] = [sub.replace('_m', '') for sub in list(base['variable'].values)]
    base['variable'] = base['variable'].astype(int)

    # Agrupamos a base pelas datas e pela cohort mínima que chegou na maturação
    base = base.groupby([col_data], as_index=False)[['variable']].min()


    # Tiramos a média do número de cohorts fechadas nas semanas selecionadas que maturaram
    # a cohort aberta em 99% e arredondamos para cima:

    # Vamos checar se por um acaso todas as cohorts da base que maturaram acima de 99% são as mesmas.
    # Nesse caso, vamos assumir que a maturação ocorre na próxima. Fazemos isso para evitar os casos
    # onde foi coincidência e na verdade estamos influando ao máximo a W5+.
    if np.average(base['variable'].values) == np.ceil(np.average(base['variable'].values)) and int(np.average(base['variable'].values)) != int(max_origin):
      maturacao_media = np.ceil(np.average(base['variable'].values))+1
    else:
      maturacao_media = np.ceil(np.average(base['variable'].values))


    if maturacao_media >= max_origin or np.isnan(maturacao_media):
      maturacao_media = max_origin

    return maturacao_media




