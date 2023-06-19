#@title Def Share Diário
import pandas as pd
import datetime
from datetime import datetime 

def share_diario(df_parametro, #df que será a base
                 data_inicio, #data inicial do filtro
                 data_fim, #data final do filtro
                 coluna_semanas, #week_start
                 coluna_datas, #date
                 etapas_vol, #nome das etapas que serão buscadas. Ex: vb/visits_booked, etc
                 min_diario, #valor mínimo que um share diário deve ter
                 max_diario, #valor máximo que um share diário deve ter
                 aberturas, #nome das aberturas que serão consideradas
                 df_planning): #combinações que serão calculadas, conforme o planning
    '''
    Tratamento inicial dos dados
    '''
    
    max_share = float(max_diario) #Aqui transformamos o min e max permitdo em float
    min_share = float(min_diario)
    days = ['Sunday', 'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'] #lista com os nomes dos dias para incluir posteriormente nos campos vazios.      

    etapas = etapas_vol #Aqui criamos as listas com os nomes dos kpis. Geramos para cada etapa para facilitar os merges e group bys
    etapas_day = [e+"_day" for e in etapas]
    etapas_week = [e+"_week" for e in etapas]
    etapas_share = [e+"_share" for e in etapas]
    etapas_share_soma = [e+"_y" for e in etapas_share]
    etapas_share_dia = [e+"_x" for e in etapas_share]

    # Caso não encontremos a coluna de semanas na base, vamos criar uma:
    if coluna_semanas not in df_parametro.columns.values:
      coluna_semanas = 'week_start'
      df_parametro[coluna_semanas] = df_parametro[coluna_datas].dt.to_period('W').apply(lambda r: r.start_time)

    df_parametro[coluna_semanas] = pd.to_datetime(df_parametro[coluna_semanas], infer_datetime_format = True) #Convertendo datas para datetime
    df_parametro[coluna_datas] = pd.to_datetime(df_parametro[coluna_datas], infer_datetime_format = True)
    df_parametro['dia da semana'] = df_parametro[coluna_datas].dt.day_name() #Inclusão da coluna dia da semana. Com o nome do dia em inglês

    df_parametro = df_parametro[(df_parametro[coluna_semanas] >= data_inicio) & (df_parametro[coluna_semanas] <= data_fim)] #Filtro de data inserido no painel de controle ou fixo no código
    df_bases_totais = df_planning.copy()
    df_bases_totais['aux'] = 1
    df_bases_totais = df_bases_totais.groupby(aberturas, as_index = False)['aux'].sum() #criação de base com todas as combinações de aberturas + dias disponíveis
    df_bases_totais = df_bases_totais.drop(columns = ['aux']) #Remoção dos kpis para a base virar apenas dias + aberturas.

    df_bases_totais['dia da semana'] = days[0] #como a base não tem mais kpis, transformamos todos em sunday. Para em seguida fazer o loop de adicionar todos os dias.

    aux = df_bases_totais.copy()
    for w in days[1:]: #Nesse for, inserimos na base todos os dias da semana para cada região+abertura disponível
      aux['dia da semana'] = w
      df_bases_totais = pd.concat([df_bases_totais,aux])
      #a partir de agora, todas as combinações de aberturas tem todos os dias da semana, mas sem nenhum kpi. Os joins serão feitos mais abaixo.


    df_weeks = df_parametro.groupby([coluna_semanas] + aberturas, as_index=False)[etapas_vol].sum() #groupby para transformar a base em um df de week_starts
    df_days = df_parametro.groupby([coluna_semanas] + aberturas + ['dia da semana'], as_index=False)[etapas_vol].sum() #groupby para transformar a base em um df de dias da semana
    df_share = pd.merge(df_days, df_weeks, how='left', on = [coluna_semanas] + aberturas, suffixes= ('_dia da semana', '_week')) #merge entre os dois dfs acima para que tenhamos em um mesmo df o valor total da semana e o do dia.
    df_share = pd.merge(df_bases_totais, df_share, how = 'left', on = aberturas + ['dia da semana']) #merge da base com todas aberturas possíveis com os kpis


    df_share = df_share.fillna(0) #transformando os NaNs em zero.
    df_share[etapas_share] = df_share[etapas_day].astype(float).values/df_share[etapas_week].astype(float).values #criação de uma terceira conta onde dividimos o valor diário pelo total semanal.
    df_share = df_share.fillna(0) #Por precaução transformando novamente os NaNs em zero.


    #teste = gc.open(Nome_do_arquivo_sheets)
    #aba = teste.worksheet("share_diario")
    df_share = df_share.groupby(aberturas+['dia da semana'], as_index=False)[etapas_share].mean() #média dos percentuais de todos os week_starts

    for etapa in etapas_share: #Tudo que é menor que o mínimo, vira o mínimo permitido. Tratamos fins de semanas com pesos diferentes
      df_share.loc[( (df_share['dia da semana'] == 'Sunday') & (df_share[etapa] < min_share) ), [etapa]] = 1./78
      df_share.loc[( (df_share['dia da semana'] == 'Saturday') & (df_share[etapa] < min_share) ), [etapa]] = 1./10
      df_share.loc[( (df_share['dia da semana'] != 'Sunday') & (df_share['dia da semana'] != 'Saturday') & (df_share[etapa] < min_share) ), [etapa]] = 1.0/7
    df_share[etapas_share] = np.where(df_share[etapas_share] > max_share, max_share, df_share[etapas_share]) #Tudo que é maior que o máximo, vira o máximo permitido.

    df_soma = df_share.groupby(aberturas, as_index=False)[etapas_share].sum() #criação de um df que soma todas as médias desses percentuais.
    df_share = pd.merge(df_share,df_soma,how='left',on=aberturas) #inclusão desses valores acima no df principal
    df_share[etapas_share] = df_share[etapas_share_dia].astype(float).values/df_share[etapas_share_soma].astype(float).values #Para que a divisão da semana seja sempre 100%, fazemos a nova divisão.
    df_share = df_share.drop(columns = etapas_share_dia + etapas_share_soma) #retiramos as colunas desnecessárias
    df_share = df_share.fillna(0)
    #df_share = df_share.rename(columns={'day':'dia da semana'})
    df_share = df_share.rename(columns=dict(zip(etapas_share,etapas)))

    
    return df_share
