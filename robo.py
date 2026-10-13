#Dentro da pasta Bases tem o arquivo zipado de todas as bases de dados que eu quero pegar, 
#o código do app.py foi feito para descompactar apenas o txt para teste agora eu quero descompactar tudo e juntar em um só tendo nela as informações de variações de mes a mes e se tiver duplicatas eu quero somar a quantidade de cada uma delas e manter apenas uma linha com a soma da quantidade, e depois filtrar apenas os anos de 2023 a 2026 e que sejam carros elétricos e híbridos, e que estejam nos estados de Goiás e Distrito Federal.
import pandas as pd
import os 
import glob 

# Primeiramente vou pegar os meus arquivos
arquivos_zip = glob.glob("Bases/*.zip")

#Colunas para pegar dentro da base que tem as informações de carros elétricos, na original da renavam
colunas_limpas = ['UF', 'Municipio', 'Marca_Modelo', 'Ano_Fabricacao', 'Quantidade']
lista_geral = []
marcas_regex = r'BYD|GWM|GEELY|CHERY|RENAULT'

print("Iniciando a leitura e filtragem inicial...")

#Dicionario para converter o texto em um mes para facilitar a filtragem
meses_map = {
    'janeiro': '01', 'fevereiro': '02', 'marco': '03', 'abril': '04',
    'maio': '05', 'junho': '06', 'julho': '07', 'agosto': '08',
    'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
}
print(f"Iniciando o robô... Total de arquivos ZIP encontrados: {len(arquivos_zip)}\n")
#Loop PRINCIPAL para descompactar e processar cada arquivo ZIP
for caminho_arquivo in arquivos_zip:

    nome_arquivo = os.path.basename(caminho_arquivo).replace('.zip', '')
    mes_ano_texto = nome_arquivo.split('_ano_')[-1] if '_ano_' in nome_arquivo else 'desconhecido'
    print(f"Lendo base de: {mes_ano_texto}...")
    
    try:
        mes_texto, ano_texto = mes_ano_texto.split('_')
        mes_numero = meses_map.get(mes_texto, '01')
        data_referencia = f"01/{mes_numero}/{ano_texto}"
    except:
        data_referencia = mes_ano_texto

#Loop SECUNDÁRIO para ler em 100 mil linhas 
    for chunk in pd.read_csv(
            caminho_arquivo, 
            sep=";", 
            encoding="utf-8", 
            chunksize=100000, 
            low_memory=False, 
            header=0, 
            names=colunas_limpas,
            compression='zip' 
    ):
        #Filtros
        chunk['UF'] = chunk['UF'].astype(str).str.strip().str.upper()
        chunk_filtrado = chunk[chunk['UF'].isin(['DISTRITO FEDERAL', 'DF', 'GOIAS', 'GOIÁS', 'GO'])].copy()

        #Validação de dados
        if not chunk_filtrado.empty:
            
            # Tratamento da Quantidade
            chunk_filtrado['Quantidade'] = pd.to_numeric(chunk_filtrado['Quantidade'], errors='coerce').fillna(0)
            
            #Filtro de Ano e Quantidade
            chunk_filtrado = chunk_filtrado[
                (chunk_filtrado['Ano_Fabricacao'].astype(str).isin(['2023', '2024', '2025', '2026'])) &    #Pega os anos 23 a 26 e quantidade maior que 0
                (chunk_filtrado['Quantidade'] > 0)
            ]
            
            #Filtro das Marcas
            chunk_filtrado = chunk_filtrado[
                chunk_filtrado['Marca_Modelo'].astype(str).str.contains(marcas_regex, regex=True, na=False)
            ]
            
            if not chunk_filtrado.empty:
                #Carimba a data de referência em todas as linhas filtradas
                chunk_filtrado['Data_Ref'] = data_referencia
                lista_geral.append(chunk_filtrado)

#Mensagem de conclusão e consolidação 
print("\nTodos os arquivos lidos! Consolidando a base histórica...")

if len(lista_geral) > 0:
    df_final = pd.concat(lista_geral, ignore_index=True)
    
    # Quebra de Marca e Modelo
    df_final[['Marca', 'Modelo']] = df_final['Marca_Modelo'].str.split('/', n=1, expand=True)
    df_final = df_final.drop(columns=['Marca_Modelo'])
    
    # Agrupamento de tudo para remover duplicatas e somar a Quantidade
    print("Somando quantidades de registros duplicados...")
    chaves_agrupamento = ['Data_Ref', 'UF', 'Municipio', 'Marca', 'Modelo', 'Ano_Fabricacao']
    
    # O as_index=False garante que as chaves continuem sendo colunas normais na tabela
    df_final = df_final.groupby(chaves_agrupamento, as_index=False)['Quantidade'].sum()
    
    # Exportação final do CSV
    df_final.to_csv("Base_Eletricos_DF_GO_2024_2026.csv", index=False, sep=";", encoding="utf-8")
    print(f"Sucesso! Arquivo gerado com {len(df_final)} registros únicos após a soma.")
    print("Amostra dos dados:")
    print(df_final[['Data_Ref', 'UF', 'Marca', 'Modelo', 'Quantidade']].head())
else:
   print("Nenhum dado correspondente aos filtros foi encontrado.")


#Resumo dos carros elétricos

print("/nGerando os resumos elétricos que ce tem dentro dos meses de 2023 a 2026...")

df_resumo_mensal = df_final.groupby(['Data_Ref', 'Marca', 'Modelo'], as_index=False)['Quantidade'].sum()

df_resumo_mensal.rename(columns={'Quantidade': 'Volume_Elétrico'}, inplace=True)

df_resumo_mensal['Data_Ordenacao'] = pd.to_datetime(df_resumo_mensal['Data_Ref'], format='%d/%m/%Y')
df_resumo_mensal = df_resumo_mensal.sort_values(by=['UF', 'Data_Ordenacao']).drop(columns=['Data_Ordenacao'])


df_resumo_mensal.to_csv("Resumo_Eletricos_2023_2026.csv", index=False, sep=";", encoding="utf-8")
