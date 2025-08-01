from flask import Flask, render_template, request
import pandas as pd
import os
from ai_helper import interpretar_comando
from compare import comparar_planilhas

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    resultado_html = None
    erro = None

    if request.method == "POST":
        try:
            file1 = request.files["file1"]
            file2 = request.files["file2"]
            comando_usuario = request.form.get("comando")

            path1 = os.path.join(UPLOAD_FOLDER, file1.filename)
            path2 = os.path.join(UPLOAD_FOLDER, file2.filename)
            file1.save(path1)
            file2.save(path2)

            df1 = pd.read_excel(path1)
            df2 = pd.read_excel(path2)

            resultado = comparar_planilhas(df1, df2, comando_usuario, interpretar_comando)

            if isinstance(resultado, pd.DataFrame):
                resultado_html = resultado.to_html(classes="table table-bordered", index=False)
            else:
                resultado_html = f"<pre>{resultado}</pre>"

        except Exception as e:
            erro = str(e)

    return render_template("index.html", resultado=resultado_html, erro=erro)

if __name__ == "__main__":
    app.run(debug=True)
