# compare.py

def comparar_planilhas(df1, df2, comando_usuario, interpretador):
    colunas_disponiveis = list(set(df1.columns) & set(df2.columns))
    codigo = interpretador(comando_usuario, colunas_disponiveis)

    # Adicione esta linha para depuração
    print(f"--- CÓDIGO GERADO PELA IA ---\n{codigo}\n-----------------------------")

    local_vars = {"df1": df1, "df2": df2}
    exec(codigo, {}, local_vars)

    if "resultado" in local_vars:
        return local_vars["resultado"]
    else:
        return "Erro: resultado não foi definido no código da IA."