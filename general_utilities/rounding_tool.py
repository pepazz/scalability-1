import pandas as pd

def rounding_tool(df,          # DataFrame a ser arredondado
                  aberturas,   # aberturas da base, incluíndo colunas de datas (todas colunas q não são de valores)
                  col_valores, # sempre lista, mesmo se for só 1. Colunas com os valores a serem arredondados
                  ordem_hirarquica): # ordem de aberturas com a priorização de manter os valores, em ordem crescente de prioridade

  # Garantimos que as colunas de valores são numéricas
  df[col_valores] = df[col_valores].astype(float)

  # Criamos uma cópia do df original
  df_rounded = df.copy()

  # Arredondamos todos os valores
  df_rounded[col_valores] = df_rounded[col_valores].round()

  # Coluna auxiliar
  df_rounded['aux'] = 1

  # Definimos os nomes das colunas de valores auxiliares
  col_delta = [x+'_delta' for x in col_valores]
  col_round = [x+'_round' for x in col_valores]
  col_round_grouped = [x+'_round_grouped' for x in col_valores]
  col_x = [x+'_x' for x in col_valores]
  col_y = [x+'_y' for x in col_valores]
  col_abs = [x+'_abs' for x in col_valores]

  # Na base arredondada, mudamos os nomes das colunas de valores para não conflitar com os nomes originais
  df_rounded = df_rounded.rename(columns=dict(zip(col_valores, col_round)))

  # Unimos a base original e a base arredondada
  df_rounded = pd.merge(df_rounded,df,how='left',on=aberturas)

  '''
  __________________________________________________________________________________________________
  Para cada abertura na lista de hierarquia, vamos remover a abertura e todas as selecionadas anteriormente
  da lista de aberturas e agrupar a base pelas aberturas que sobraram.

  Com a base agrupada, calculamos as diferenças entre os valores arredondados e originais e distribuímos a
  diferença entre as linhas da abertura que foi removida.
  '''
  chaves_excluidas = []
  for abertura in ordem_hirarquica:

    # Caso não seja a última abertura (para não zerar o agrupamento)
    if abertura != ordem_hirarquica[-1]:

      chaves_excluidas = chaves_excluidas+[abertura]
      chaves = list(set(aberturas)-set(chaves_excluidas))

      # Criamos uma base agrupada e salvamos os valores agrupados com outros nomes
      df_rounded_grouped = df_rounded.groupby(chaves,as_index=False)[col_round+col_valores].sum()
      df_rounded_grouped = df_rounded_grouped.rename(columns=dict(zip(col_round,col_round_grouped)))

      # Calculamos os deltas entre valores originais e valore arredondados no agrupamento
      df_rounded_grouped[col_delta] = df_rounded_grouped[col_valores].values - df_rounded_grouped[col_round_grouped].values
      df_rounded_grouped = df_rounded_grouped[chaves+col_delta+col_round_grouped]

      # Calculamos o maior inteiro possível dos deltas, pois só podemos redistribuir números inteiros
      # para não remover o arredondamento. A diferença que sobrar vai ser acrescentada nos deltas
      # do próximo agrupamento.
      df_rounded_grouped[col_delta] = df_rounded_grouped[col_delta].astype(int)

      # Unimos com a base que contém as aberturas completas. Assim, os deltas do agrupamento
      # serão repetidos em todas as linhas da abertura agrupada.
      df_rounded = pd.merge(df_rounded,df_rounded_grouped,how='left',on=chaves)

      '''
      print("************************************************")
      print(chaves)
      print(df_rounded)
      '''

      # Para cada coluna de valor, vamos prosseguir com a distribuição dos deltas
      for val in col_valores:
        #-------------------------------------------------------------------------------------------

        # Vamos garantir que nenhuma abertura fique completamente zerada
        df_rounded.loc[(df_rounded[val+'_round_grouped'] == 0) & (df_rounded[val+'_delta'] == 0) & (df_rounded[val] > 0),val+'_delta'] = 1

        # Ordemaos a base pelas aberturas e pelo valor que iremos arredondar, de forma a facilitar
        # uma distribuição proporcional dos deltas
        print("----------------------------------------------------")
        print(df_rounded.columns.values)
        df_rounded = df_rounded.sort_values(by=aberturas+[val], ascending=False)
        print(df_rounded.columns.values)
        # Criamos colunas auxilires para alocar os deltas corretamente
        df_rounded_count = df_rounded.groupby(chaves,as_index=False)['aux'].sum()
        df_rounded_count = df_rounded_count.rename(columns={'aux':'count'})
        df_rounded_count = df_rounded_count[chaves+['count']]

        # A coluna 'order' guarda a ordem dos valores originais dentro da abertura agrupada
        df_rounded['order'] = df_rounded.groupby(chaves)['aux'].cumsum()
        df_rounded = pd.merge(df_rounded,df_rounded_count,how='left',on=chaves)

        # Salvamos também a ordem invertida, para distribuir deltas negativos nos menores valores.
        # Como os menores valores podem ser zerados, precisamos garantir a ordem somente onde existem
        # valores arredondados para serem subtruídos deltas negativos.
        df_rounded['invert_order'] = df_rounded['order'].values - df_rounded['count']
        df_rounded.loc[df_rounded[val+'_round'] <= 0,'invert_order'] = 0

        # Colunas auxiliares para aplicar deltas negativos
        df_rounded_min = df_rounded.groupby(chaves,as_index=False)['invert_order'].min()
        df_rounded_min = df_rounded_min.rename(columns={'invert_order':'invert_order_min'})
        df_rounded = pd.merge(df_rounded,df_rounded_min,how='left',on=chaves)

        df_rounded[val+'_delta_abs'] = df_rounded[val+'_delta'].abs()

        df_rounded['invert_order_2'] = df_rounded['invert_order'].values - df_rounded['invert_order_min'].values
        df_rounded['invert_order_3'] = df_rounded['invert_order_2'].values - df_rounded[val+'_delta_abs'].values

        # Aqui definimos onde os deltas negativos serão aplicados
        df_rounded['delta_order_invert']=0
        df_rounded.loc[(df_rounded['invert_order_2'] > 0) & (df_rounded['invert_order_3'] <= 0), 'delta_order_invert'] = -1

        # Aqui definimos onde os deltas positivos serão aplicados
        df_rounded['delta_order'] = df_rounded[val+'_delta'].values - df_rounded['order'].values

        df_rounded.loc[df_rounded['delta_order'] >= 0,'delta_order'] = 1
        df_rounded.loc[df_rounded['delta_order'] < 0,'delta_order'] = 0

        # Aplicamos os deltas nos valores arredondados
        df_rounded.loc[df_rounded[val+'_delta'] > 0, val+'_round'] = df_rounded.loc[df_rounded[val+'_delta'] > 0][val+'_round'].values + df_rounded.loc[df_rounded[val+'_delta'] > 0]['delta_order'].values
        df_rounded.loc[df_rounded[val+'_delta'] < 0, val+'_round'] = df_rounded.loc[df_rounded[val+'_delta'] < 0][val+'_round'].values + df_rounded.loc[df_rounded[val+'_delta'] < 0]['delta_order_invert'].values
        '''
        print("---------------------------------------------")
        print(df_rounded)
        '''
        # Removemos todas as colunas auxiliares, pois elas são redefinidas a cada coluna nova de valor
        df_rounded = df_rounded[aberturas+col_valores+col_round+col_round_grouped+col_delta+['aux']]

        # Transformamos o valor arredondado em inteiro (só pra ficar mais bonito e claro que o número foi arredondado)
        df_rounded[val+'_round'] = df_rounded[val+'_round'].astype(int)

        #-------------------------------------------------------------------------------------------


      df_rounded = df_rounded[aberturas+col_valores+col_round+['aux']]

  # Retornamos a base arredondada com os nomes corretos das colunas
  df_rounded = df_rounded[aberturas+col_round]
  df_rounded = df_rounded.rename(columns=dict(zip(col_round, col_valores)))
  return df_rounded[aberturas+col_valores]
