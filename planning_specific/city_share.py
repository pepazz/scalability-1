#@title Def City Share

def city_share(df_parametro, #df que será a base de cálculo
               coluna_semanas, #week_start
               etapas_vol, #nome das etapas que serão buscadas. Ex: vb/visits_booked, etc
               city_group, #lista das aberturas que serão consideradas
               city_name,
               uf): #nome da coluna que tem o nome da cidade

    '''
    Tratamento inicial
    '''
    etapas = etapas_vol
    etapas_share = [e+"_share" for e in etapas]
    etapas_share_group = [e+"_y" for e in etapas]
    etapas_share_city = [e+"_x" for e in etapas]    


    df_parametro[coluna_semanas] = pd.to_datetime(df_parametro[coluna_semanas], infer_datetime_format = True) #Convertendo datas para datetime



    '''
    Separações para fazer os cálculos
    '''

    df_total = df_parametro.groupby([uf]+[city_group], as_index=False)[etapas_vol].sum() #df com os valores por city_group
    df_cities = df_parametro.groupby([uf] + [city_group] + [city_name], as_index=False)[etapas_vol].sum() #df com os valores por city_name
    df_city_share = pd.merge(df_cities, df_total, how = 'left', on =[uf] + [city_group]) #merge para no mesmo df existir o total da cidade e total do grupo
    df_city_share[etapas] = df_city_share[etapas_share_city].astype(float).values/df_city_share[etapas_share_group].astype(float).values #divisão do total da cidade pelo grupo
    df_city_share = df_city_share.drop(columns = (etapas_share_group + etapas_share_city))
    df_city_share = df_city_share.fillna(0) #transformando os nans em zero


#incluir a UF pela query
    return df_city_share
