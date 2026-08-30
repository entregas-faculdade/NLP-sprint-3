import os
import sys
import json
import requests
import re
import time
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder
import fitz  # PyMuPDF

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("GROQ-API-KEY")
OPENROUTER_API_KEY = os.getenv("OPEN_ROUTER_API_KEY") or os.getenv("OPEN-ROUTER-API-KEY")

script_dir = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(script_dir, "..", "..", "docs", "WEG-w22-motor-eletrico-trifasico-brochure.pdf")

# ==========================================
# 1. Chunking Inteligente (Semântico)
# ==========================================
def intelligent_chunk_text(text, max_chunk_size=1000):
    """Quebra o documento em parágrafos para não cortar frases ao meio."""
    paragraphs = re.split(r'\n\s*\n', text)
    chunks = []
    current_chunk = ""
    
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if len(current_chunk) + len(p) <= max_chunk_size:
            current_chunk += p + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = p + "\n\n"
            
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

# ==========================================
# 2. Retriever com Re-ranking
# ==========================================
class RAGRetriever:
    def __init__(self, collection):
        self.collection = collection
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Carregando modelo de Re-ranking (CrossEncoder)...")
        self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    
    def invoke(self, query, top_k=5, final_k=2):
        # Passo 1: Recuperação inicial ampla
        query_embedding = self.model.encode(query).tolist()
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        
        docs = results['documents'][0] if results['documents'] else []
        if not docs:
            return []
            
        # Passo 2: Re-ranking usando CrossEncoder
        pairs = [[query, doc] for doc in docs]
        scores = self.cross_encoder.predict(pairs)
        
        scored_docs = sorted(zip(scores, docs), key=lambda x: x[0], reverse=True)
        
        # Retorna apenas os 'final_k' documentos mais relevantes
        return [doc for score, doc in scored_docs[:final_k]]

def get_retriever():
    print(f"Carregando documento PDF: {PDF_PATH}")
    doc = fitz.open(PDF_PATH)
    full_text = ""
    for page in doc:
        extracted = page.get_text()
        if extracted:
            full_text += extracted + "\n"
    
    print("Realizando chunking inteligente...")
    splits = intelligent_chunk_text(full_text)
    print(f"Total de chunks (semânticos): {len(splits)}")

    print("Gerando embeddings e vectorstore...")
    chroma_client = chromadb.Client()
    try:
        chroma_client.delete_collection("weg_manual")
    except Exception:
        pass
        
    collection = chroma_client.create_collection(name="weg_manual")
    
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(splits).tolist()
    
    ids = [str(i) for i in range(len(splits))]
    collection.add(
        embeddings=embeddings,
        documents=splits,
        ids=ids
    )
    return RAGRetriever(collection)

# ==========================================
# 3. Integração com LLM e Memória
# ==========================================
class ConversationalAssistant:
    def __init__(self, retriever):
        self.retriever = retriever
        self.history = []
        
    def chat(self, query, state_context=""):
        retrieved_docs = self.retriever.invoke(query)
        context = "\n\n".join(retrieved_docs)
        
        # Injeção de histórico no prompt (Memória de curto prazo - ultimas 2 interações)
        hist_text = "\n".join([f"Usuário: {u}\nAssistente: {a}" for u, a in self.history[-2:]])
        if hist_text:
            hist_text = "Histórico Recente:\n" + hist_text + "\n"
            
        prompt = f"""Você é um Engenheiro Especialista em Manutenção de Motores Elétricos.
Use o contexto técnico fornecido abaixo para responder a pergunta. Cite trechos do manual, se possível.

Contexto Técnico do Manual Recuperado:
{context}

Estado Atual (Telemetria) da Máquina:
{state_context}

{hist_text}
Pergunta Atual do Usuário: {query}
Responda com confiança, assertividade e indique seu nível de confiança na resposta baseada no documento."""

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        # Tenta modelos na Groq primeiro
        models_groq = ["qwen/qwen3.8-27b", "llama3-8b-8192"]
        for model in models_groq:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }
            try:
                resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
                resp.raise_for_status()
                answer = resp.json()["choices"][0]["message"]["content"]
                self.history.append((query, answer))
                return answer, context
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    print(f"[Aviso] Rate limit Groq ({model})...")
                    continue
            except Exception:
                continue
                
        # Fallback Provedor: OpenRouter
        if OPENROUTER_API_KEY:
            print("[Aviso] Alternando para OpenRouter (Fallback de Provedor)...")
            headers_or = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            payload_or = {
                "model": "openrouter/free",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }
            try:
                resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers_or, json=payload_or)
                resp.raise_for_status()
                answer = resp.json()["choices"][0]["message"]["content"]
                self.history.append((query, answer))
                return answer, context
            except Exception as e:
                return f"Erro em todos os provedores (Groq e OpenRouter). Último erro: {e}", context
                
        return "Erro: Falha na Groq e OpenRouter não configurado.", context

