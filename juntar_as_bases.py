import pandas as pd
import re

#1. Leitura
df_resumo_mensal = pd.read_csv("Resumo_Mensal_Eletricos_DF_GO.csv", sep=";", encoding="latin1")
df_share_otto = pd.read_excel("share ottto 24-26.xlsx")

#2. Padronização da UF
dicionario_uf = {
    'DF': 'DISTRITO FEDERAL',
    'GO': 'GOIAS',
    'GOIÁS': 'GOIAS'
}
df_share_otto['UF'] = df_share_otto['UF'].astype(str).str.strip().str.upper().replace(dicionario_uf)
df_resumo_mensal['UF'] = df_resumo_mensal['UF'].astype(str).str.strip().str.upper()

#3. Tratamento Híbrido de Datas (O Truque Final)
def criar_chave_data(valor):
    if pd.isna(valor): 
        return None
    
    # Cenário A: Se o Pandas leu como Data real (o Excel faz isso nos bastidores)
    if hasattr(valor, 'strftime'):
        return valor.strftime('%Y-%m')
    
    # Cenário B: Se é texto (CSV ou máscara)
    texto = str(valor).lower().strip()
    
    # Se o Pandas transformou a data em texto no formato americano (YYYY-MM-DD)
    if re.match(r'\d{4}-\d{2}-\d{2}', texto):
        return texto[:7]
        
    # Cenário C: Texto puro em português (jan/24, junho-26)
    meses = {'jan':'01', 'fev':'02', 'mar':'03', 'abr':'04', 'mai':'05', 'jun':'06',
             'jul':'07', 'ago':'08', 'set':'09', 'out':'10', 'nov':'11', 'dez':'12'}
    
    letras = re.sub(r'[^a-z]', '', texto)
    numeros = re.sub(r'[^0-9]', '', texto)
    
    mes = meses.get(letras[:3], '01') if len(letras) >= 3 else '01'
    # Pega sempre os 2 últimos números do ano (ex: 26 de 2026) e coloca o '20' na frente
    ano = '20' + numeros[-2:] if len(numeros) >= 2 else '2000'
    
    return f"{ano}-{mes}"

#Guardando as datas com o formato visual original para o arquivo final
df_resumo_mensal['Data_Original'] = df_resumo_mensal['Data_Ref']
df_share_otto['Data_Original'] = df_share_otto['Data_Ref']

#Aplicando a função matadora para criar a chave de ligação
df_resumo_mensal['Chave_Data'] = df_resumo_mensal['Data_Ref'].apply(criar_chave_data)
df_share_otto['Chave_Data'] = df_share_otto['Data_Ref'].apply(criar_chave_data)

#--- RAIO-X PARA DIAGNÓSTICO (Veja o terminal) ---
print("--- CHAVES DO CSV (ELÉTRICOS) ---")
print(df_resumo_mensal[['Data_Original', 'Chave_Data', 'UF']].head(2))
print("\n--- CHAVES DO EXCEL (OTTO) ---")
print(df_share_otto[['Data_Original', 'Chave_Data', 'UF']].head(2))
print("\nCruzando as bases...\n")

#4. Merge
df_final = pd.merge(
    df_resumo_mensal,
    df_share_otto,
    on=['Chave_Data', 'UF'],
    how='outer'
)

#5. Limpeza e Organização Final
df_final['Data_Ref'] = df_final['Data_Original_x'].fillna(df_final['Data_Original_y'])

# Remove as colunas temporárias
colunas_lixo = ['Chave_Data', 'Data_Original_x', 'Data_Original_y', 'Data_Ref_x', 'Data_Ref_y']
df_final = df_final.drop(columns=[col for col in colunas_lixo if col in df_final.columns], errors='ignore')

# Coloca a Data e a UF na frente de tudo
colunas_ordenadas = ['Data_Ref', 'UF'] + [col for col in df_final.columns if col not in ['Data_Ref', 'UF']]
df_final = df_final[colunas_ordenadas]

#Multiplicando as escalas
df_final['share'] = df_final['share'] * 100000
df_final['vendas'] = df_final['vendas'] * 1000


#6. Exportação BR
df_final.to_csv("Pesquisa_Eletricos_DF_GO_2024_2026.csv", index=False, sep=";", encoding="utf-8-sig", decimal=',')

print("Sucesso! Bases alinhadas.")
# Exibe um pedaço focado nas colunas mais importantes para confirmar
print(df_final[['Data_Ref', 'UF', 'Volume_Eletricos', 'produto', 'share', 'vendas']].head(6))