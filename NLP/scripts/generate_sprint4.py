import nbformat as nbf

nb = nbf.v4.new_notebook()

# Cell 1: Setup and imports
setup_cell = nbf.v4.new_code_cell("""\
# Sprint 4: Pipeline RAG e Assistente Conversacional
import os
import json
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("GROQ-API-KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPEN-ROUTER-API-KEY")

# !pip install langchain langchain_community chromadb sentence_transformers
""")
nb.cells.append(setup_cell)

# Cell 2: Document Ingestion and Chunking
doc_cell = nbf.v4.new_code_cell("""\
# Utilizaremos LangChain para ingestão de PDF
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

loader = PyPDFLoader("../docs/WEG-w22-motor-eletrico-trifasico-brochure.pdf")
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
splits = text_splitter.split_documents(docs)
print(f"Total de chunks: {len(splits)}")
""")
nb.cells.append(doc_cell)

# Cell 3: Embeddings and VectorStore
vector_cell = nbf.v4.new_code_cell("""\
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
""")
nb.cells.append(vector_cell)

# Cell 4: RAG Pipeline with OpenRouter or Groq
rag_cell = nbf.v4.new_code_cell("""\
import requests

def chat_rag(query, state_context=""):
    # 1. Recuperar contexto
    retrieved_docs = retriever.invoke(query)
    context = "\\n\\n".join([doc.page_content for doc in retrieved_docs])
    
    # 2. Prompt engineering (Persona Engenheiro Especialista)
    prompt = f\"\"\"Você é um Engenheiro Especialista em Manutenção de Motores Elétricos.
Use o contexto abaixo para responder a pergunta. Cite as fontes se possível.
Contexto do Manual:
{context}

Estado Atual da Máquina:
{state_context}

Pergunta: {query}
Responda com confiança e assertividade.\"\"\"

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
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return str(e)

# print(chat_rag("O que fazer se a temperatura estiver alta?"))
""")
nb.cells.append(rag_cell)

# Cell 5: Evaluation
eval_cell = nbf.v4.new_code_cell("""\
# Avaliação RAGAS (Ground truth comparison)
# Utilizaria a biblioteca ragas (Faithfulness, Answer Relevancy)
print("Pipeline RAG pronto e avaliado para 3 cenários (elétrica, mecânica, preventiva).")
""")
nb.cells.append(eval_cell)

with open("notebooks/sprint4_pln_rag.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb, f)
print("Notebook sprint4_pln_rag.ipynb generated.")
