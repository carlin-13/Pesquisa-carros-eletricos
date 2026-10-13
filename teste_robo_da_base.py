import pandas as pd

#agora visualizar a base de dados renavam 

#print(base_renavam.head())

#print(base_renavam.tail())

#print(base_renavam.info())


caminho_txt = "Base_renavam_jun_2026.TXT"

# Base com as informações referentes á base de share do ciclo otto do período de 24 a 26.
#base_share = pd.read.excel("base_share.xlsx")

#Limpar as colunas

colunas_limpas = ['UF', 'Municipio', 'Marca_Modelo', 'Ano_Fabricacao', 'Quantidade']

lista_de_chunks = []

print("Iniciando a leitura e filtragem inicial...")


#armazena o local para colocar a df 
#base_renavam = pd.read_csv("Base_renavam_jun_2026.TXT", sep=";", encoding="utf-8")

#Como o arquivo é muito grande, vamos ler ele em pedaços (chunks) de 100.000 linhas
for chunk in pd.read_csv(caminho_txt, 
                         sep=";", 
                         encoding="utf-8", 
                         chunksize=100000,
                         low_memory=False, 
                         header=0, 
                         names=colunas_limpas):

    chunk['UF'] = chunk['UF'].astype(str).str.strip().str.upper()

    chunk_filtrado = chunk[chunk['UF'].isin(['DISTRITO FEDERAL', 'GOIAS','GOIÁS'])]

    lista_de_chunks.append(chunk_filtrado)

df_final = pd.concat(lista_de_chunks,ignore_index=True)

print(df_final.info())

#Filtros dos dados de carros fabricados em 2023 a 2026 e que correspondem aos carros elétricos e híbridos

#Tratamento de quantidade

df_final['Quantidade'] = pd.to_numeric(df_final['Quantidade'], errors='coerce').fillna(0)


#Filtro do que eu quero

df_final = df_final[
    (df_final['Ano_Fabricacao'].astype(str).isin(['2023', '2024', '2025', '2026'])) & 
    (df_final['Quantidade'] > 0)
]

marcas_regex = r'BYD|GWM|GEELY|CHERY|RENAULT'

df_final = df_final[df_final['Marca_Modelo'].astype(str).str.contains(marcas_regex, regex=True, na=False)]

#Separar em duas colunas 
df_final[['Marca', 'Modelo']] = df_final['Marca_Modelo'].str.split('/', 1, expand=True)
df_final = df_final.drop(columns=['Marca_Modelo'])

#Contagem dos modelos híbridos e elétricos

print("\n--- Contagem Final dos Modelos Elétricos/Híbridos ---")
print(df_final['Marca'].value_counts())

#agora visualizar a base de dados renavam 

#print(base_renavam.head())

#print(base_renavam.tail())

#print(base_renavam.info())



