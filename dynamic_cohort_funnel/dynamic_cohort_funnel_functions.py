# Deslocar colunas de datas pela conversão

# Dado uma tabela de dados contendo os volumes das cohorts e suas respectivas datas,
# podemos facilmente somar o valor coincident correspondente à estas cohorts nas datas corretas criando
# uma coluna de datas auxiliares.

# Como a forma correta de somar o volume coincident oriundo das cohorts é somar o volume da W0, com o volume
# da W1 da semana anterior, o volume da W2 da anterior da anterior e assim por diante, criamos uma coluna
# de datas que é igual às datas das cohorts, mas somada à cada data o número de semanas daquela cohort.

# Assim, quando precisamos obter o volume coincident por semana, basta somar as cohorts agrupando pelas
# semanas "deslocadas" que criamos.

def shift_datas(datas,     # vetor contendo as datas das cohorts em formato datetime                     
                conv,      # vetor contendo as cohorts correspondentes
                intervalo, # interio que define o intervalo da cohort em dias (no caso semanal = 7 dias)
                max_conv): # inteiro que define qual é a cohort máxima (no caso = 5)

  conv = conv.replace(['Coincident'],str(max_conv))
  conv = conv.astype(int)
  temp = conv.apply(lambda x: pd.Timedelta(x*intervalo, unit='D'))
  datas = datas + temp
  datas = [pd.Timestamp(x, freq=None) for x in datas]
  datas = [x.normalize() for x in datas]

  return datas # <-- datas (vetor de datas datetime deslocado através das conversões em relação às datas originais)
#---------------------------------------------------------------------------------------------------





#@title Def progressao_funil

# Multiplica conv x vol, gera vol_coh e soma o volume da nova etapa.

# Essa função literalmente faz a conta de progressão do funil. Com a base única, multiplicamos
# as colunas contendo ToF pelas colunas correspondentes de conversão, obtendo o volume da cohort.
# Somando esse volume obtemos o volume da etapa seguinte.

# Além disso, essa função também já faz o split da etapa em fluxos distintos, caso ele exista

def progressao_funil(base_merged, # DataFrame total gerado pela função auxiliar "def base_geral"
                     etapa_coh,   # string da etapa cohort que está sendo calculada
                     chaves_coh,  # lista com as aberturas cohort gerado pela função auxiliar "def base_geral"
                     chaves_ToF,  # lista com as aberturas ToF gerado pela função auxiliar "def base_geral"
                     max_origin,  # inteiro representando a cohort máxima, gerado pela função auxiliar "def base_geral"
                     nome_coluna_week_origin,
                     coluna_de_semanas): 
  
  # com base na etapa de conversão, criamos o nome da coluna que irá conter o volume cohort da conversão
  etapa_coh_vol = "coh_vol_"+etapa_coh
  # definimos qual é a etapa de volume anterior e posterior da conversão também com base na etapa de conversão
  etapa_vol = etapa_coh.split("2")[0]
  proxima_etapa_vol = etapa_coh.split("2")[1]

  # as chaves usadas para agredar o volume das cohorts no volume coincident.
  chaves = chaves_ToF.copy()
  # o volume coincident deve ser agregado na "diagonal", por isso substituímos a chave da data pela
  # chave da data deslocada "Shifted"
  chaves[0] = 'shifted'
  
  # Calculamos o volume da cohort multiplicando a coluna da conversão cohort pela coluna do volume da
  # etapa anterior
  base_merged[etapa_coh_vol] = base_merged[etapa_coh].astype('float')*\
                               base_merged[etapa_vol].astype('float')

  # definimos a base que vai somar o volume coincident excluíndo a última cohort, pois para recompor
  # a coincident utilizamos no lugar da maior cohort a cohort de ajuste
  agg_vol_novo = base_merged.loc[base_merged[nome_coluna_week_origin] != str(max_origin)]


  # agrupamos e somamos a coluna de vol cohort para obter o volume coincident da próxima etapa
  agg_vol_novo = agg_vol_novo.groupby(chaves, as_index=False)[[etapa_coh_vol]].sum()

  # Mudamos o nome da coluna das datas, pois estas são as datas finais e não consideramos mais que
  # estão deslocadas. Também redefinimos o nome da coluna com o volume cohort para o nome
  # provisório da próxima etapa do funil. Utilizamos um nome provisório ("P_+etapa") para não
  # confundir com o nome da etapa de ToF, caso ela já exista na base, como seria o caso de funis com 
  # dois ToF's, como o caso de demanda com VB e OS
  agg_vol_novo = agg_vol_novo.rename(columns = {'shifted': coluna_de_semanas, etapa_coh_vol: "p_"+proxima_etapa_vol})

  # definimos uma lista com o cabeçalho da base agregada de volume coincident
  cb_agg = list(agg_vol_novo.columns.values)[:-1]

  # unimos a base geral com a base de volume coincident
  base_merged = pd.merge(base_merged,agg_vol_novo,how='left',on=cb_agg)

  # verificamos se a etapa de volume coincident recém calculada já existia na base geral:
  if proxima_etapa_vol in base_merged.columns:
    # caso já existisse, somamos o volume coincident calculado ao ToF já existente
    base_merged[proxima_etapa_vol] = base_merged[proxima_etapa_vol].astype('float').add(base_merged["p_"+proxima_etapa_vol].astype('float'), fill_value=0)
    # removemos a coluna com o volume calculado (pois já foi somado ao ToF)
    base_merged.drop(["p_"+proxima_etapa_vol],axis=1, inplace=True)

  # Caso contrário, mudamos o nome provisório para o nome da etapa definitivo
  else:
    base_merged = base_merged.rename(columns = {"p_"+proxima_etapa_vol: proxima_etapa_vol})

  return base_merged # <-- retorna o mesmo DataFrame total, mas acrescido do volume da cohort e o volume
                     #     coincident da etapa seguinte
#---------------------------------------------------------------------------------------------------