# ==========================================
# 4. Avaliação (LLM-as-a-Judge) 20 Perguntas
# ==========================================
def evaluate_rag(query, answer, context, ground_truth):
    prompt = f"""Avalie a resposta RAG gerada baseada nos seguintes critérios, retornando APENAS um JSON válido e nada mais.
Critérios:
1. faithfulness: A resposta (answer) é fiel ao contexto (context) fornecido, sem alucinar ou inventar dados? (Dar nota de 1 a 5)
2. answer_relevancy: A resposta atende e resolve a pergunta (query) baseada na referência (ground_truth)? (Dar nota de 1 a 5)

Pergunta: {query}
Contexto Recuperado: {context}
Resposta Gerada: {answer}
Gabarito de Referência (Ground Truth): {ground_truth}

Retorne ESTRITAMENTE o formato JSON:
{{"faithfulness": score, "answer_relevancy": score, "justificativa": "sua justificativa breve"}}"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    models_groq = ["qwen/qwen3.8-27b", "llama3-8b-8192"]
    
    for model in models_groq:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
        
        try:
            resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            return json.loads(content)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                continue
        except Exception:
            continue
            
    if OPENROUTER_API_KEY:
        headers_or = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload_or = {
            "model": "openrouter/free",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1
        }
        try:
            resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers_or, json=payload_or)
            resp.raise_for_status()
            
            content = resp.json()["choices"][0]["message"]["content"]
            # OpenRouter pode não respeitar estritamente o json_object de forma nativa sempre, mas vamos tentar ler
            try:
                return json.loads(content)
            except:
                import re
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
                return {"faithfulness": 0, "answer_relevancy": 0, "justificativa": "JSON inválido do OpenRouter"}
        except Exception as e:
            return {"faithfulness": 0, "answer_relevancy": 0, "justificativa": f"Erro Fallback OpenRouter: {e}"}
            
    return {"faithfulness": 0, "answer_relevancy": 0, "justificativa": "Erro: Limite de taxa na Groq. OpenRouter indisponível."}

def run_evaluation(assistant):
    perguntas_teste = [
        {"q": "O que indica a proteção térmica PTC?", "gt": "Indica sobreaquecimento, variando resistência e desligando o circuito principal."},
        {"q": "Qual a classe de isolamento padrão do W22?", "gt": "O motor W22 padrão possui classe de isolamento F."},
        {"q": "Qual o limite de temperatura ambiente para operação?", "gt": "-30°C a +40°C."},
        {"q": "Como é a proteção contra correntes de mancal para carcaças 315S/M?", "gt": "Uso de rolamento isolado ou tampa com cubo isolado e escova de aterramento."},
        {"q": "Para que serve a graxa nos rolamentos?", "gt": "Para lubrificação e redução de atrito e temperatura."},
        {"q": "Os motores com rendimento IR3 podem operar com inversor de frequência?", "gt": "Sim, são otimizados para operar com inversores."},
        {"q": "Qual o grau de proteção dos motores padrão?", "gt": "Grau de proteção IP55."},
        {"q": "Qual fator afeta a vida útil dos rolamentos?", "gt": "Operação em velocidades variadas ou desalinhamento mecânico."},
        {"q": "Quais cores são usadas no esquema de pintura?", "gt": "Azul RAL 5009 padrão."},
        {"q": "O que deve ser feito se a tensão estiver fora do padrão?", "gt": "Usar relés de proteção para evitar sobrecarga."},
        {"q": "Como funciona o dreno de condensação?", "gt": "Os drenos permitem a saída de água condensada e devem ser abertos periodicamente."},
        {"q": "O motor possui resistência de aquecimento?", "gt": "Opcional, usada para prevenir condensação durante paradas prolongadas."},
        {"q": "Quando usar rolamentos de rolo?", "gt": "Recomendados para aplicações com altas cargas radiais."},
        {"q": "Qual material da carcaça do motor W22?", "gt": "Ferro fundido FC-200."},
        {"q": "Qual a vantagem das aletas na tampa dianteira?", "gt": "Melhora a ventilação e reduz a temperatura do rolamento."},
        {"q": "Como é o balanceamento do eixo?", "gt": "O motor é balanceado dinamicamente com meia chaveta padrão."},
        {"q": "Para qual frequência os motores são projetados?", "gt": "Opcionalmente 50Hz ou 60Hz."},
        {"q": "O que acontece se o motor vibrar excessivamente?", "gt": "Pode haver desbalanceamento mecânico exigindo parada imediata."},
        {"q": "O que é derating de potência?", "gt": "Redução da potência útil se temperatura ambiente > 40°C ou altitude > 1000m."},
        {"q": "Qual a função do anel V-ring?", "gt": "Promover vedação contra poeira e água no eixo."}
    ]
    
    print("\n" + "="*60)
    print(" INICIANDO AVALIAÇÃO RAGAS (LLM-as-a-Judge) - 20 PERGUNTAS")
    print("="*60)
    
    total_faithfulness = 0
    total_relevancy = 0
    num_questions = len(perguntas_teste)
    
    for i, item in enumerate(perguntas_teste):
        print(f"\n[Avaliando {i+1}/{num_questions}] P: {item['q']}")
        # Limpa o histórico antes de avaliar cada pergunta solta do dataset
        assistant.history = []
        ans, ctx = assistant.chat(item['q'], state_context="Condições normais.")
        
        eval_metrics = evaluate_rag(item['q'], ans, ctx, item['gt'])
        
        f_score = eval_metrics.get('faithfulness', 0)
        r_score = eval_metrics.get('answer_relevancy', 0)
        
        total_faithfulness += f_score
        total_relevancy += r_score
        
        print(f"   --> Faithfulness: {f_score}/5 | Answer Relevancy: {r_score}/5")
        print(f"   --> Justificativa: {eval_metrics.get('justificativa', '')}")
        time.sleep(3) # Tempo de espera aumentado para garantir respiro à API
        
    print("\n" + "="*60)
    print(f" RESULTADOS FINAIS DA AVALIAÇÃO RAG")
    print(f" Média Faithfulness:     {total_faithfulness/num_questions:.2f} / 5.0")
    print(f" Média Answer Relevancy: {total_relevancy/num_questions:.2f} / 5.0")
    print("="*60)


def main():
    print("Iniciando RAG Sprint 4 com Adequações...")
    if not os.path.exists(PDF_PATH):
        print(f"PDF não encontrado no caminho: {PDF_PATH}")
        return

    retriever = get_retriever()
    assistant = ConversationalAssistant(retriever)
        
    print("\n--- Demonstração: Assistente Conversacional (Com Histórico) ---")
    
    print("\n>>> Cenário 1: Temperatura Crítica (Injeção de Estado)")
    estado_1 = "Temperatura crítica registrada (47°C) - Falha pendente"
    p1 = "A temperatura do motor disparou para 47°C, o alarme tocou. O que eu faço?"
    print(f"Pergunta: {p1}")
    r1, _ = assistant.chat(p1, estado_1)
    print(f"Resposta:\n{r1}")

    print("\n>>> Cenário 2: Teste de Memória de Curto Prazo (Diálogo)")
    p2 = "E quais as possíveis causas raiz desse problema que você acabou de citar?"
    print(f"Pergunta: {p2}")
    r2, _ = assistant.chat(p2, estado_1) 
    print(f"Resposta:\n{r2}")
    
    # Executa a suíte de avaliação
    run_evaluation(assistant)

if __name__ == "__main__":
    main()
