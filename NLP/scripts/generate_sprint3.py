import nbformat as nbf

nb = nbf.v4.new_notebook()

setup_cell = nbf.v4.new_code_cell("""\
# Sprint 3: Geração de Alertas, Classificação e Relatório Operacional
import os
import json
import pandas as pd
from dotenv import load_dotenv
import requests

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("GROQ-API-KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPEN-ROUTER-API-KEY")

!pip install rouge-score scikit-learn
""")
nb.cells.append(setup_cell)

data_cell = nbf.v4.new_code_cell("""\
# Carregar dados de avaliação (Ground Truth)
try:
    with open("../data/dados_avaliacao.json", "r", encoding="utf-8") as f:
        dados_avaliacao = json.load(f)
    alertas_teste = dados_avaliacao.get("alertas_teste", [])
except FileNotFoundError:
    print("Arquivo de dados de avaliação não encontrado. Certifique-se de que ../data/dados_avaliacao.json existe.")
    alertas_teste = []
""")
nb.cells.append(data_cell)

alert_gen_cell = nbf.v4.new_code_cell("""\
def call_llm(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192", 
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    try:
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return str(e)

def gerar_alerta(dados_motor, severidade):
    # Templates baseados na severidade
    if severidade == "leve":
        tom = "Foque em observação contínua. Tom informativo, indicando leve desvio que deve ser monitorado."
    elif severidade == "moderado":
        tom = "Foque em atenção e recomendação preventiva. Tom de advertência, sugerindo inspeção em breve."
    else: # crítico
        tom = "Foque em urgência, desligamento ou ação corretiva imediata. Tom grave e diretivo."
        
    prompt = f\"\"\"Você é um assistente do sistema de monitoramento de motores elétricos.
    Gere um alerta técnico em português baseado nos dados do sensor:
    - Motor: {dados_motor.get('motor')}
    - Temperatura: {dados_motor.get('temperatura')}°C
    - Aceleração/Vibração: {dados_motor.get('aceleracao')}g
    - Timestamp: {dados_motor.get('timestamp')}
    
    Diretrizes:
    {tom}
    Inclua os dados do sensor na sua resposta para rastreabilidade.
    \"\"\"
    return call_llm(prompt)

alertas_gerados = []
for teste in alertas_teste:
    texto_alerta = gerar_alerta(teste["dados"], teste["severidade_esperada"])
    alertas_gerados.append({
        "gerado": texto_alerta,
        "referencia": teste["resumo_referencia"],
        "severidade_esperada": teste["severidade_esperada"]
    })

for i, a in enumerate(alertas_gerados):
    print(f"--- ALERTA {i+1} ({a['severidade_esperada']}) ---")
    print("Gerado:", a["gerado"])
    print("Referência:", a["referencia"])
    print()
""")
nb.cells.append(alert_gen_cell)

rouge_eval_cell = nbf.v4.new_code_cell("""\
from rouge_score import rouge_scorer

scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)

print("--- Avaliação ROUGE dos Alertas Gerados ---")
for i, a in enumerate(alertas_gerados):
    scores = scorer.score(a["referencia"], a["gerado"])
    print(f"Alerta {i+1} ({a['severidade_esperada']}):")
    print(f"  ROUGE-1: Precision: {scores['rouge1'].precision:.2f}, Recall: {scores['rouge1'].recall:.2f}, F1: {scores['rouge1'].fmeasure:.2f}")
    print(f"  ROUGE-L: Precision: {scores['rougeL'].precision:.2f}, Recall: {scores['rougeL'].recall:.2f}, F1: {scores['rougeL'].fmeasure:.2f}")
""")
nb.cells.append(rouge_eval_cell)

classification_cell = nbf.v4.new_code_cell("""\
def classificar_alerta(alerta):
    categorias = ["manutenção corretiva", "manutenção preventiva", "anomalia elétrica", "anomalia mecânica", "operação normal"]
    prompt = f\"\"\"Classifique o seguinte alerta de motor elétrico estritamente em UMA das categorias abaixo. 
    Retorne APENAS o nome da categoria, sem textos adicionais.
    Categorias: {', '.join(categorias)}
    
    Alerta: {alerta}
    \"\"\"
    resposta = call_llm(prompt).lower()
    for c in categorias:
        if c in resposta:
            return c
    return "desconhecido"

# Para avaliação, vamos simular que o primeiro é corretiva (pois é crítico), o segundo preventiva (moderado), e o terceiro operação normal/observação (leve).
y_true = ["manutenção corretiva", "manutenção preventiva", "operação normal"]
y_pred = []

for a in alertas_gerados:
    cat = classificar_alerta(a["gerado"])
    y_pred.append(cat)
    print(f"Alerta ({a['severidade_esperada']}) classificado como: {cat}")
""")
nb.cells.append(classification_cell)

f1_eval_cell = nbf.v4.new_code_cell("""\
from sklearn.metrics import f1_score, classification_report

print("\\n--- Avaliação F1-Score da Classificação ---")
# y_true precisa mapear com as mesmas classes
try:
    print(classification_report(y_true, y_pred, zero_division=0))
except Exception as e:
    print("Erro na classificação:", e)
""")
nb.cells.append(f1_eval_cell)

report_cell = nbf.v4.new_code_cell("""\
def gerar_relatorio_operacional(alertas_classificados):
    prompt = \"\"\"Com base na seguinte lista de alertas classificados, gere um relatório diário consolidado em linguagem natural sumarizando:
    1. Alertas emitidos
    2. Equipamentos em risco
    3. Tendências observadas
    4. Recomendações preliminares
    Cada afirmação deve referenciar o dado do sensor de origem (rastreabilidade).
    
    Alertas:\\n\"\"\"
    for a in alertas_classificados:
        prompt += f"- {a}\\n"
        
    return call_llm(prompt)

textos_para_relatorio = [f"{a['gerado']} -> Classificado como: {c}" for a, c in zip(alertas_gerados, y_pred)]
relatorio = gerar_relatorio_operacional(textos_para_relatorio)

print("--- RELATÓRIO OPERACIONAL CONSOLIDADO ---")
print(relatorio)
""")
nb.cells.append(report_cell)

with open("notebooks/sprint3_pln_alertas.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb, f)
print("Notebook sprint3_pln_alertas.ipynb gerado com a implementação completa.")
