from flask import Flask, render_template, request
import pandas as pd
import os
# A importação do 'ai_helper' foi removida.
from compare import comparar_planilhas

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Define a pasta de templates explicitamente
app.template_folder = 'templates'

@app.route("/", methods=["GET", "POST"])
def index():
    resultado_html = None
    erro = None

    if request.method == "POST":
        try:
            # Validação básica de arquivos
            if 'file1' not in request.files or 'file2' not in request.files:
                raise ValueError("Por favor, envie os dois arquivos de planilha.")

            file1 = request.files["file1"]
            file2 = request.files["file2"]

            if file1.filename == '' or file2.filename == '':
                raise ValueError("Um ou mais arquivos não foram selecionados.")

            # Coleta dos dados do formulário
            comando_selecionado = request.form.get("comando")
            entrada_col1 = request.form.get("coluna1")
            entrada_col2 = request.form.get("coluna2")

            # Salva os arquivos no servidor
            path1 = os.path.join(UPLOAD_FOLDER, file1.filename)
            path2 = os.path.join(UPLOAD_FOLDER, file2.filename)
            file1.save(path1)
            file2.save(path2)

            # Lê os arquivos excel
            df1 = pd.read_excel(path1)
            df2 = pd.read_excel(path2)

            # Chama a nova função 'comparar_planilhas' com os argumentos corretos
            resultado = comparar_planilhas(df1, df2, comando_selecionado, entrada_col1, entrada_col2)

            # Verifica se o resultado é um DataFrame (sucesso) ou uma string (erro/aviso)
            if isinstance(resultado, pd.DataFrame):
                # Usa as classes do novo CSS para a tabela
                resultado_html = resultado.to_html(classes="table", index=False)
            else:
                # Se for uma string, trata como um erro/aviso para exibir no alerta
                erro = resultado

        except Exception as e:
            erro = str(e)

    return render_template("index.html", resultado=resultado_html, erro=erro)

if __name__ == "__main__":
    app.run(debug=True)
