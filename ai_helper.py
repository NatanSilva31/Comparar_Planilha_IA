# ai_helper.py

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configura a API key do Gemini
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except Exception as e:
    # Trata o caso em que a API key não está configurada
    raise ValueError("A variável de ambiente GEMINI_API_KEY não foi encontrada. Verifique seu arquivo .env.") from e

# Configuração do modelo generativo
generation_config = {
    "temperature": 0.2,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Inicializa o modelo Gemini Pro
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,
    safety_settings=safety_settings
)

def interpretar_comando(comando_usuario: str, colunas_disponiveis: list) -> str:
    """
    Usa o Gemini para traduzir um comando de usuário em um script Python para comparar DataFrames.

    Args:
        comando_usuario: O comando em linguagem natural fornecido pelo usuário.
        colunas_disponiveis: Uma lista de nomes de colunas que são comuns aos dois DataFrames.

    Returns:
        Um string contendo o código Python a ser executado.
    """
    prompt = f"""
    Você é um assistente especialista em Python e na biblioteca Pandas. Sua tarefa é gerar **APENAS** o código Python necessário para comparar dois DataFrames chamados `df1` e `df2`.

    Regras importantes:
    1.  O resultado final da sua análise **DEVE** ser armazenado em uma variável chamada `resultado`.
    2.  Não adicione nenhum texto, explicação, comentário ou formatação como ```python ``` ao redor do código. Gere apenas o código Python puro.
    3.  Os DataFrames `df1` (representando a primeira planilha) e `df2` (representando a segunda planilha) já estão carregados na memória. Não inclua código para carregar ou ler arquivos.
    4.  As colunas disponíveis para comparação, que são comuns a ambos os DataFrames, são: {colunas_disponiveis}. Use apenas estas colunas em sua análise.
    5.  O tipo do `resultado` deve ser, preferencialmente, um DataFrame do Pandas para ser exibido corretamente.

    Comando do usuário: "{comando_usuario}"

    Gere o código Python abaixo:
    """

    try:
        # Envia o prompt para o modelo
        response = model.generate_content(prompt)
        
        # Extrai o código gerado da resposta
        codigo_gerado = response.text.strip()
        
        return codigo_gerado
        
    except Exception as e:
        # Retorna uma mensagem de erro se a chamada da API falhar
        return f"print('Erro ao se comunicar com a API do Gemini: {str(e)}')"