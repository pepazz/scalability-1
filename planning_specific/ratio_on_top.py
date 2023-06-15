#@title Def Ratio on top

# Importando bibliotecas necessárias
import pandas as pd
import numpy as np

def ratio_on_top(df_parametro, #df que será a base de cálculo
                 df_planning, #combinações que serão calculadas, conforme o planning
                 data_inicio, #data inicial do filtro
                 data_fim, #data final do filtro
                 coluna_semanas, #week_start
                 etapas_vol, #nome das etapas que serão buscadas. Ex: vb/visits_booked, etc
                 aberturas, #nome das aberturas que serão consideradas
                 div_racionais, #lista informando os racionais a serem calculados e quais aberturas e devem ser zeradas para cada racional. Inicialmente VISIT para fluxo em os/vb e os/vc
                 min_std, #qtd de desvio padrões que deve ser considerados para remover outlier inferior
                 max_std): #qtd de desvio padrões que deve ser considerados para remover outlier superior

    max_std = float(max_std) #Aqui transformamos o min e max permitdo em float
    min_std = float(min_std)
    '''
    Splitando em listas os racionais e aberturas a zerar
    '''
    div_racionais = div_racionais.split(',')
    racionais = [item.strip().split('|') for item in div_racionais] #Primeira separação dos racionais que devem ser zerados, em certas circusntâncias.
    aux = list() #Criação da lista que vai possuir as listas de racionais e regras.
    for i in range (len(racionais)): #Nesse for o aux se torna uma lista, dentro de uma lista, dentro de outra. trazendo no micro: 'vb/os', 'abertura', 'todos'
      a = [item.strip().split(':') for item in racionais[i]]
      aux.append(a) 
    ratios = list()
    for i in range (len(aux)): #separação de uma lista trazendo só os racionais.
      kpi = aux[i][0][0].strip()
      ratios.append(kpi)

    ratios = [x.lower() for x in ratios] #transforma a lista de strings para letras minúsculas
    ratios_split_1 = [item.split('/', 1)[0].strip() for item in ratios] #Separação para pegar só os dividendos
    ratios_split_2 = [item.split('/', 1)[1].strip() for item in ratios] #Separação para pegar só os divisores

    '''
    Criando um DataFrame com todas as bases exigidas no planning
    '''

    df_completo = df_planning
    df_completo['aux'] = 1
    df_completo = df_completo.groupby(aberturas, as_index=False)['aux'].sum() #Criação de uma base com todas as aberturas possíveis na query
    df_completo = df_completo.drop(columns = 'aux') #Remoção dos kpis para a base virar apenas aberturas.
    
    '''
    Criando o DataFrame com a média global de cada ratio
    '''

    df_media_global = df_parametro.copy()
    df_media_global[coluna_semanas] = pd.to_datetime(df_media_global[coluna_semanas], infer_datetime_format = True) #Convertendo datas para datetime
    df_media_global = df_media_global.groupby([coluna_semanas] + aberturas, as_index=False)[etapas_vol].sum() #groupby do df media global para trazer sum por week_start
    df_media_global[ratios] = df_media_global[ratios_split_2].astype(float).values/df_media_global[ratios_split_1].astype(float).values #Calculando os racionais. Dividindo os kpis para da base total de medias.
    df_media_global.replace([np.inf, -np.inf], 0.0, inplace=True) #transformando os infinitos em zero
    for i in range (len(aux)): # Removendo os ratios onde não fazem sentido na media e std
      if aux[i][1][0].strip().lower() != 'todos':
        df_media_global[aux[i][0][0].strip()] = np.where(df_media_global[aux[i][1][0].strip().lower()] == aux[i][1][1].strip(), np.nan, df_media_global[aux[i][0][0].strip()])
    df_media_global.replace(0.0, np.nan, inplace=True) #transformando as linhas com 0 em nans para remover abaixo
    df_media_global.dropna(inplace=True)    #removendo as linhas que estão com nan, para que a média global faça mais sentido.
    df_media_global['aux_mean'] = 0
    df_media_global = df_media_global.groupby(['aux_mean'], as_index=False)[ratios].mean() #trazemos a média global de todos os racionais
    df_media_global = df_media_global.drop(columns = 'aux_mean') #retiramos a coluna auxiliar criada
   
    '''
    Criando o DataFrame com a média histórica.
    '''

    df_media = df_parametro.copy() #Caso o usuário coloque poucas semanas, aqui nós salvamos os números da base toda, para fazermos uma média e um std mais coerente.
    df_media[coluna_semanas] = pd.to_datetime(df_media[coluna_semanas], infer_datetime_format = True) #Convertendo datas para datetime
    df_media = df_media.groupby([coluna_semanas] + aberturas, as_index=False)[etapas_vol].sum() #groupby do df media para transformar em um df com datas
    df_media = pd.merge(df_completo, df_media, how = 'left', on = aberturas) #merge entre a base completa e a base com os valores totais sem filtro
    df_media[ratios] = df_media[ratios_split_2].astype(float).values/df_media[ratios_split_1].astype(float).values #Calculando os racionais. Dividindo os kpis para da base total de medias.
    df_media.replace([np.inf, -np.inf], 0.0, inplace=True) #transformando os infinitos em zero

    df_mean = df_media.groupby(aberturas, as_index=False)[ratios].mean() #criando df com as médias por mix sem datas
    df_std = df_media.groupby(aberturas, as_index=False)[ratios].std() #criando df com os stds por mix sem datas
    df_media = pd.merge(df_completo, df_media, how = 'left', on = aberturas) #merge entre a base completa e a base com os valores totais sem filtro
    for i in range (len(aux)): # Removendo os ratios onde não fazem sentido na media e std
      if aux[i][1][0].strip().lower() != 'todos':
        df_mean[aux[i][0][0].strip()] = np.where(df_mean[aux[i][1][0].strip().lower()] == aux[i][1][1].strip(), 0, df_mean[aux[i][0][0].strip()])
        df_std[aux[i][0][0].strip()] = np.where(df_std[aux[i][1][0].strip().lower()] == aux[i][1][1].strip(), 0, df_std[aux[i][0][0].strip()])
    
    df_mean_e_std = pd.merge(df_mean, df_std, how = 'left', on = aberturas, suffixes= ('_mean', '_std')) #merge pra ter no mesmo df a media e o std de cada combinação.
    df_media = pd.merge(df_completo, df_mean_e_std, how = 'left', on = aberturas) #merge entre a base completa e a base com os valores totais sem filtro
    #df_media.replace(0, np.nan, inplace=True) #transformando os zeros em nans - Retiramos porque alguns casos realmente devem ser zero.
    
    for etapa in ratios:
      df_media[etapa+'_mean'] = df_media[etapa+'_mean'].fillna(df_media_global[etapa][0]) #transformando os NaN´s da média na média global
      df_media[etapa+'_std'] = df_media[etapa+'_std'].fillna(0) #transformando os NaN´s do std em zero
    
    for i in range (len(aux)): # Removendo os ratios onde não fazem sentido na media e std
      if aux[i][1][0].strip().lower() != 'todos':
        df_media[aux[i][0][0].strip()+'_mean'] = np.where(df_media[aux[i][1][0].strip().lower()] == aux[i][1][1].strip(), 0, df_media[aux[i][0][0].strip()+'_mean'])
        df_media[aux[i][0][0].strip()+'_std'] = np.where(df_media[aux[i][1][0].strip().lower()] == aux[i][1][1].strip(), 0, df_media[aux[i][0][0].strip()+'_std'])
      

    '''
    Criando o df_ratio com dados filtrados que serão utilizados para os racionais
    '''

    df_parametro[coluna_semanas] = pd.to_datetime(df_parametro[coluna_semanas], infer_datetime_format = True) #Convertendo datas para datetime
    df_parametro = df_parametro[(df_parametro[coluna_semanas] >= data_inicio) & (df_parametro[coluna_semanas] <= data_fim)] #Filtro de data inserido no painel de controle ou fixo no código
    df_ratio = df_parametro.groupby(aberturas, as_index=False)[etapas_vol].sum() #groupby para transformar em um df sem datas
    df_ratio = pd.merge(df_completo, df_ratio, how = 'left', on = aberturas) #merge entre a base completa e a base com os valores 
    df_ratio[ratios] = df_ratio[ratios_split_2].astype(float).values/df_ratio[ratios_split_1].astype(float).values #Calculando os racionais. Dividindo os kpis.
    df_ratio.replace([np.inf, -np.inf], np.nan, inplace=True) #removendo os valores infinitos
    for i in range (len(aux)): # Removendo os ratios onde não fazem sentido. Inserido pelo usuário no painel de controle. Deve seguir o modelo
      if aux[i][1][0].strip().lower() != 'todos':
        df_ratio[aux[i][0][0].strip()] = np.where(df_ratio[aux[i][1][0].strip().lower()] == aux[i][1][1].strip(), 0, df_ratio[aux[i][0][0].strip()])     
    df_ratio = df_ratio.fillna(0) #transformando os NaN´s em 0


    #Merge no df_ratio com o df de médias e std´s
    df_ratio = pd.merge(df_ratio, df_media, how = 'left', on = aberturas)
    df_ratio = df_ratio.drop(columns = etapas_vol) #Remoção de colunas desnecessárias
    
    '''
    Remoção de outliers
    '''
    
    for etapa in ratios:
      df_ratio.loc[ df_ratio[etapa] > ( (df_ratio[etapa+'_mean'] ) + ( (df_ratio[etapa+'_std'] ) * max_std) ), [etapa] ] = ( (df_ratio[etapa+'_mean'] ) + ( (df_ratio[etapa+'_std'] ) * max_std) )
      df_ratio.loc[ df_ratio[etapa] < ( (df_ratio[etapa+'_mean'] ) - ( (df_ratio[etapa+'_std'] ) * min_std) ), [etapa] ] = ( (df_ratio[etapa+'_mean'] ) - ( (df_ratio[etapa+'_std'] ) * min_std) )
      df_ratio.loc[ df_ratio[etapa] <= 0.0, [etapa] ] = df_ratio[etapa+'_mean'] #Removedor de ratios negativos e nulos?
  


    #Remoção de colunas auxiliares desnecessárias
    for etapa in ratios:
      df_ratio = df_ratio.drop(columns = (etapa+'_mean')) #retiramos as colunas desnecessárias de média
      df_ratio = df_ratio.drop(columns = (etapa+'_std')) #retiramos as colunas desnecessárias de desvio padrão
    

    return df_ratio

 
