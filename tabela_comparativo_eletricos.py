import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt 

#Iremos fazer uma tabela comparativa entre o avanço dos elétricos e o share de vendas do Otto e as Vendas do Cliente

#as Tabelas de comparativo da curva de share de vendas do otto e o volume de carros elétricos com as vendas do cliente

df_pesquisa = pd.read_csv("Pesquisa_Eletricos_DF_GO_2024_2026.csv",sep = ";", encoding = "utf-8")

#essa já tem tudo 

#Coluna Volume_Eletricos tem o valor duplicado em etanol e gasolina pois eles tao no memso mês 
#Coluna Share representa o share de vedas de gasolina e etanol respectivamente
#Coluna UF representa o estado de Goiás e Distrito Federal
#Coluna Vendas representa o volume de vendas do cliente que atua em Goiás e Distrito Federal

#df_comparativo = df_pesquisa.groupby(['Data_Ref','UF']).agg({'Volume_Eletricos':'sum','share':'sum','vendas':'sum'}).reset_index()

#Essa df_comparativo tem o volume de elétricos, share de vendas do otto e vendas do cliente por mês e por UF

#Nao é necessária ela já tá feita

#Criar uma coluna para variação do volume de eletricos em relação ao share de vendas do otto

df_pesquisa['Variacao_Volume_Eletricos'] = df_pesquisa.groupby(['UF', 'Combustivel'])['Volume_Eletricos'].diff()

df_pesquisa['Variacao_Volume_Share'] = df_pesquisa.groupby(['UF', 'Combustivel'])['share'].diff()

df_pesquisa['Variacao_Volume_Vendas'] = df_pesquisa.groupby(['UF', 'Combustivel'])['vendas'].diff()


#Fazer tabela comparativa e gráfico que mostra a curva de share de vendas do otto e o volume de carros eletricos com as vendas do cliente

#Adicionar setinhas para mostrar a variação de volume de eletricos em relação ao share de vendas do otto e a variação de vendas do cliente em relação ao volume de eletricos

def adicionar_parada(df, coluna):
    df[f'{coluna}_Parada'] = '-'
    df.loc[df[coluna] > 0, f'{coluna}_Parada'] = '▲'
    df.loc[df[coluna] < 0, f'{coluna}_Parada'] = '▼'
    return df

df_pesquisa = adicionar_parada(df_pesquisa, 'Variacao_Volume_Eletricos')
df_pesquisa = adicionar_parada(df_pesquisa, 'Variacao_Volume_Share')
df_pesquisa = adicionar_parada(df_pesquisa, 'Variacao_Volume_Vendas')


#salvar a DF
df_pesquisa.to_excel("Tabela_Comparativa_Eletricos.xlsx", index=False)


#Gerar gráficos com escalas diferentes

df_pesquisa['Ano'] = df_pesquisa['Data_Ref'].dt.year
df_pesquisa['Mes_Str'] = df_pesquisa['Data_Ref'].dt.strftime('%b')

anos = [2024, 2025, 2026]
ufs = ['GO', 'DF']
combustiveis = ['Gasolina', 'Etanol']

for ano in anos:
    for uf in ufs:
        for comb in combustiveis:
            df_plot = df_pesquisa[(df_pesquisa['UF'] == uf) & 
                                  (df_pesquisa['Ano'] == ano) & 
                                  (df_pesquisa['Combustivel'] == comb)]

#Com essa coluna agora iremo fazer o gráfico
   
   #Separar por ano e mes e o tipo de combustivel que foi vendido, mas fazer tres gráficos com 2023, 2024, 2025 e 2026

#colocar todas as variações no gráfico porém com escalas diferentes

#É um pra cada um deles, ou seja, os de goias e os de df 

#fig_etanol_24 = 
#fig_gasolina_24

            if df_plot.empty:
                continue
                
            fig, ax1 = plt.subplots(figsize=(10, 6))

            # Eixo 1: Vendas (Gráfico de Barras)
            color1 = '#3498db'
            ax1.bar(df_plot['Mes_Str'], df_plot['vendas'], color=color1, alpha=0.6, label='Vendas Cliente')
            ax1.set_xlabel('Mês')
            ax1.set_ylabel('Vendas (Volume)', color=color1, fontweight='bold')
            ax1.tick_params(axis='y', labelcolor=color1)

            # Eixo 2: Share (Linha) - Cria um segundo eixo Y (twinx)
            ax2 = ax1.twinx()
            color2 = '#e74c3c'
            ax2.plot(df_plot['Mes_Str'], df_plot['share'], color=color2, marker='o', linewidth=2, label='Share Otto (%)')
            ax2.set_ylabel('Share Otto (%)', color=color2, fontweight='bold')
            ax2.tick_params(axis='y', labelcolor=color2)

            # Eixo 3: Volume Eletricos (Linha) - Cria um terceiro eixo Y 
            ax3 = ax1.twinx()
            color3 = '#2ecc71'
            # Deslocar a terceira escala para a direita para não ficar em cima da escala do Share
            ax3.spines.right.set_position(("axes", 1.15))
            ax3.plot(df_plot['Mes_Str'], df_plot['Volume_Eletricos'], color=color3, marker='s', linewidth=2, label='Volume Elétricos')
            ax3.set_ylabel('Volume de Elétricos', color=color3, fontweight='bold')
            ax3.tick_params(axis='y', labelcolor=color3)

            plt.title(f'Comparativo: {uf} - {comb} ({ano})', fontsize=14, fontweight='bold')
            fig.tight_layout()
            
            # Salvar o gráfico gerado
            plt.savefig(f'Grafico_{uf}_{comb}_{ano}.png', bbox_inches='tight', dpi=150)
            plt.close()