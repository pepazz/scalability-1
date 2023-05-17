#@title Def redutor_de_base

# Função auxiliar para remover linhas zeradas das bases finais

def redutor_de_base(df,col_valores):
  '''
  Esta função tem como intuito eliminar as linhas zeradas da base de output diario.
  Criamos uma coluna auxiliar que contém a soma de todas as etapas e damos um 
  'filter out' nas linhas cuja coluna auxiliar está zerada
  '''

  df['aux'] = df[col_valores].sum(axis=1)
  df = df[df['aux'] != 0]
  
  df = df.drop(columns=['aux'])
  
  return df
#-----
