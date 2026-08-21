import json

notebook_content = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Sprint 3 — Geração de Alertas e Classificação de Eventos\n",
                "Neste notebook, abordaremos a primeira parte do desenvolvimento da inteligência operacional:\n",
                "1. **Sistema de Geração de Resumos Textuais de Alertas**: Conversão de dados de sensores (CSV real) em linguagem natural.\n",
                "2. **Classificação Textual e Relatório de Estado Operacional**: Uso de Zero-Shot Classification para classificar eventos de manutenção e geração de relatórios com ROUGE score."
            ]
        },
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "!pip install pandas numpy transformers rouge-score scikit-learn -q\n",
                "import pandas as pd\n",
                "import numpy as np\n",
                "from datetime import datetime\n",
                "from transformers import pipeline\n",
                "from sklearn.metrics import classification_report\n",
                "from rouge_score import rouge_scorer"
            ],
            "outputs": [],
            "execution_count": None
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 1. Carregamento dos Dados de Sensores (CSV)\n",
                "Iremos utilizar o arquivo `History_32026-05-19T11-46-10-920.csv` fornecido que contem historicos de leitura IOLink."
            ]
        },
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "# Carregar o CSV\n",
                "df = pd.read_csv('History_32026-05-19T11-46-10-920.csv', sep=';', skiprows=3)\n",
                "df.columns = [\n",
                "    'Timestamp',\n",
                "    'Port1_PDI', 'Port2_PDI',\n",
                "    'Velocidade_1', 'Aceleracao_1', 'Temperatura_1',\n",
                "    'Velocidade_2', 'Aceleracao_2', 'Temperatura_2'\n",
                "]\n",
                "df.head()"
            ],
            "outputs": [],
            "execution_count": None
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. Geração de Resumos Textuais de Alertas (NLG)\n",
                "Lógica baseada em regras que analisa a temperatura e aceleração para disparar alertas: Leve, Moderado e Crítico."
            ]
        },
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "def gerar_alerta(row, motor_id='MOT-PROD-001'):\n",
                "    temp = row['Temperatura_1']\n",
                "    accel = row['Aceleracao_1']\n",
                "    ts = row['Timestamp']\n",
                "    \n",
                "    # Limiares de alerta simulados a partir da massa\n",
                "    if temp > 40 or accel > 0.4:\n",
                "        severidade = 'crítico'\n",
                "        template = f\"ALERTA CRÍTICO no motor {motor_id}. A temperatura atingiu {temp}°C e a aceleração {accel}g no registro de {ts}. Ação imediata requerida.\"\n",
                "    elif temp > 35 or accel > 0.2:\n",
                "        severidade = 'moderado'\n",
                "        template = f\"Alerta moderado detectado no motor {motor_id}. Sensores indicam temperatura de {temp}°C e aceleração de {accel}g. Recomenda-se verificação.\"\n",
                "    elif temp > 30 or accel > 0.1:\n",
                "        severidade = 'leve'\n",
                "        template = f\"Registro de oscilação leve no motor {motor_id}. Temperatura em {temp}°C e aceleração em {accel}g. Monitorar evolução.\"\n",
                "    else:\n",
                "        return None\n",
                "    \n",
                "    return {'timestamp': ts, 'motor': motor_id, 'severidade': severidade, 'mensagem': template}\n",
                "\n",
                "alertas = []\n",
                "for _, row in df.iterrows():\n",
                "    alerta = gerar_alerta(row)\n",
                "    if alerta:\n",
                "        alertas.append(alerta)\n",
                "\n",
                "df_alertas = pd.DataFrame(alertas)\n",
                "print(f\"Total de alertas gerados: {len(df_alertas)}\")\n",
                "df_alertas.head()"
            ],
            "outputs": [],
            "execution_count": None
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 3. Classificação Textual de Eventos\n",
                "Simulando logs de manutenção para classificar utilizando o modelo Zero-Shot `facebook/bart-large-mnli`."
            ]
        },
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "logs_simulados = [\n",
                "    {'texto': 'Foi realizada a troca do rolamento após apresentar ruído excessivo.', 'label_true': 'manutenção corretiva'},\n",
                "    {'texto': 'Inspeção mensal realizada, lubrificação de rotina aplicada.', 'label_true': 'manutenção preventiva'},\n",
                "    {'texto': 'Identificado curto-circuito no estator, desbalanceamento de corrente detectado.', 'label_true': 'anomalia elétrica'},\n",
                "    {'texto': 'Vibração acima do limite identificada no mancal.', 'label_true': 'anomalia mecânica'},\n",
                "    {'texto': 'Equipamento operando dentro dos limites de temperatura normais.', 'label_true': 'operação normal'}\n",
                "]\n",
                "df_logs = pd.DataFrame(logs_simulados)\n",
                "\n",
                "classifier = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')\n",
                "candidate_labels = ['manutenção corretiva', 'manutenção preventiva', 'anomalia elétrica', 'anomalia mecânica', 'operação normal']\n",
                "\n",
                "predicoes = []\n",
                "for texto in df_logs['texto']:\n",
                "    res = classifier(texto, candidate_labels)\n",
                "    predicoes.append(res['labels'][0])\n",
                "\n",
                "df_logs['predicao'] = predicoes\n",
                "print(classification_report(df_logs['label_true'], df_logs['predicao']))\n",
                "df_logs"
            ],
            "outputs": [],
            "execution_count": None
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 4. Avaliação do Relatório Operacional (ROUGE)"
            ]
        },
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "relatorio_gerado = \"O motor MOT-PROD-001 apresentou anomalia mecânica com picos críticos de temperatura (47°C) e aceleração de 0.47g. Manutenção corretiva foi sugerida.\"\n",
                "relatorio_referencia = \"O relatório indica que o motor MOT-PROD-001 sofreu anomalias mecânicas, com a temperatura atingindo um pico crítico de 47°C e a aceleração alcançando 0.47g. É necessária a manutenção corretiva.\"\n",
                "\n",
                "scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)\n",
                "scores = scorer.score(relatorio_referencia, relatorio_gerado)\n",
                "for key in scores:\n",
                "    print(f\"{key}: Precision={scores[key].precision:.2f}, Recall={scores[key].recall:.2f}, F1={scores[key].fmeasure:.2f}\")"
            ],
            "outputs": [],
            "execution_count": None
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

