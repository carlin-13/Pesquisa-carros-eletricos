#bibliotecas

import os
import zipfile
import re
import pandas as pd
from flask import Flask, jsonify, request


app = Flask(__name__)

#Pasta onde estãoos arquivos zipados 
PASTA_BASES = "Bases"


def listar_arquivos_zip():
    if not os.path.exists(PASTA_BASES):   #lista os arquivos zipados na pasta Bases
        return []
    return [f for f in os.listdir(PASTA_BASES) if f.endswith(".zip")]





def extrair_ano(nome_arquivo):   #extrai o ano do nome do arquivo zipado
    match = re.search(r"\b(20\d{2})\b", nome_arquivo)
    return match.group(1) if match else "Desconhecido" #desconhecido se nao tiver o ano

def ler_e_filtrar_zip(caminho_zip): 
    with zipfile.ZipFile(caminho_zip, 'r') as z: #le o zip
        nome_interno = [f for f in z.namelist() if f.endswith(('.csv', '.txt'))][0]
        with z.open(nome_interno) as f:
            df = pd.read_csv(f, sep=";", encoding="latin1", low_memory=False) #le o csv e considera a linguagem latin1
            df.columns = [c.strip().upper() for c in df.columns]
            coluna_uf = next((c for c in df.columns if "UF" in c), None)
            if coluna_uf:
                df = df[df[coluna_uf].isin(["DF", "GO"])]
            return df



@app.route("/bases", methods=["GET"])
def get_anos():
    arquivos = listar_arquivos_zip()        #lista os arquivos
    anos = sorted(list({extrair_ano(f) for f in arquivos}))  #extrai o ano de cada arquivo
    return jsonify({"anos_disponiveis": anos})   #retorna os anos

@app.route("/api", methods=["GET"])
def get_dados(): 
    ano_filtro = request.args.get("ano")     #pega o ano da url
    arquivos = listar_arquivos_zip()
    if ano_filtro:          #laço para filtrar o ano
        arquivos = [f for f in arquivos if extrair_ano(f) == str(ano_filtro)]
    dfs = []
    for arq in arquivos:
        caminho = os.path.join(PASTA_BASES, arq)
        try:
            df_temp = ler_e_filtrar_zip(caminho)
            df_temp["ANO_REFERENCIA"] = extrair_ano(arq)
            dfs.append(df_temp)
        except Exception as e:
            continue
    if not dfs:
        return jsonify({"mensagem": "Nenhum dado encontrado para os parâmetros informados.", "dados": []}), 404
    df_final = pd.concat(dfs, ignore_index=True)    #concatena os dataframes
    return jsonify(df_final.to_dict(orient="records"))   #retorna os dados
@app.route("/api/gerar_resumo", methods=["GET"])
def gerar_resumo():
    arquivos = listar_arquivos_zip()
    dfs = []
    for arq in arquivos:
        caminho = os.path.join(PASTA_BASES, arq)   #pega o caminho dos arquivos
        try:
            df_temp = ler_e_filtrar_zip(caminho)    #le os arquivos
            df_temp["ANO_REFERENCIA"] = extrair_ano(arq)
            dfs.append(df_temp)
        except Exception:
            continue

    if not dfs:
        return jsonify({"mensagem": "Nenhum dado disponível para resumo."}), 404

    df_final = pd.concat(dfs, ignore_index=True)
    coluna_uf = next((c for c in df_final.columns if "UF" in c), "UF")
    coluna_qtd = next((c for c in df_final.columns if "QTD" in c or "TOTAL" in c), None)

    if coluna_qtd:
        df_final[coluna_qtd] = pd.to_numeric(df_final[coluna_qtd], errors="coerce").fillna(0)
        resumo = df_final.groupby([coluna_uf, "ANO_REFERENCIA"])[coluna_qtd].sum().reset_index()
    else:
        resumo = df_final.groupby([coluna_uf, "ANO_REFERENCIA"]).size().reset_index(name="TOTAL_REGISTROS")  #cria o resumo
    return jsonify(resumo.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)   #devolve o debug e a porta 5000 para rodar a api