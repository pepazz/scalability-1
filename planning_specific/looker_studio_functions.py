#@title Def Data Studio Mensal

# Importando bibliotecas necessárias
import pandas as pd
import numpy as np
from datetime import datetime

def data_studio_mensal(df_actual_mensal,
                      df_planning_diario,
                      df_actual_tp,
                      df_metas_tp,
                      aberturas,
                      col_valores,
                      qtd_meses_resumo):

  # Modificar a base de planning:
  #-------------------------------------------------------------------------------------------------
  df_planning = df_planning_diario.copy()
  #print(df_actual_mensal)
  # Agrupando por mês:
  df_planning = df_planning.groupby(['ano','mês','building block cohort','building block tof']+aberturas, as_index=False)[col_valores].sum()
  
  # transformando a data mensal:
  df_planning['dia'] = 1
  df_planning = df_planning.rename(columns={'ano':'year','mês':'month','dia':'day'})
  df_planning['período'] = pd.to_datetime(df_planning[['year', 'month', 'day']])

  # Vamos selecionar apenas os meses completos:
  ultimo_periodo = df_planning['período'].max()
  primeiro_periodo = df_planning['período'].min()
  #primeiro_periodo = datetime(2022,9,26)

  ultimo_mes = ultimo_periodo.month
  ultimo_ano = ultimo_periodo.year

  primeiro_mes = primeiro_periodo.month
  primeiro_ano = primeiro_periodo.year

  penultimo_mes = ultimo_mes
  penultimo_ano = ultimo_ano

  segundo_mes = primeiro_mes
  segundo_ano = primeiro_ano

  if segundo_mes == 12:
    segundo_mes = 1
    segundo_ano = primeiro_ano + 1
  else:
    segundo_mes = primeiro_mes + 1

  if penultimo_mes == 1:
    penultimo_mes  = 12
    penultimo_ano  = ultimo_ano - 1
  else:
    penultimo_mes = ultimo_mes - 1

  ultimo_dia_do_periodo = datetime(ultimo_ano,ultimo_mes,1) #- pd.Timedelta(1, unit='D')   Comentei essa subtração, se não iria para 30/11
  primeiro_dia_do_periodo = datetime(primeiro_ano,primeiro_mes,1)

  ultimo_dia = df_planning_diario['data'].max()
  primeiro_dia = df_planning_diario['data'].min()
  
  periodo_maximo = ultimo_periodo
  if ultimo_dia_do_periodo != ultimo_dia:
    periodo_maximo = datetime(ultimo_ano,ultimo_mes,1) 

  periodo_minimo = primeiro_periodo
  if primeiro_dia_do_periodo != primeiro_dia:
    periodo_minimo = datetime(segundo_ano,segundo_mes,1) 

  df_planning = df_planning.loc[(df_planning['período'] <= periodo_maximo) & (df_planning['período'] >= periodo_minimo)]

  # Adicionando tier
  tier = df_actual_mensal.groupby(['região','tier'], as_index=False)[col_valores[0]].sum()
  tier = tier[['região','tier']]
  df_planning = pd.merge(df_planning,tier,how='left',on=['região'])

  # Adicionando colunas auxiliares:
  df_planning['fonte'] = 'BUP - Planning'

  # Selecionando apenas as colunas que importam:
  df_planning = df_planning[['período','fonte','tier','building block cohort','building block tof']+aberturas+col_valores]
  
  # definindo primeiro mês de planning:
  primeiro_periodo_planning = df_planning['período'].min()

  # Modificar a base de actual:
  #-------------------------------------------------------------------------------------------------

  df_actual_mensal['building block cohort'] = 'baseline'
  df_actual_mensal['building block tof'] = 'baseline'

  df_actual_mensal['fonte'] = 'Actual'

  # Selecionando apensas as colunas que importam:
  df_actual_mensal = df_actual_mensal[['período','fonte','tier','building block cohort','building block tof']+aberturas+col_valores]

  # Formatando as datas
  df_actual_mensal = df_actual_mensal.loc[df_actual_mensal['período'] < primeiro_periodo_planning]


  # Unir as bases:
  #-------------------------------------------------------------------------------------------------
  df_data_studio_mensal = pd.concat([df_actual_mensal,df_planning])
  df_data_studio_mensal[col_valores] = df_data_studio_mensal[col_valores].astype(float)

  # Adicionar Colunas Auxiliares
  #-------------------------------------------------------------------------------------------------

  # Quantidade de meses que aparecem na visão resumo:
  meses = df_data_studio_mensal['período'].unique()
  meses.sort()
  meses_resumo = meses[len(meses)-qtd_meses_resumo:]
  mes_minimo = meses_resumo[0]


  df_data_studio_mensal['auxiliar resumo'] = 'Outros'
  df_data_studio_mensal.loc[df_data_studio_mensal['período'] >= mes_minimo, ['auxiliar resumo']] = 'Resumo'

  # Auxiliar Fonte:
  df_data_studio_mensal['auxiliar fonte'] = 0
  df_data_studio_mensal.loc[df_data_studio_mensal['fonte'] == 'BUP - Planning', ['auxiliar fonte']] = 1

  # Remove linhas zeradas:
  df_data_studio_mensal = df_data_studio_mensal.fillna(0)
  df_data_studio_mensal['Soma'] = df_data_studio_mensal[col_valores].sum(axis=1)
  df_data_studio_mensal = df_data_studio_mensal.loc[df_data_studio_mensal['Soma'] != 0]
  df_data_studio_mensal = df_data_studio_mensal.drop(columns=['Soma'])

  # Agrupar aberturas repetidas:
  df_data_studio_mensal = df_data_studio_mensal.groupby(['período','fonte','auxiliar fonte','auxiliar resumo','tier','building block cohort','building block tof']+aberturas, as_index=False)[col_valores].sum()

  # Renomear os nomes das colunas:
  nomes_1 = ['período','fonte','auxiliar fonte','auxiliar resumo','tier']
  nomes_1 = [n.title() for n in nomes_1]
  aberturas_1 = [a.title() for a in aberturas]
  col_valores_1 = [c.upper() for c in col_valores]
  colunas_novas = nomes_1+['building block cohort','building block tof']+aberturas_1+col_valores_1

  df_data_studio_mensal = df_data_studio_mensal.rename(columns = dict(zip(df_data_studio_mensal.columns.values, colunas_novas)))

  # Criar linhas para o join dos TP's:
  base_tp = df_data_studio_mensal.loc[df_data_studio_mensal['Auxiliar Resumo'] == 'Resumo']
  base_tp = base_tp.groupby(['Período','Fonte','Auxiliar Fonte','Auxiliar Resumo'], as_index=False)[col_valores_1[0]].sum()
  base_tp = base_tp[['Período','Fonte','Auxiliar Fonte','Auxiliar Resumo']]
  base_tp['building block cohort'] = 'baseline'
  base_tp['building block tof'] = 'baseline'
  base_tp['Auxiliar Resumo'] = 'TP'

  df_data_studio_mensal = pd.concat([df_data_studio_mensal,base_tp]).fillna('')

  # Adicionar a base de TP's:
  if len(df_actual_tp) > 0 and len(df_metas_tp) > 0:

    cb_actual_tp = list(df_actual_tp.columns.values)
    cb_metas_tp = list(df_metas_tp.columns.values)

    col_data_actual_tp = cb_actual_tp[0]
    col_data_metas_tp = cb_metas_tp[0]

    df_actual_tp = df_actual_tp.rename(columns={col_data_actual_tp:'col_data_original'})
    df_metas_tp = df_metas_tp.rename(columns={col_data_metas_tp:'col_data_original'})

    col_data_actual_tp = 'col_data_original'
    col_data_metas_tp = 'col_data_original'

    df_actual_tp['month'] = df_actual_tp[col_data_actual_tp].dt.month
    df_metas_tp['month'] = df_metas_tp[col_data_metas_tp].dt.month
    df_actual_tp['year'] = df_actual_tp[col_data_actual_tp].dt.year
    df_metas_tp['year'] = df_metas_tp[col_data_metas_tp].dt.year
    df_actual_tp['day'] = 1
    df_metas_tp['day'] = 1


    df_actual_tp['Período'] = pd.to_datetime(df_actual_tp[['year', 'month', 'day']])
    df_metas_tp['Período'] = pd.to_datetime(df_metas_tp[['year', 'month', 'day']])

    df_actual_tp = df_actual_tp.loc[df_actual_tp['Período'] < primeiro_periodo_planning]
    df_metas_tp = df_metas_tp.loc[df_metas_tp['Período'] >= primeiro_periodo_planning]

    df_tp = pd.concat([df_actual_tp,df_metas_tp])

    df_tp = df_tp.groupby('Período',as_index=False)['tp'].sum()

    df_tp['Auxiliar Resumo'] = 'TP'

    df_data_studio_mensal = pd.merge(df_data_studio_mensal,df_tp,how='left',on=['Período','Auxiliar Resumo'])

    df_data_studio_mensal = df_data_studio_mensal.fillna(0)

    df_data_studio_mensal = df_data_studio_mensal.rename(columns={'tp':'nTP + rTP'})



  # Formatar coluna de datas:
  #df_data_studio_mensal['período']=pd.to_datetime(df_data_studio_mensal['período'].astype(str), format='%YYYY/%mm/%dd')

  return df_data_studio_mensal
