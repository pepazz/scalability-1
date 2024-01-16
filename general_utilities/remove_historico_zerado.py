#@title Def remove_historico_zerado

'''
Através de uma soma cumulativa das datas mais antigas para a mais recente,
remove os dados zerados
'''


def remove_historico_zerado(train_data,endogenous,col_data,abertura):

  # Checar se existe histórico
  if len(train_data[col_data].values) > 0:

    # Romove histórico zerado de trás para frente
    train_data = train_data.sort_values(by=col_data)
    train_data[endogenous] = train_data[endogenous].astype(float)

    if sum(train_data[endogenous].values) != 0:
      cumsum = train_data.copy()
      train_data['cumsum'] = cumsum[endogenous].values.cumsum()
      train_data = train_data.loc[train_data['cumsum'] != 0]
      train_data = train_data.drop('cumsum',axis=1)

  return train_data
