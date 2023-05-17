#@title Def gerador_baseline_conversoes



def gerador_baseline_conversoes_v2(baseline_cohort_df, inputs_df, dict_grupos, nome_coluna_week_origin,coluna_de_semanas):
  '''
  Esta função aplica os inputs no dataframe de baselines.
  Inicialmente ela faz uma cópia do dataframe de inputs e altera suas células que tem
  'Total', inserindo uma lista com todos os itens únicos da mesma coluna correspondente
  na base de baseline.
  Após isso são mapeados os Grupos e é feita uma substituição correpondente através do
  'dict_grupos'.
  Essas duas substituições ocorrem somente para as categorias mutáveis da aba de inputs.

  O passo seguinte é replicar 5 vezes as linhas cujas aplicações são 'Cohort aberta'
  ou 'Coincident'. Após replicá-las fazemos as substituição por cada uma das week origins
  (0,1,2,3,4,5) e no caso da Coincident (0,1,2,3,4,Coincident). Além disso as datas na Coincident
  são shiftadas em relação ao índice da week origin. Na w0 a data é ela própria, na w1 é
  uma semana antes, w2 2 semanas antes e assim sucessivamente.

  Depois disso é feito um Loop que percorre todas as linhas e gera um novo dataframe 
  pra cada linha de inputs. Estes dataframes vão sendo empilhados no 'inputs_combinados'
  É importante notar que neste momento os formatos dos elementos de cada linha são passados 
  para lista, garantindo a funcionalidade do 'pd.MultiIndex.from_product'

  '''

  # Definições iniciais:
  #-------------------------------------------------------------------------------------------------
  posi_pre_dados = list(inputs_df.columns).index("etapa")
  
  categorias = list(inputs_df.columns)[:1+posi_pre_dados]
  categorias_mutaveis = list(set(categorias)-set(['conversão','aplicação','etapa']))
  datas = list(inputs_df.columns)[1+posi_pre_dados:]

  baseline_cohort_df_c = baseline_cohort_df.copy()

  # Notar adição de datas anteriores às do planning para os casos de inputs Coincident
  # nas primeiras semanas do planning
  datas_adicionais = pd.date_range(pd.to_datetime(datas[0])-pd.to_timedelta(5,unit="W"),pd.to_datetime(datas[0])-pd.to_timedelta(1,unit="W"), freq="7D")
  datas_adicionais = [pd.Timestamp(x, freq=None) for x in datas_adicionais]
  datas_adicionais = [x.normalize() for x in datas_adicionais]

  etapas = list(filter(lambda x: '2' in x, baseline_cohort_df_c.columns))
  #-------------------------------------------------------------------------------------------------


  # Caso a base de inputs esteja vazia, vamos criar uma base de conversões que nada mais é do que a repetição
  # do baseline para cada data do planning:
  if len(inputs_df) == 0:

    datas.sort()
    baseline_cohort_df_c[coluna_de_semanas] = datas[0]
    aux = baseline_cohort_df_c.copy()
    for data in datas[1:]:
      aux[coluna_de_semanas] = data
      baseline_cohort_df_c = pd.concat([baseline_cohort_df_c,aux])

    # Colocando a 'Data' como primeira coluna para não dar erro na função de ajuste_teto_cohort
    cols = list(baseline_cohort_df_c.columns)
    cols = [cols[-1]] + cols[:-1]
    baseline_cohort_df_c = baseline_cohort_df_c[cols]

    inputs_combinados_output = []


  # Caso existam inputs:
  #_________________________________________________________________________________________________
  else:

    inputs_df['etapa'] = inputs_df['etapa'].str.lower()
    inputs = inputs_df.copy()
    # Melt nas datas para elas passarem de colunas para linhas
    inputs = inputs.melt(id_vars=categorias, value_vars=datas, var_name='data')
    #inputs = inputs.rename(columns={'variable':'data'})
    inputs['value']=pd.to_numeric(inputs['value'], errors='coerce')
    inputs = inputs.dropna(axis=0)


    for categoria in categorias_mutaveis:
      inputs.loc[inputs[categoria].str.contains('Grupo'), [categoria]] = inputs[categoria].map(dict_grupos)

      inputs_totais = inputs[inputs[categoria] == 'Total'] ###
      inputs_totais[categoria] = inputs_totais.apply(lambda row: list(baseline_cohort_df_c[categoria].unique()) , axis=1) ###
      inputs = inputs[inputs[categoria] != 'Total'] ###
      inputs = inputs.append(inputs_totais) ###

    #-----------------------------------------------------------------------------
    # Replicação das linhas de cohort aberta
    inputs_c_aberta = inputs[inputs['conversão'] == 'Cohort Aberta']
    inputs_c_aberta['conversão'] = 0

    inputs = inputs[inputs['conversão'] != 'Cohort Aberta']

    for i in range (1,6):
      copy_c_aberta = inputs_c_aberta[inputs_c_aberta['conversão'] == 0]
      copy_c_aberta['conversão'] = i
      inputs_c_aberta = inputs_c_aberta.append(copy_c_aberta)
    
    inputs = inputs.append(inputs_c_aberta)
    #-----------------------------------------------------------------------------
    inputs_coincident = inputs[inputs['conversão'] == 'Coincident']
    inputs_coincident['conversão'] = 0

    inputs = inputs[~(inputs['conversão'] == 'Coincident')]

    for i in range (1,6):
      copy_coincident = inputs_coincident[inputs_coincident['conversão'] == 0]
      copy_coincident['conversão'] = i
      inputs_coincident = inputs_coincident.append(copy_coincident)

    
    inputs_coincident[coluna_de_semanas] = pd.to_datetime(inputs_coincident[coluna_de_semanas])-(pd.to_timedelta(inputs_coincident['conversão'],unit="W"))
    #inputs_coincident['data'] = inputs_coincident['data'].dt.strftime('%m/%d/%Y')
    inputs_coincident.loc[inputs_coincident['conversão'] == 5, ['conversão']] = 'Coincident'

    inputs = inputs.append(inputs_coincident)
    
    datas = datas + datas_adicionais
    datas.sort()

    inputs[coluna_de_semanas] = inputs.apply(lambda row: datas[datas.index(row.data):] if row.aplicação == 'Permanente' else row.data, axis=1)

    #-----------------------------------------------------------------------------
    # Notar empilhamento de dataframes e ajuste de formato dos elementos das células
    # Notar também mudança no type da coluna de conversão. Mudança importante para 
    # o 'match' correto posteriormente no código
    inputs['conversão'] = inputs['conversão'].astype('str') ###
    
    aux_categorias_mutaveis = categorias_mutaveis + ['data']
    for coluna in list(set(inputs.columns)-set(aux_categorias_mutaveis)):
      inputs[coluna] = inputs[coluna].apply(lambda x: [x])

    for coluna in aux_categorias_mutaveis:
      inputs[coluna] = inputs[coluna].apply(lambda x: [x] if type(x) != list else x )
    
    inputs_combinados = pd.DataFrame([], columns=list(inputs.columns))  
    for linha in inputs.iterrows():
      idx = pd.MultiIndex.from_product(linha[1],names=inputs.columns.values)
      df_aux = pd.DataFrame(index=idx).reset_index()
      inputs_combinados = inputs_combinados.append(df_aux)
      
    '''
    inputs_combinados = pd.DataFrame([], columns=list(inputs.columns))
    for linha in inputs.iterrows():
      for i in range(len(linha[1])):
        if (type(linha[1][i]) is not list):
          linha[1][i] = [linha[1][i]]


      idx = pd.MultiIndex.from_product(linha[1],names=inputs.columns.values)
      df_aux = pd.DataFrame(index=idx).reset_index()
      inputs_combinados = inputs_combinados.append(df_aux)
    '''
    #-----------------------------------------------------------------------------
    # Soma-se 1 em todos os inputs e depois realiza-se um groupby multiplicando os valores
    # desta forma os inputs são combinados em uma única linha
    inputs_combinados['value'] = inputs_combinados['value'] + 1
    inputs_combinados = inputs_combinados.drop(columns=['aplicação'])
    inputs_combinados = inputs_combinados.groupby(list(inputs_combinados.columns[:-1]),as_index=False)[(inputs_combinados.columns[-1])].prod()

    lista_index_pivot = list(inputs_combinados.columns)
    lista_index_pivot.remove('etapa')
    lista_index_pivot.remove('value')

    # Pivotamento para a base de inputs combinados ficar no mesmo formato do baseline
    inputs_combinados = inputs_combinados.pivot(index=lista_index_pivot,columns='etapa',values='value').reset_index()

    inputs_combinados = inputs_combinados.rename(columns={'conversão':nome_coluna_week_origin})
    inputs_combinados = inputs_combinados.fillna(1)

    # Criação de cópia para o Output da função
    inputs_combinados_output = inputs_combinados.copy()

    #-----------------------------------------------------------------------------
    

    for etapa in etapas:
      inputs_combinados = inputs_combinados.rename(columns={etapa:f'{etapa}_inputs'})

    baseline_cohort_df_c[nome_coluna_week_origin] = baseline_cohort_df_c[nome_coluna_week_origin].astype(str)
    inputs_combinados[nome_coluna_week_origin] = inputs_combinados[nome_coluna_week_origin].astype(str)

    # Aqui adicionamos as datas à base de baseline
    baseline_cohort_df_c[coluna_de_semanas] = datas[0]
    for data in range(len(datas[1:])):
      b_aux = baseline_cohort_df_c[baseline_cohort_df_c[coluna_de_semanas]==datas[0]]
      b_aux[coluna_de_semanas] = datas[data+1]
      baseline_cohort_df_c = baseline_cohort_df_c.append(b_aux)
    
    # Nesta etapa juntamos a base de baseline com os inputs combinados
    lista_index_pivot.remove('conversão')
    lista_index_pivot.append(nome_coluna_week_origin)
    baseline_cohort_df_c = pd.merge(baseline_cohort_df_c, inputs_combinados, how='left', on=lista_index_pivot)
    baseline_cohort_df_c = baseline_cohort_df_c.fillna(1)

    for etapa in etapas:
      baseline_cohort_df_c[etapa] = baseline_cohort_df_c[etapa].astype('float')
      try:
        baseline_cohort_df_c[etapa] = baseline_cohort_df_c[etapa]*baseline_cohort_df_c[f'{etapa}_inputs']
      except:
        pass

    # Remoção das colunas auxiliares
    baseline_cohort_df_c = baseline_cohort_df_c.loc[:, ~baseline_cohort_df_c.columns.str.endswith('_inputs')]
    # Dando Filter out nas datas anteriores ao planning
    baseline_cohort_df_c = baseline_cohort_df_c[~baseline_cohort_df_c[coluna_de_semanas].isin(datas_adicionais)]

    # Colocando a 'Data' como primeira coluna para não dar erro na função de ajuste_teto_cohort
    cols = list(baseline_cohort_df_c.columns)
    cols = [cols[-1]] + cols[:-1]
    baseline_cohort_df_c = baseline_cohort_df_c[cols]
  
  return baseline_cohort_df_c,inputs_combinados_output
