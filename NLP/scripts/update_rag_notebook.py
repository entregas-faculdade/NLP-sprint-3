import nbformat
import sys
import os

def update_notebook(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    # Nova célula de imports (célula 1)
    new_imports = """!pip install sentence-transformers faiss-cpu langchain langchain-community huggingface_hub -q
import json
import numpy as np
import faiss
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain.docstore.document import Document
from sentence_transformers import SentenceTransformer"""

    # Nova célula de chunking (célula 3)
    new_chunking = """corpus_textos = [
    \"\"\"# Manual do Motor W22 Plus\\n\\n## 1. Lubrificação e Manutenção\\nOs rolamentos devem ser lubrificados a cada 2.000 horas de operacao ou 6 meses. O torque de aperto dos parafusos de fixacao deve ser de 25 N.m.\\n\\n## 2. Limites Operacionais\\nA vibracao maxima permitida eh de 2,8 mm/s RMS conforme ISO 10816. Corrente de partida (Ia/In) 6,5x a corrente nominal.\\n\"\"\",
    \"\"\"# Siemens 1LA7 Series Manual\\n\\n## 1. Commissioning\\nInsulation resistance must be measured before commissioning. Minimum insulation resistance 100 MOhm at 1000V DC 60 seconds.\\n\\n## 2. Maintenance and Limits\\nRegreasing interval 3500 hours for bearings under normal load. Vibration limits per ISO 10816 Class B less than 2.8 mm/s RMS. Temperatura maxima do enrolamento 155C Classe F.\\n\"\"\"
]

# 1. Chunking Semântico com Markdown
headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
]
markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

docs_markdown = []
for text in corpus_textos:
    docs_markdown.extend(markdown_splitter.split_text(text))

# 2. Chunking Secundário Recursivo
text_splitter = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=30)
chunks = text_splitter.split_documents(docs_markdown)

chunk_texts = [chunk.page_content for chunk in chunks]
chunk_metadata = [chunk.metadata for chunk in chunks]

print(f"Total de {len(chunk_texts)} chunks gerados.")

# 3. Indexação no FAISS
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
embeddings = model.encode(chunk_texts, convert_to_numpy=True, normalize_embeddings=True)

dim = embeddings.shape[1]
index = faiss.IndexFlatIP(dim)
index.add(embeddings)
print(f"Indexado {index.ntotal} vetores no FAISS.")"""

    # Nova célula de Retriever / LLM (célula 5)
    new_retriever = """def buscar_contexto_com_rerank(query, alerta_atual="", top_k=3, k_inicial=10):
    # 1. Busca inicial (Retrieval FAISS)
    q_emb = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    distances, indices = index.search(q_emb, k_inicial)
    
    resultados_iniciais = []
    for i, idx in enumerate(indices[0]):
        if idx == -1 or idx >= len(chunk_texts): continue
        resultados_iniciais.append({
            "id": idx,
            "score": float(distances[0][i]),
            "text": chunk_texts[idx],
            "metadata": chunk_metadata[idx]
        })
        
    # 2. Re-ranking (Cross-Encoder Rule-based para o estado atual)
    # Avaliamos os metadados gerados pelo MarkdownHeaderTextSplitter.
    for res in resultados_iniciais:
        doc_header = res["metadata"].get("Header 1", "").lower()
        bonus = 0.0
        
        # O re-ranker aumenta o score de similaridade se o chunk 
        # pertencer ao motor listado no alerta ativo atual.
        if "w22" in alerta_atual.lower() and "w22" in doc_header:
            bonus = 0.5
        elif "siemens" in alerta_atual.lower() and "siemens" in doc_header:
            bonus = 0.5
            
        res["score_reranked"] = res["score"] + bonus
        
    # Ordenar pelos scores recalculados (descendente)
    resultados_iniciais.sort(key=lambda x: x["score_reranked"], reverse=True)
    
    top_results = resultados_iniciais[:top_k]
    
    contexto = ""
    for r in top_results:
        contexto += f"[Origem: {r['metadata']}] {r['text']}\\n"
        
    return contexto, top_results

def simular_assistente(query, alerta_contexto=""):
    contexto_recuperado, _ = buscar_contexto_com_rerank(query, alerta_contexto)
    prompt = f\"\"\"[PERSONA]: Assistente técnico especialista em motores elétricos.
[ESTADO ATUAL DO ATIVO]: {alerta_contexto}
[INFORMAÇÃO RECUPERADA (RAG)]: 
{contexto_recuperado}
[PERGUNTA DO OPERADOR]: {query}
\"\"\"
    print("--- PROMPT FINAL GERADO ---")
    print(prompt)
    return "Resposta Simulada do LLM: Os limites de vibração permitidos são X, com base no manual recuperado."

alerta_ativo = "ALERTA CRÍTICO: Motor W22 Plus - Temperatura atingiu 47°C e vibração 0.47g."
pergunta = "Quais são os limites de vibração aceitáveis?"
simular_assistente(pergunta, alerta_ativo)"""

    # Atualiza as células (os índices baseiam-se na estrutura do notebook que vimos)
    nb.cells[1].source = new_imports
    nb.cells[3].source = new_chunking
    nb.cells[5].source = new_retriever

    with open(notebook_path, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)
        
    print("Notebook atualizado com sucesso!")

if __name__ == "__main__":
    notebook_path = sys.argv[1]
    update_notebook(notebook_path)
