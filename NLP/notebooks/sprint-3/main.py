import os
import sys
import json
import requests
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

# Dependências adicionais requeridas:
# pip install rouge-score scikit-learn python-dotenv requests
try:
    from rouge_score import rouge_scorer
    from sklearn.metrics import classification_report
except ImportError as e:
    print(f"Erro de importação: {e}. Certifique-se de instalar as dependências necessárias.")

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("GROQ-API-KEY")

# Caminhos baseados na localização atual do script (notebooks/sprint-3)
script_dir = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(script_dir, "..", "..", "data", "dados_avaliacao.json")

def carregar_dados():
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            dados_avaliacao = json.load(f)
        return dados_avaliacao.get("alertas_teste", [])
    except FileNotFoundError:
        print(f"Arquivo não encontrado em: {DATA_PATH}")
        return []

def call_llm(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen/qwen3.8-27b", 
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    try:
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return str(e)

def gerar_alerta(dados_motor, severidade):
    if severidade == "leve":
        tom = "Foque em observação contínua. Tom informativo, indicando leve desvio que deve ser monitorado."
    elif severidade == "moderado":
        tom = "Foque em atenção e recomendação preventiva. Tom de advertência, sugerindo inspeção em breve."
    else: # crítico
        tom = "Foque em urgência, desligamento ou ação corretiva imediata. Tom grave e diretivo."
        
    prompt = f"""Você é um assistente do sistema de monitoramento de motores elétricos.
    Gere um alerta técnico em português baseado nos dados do sensor:
    - Motor: {dados_motor.get('motor')}
    - Temperatura: {dados_motor.get('temperatura')}°C
    - Aceleração/Vibração: {dados_motor.get('aceleracao')}g
    - Timestamp: {dados_motor.get('timestamp')}
    
    Diretrizes:
    {tom}
    Inclua os dados do sensor na sua resposta para rastreabilidade.
    """
    return call_llm(prompt)

def avaliar_rouge(alertas_gerados):
    try:
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
        print("\\n--- Avaliação ROUGE dos Alertas Gerados ---")
        for i, a in enumerate(alertas_gerados):
            scores = scorer.score(a["referencia"], a["gerado"])
            print(f"Alerta {i+1} ({a['severidade_esperada']}):")
            print(f"  ROUGE-1: Precision: {scores['rouge1'].precision:.2f}, Recall: {scores['rouge1'].recall:.2f}, F1: {scores['rouge1'].fmeasure:.2f}")
            print(f"  ROUGE-L: Precision: {scores['rougeL'].precision:.2f}, Recall: {scores['rougeL'].recall:.2f}, F1: {scores['rougeL'].fmeasure:.2f}")
    except NameError:
        print("Biblioteca rouge_scorer não importada.")

def classificar_alerta(alerta):
    categorias = ["manutenção corretiva", "manutenção preventiva", "anomalia elétrica", "anomalia mecânica", "operação normal"]
    prompt = f"""Classifique o seguinte alerta de motor elétrico estritamente em UMA das categorias abaixo. 
    Retorne APENAS o nome da categoria, sem textos adicionais.
    Categorias: {', '.join(categorias)}
    
    Alerta: {alerta}
    """
    resposta = call_llm(prompt).lower()
    for c in categorias:
        if c in resposta:
            return c
    return "desconhecido"

def gerar_relatorio_operacional(alertas_classificados):
    prompt = """Com base na seguinte lista de alertas classificados, gere um relatório diário consolidado em linguagem natural sumarizando:
    1. Alertas emitidos
    2. Equipamentos em risco
    3. Tendências observadas
    4. Recomendações preliminares
    Cada afirmação deve referenciar o dado do sensor de origem (rastreabilidade).
    
    Alertas:
"""
    for a in alertas_classificados:
        prompt += f"- {a}\n"
        
    return call_llm(prompt)

def main():
    print("Iniciando PLN Sprint 3...")
    alertas_teste = carregar_dados()
    if not alertas_teste:
        return
        
    alertas_gerados = []
    
    # 1. Geração de Alertas
    print("1. Gerando Alertas...")
    for teste in alertas_teste:
        texto_alerta = gerar_alerta(teste["dados"], teste["severidade_esperada"])
        alertas_gerados.append({
            "gerado": texto_alerta,
            "referencia": teste["resumo_referencia"],
            "severidade_esperada": teste["severidade_esperada"]
        })

    for i, a in enumerate(alertas_gerados):
        print(f"\\n--- ALERTA {i+1} ({a['severidade_esperada']}) ---")
        print("Gerado:", a["gerado"])
        print("Referência:", a["referencia"])

    # 2. Avaliação ROUGE
    avaliar_rouge(alertas_gerados)

    # 3. Classificação e Avaliação F1
    print("\\n2. Classificando Alertas...")
    y_true = ["manutenção corretiva", "manutenção preventiva", "operação normal"]
    y_pred = []

    for a in alertas_gerados:
        cat = classificar_alerta(a["gerado"])
        y_pred.append(cat)
        print(f"Alerta ({a['severidade_esperada']}) classificado como: {cat}")

    try:
        print("\\n--- Avaliação F1-Score da Classificação ---")
        print(classification_report(y_true, y_pred, zero_division=0))
    except NameError:
        print("Biblioteca sklearn não importada para classification_report.")

    # 4. Relatório Operacional
    print("\\n3. Gerando Relatório Operacional Consolidado...")
    textos_para_relatorio = [f"{a['gerado']} -> Classificado como: {c}" for a, c in zip(alertas_gerados, y_pred)]
    relatorio = gerar_relatorio_operacional(textos_para_relatorio)
    print("\\n--- RELATÓRIO ---")
    print(relatorio)

if __name__ == "__main__":
    main()
