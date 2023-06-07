#@title Def formata_output_cohort_coincident

def formata_output_cohort_coincident(output_cohort_unico,
                                     coluna_de_conversoes,
                                     aberturas_das_bases,
                                     coluna_de_semanas):
  
  posicao_week_origin = list(output_cohort_unico.columns).index(coluna_de_conversoes.lower())
  aberturas_group_by = [coluna_de_semanas.lower()]+[x.lower() for x in aberturas_das_bases]+[coluna_de_conversoes.lower()]

  output_cohort_coincident = output_cohort_unico.groupby(aberturas_group_by,as_index=False).sum(list(output_cohort_unico.columns)[posicao_week_origin+1:])

  return output_cohort_coincident
