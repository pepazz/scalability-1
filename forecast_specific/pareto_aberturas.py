#@title Def pareto_aberturas
import pandas as pd
import numpy as np

def pareto_aberturas(df_historico,   # DataFrame do histórico Cohort
                     etapas_funil,
                     topos,          # Lista com os topos do funil
                     col_data,       # string da coluna que contém datas
                     aberturas,      # lista com as aberturas das bases
                     qtd_periodos,   # int com a quantidade de períodos usados na soma do histórico
                     freq,           # int com a quantidade de dias no perído das datas
                     intervalos,
                     flag_pareto):    # lista com 2 floats indicando os intervalos do pareto [80%,90%]

  if flag_pareto:

    intervalos = [float(i) for i in intervalos]

    # Definimos as datas do histórico a serem somadas e somamos tudo
    data_final = df_historico[col_data].max()
    data_inicial = data_final - pd.Timedelta(qtd_periodos*freq, unit='D')

    etapa_final = etapas_funil[-1]
    etapas = [x for x in etapas_funil if x.split('2')[0] in topos] + [etapa_final]

    df_historico_soma = df_historico.loc[df_historico[col_data]>=data_inicial]
    df_historico_soma = df_historico_soma.groupby(aberturas,as_index=False)[etapas].sum()

    # iniciamos a base final
    pareto_final = pd.DataFrame()
    colunas_pareto = []


    # Para cada etapa de topo e a etapa final do funil, vamos classificar as aberturas em relação ao total
    for etapa in etapas:

      pareto = df_historico_soma[aberturas+[etapa]]

      total = pareto[etapa].sum()
      pareto['total'] = total

      pareto = pareto.sort_values(by=etapa, ascending=False)

      cumsum = pareto[etapa]
      cumsum = cumsum.cumsum()
      pareto['cumsum'] = cumsum

      pareto['%_total_'+etapa] = pareto['cumsum']/pareto['total']

      pareto['pareto_'+etapa] = 3
      pareto.loc[pareto['%_total_'+etapa] <= intervalos[0], ['pareto_'+etapa]] = 1
      pareto.loc[(pareto['%_total_'+etapa] > intervalos[0]) & (pareto['%_total_'+etapa] <= intervalos[1]), ['pareto_'+etapa]] = 2

      # Não vamos realizar o cálculo de pareto se tivermos menos do que 10 aberturas:
      if len(df_historico_soma) < 10:
        pareto['pareto_'+etapa] = 1

      if len(pareto_final) == 0:
        pareto_final = pareto[aberturas+['pareto_'+etapa,'%_total_'+etapa]]
      else:
        pareto_final = pd.merge(pareto_final,pareto[aberturas+['pareto_'+etapa,'%_total_'+etapa]],how='left',on=aberturas)

      colunas_pareto = colunas_pareto + ['pareto_'+etapa,'%_total_'+etapa]

    pareto_final = pareto_final.rename(columns={'pareto_'+etapa_final:'pareto_etapa_final'})
    pareto_final = pareto_final.rename(columns={'%_total_'+etapa_final:'%_total_final'})
    colunas_pareto[-2:] = ['pareto_etapa_final','%_total_final']

    # Vamos aumentar a relevância da abertura no volume de topo se sua relevância na última
    # etapa do funil for maior:
    for etapa in etapas[:-1]:
      pareto_final.loc[pareto_final['pareto_'+etapa] > pareto_final['pareto_etapa_final'],['pareto_'+etapa]] = pareto_final.loc[pareto_final['pareto_'+etapa] > pareto_final['pareto_etapa_final'],['pareto_etapa_final']].values

  else:
    pareto_final = pd.DataFrame()
    colunas_pareto = []

  return pareto_final,colunas_pareto

