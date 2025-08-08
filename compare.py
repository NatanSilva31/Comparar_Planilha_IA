import pandas as pd
import numpy as np

def _excel_col_to_int(letra_coluna: str) -> int:
    """Converte uma letra de coluna do Excel (A, B, ..., Z, AA) para um índice 0-based."""
    num = 0
    letra_coluna = letra_coluna.upper()
    for c in letra_coluna:
        if not 'A' <= c <= 'Z':
            return -1 # Retorna -1 se não for uma letra válida
        num = num * 26 + (ord(c) - ord('A')) + 1
    return num - 1

def _obter_indice_da_coluna(df: pd.DataFrame, entrada: str) -> int:
    """
    Interpreta a entrada do usuário e retorna o índice 0-based da coluna.
    Retorna -1 se não encontrar.
    """
    if not entrada:
        return -1

    entrada = entrada.strip()

    # 1. Tenta converter para NÚMERO
    try:
        idx = int(entrada) - 1
        if 0 <= idx < len(df.columns):
            return idx
    except (ValueError, TypeError):
        pass

    # 2. Tenta encontrar como NOME da coluna (case-insensitive)
    colunas_upper = [str(col).upper() for col in df.columns]
    try:
        idx = colunas_upper.index(entrada.upper())
        return idx
    except ValueError:
        pass

    # 3. Tenta encontrar como LETRA de coluna
    idx = _excel_col_to_int(entrada)
    if 0 <= idx < len(df.columns):
        return idx

    return -1

def comparar_planilhas(df1, df2, comando, entrada_col1, entrada_col2):
    """
    Compara dois DataFrames com base na entrada do usuário (número, nome ou letra).
    """
    idx1 = _obter_indice_da_coluna(df1, entrada_col1)
    idx2 = _obter_indice_da_coluna(df2, entrada_col2)

    if idx1 == -1:
        return f"Erro: A entrada '{entrada_col1}' não corresponde a nenhuma coluna válida na Planilha 1."
    if idx2 == -1:
        return f"Erro: A entrada '{entrada_col2}' não corresponde a nenhuma coluna válida na Planilha 2."

    key1 = df1.columns[idx1]
    key2 = df2.columns[idx2]
    
    df1_temp = df1.copy()
    df2_temp = df2.copy()
    
    temp_key = "_temp_merge_key_"
    df1_temp.rename(columns={key1: temp_key}, inplace=True)
    df2_temp.rename(columns={key2: temp_key}, inplace=True)

    df1_temp.dropna(subset=[temp_key], inplace=True)
    df2_temp.dropna(subset=[temp_key], inplace=True)

    resultado = pd.DataFrame()

    if comando == "intersecao":
        resultado = pd.merge(df1_temp, df2_temp, on=temp_key, how='inner')
        resultado.rename(columns={temp_key: f"Chave_Comum ({key1}/{key2})"}, inplace=True)

    elif comando == "diferenca_a":
        merged = pd.merge(df1_temp, df2_temp, on=temp_key, how='left', indicator=True)
        resultado = merged[merged['_merge'] == 'left_only'].drop(columns=['_merge'])
        resultado.rename(columns={temp_key: key1}, inplace=True)

    elif comando == "diferenca_b":
        merged = pd.merge(df1_temp, df2_temp, on=temp_key, how='right', indicator=True)
        resultado = merged[merged['_merge'] == 'right_only'].drop(columns=['_merge'])
        resultado.rename(columns={temp_key: key2}, inplace=True)
    
    # NOVA LÓGICA DE DIVERGÊNCIA
    elif comando == "divergencia":
        # Junta as planilhas mantendo ambas as versões das colunas com o mesmo nome
        merged = pd.merge(df1_temp, df2_temp, on=temp_key, how='inner', suffixes=('_P1', '_P2'))
        
        divergencias = []
        # Itera sobre as linhas que têm a mesma chave
        for i, row in merged.iterrows():
            diffs = {}
            tem_divergencia = False
            # Compara cada coluna (exceto a chave)
            for col in df1.columns:
                if col == key1: continue # Pula a própria chave
                col_p1 = col + '_P1'
                col_p2 = col + '_P2'
                
                # Verifica se as colunas existem em ambas as planilhas após o merge
                if col_p1 in merged.columns and col_p2 in merged.columns:
                    val1 = row[col_p1]
                    val2 = row[col_p2]
                    # Compara os valores (tratando NaNs como iguais)
                    if val1 != val2 and not (pd.isna(val1) and pd.isna(val2)):
                        tem_divergencia = True
                        diffs[col] = {'Planilha 1': val1, 'Planilha 2': val2}
            
            if tem_divergencia:
                linha_divergencia = {f"Chave ({key1})": row[temp_key]}
                for col, valores in diffs.items():
                    linha_divergencia[f"{col} (P1)"] = valores['Planilha 1']
                    linha_divergencia[f"{col} (P2)"] = valores['Planilha 2']
                divergencias.append(linha_divergencia)
        
        if divergencias:
            resultado = pd.DataFrame(divergencias)
        
    else:
        return "Erro: Comando de comparação desconhecido."

    if resultado.empty:
        return "A comparação não encontrou nenhum resultado para exibir."

    return resultado
