#@title Def building_blocks

#Importando funções necessárias para rodar "building_blocks":
import * from planning_cohort_funnel_auxiliary_functions
from gerador_baseline_conversoes_v2 import gerador_baseline_conversoes_v2


def building_blocks(inputs_df,
                    baseline_cohort,
                    ToF_semanal,
                    aplicacao_ajuste,
                    base_df_on_top,
                    base_df_impacto_feriados,
                    dict_grupos,
                    nome_coluna_week_origin,
                    coluna_de_semanas):


  # Define a lista de BB's ToF
  lista_bb_tof = list(ToF_semanal['building block tof'].unique())

  # Abrimos os inputs aplicados em todos os BB's ToF
  inputs_df_total = inputs_df.loc[inputs_df['building block tof'] == 'Total']

  inputs_df_aux = pd.DataFrame()
  for tof in lista_bb_tof:
    aux = inputs_df_total.copy()
    aux['building block tof'] = tof
    inputs_df_aux = pd.concat([inputs_df_aux,aux])

  inputs_df = inputs_df.loc[inputs_df['building block tof'] != 'Total']
  inputs_df = pd.concat([inputs_df,inputs_df_aux])

  # Substituimos todas as formas das aparições da string "baseline" nos BB's cohort da base de input
  # por uma única forma, paa facilitar a separação dos BB's cohort de baseline e de projetos:
  inputs_df['building block cohort'] = inputs_df['building block cohort'].str.replace('Baseline','baseline')
  inputs_df['building block cohort'] = inputs_df['building block cohort'].str.replace('BASELINE','baseline')

  # Separar os Inputs que contém somente o BB baseline
  # ------------------------------------------------------------------------------------------------
  baseline_df = inputs_df[inputs_df['building block cohort'].str.contains('baseline')]

  baselines = list(baseline_df['building block cohort'].unique())

  projetos = list(inputs_df['building block cohort'].unique())

  # Define a lista dos projetos de inputs que não são baseline
  projetos = [p for p in projetos if p not in baselines]



  # Para cada BB ToF, calculamos os efeitos dos BB's cohort em comparação com os BB's de baseline:
  #_________________________________________________________________________________________________
  
  # Definindo as bases finais
  output_cohort_final_final = pd.DataFrame()
  output_coincident_final_final = pd.DataFrame()

  # paracada BB ToF
  for tof in lista_bb_tof:

    clear_output(wait=True)
    print('Calculando Funil Baseline do ToF: ',tof)

    #Calcula funil Baseline:
    #-----------------------------------------------------------------------------------------------
    # Separamos o tof específico na base de inputs e na base de tof semanal
    baseline_df_tof = baseline_df.loc[baseline_df['building block tof'] == tof]
    ToF_semanal_tof = ToF_semanal.loc[ToF_semanal['building block tof'] == tof]

    # Removemos as colunas de BB ToF das bases para conseguir rodar o funil
    baseline_df_tof = baseline_df_tof.drop(columns=['building block tof'])
    baseline_df_tof = baseline_df_tof.drop(columns=['building block cohort'])

    ToF_semanal_tof = ToF_semanal_tof.drop(columns=['building block tof'])


    # Geramos o baseline de conversões
    base_cohort,inputs = gerador_baseline_conversoes_v2(baseline_cohort_df = baseline_cohort,
                                                        inputs_df = baseline_df_tof,
                                                        dict_grupos = dict_grupos,
                                                        nome_coluna_week_origin = nome_coluna_week_origin,
                                                        coluna_de_semanas = coluna_de_semanas)

    base_cohort = ajusta_teto_cohort(df_cohort = base_cohort,
                                     nome_coluna_week_origin = nome_coluna_week_origin)

    # Rodamos o funil:
    output_cohort_baseline,output_coincident_baseline,topo_de_funil,topos_de_funil = Funil_Dinamico_DataFrame(df_ToF = ToF_semanal_tof,             
                                                                                            df_cohort = base_cohort,            
                                                                                            df_ratio = base_df_on_top,             
                                                                                            df_impacto_feriados = base_df_impacto_feriados,    
                                                                                            nome_coluna_week_origin = nome_coluna_week_origin,
                                                                                            aplicacao_ajuste = aplicacao_ajuste,
                                                                                            coluna_de_semanas = coluna_de_semanas)
    
    
    output_cohort_baseline[coluna_de_semanas] = pd.to_datetime(output_cohort_baseline[coluna_de_semanas], infer_datetime_format=True)
    output_coincident_baseline[coluna_de_semanas] = pd.to_datetime(output_coincident_baseline[coluna_de_semanas], infer_datetime_format=True)
    
    # Com base no primeiro output, definimos as chaves e as colunas das estapas:
    #-------------------------------------------------------------------------------------------------
    cb_cohort = list(output_cohort_baseline.columns.values)
    etapas_cohort = cb_cohort[cb_cohort.index(nome_coluna_week_origin)+1:]
    chaves_cohort = cb_cohort[:cb_cohort.index(nome_coluna_week_origin)+1]

    cb_coincident = list(output_coincident_baseline.columns.values)
    posi_primeira_etapa = len(chaves_cohort)-1
    etapas_coincident = cb_coincident[posi_primeira_etapa:]
    chaves_coincident = cb_coincident[:posi_primeira_etapa]

    # Definimos os nomes que as etapas vão ter depois de mergeadas entre 2 bases:
    etapas_cohort_x = [x+"_x" for x in etapas_cohort]
    etapas_cohort_y = [y+"_y" for y in etapas_cohort]

    etapas_coincident_x = [x+"_x" for x in etapas_coincident]
    etapas_coincident_y = [y+"_y" for y in etapas_coincident]


    # Vamos definir a base do baseline como modelo da base final adicionando uma coluna com o nome
    # do projeto
    #-------------------------------------------------------------------------------------------------
    output_cohort_final = output_cohort_baseline.copy()
    output_coincident_final = output_coincident_baseline.copy()

    output_cohort_final['building block cohort'] = 'baseline'
    output_coincident_final['building block cohort'] = 'baseline'


    # Calculamos cada projeto individualmente:
    #_______________________________________________________________________________________________
    for projeto in projetos:

      clear_output(wait=True)
      print('Calculando Funil do Building Block')
      print('BB ToF', tof)
      print('BB Cohort', projeto)

      # Seleciona o projeto e o ToF correspondente
      inputs_projeto_df = inputs_df.loc[(inputs_df['building block cohort'] == projeto) & (inputs_df['building block tof'] == tof)]

      # Se o projeto não for aplicado no tof, pulamos o projeto até chegar no tof onde é aplicado:
      if len(inputs_projeto_df) > 0:


        # Adicionando o baseline:
        baseline_df_tof = baseline_df.loc[baseline_df['building block tof'] == tof]
        inputs_projeto_df = pd.concat([inputs_projeto_df,baseline_df_tof])

        # Após selecionar os BB's, remover as colunas dos inputs:
        inputs_projeto_df= inputs_projeto_df.drop(columns=['building block tof'])
        inputs_projeto_df = inputs_projeto_df.drop(columns=['building block cohort'])

        # Geramos o baseline de conversões
        base_cohort,inputs = gerador_baseline_conversoes_v2(baseline_cohort_df = baseline_cohort,
                                                            inputs_df = inputs_projeto_df,
                                                            dict_grupos = dict_grupos,
                                                            nome_coluna_week_origin = nome_coluna_week_origin,
                                                            coluna_de_semanas = coluna_de_semanas)

        base_cohort = ajusta_teto_cohort(df_cohort = base_cohort,
                                        nome_coluna_week_origin = nome_coluna_week_origin)

        # Rodamos o funil:
        output_cohort_projeto,output_coincident_projeto,topo_de_funil,topos_de_funil = Funil_Dinamico_DataFrame(df_ToF = ToF_semanal_tof,             
                                                                                                df_cohort = base_cohort,            
                                                                                                df_ratio = base_df_on_top,             
                                                                                                df_impacto_feriados = base_df_impacto_feriados,    
                                                                                                nome_coluna_week_origin = nome_coluna_week_origin,
                                                                                                aplicacao_ajuste = aplicacao_ajuste,
                                                                                                coluna_de_semanas = coluna_de_semanas)
      
      
        # Subtrair os valores de baseline para ficar somente com oq o projeto agrega:
        #-----------------------------------------------------------------------------------------------

        # Unimos as bases finais dos projetos+baseline com a base final de somente o baseline:
        output_cohort_projeto[coluna_de_semanas] = pd.to_datetime(output_cohort_projeto[coluna_de_semanas], infer_datetime_format=True)
        output_coincident_projeto[coluna_de_semanas] = pd.to_datetime(output_coincident_projeto[coluna_de_semanas], infer_datetime_format=True)
        
        merged_cohort = pd.merge(output_cohort_projeto,output_cohort_baseline,how='left',on=chaves_cohort)
        merged_coincident = pd.merge(output_coincident_projeto,output_coincident_baseline,how='left',on=chaves_coincident)

        # Adicionamos as colunas que contém a diferença dos valores entre projeto e baseline:
        merged_cohort[etapas_cohort] = merged_cohort[etapas_cohort_x].astype(float).values - merged_cohort[etapas_cohort_y].astype(float).values
        merged_coincident[etapas_coincident] = merged_coincident[etapas_coincident_x].astype(float).values - merged_coincident[etapas_coincident_y].astype(float).values

        # Selecionamos apenas as colunas que importam:
        output_cohort_projeto = merged_cohort[chaves_cohort+etapas_cohort]
        output_coincident_projeto = merged_coincident[chaves_coincident+etapas_coincident]

        output_cohort_projeto['building block cohort'] = projeto
        output_coincident_projeto['building block cohort'] = projeto

      
      else:
        output_cohort_projeto = pd.DataFrame()
        output_coincident_projeto = pd.DataFrame()
        base_diaria_projeto = pd.DataFrame()


      # Para cada BB de projeto, adicionamos o funil calculado ao BB do projeto anterior
      output_cohort_final = pd.concat([output_cohort_final,output_cohort_projeto])
      output_coincident_final = pd.concat([output_coincident_final,output_coincident_projeto])

      #---------------------------------------------------------------------------------------------

    # Para cada BB de ToF, adicionamos o nome do BB ToF e adicionamos ao funil anterior
    output_cohort_final['building block tof'] = tof
    output_coincident_final['building block tof'] = tof

    output_cohort_final_final = pd.concat([output_cohort_final_final,output_cohort_final])
    output_coincident_final_final = pd.concat([output_coincident_final_final,output_coincident_final])

  #_________________________________________________________________________________________________

  # Remover linhas completamente zeradas:
  output_cohort_final_final = redutor_de_base(df = output_cohort_final_final,
                                              col_valores = etapas_cohort)

  output_coincident_final_final = redutor_de_base(df = output_coincident_final_final,
                                              col_valores = etapas_coincident)
  
  # Reorganizando a ordem das colunas:
  output_cohort_final_final = output_cohort_final_final[[chaves_cohort[0]]+['building block cohort','building block tof']+chaves_cohort[1:]+etapas_cohort]
  output_coincident_final_final = output_coincident_final_final[[chaves_coincident[0]]+['building block cohort','building block tof']+chaves_coincident[1:]+etapas_coincident]

  return output_cohort_final_final,output_coincident_final_final,etapas_coincident,etapas_cohort


