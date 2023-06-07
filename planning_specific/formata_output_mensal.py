

def formata_output_mensal(output_diario,
                          aberturas_das_bases,
                          etapas_volume):
  
  output_mensal = output_diario.copy()

  output_mensal['month_start'] = output_mensal['data'].apply(lambda dt: dt.replace(day=1))


  output_mensal = output_mensal.groupby(['month_start','building block cohort','building block tof']+[x.lower() for x in aberturas_das_bases],as_index=False).sum(etapas_volume)
  
  # Comando necessário para garantir que colunas como mês e ano, por exemplo, sejam
  # consideradas como numéricas pelo python e, apesar de não estarem dentro do sum()
  # do groupby, saírem no dataframe de output
  output_mensal = output_mensal[['month_start','building block cohort','building block tof']+[x.lower() for x in aberturas_das_bases]+etapas_volume]

  return output_mensal
