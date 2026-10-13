import pandas as pd 

print("/nLendo a base processada")

df_final = pd.read_csv("Base_Eletricos_DF_GO_2024_2026.csv", sep=";", encoding="utf-8")

print("\nGerando os resumos elétricos dentro dos meses de 2024 a 2026...")

#2. Agrupa por Data e Estado
#O .reset_index() no final é a peça-chave que corrige o KeyError: 'UF'
df_resumo_mensal = df_final.groupby(['Data_Ref', 'UF'])['Quantidade'].sum().reset_index()

#3. Renomeia a coluna de quantidade para facilitar o cruzamento com o ciclo Otto
df_resumo_mensal = df_resumo_mensal.rename(columns={'Quantidade': 'Volume_Eletricos'})

#4. Ordenação Cronológica
# Transforma a data em formato datetime temporariamente para o Python saber que Jan/24 vem antes de Fev/24
df_resumo_mensal['Data_Ordenacao'] = pd.to_datetime(df_resumo_mensal['Data_Ref'], format='%d/%m/%Y')

#Agora o sort_values vai funcionar perfeitamente
df_resumo_mensal = df_resumo_mensal.sort_values(by=['UF', 'Data_Ordenacao']).drop(columns=['Data_Ordenacao'])

#transforma o volume de elétricos em inteiro 
df_resumo_mensal['Volume_Eletricos'] = df_resumo_mensal['Volume_Eletricos'].astype(int)

#5. Salva o arquivo final super leve para o Dashboard
df_resumo_mensal.to_csv("Resumo_Mensal_Eletricos_DF_GO.csv", index=False, sep=";", encoding="utf-8")

print("Sucesso! Resumo mensal gerado e salvo.")
print("\nAmostra do formato final:")
print(df_resumo_mensal.head(10))