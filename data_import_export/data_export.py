
#@title Def exportar_base

# Importando funções auxiliares:
from colored import colored
from data_import import *
import pandas as pd
import time
import numpy as np

def exportar_base(base_df,                     # DataFrame
                  nome_do_painel_de_controle,  # String com o nome do arquivo sheets com o painel de controle
                  arquivo_de_destino,          # String com o nome do arquivo sheets de destino ou o caminho do Google Drive
                  nome_da_aba,                 # String com o nome da aba no arquivo sheets de destino ou nome final do CSV que será salvo
                  substituir,                  # Booleano indicando se o arquivo CSV será salvo por cima de um existente com mesmo nome ou se será salva uma cópia com nome diferente
                  client = 'client'):               
  
  # Iniciamos uma flag indicando se conseguimos exportar a base
  base_exportada = True


  # Definir a lista de destinos:
  #-------------------------------------------------------------------------------------------------
  if "," in arquivo_de_destino:
    lista_arquivos_destino = arquivo_de_destino.split(",")
    lista_arquivos_destino = [l.strip() for l in lista_arquivos_destino]
  else:
    lista_arquivos_destino = [arquivo_de_destino]

  if "," in nome_da_aba:
    lista_nome_das_abas = nome_da_aba.split(",")
    lista_nome_das_abas = [l.strip() for l in lista_nome_das_abas]
  else:
    lista_nome_das_abas = [nome_da_aba]

  if len(lista_nome_das_abas) != len(lista_arquivos_destino):
    try:
      nome_base = base_df.name
    except:
      nome_base = 'base'
    print('\n\nNão foi possível exportar a base '+colored(nome_base,'yellow')+' para a aba '+colored(nome_da_aba,'blue')+' do arquivo '+colored(nome_do_arquivo,'blue')+'\nParece que existe mais de um arquivo/aba de destino, mas a quantidade de arquivos e abas de destino informados são distintos.'+'\n\nSerá feita uma tentativa de baixar os dados no formato CSV.')
    base_exportada = False

  if base_exportada:
    for i in range(len(lista_nome_das_abas)):
      arquivo_de_destino = lista_arquivos_destino[i]
      nome_da_aba = lista_nome_das_abas[i]
      

      
      # Definimos o nome da base a ser exportada
      #-------------------------------------------------------------------------------------------------
      # Caso o arquivo de destino seja um caminho para o google drive, definimos o nome do arquivo com ba no nome da aba
      if '/' in arquivo_de_destino:
        if nome_da_aba == '':
          nome_base = 'base'
        else:
          nome_base = nome_da_aba
      # Caso contrário, o nome da base vai ser aquele registrado no DataFrame
      else:
        try:
          nome_base = base_df.name
        except:
          if nome_da_aba == '':
            nome_base = 'base'
          else:
            nome_base = nome_da_aba
      #-------------------------------------------------------------------------------------------------

      # Caso o arquivo CSV no drive não possa substituir um já existente, salvamos o aqruivo atual
      # adicionando a data e hora local no nome
      if not substituir:
        nome_base = nome_base+'_'+str(time.asctime(time.localtime())).replace(' ','_')

      # Caso o arquivo de destine seja o "Atual", mudamos o nome do arquivo para no nome do sheets do painel de controle
      if arquivo_de_destino == 'Atual' or arquivo_de_destino == 'atual':
        arquivo_de_destino = nome_do_painel_de_controle

      # Removemos do nome do arquivo possíveis caracteres que impossibilitem seu salvamento. 
      nome_base = nome_base.replace(' ','_')
      nome_base = nome_base.replace('/','_')
      nome_base = nome_base.replace('.csv','')


      # Vamos garantir que na base exportada não existem infinitos ou nans:
      base_df.replace([np.inf, -np.inf], 0, inplace=True)
      base_df = base_df.fillna(0)


      # Caso exista "/" no nome do arquivo, vamos considerar que se trata de um caminho para
      # uma pasta do google drive onde vamos salvar um arquivo CSV.
      if '/' in arquivo_de_destino and 'https://' not in arquivo_de_destino:

        print('\n\nExportando a base '+colored(nome_base,'yellow')+' na forma de CSV para '+colored(arquivo_de_destino,'blue'))

        path = path = '/content/drive/'+arquivo_de_destino+'/'

        try:
          with open(path+nome_base+'.csv', 'w', encoding = 'utf-8-sig') as f:
            base_df.to_csv(f, index=False)
        except Exception as e:
          base_exportada = False
          print('\n\nNão foi possível exportar a base '+colored(nome_base,'yellow')+' como CSV para a seguinte pasta do Google Drive:\n'+colored(arquivo_de_destino,'red')+'\nA tentativa de exportar o arquivo resultou no seguinte erro:\n'+colored(str(e),'red')+'\n\nSerá feita uma tentativa de baixar os dados no formato CSV.')



      # Caso contrário, vamos tentar salvar a base numa aba de um sheets:
      else:

        print('\n\nExportando a base '+colored(nome_base,'yellow')+' na forma tabela para a aba '+colored(nome_da_aba,'blue')+' do arquivo sheets '+colored(arquivo_de_destino,'blue'))

        dados_sheets,base,mensagem,flag_abriu,nome_do_arquivo = abertura_do_arquivo(nome_do_arquivo = arquivo_de_destino, # string com o nome do arquivo sheets a ser aberto
                                                                                    sheets_aberto = False,    # Booleano indicando se o sheets já foi aberto
                                                                                    sheets = [],           # Arquivo sheets já aberto
                                                                                    nome_da_aba = nome_da_aba, # string com o nome da aba a ser aberta
                                                                                    client = client)     


        # Caso o sheets e a aba existam, vamos tentar salvar a base:
        if flag_abriu:

          try:
            output = dados_sheets.worksheet(nome_da_aba)
            output.clear()
            set_with_dataframe(output,base_df)
          except:

            try:

              from google.colab import auth
              auth.authenticate_user()

              import gspread
              from google.auth import default
              creds, _ = default()

              gc = gspread.authorize(creds)

              output = dados_sheets.worksheet(nome_da_aba)
              output.clear()
              set_with_dataframe(output,base_df)

            except Exception as e:
              print('\n\nNão foi possível exportar a base '+colored(nome_base,'yellow')+' para a aba '+colored(nome_da_aba,'blue')+' do arquivo '+colored(nome_do_arquivo,'blue')+'\nA tentativa de exportar o arquivo resultou no seguinte erro:\n'+colored(str(e),'red')+'\n\nSerá feita uma tentativa de baixar os dados no formato CSV.')
              base_exportada = False
        
        else:
          print(mensagem+'\n\nNão foi possível exportar a base '+colored(nome_base,'yellow')+' para a aba '+colored(nome_da_aba,'blue')+' do arquivo '+colored(nome_do_arquivo,'blue')+'\n\nSerá feita uma tentativa de baixar os dados no formato CSV.')
          base_exportada = False



  # Caso a tentativa de exportar a base tenha falhado, vamos tentar baixar o CSV
  if not base_exportada:
    try:
      '''
      Código antigo p/ Colab:
      base_df.to_csv(nome_base+'.csv', index=False)
      files.download(nome_base+'.csv')  
      '''
      print("Baixe manualmente a base ",colored(nome_base,'yellow')," mostrada abaixo:\n")
      #display(base_df)
      base_exportada = True 
    except Exception as e:
      base_exportada = False
      print('\n\nNão foi possível baixar a base '+colored(nome_base,'yellow')+'\nA tentativa de baixar o arquivo resultou no seguinte erro:\n'+colored(str(e),'red'))


  # Imprimimos uma mensam final
  if base_exportada:
    print('\n\n'+colored('Base '+nome_base+' Exportada','green')+'\n\n_______________________________________________________________________')
  else:
    print('\n\n'+colored('Base '+nome_base+' Não foi exportada','red')+'\n\n_______________________________________________________________________')
