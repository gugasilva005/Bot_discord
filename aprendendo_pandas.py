import pandas
import pandas as pd

lista_alunos = pd.read_excel('alunos.xlsx')
lista_professores = pd.read_excel('professores.xlsx')

email = str(input())

print(email in lista_alunos['E-mail academico'].values or email in lista_professores['E-mail'].values)