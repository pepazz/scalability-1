from teste_soma import teste_soma
from colored import colored

def teste_nested(a,b):
  print(colored("from teste_soma import teste_soma",'g'))
  return teste_soma(a,b)+10