#----------------------------------------------------------------------------------------------------------------------



#@title Def Data Studio Cohort


def data_studio_cohort(df_actual_cohort,
                        df_planning_cohort_unico,
                       col_valores,
                       nome_coluna_week_origin,
                       aberturas,
                       qtd_meses_hist,
                       agrupar_bb):

  # Modificar a base de planning:
  #-------------------------------------------------------------------------------------------------

  df_planning = df_planning_cohort_unico.copy()

  # Adicionando tier
  tier = df_actual_cohort.groupby(['região','tier'], as_index=False)[col_valores[0]].sum()
  tier = tier[['região','tier']]
  df_planning = pd.merge(df_planning,tier,how='left',on=['região']) 

  # Adicionando colunas auxiliares:
  df_planning['fonte'] = 'BUP - Planning'

  # Selecionando apenas as colunas que importam:
  col_data_planning = list(df_planning.columns.values)[0]
  df_planning = df_planning.rename(columns={col_data_planning:'período'})
  df_planning = df_planning[['período','fonte','tier','building block cohort','building block tof']+[nome_coluna_week_origin]+aberturas+col_valores]

  # definindo primeira semana de planning:
  primeiro_periodo_planning = df_planning['período'].min() 
  #primeiro_periodo_planning = datetime(2022,9,26)

  # Modificar a base de actual:
  #-------------------------------------------------------------------------------------------------

  # Mudando o nome das cohorts
  df_actual_cohort[nome_coluna_week_origin] = df_actual_cohort[nome_coluna_week_origin].str.replace('W','')
  df_actual_cohort[nome_coluna_week_origin] = df_actual_cohort[nome_coluna_week_origin].str.replace('+','')
  df_actual_cohort[nome_coluna_week_origin] = df_actual_cohort[nome_coluna_week_origin].replace(r'^\s*$', np.NaN, regex=True)
  df_actual_cohort[nome_coluna_week_origin] = df_actual_cohort[nome_coluna_week_origin].fillna('Não Convertido')

  # Formatando as datas
  # Definindo a primeira data do historico:
  #data_min = primeiro_periodo_planning-pd.to_timedelta(qtd_meses_hist*30,unit="D")
  #df_actual_cohort = df_actual_cohort.loc[(df_actual_cohort['período'] < primeiro_periodo_planning) & (df_actual_cohort['período'] >= data_min)]
  df_actual_cohort = df_actual_cohort.loc[df_actual_cohort['período'] < primeiro_periodo_planning]

  # Adicionando colunas auxiliares:
  df_actual_cohort['fonte'] = 'Actual'

  # Adicionando colunas de BB's
  df_actual_cohort['building block cohort'] = 'baseline'
  df_actual_cohort['building block tof'] = 'baseline'

  # Unir as bases:
  #-------------------------------------------------------------------------------------------------
  df_data_studio_cohort = pd.concat([df_actual_cohort,df_planning])


  chaves_modelo = ['período','building block cohort','building block tof','fonte','tier']+aberturas
  cohorts = list(df_data_studio_cohort[nome_coluna_week_origin].unique())
  modelo_l = df_data_studio_cohort.groupby(chaves_modelo, as_index=False)[col_valores].sum()
  modelo_l = modelo_l[chaves_modelo]
  modelo_l[nome_coluna_week_origin] = cohorts[0]
  aux = modelo_l.copy()
  for c in cohorts[1:]:
    aux[nome_coluna_week_origin] = c
    modelo_l = pd.concat([modelo_l,aux])

  df_data_studio_cohort = pd.merge(modelo_l,df_data_studio_cohort,how='left',on=chaves_modelo+[nome_coluna_week_origin])

  df_data_studio_cohort = df_data_studio_cohort.fillna(0)


  # Renomeamos as colunas da base antes de criar as colunas auxiliares:
  nomes_1 = ['período','fonte','tier']+[nome_coluna_week_origin]
  nomes_1 = [n.title() for n in nomes_1]
  aberturas_1 = [a.title() for a in aberturas]
  col_valores_1 = [c.upper() for c in col_valores]
  chaves_novas = nomes_1+['building block cohort','building block tof']+aberturas_1
  chaves_novas_sem_conversao = ['Período','Fonte','Tier']+['building block cohort','building block tof']+aberturas_1
  colunas_novas_aux = chaves_novas+col_valores_1

  # reordenar as colunas novas antes de mudar na base:
  colunas_novas_minusculo = [c.lower() for c in colunas_novas_aux]
  colunas_originais = list(df_data_studio_cohort.columns.values)
  colunas_novas = []
  for c in range(len(colunas_originais)):
    index = colunas_novas_minusculo.index(colunas_originais[c])
    colunas_novas = colunas_novas + [colunas_novas_aux[index]]


  df_data_studio_cohort = df_data_studio_cohort.rename(columns = dict(zip(df_data_studio_cohort.columns.values, colunas_novas)))
  df_data_studio_cohort = df_data_studio_cohort.rename(columns = {nome_coluna_week_origin.title():'Weeks Conversion'})


  # Criamos as colunas auxiliares do cálculo de cohorts
  vol_cohort_aberta = df_data_studio_cohort.loc[df_data_studio_cohort['Weeks Conversion'] != 'Coincident']
  vol_cohort_aberta = vol_cohort_aberta.groupby(chaves_novas_sem_conversao, as_index=False)[col_valores_1].sum()
  nomes_col_abertas = ['Total '+e for e in col_valores_1]
  vol_cohort_aberta = vol_cohort_aberta.rename(columns=dict(zip(col_valores_1,nomes_col_abertas)))

  df_data_studio_cohort = pd.merge(df_data_studio_cohort,vol_cohort_aberta,how='left',on=chaves_novas_sem_conversao)

  # Caso não seja necessária a abertura de BB's:
  if agrupar_bb:
    chaves_sem_bb = list(set(chaves_novas_sem_conversao+['Weeks Conversion']) - set(['building block cohort','building block tof']))
    col_valores = col_valores_1+nomes_col_abertas
    df_data_studio_cohort = df_data_studio_cohort.groupby(chaves_sem_bb, as_index = False)[col_valores].sum()
    df_data_studio_cohort[['building block cohort','building block tof']] = "Total"


  # Criamos a coluna auxiliar de fonte:
  df_data_studio_cohort['Auxiliar Fonte'] = 0
  df_data_studio_cohort.loc[df_data_studio_cohort['Fonte'] == 'BUP - Planning', ['Auxiliar Fonte']] = 1


  # Remove linhas zeradas:

  df_data_studio_cohort = df_data_studio_cohort.fillna(0)
  df_data_studio_cohort['Soma'] = df_data_studio_cohort[col_valores_1+nomes_col_abertas].sum(axis=1)
  df_data_studio_cohort = df_data_studio_cohort.loc[df_data_studio_cohort['Soma'] != 0]
  df_data_studio_cohort = df_data_studio_cohort.drop(columns=['Soma'])



  return df_data_studio_cohort