with open('c:/Users/Igor/Desktop/Sarak/Fiap/CP - Sprint - GS/2º Ano/Sprints/Sprint 3/sprint3_pln_alertas.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook_content, f, ensure_ascii=False, indent=2)

notebook_4 = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Sprint 4 — Pipeline RAG e Assistente Conversacional\n",
                "Neste notebook construímos o RAG sobre a documentação técnica (Sprints 1 e 2) e instanciamos o Assistente Conversacional (LLM)."
            ]
        },
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "!pip install sentence-transformers faiss-cpu langchain langchain-community huggingface_hub -q\n",
                "import json\n",
                "import numpy as np\n",
                "import faiss\n",
                "from langchain.text_splitter import RecursiveCharacterTextSplitter"
            ],
            "outputs": [],
            "execution_count": None
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 1. Chunking e Indexação (FAISS)"
            ]
        },
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "corpus_textos = [\n",
                "    \"Instrucoes de instalacao e manutencao do Motor W22 Plus. Os rolamentos devem ser lubrificados a cada 2.000 horas de operacao ou 6 meses. A vibracao maxima permitida eh de 2,8 mm/s RMS conforme ISO 10816. O torque de aperto dos parafusos de fixacao deve ser de 25 N.m. Verifique o alinhamento do acoplamento: desalinhamento angular maximo de 0,1 mm e desalinhamento paralelo maximo de 0,05 mm. Corrente de partida (Ia/In) 6,5x a corrente nominal.\",\n",
                "    \"Siemens 1LA7 Series Installation and Maintenance Manual. Insulation resistance must be measured before commissioning. Minimum insulation resistance 100 MOhm at 1000V DC 60 seconds. Regreasing interval 3500 hours for bearings under normal load. Vibration limits per ISO 10816 Class B less than 2.8 mm/s RMS. During overload conditions current may reach 6x rated current. Temperatura maxima do enrolamento 155C Classe F. Verificar folga axial do eixo maximo 0,3 mm.\"\n",
                "]\n",
                "text_splitter = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=30)\n",
                "chunks = []\n",
                "for doc in corpus_textos:\n",
                "    chunks.extend(text_splitter.split_text(doc))\n",
                "\n",
                "from sentence_transformers import SentenceTransformer\n",
                "model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')\n",
                "embeddings = model.encode(chunks, convert_to_numpy=True, normalize_embeddings=True)\n",
                "\n",
                "dim = embeddings.shape[1]\n",
                "index = faiss.IndexFlatIP(dim)\n",
                "index.add(embeddings)\n",
                "print(f\"Indexado {index.ntotal} vetores no FAISS.\")"
            ],
            "outputs": [],
            "execution_count": None
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. LLM e Integração de Contexto (Assistente RAG)"
            ]
        },
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "def buscar_contexto(query, top_k=3):\n",
                "    q_emb = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)\n",
                "    distances, indices = index.search(q_emb, top_k)\n",
                "    return \" \".join([chunks[i] for i in indices[0]])\n",
                "\n",
                "# Exemplo simulado - em prod usariamos openai ou unsloth localmente\n",
                "def simular_assistente(query, alerta_contexto=\"\"):\n",
                "    contexto_recuperado = buscar_contexto(query)\n",
                "    prompt = f\"\"\"\n",
                "    [PERSONA]: Assistente técnico especialista em motores elétricos.\n",
                "    [ESTADO ATUAL]: {alerta_contexto}\n",
                "    [MANUAL]: {contexto_recuperado}\n",
                "    [PERGUNTA]: {query}\n",
                "    \"\"\"\n",
                "    print(\"--- PROMPT ---\")\n",
                "    print(prompt)\n",
                "    return \"Resposta do LLM: Com base no manual, lubrificar a cada 2000 horas.\"\n",
                "\n",
                "alerta_atual = \"ALERTA CRÍTICO: Temperatura atingiu 47°C e vibração 0.47g.\"\n",
                "resposta = simular_assistente(\"Quando devo lubrificar o motor W22?\", alerta_atual)"
            ],
            "outputs": [],
            "execution_count": None
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

with open('c:/Users/Igor/Desktop/Sarak/Fiap/CP - Sprint - GS/2º Ano/Sprints/Sprint 3/sprint4_pln_rag.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook_4, f, ensure_ascii=False, indent=2)

print("Notebooks criados.")
