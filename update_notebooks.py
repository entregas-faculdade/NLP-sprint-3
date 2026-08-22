import json
import os

files_to_update_alerta = [
    'sprint3_pln_alertas.ipynb',
    'artefatos colab/sprint3_pln_alertas.ipynb'
]

files_to_update_rag = [
    'sprint4_pln_rag.ipynb',
    'artefatos colab/sprint4_pln_rag.ipynb'
]

cell_alerta_source = [
    "from datetime import datetime\n",
    "\n",
    "def gerar_alerta(row):\n",
    "    severidade = row['severidade'].lower()\n",
    "    motor = row['motor']\n",
    "    sensor = row['sensor']\n",
    "    desvio = row['desvio']\n",
    "    unidade = row['unidade']\n",
    "    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')\n",
    "    \n",
    "    if severidade == 'leve':\n",
    "        return f\"Aviso: O motor {motor} apresenta ligeiro aumento na {sensor.lower()} (+{desvio}{unidade}). Monitoramento contínuo sugerido. Registrado em {timestamp}.\"\n",
    "    elif severidade == 'moderado':\n",
    "        return f\"Alerta moderado detectado no motor {motor}. A {sensor.lower()} apresentou desvio de +{desvio}{unidade} acima do baseline. Recomenda-se verificação na próxima janela de manutenção. Registrado em {timestamp}.\"\n",
    "    elif severidade == 'crítico':\n",
    "        return f\"CRÍTICO: Ação imediata requerida no motor {motor}! A {sensor.lower()} excedeu o limite seguro em +{desvio}{unidade}. Risco iminente de falha. Registrado em {timestamp}.\"\n",
    "    else:\n",
    "        return f\"Operação normal. Registrado em {timestamp}.\"\n",
    "\n",
    "df_alertas['texto_alerta'] = df_alertas.apply(gerar_alerta, axis=1)\n",
    "for t in df_alertas['texto_alerta'].head(3):\n",
    "    print(\"-\", t)"
]

cell_relatorio_source = [
    "def gerar_relatorio(df):\n",
    "    total_alertas = len(df)\n",
    "    criticos = len(df[df['severidade'] == 'Crítico'])\n",
    "    motores_afetados = df['motor'].unique()\n",
    "    \n",
    "    relatorio = f\"**Relatório Operacional Diário**\\n\"\n",
    "    relatorio += f\"Nas últimas 24 horas, foram registrados {total_alertas} alertas de anomalia.\\n\"\n",
    "    relatorio += f\"Identificamos {criticos} eventos de severidade CRÍTICA.\\n\\n\"\n",
    "    relatorio += \"Equipamentos afetados:\\n\"\n",
    "    for motor in motores_afetados:\n",
    "        alertas_motor = df[df['motor'] == motor]\n",
    "        relatorio += f\"- **{motor}**: {len(alertas_motor)} alerta(s).\\n\"\n",
    "        for _, row in alertas_motor.iterrows():\n",
    "            categoria = row.get('categoria_falha', 'Anomalia mecânica')\n",
    "            relatorio += f\"  - {row['sensor']}: desvio de +{row['desvio']}{row['unidade']} ({row['severidade']}) - Categoria: {categoria}.\\n\"\n",
    "            \n",
    "    relatorio += \"\\nRecomendações preliminares: Agendar inspeção imediata para equipamentos com alertas críticos e revisão do sistema de resfriamento/lubrificação.\"\n",
    "    return relatorio\n",
    "\n",
    "texto_relatorio = gerar_relatorio(df_alertas)\n",
    "print(texto_relatorio.replace('\\n', '\\n'))"
]

cell_rerank_source = [
    "def buscar_contexto_com_rerank(pergunta, alerta, top_k=2):\n",
    "    # 1. Transforma a pergunta do usuário em um vetor, combinada com o contexto do alerta\n",
    "    query = f\"{pergunta} Contexto do alerta: {alerta}\"\n",
    "    query_vector = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)\n",
    "\n",
    "    # 2. Busca no índice FAISS o dobro de candidatos\n",
    "    distancias, indices = index.search(query_vector, top_k * 2)\n",
    "\n",
    "    # 3. Recupera os textos reais baseados nos índices encontrados\n",
    "    candidatos = [chunk_texts[i] for i in indices[0]]\n",
    "\n",
    "    # 4. Reranking simples baseado em palavras-chave do alerta\n",
    "    palavras_alerta = set(alerta.lower().split())\n",
    "    pontuacoes = []\n",
    "    for cand in candidatos:\n",
    "        score = sum(1 for palavra in palavras_alerta if palavra in cand.lower())\n",
    "        pontuacoes.append(score)\n",
    "        \n",
    "    candidatos_ordenados = [x for _, x in sorted(zip(pontuacoes, candidatos), key=lambda pair: pair[0], reverse=True)]\n",
    "    contextos_recuperados = candidatos_ordenados[:top_k]\n",
    "\n",
    "    # Retorna o texto unificado e a lista (para casar com o que a célula espera)\n",
    "    return \"\\n\\n\".join(contextos_recuperados), contextos_recuperados"
]

cell_chat_source = [
    "import os\n",
    "from langchain_groq import ChatGroq\n",
    "from langchain.memory import ConversationBufferMemory\n",
    "from langchain_core.prompts import PromptTemplate\n",
    "from langchain.chains import LLMChain\n",
    "\n",
    "os.environ[\"GROQ_API_KEY\"] = os.environ.get(\"GROQ_API_KEY\", \"dummy_key_substitua_aqui\")\n",
    "\n",
    "memory = ConversationBufferMemory(memory_key=\"chat_history\", input_key=\"pergunta\")\n",
    "\n",
    "template = \"\"\"Você é um Assistente Técnico Especialista em Motores Elétricos.\n",
    "Sua função é auxiliar operadores no diagnóstico de falhas, sempre baseando-se RIGOROSAMENTE nos manuais fornecidos.\n",
    "\n",
    "[ESTADO ATUAL DO ATIVO (TELEMETRIA/ALERTAS)]\n",
    "{alerta_atual}\n",
    "\n",
    "[MANUAIS RECUPERADOS]\n",
    "{contexto}\n",
    "\n",
    "[HISTÓRICO DA CONVERSA]\n",
    "{chat_history}\n",
    "\n",
    "[NOVA PERGUNTA]\n",
    "{pergunta}\n",
    "\n",
    "INSTRUÇÕES:\n",
    "1. Responda à pergunta baseando-se APENAS nos [MANUAIS RECUPERADOS].\n",
    "2. Se a informação não estiver lá, diga explicitamente: \"Não possuo informações suficientes na documentação técnica recuperada\".\n",
    "3. Leve em consideração o [ESTADO ATUAL DO ATIVO] para contextualizar a gravidade da situação.\n",
    "4. Ao final da resposta, classifique seu \"Nível de Confiança\" (ALTO, MÉDIO, BAIXO) e cite as fontes.\n",
    "\n",
    "Resposta:\"\"\"\n",
    "\n",
    "prompt_template = PromptTemplate(\n",
    "    input_variables=[\"alerta_atual\", \"contexto\", \"chat_history\", \"pergunta\"],\n",
    "    template=template\n",
    ")\n",
    "\n",
    "try:\n",
    "    llm = ChatGroq(model_name=\"llama3-8b-8192\", temperature=0.0)\n",
    "    chain = LLMChain(llm=llm, prompt=prompt_template, memory=memory)\n",
    "except Exception as e:\n",
    "    print(\"Aviso: Falha ao inicializar LLM, verifique a API KEY.\", e)\n",
    "    llm = None\n",
    "    chain = None\n",
    "\n",
    "def chat_troubleshooting(user_input, alerta_ativo):\n",
    "    contexto_recuperado, _ = buscar_contexto_com_rerank(user_input, alerta_ativo)\n",
    "    historico = memory.buffer\n",
    "    prompt_formatado = prompt_template.format(\n",
    "        alerta_atual=alerta_ativo,\n",
    "        contexto=contexto_recuperado,\n",
    "        chat_history=historico,\n",
    "        pergunta=user_input\n",
    "    )\n",
    "\n",
    "    print(\"\\n=== PROMPT ENVIADO AO LLM ===\")\n",
    "    print(prompt_formatado)\n",
    "    print(\"===============================\\n\")\n",
    "\n",
    "    if chain:\n",
    "        try:\n",
    "            resposta_llm = chain.run(alerta_atual=alerta_ativo, contexto=contexto_recuperado, chat_history=historico, pergunta=user_input)\n",
    "        except Exception as e:\n",
    "            resposta_llm = f\"Erro na inferência do LLM: {e}\"\n",
    "    else:\n",
    "        resposta_llm = \"[ERRO] Configuração do LLM ausente. Configure a GROQ_API_KEY para a resposta dinâmica.\"\n",
    "\n",
    "    if memory:\n",
    "        memory.save_context({\"pergunta\": user_input}, {\"resposta\": resposta_llm})\n",
    "\n",
    "    return resposta_llm\n",
    "\n",
    "alerta_ativo = \"ALERTA CRÍTICO: Motor W22 Plus - Temperatura atingiu 47°C e vibração 0.47g.\"\n",
    "\n",
    "print(\">>> TURNO 1\")\n",
    "resposta = chat_troubleshooting(\"Quais são os limites de vibração aceitáveis?\", alerta_ativo)\n",
    "print(\">>> RESPOSTA DO LLM:\\n\" + resposta + \"\\n\")\n",
    "\n",
    "print(\">>> TURNO 2\")\n",
    "resposta = chat_troubleshooting(\"E como devo proceder para corrigir caso ultrapasse?\", alerta_ativo)\n",
    "print(\">>> RESPOSTA DO LLM:\\n\" + resposta + \"\\n\")"
]

cell_metrics_source = [
    "import json\n",
    "\n",
    "print(\"## Carregando Ground Truth (dados_avaliacao.json)\")\n",
    "try:\n",
    "    with open('dados_avaliacao.json', 'r', encoding='utf-8') as f:\n",
    "        dados = json.load(f)\n",
    "    qa_list = dados['qa_troubleshooting']\n",
    "    print(f\"Carregadas {len(qa_list)} perguntas de teste.\")\n",
    "except Exception as e:\n",
    "    print(\"Dataset não encontrado no caminho padrão. Usando mock gerado...\", e)\n",
    "    qa_list = [{\"pergunta\": \"Qual a temperatura máxima permitida para o enrolamento do Siemens 1LA7?\", \"ground_truth\": \"A temperatura máxima do enrolamento é de 155°C (Classe F).\"}]\n",
    "\n",
    "def calcular_metricas_rag(pergunta, ground_truth, resposta_llm, contexto):\n",
    "    if not llm:\n",
    "        return 0.0, 0.0, 0.0\n",
    "    \n",
    "    prompt_faithfulness = f\"\"\"\n",
    "    Avalie se a seguinte resposta baseia-se EXCLUSIVAMENTE no contexto fornecido.\n",
    "    Contexto: {contexto}\n",
    "    Resposta: {resposta_llm}\n",
    "    A resposta é fiel ao contexto (nao inventa fatos)? Responda apenas \"SIM\" ou \"NAO\".\n",
    "    \"\"\"\n",
    "    try:\n",
    "        resultado_f = llm.predict(prompt_faithfulness)\n",
    "        faithfulness = 1.0 if \"SIM\" in resultado_f.upper() else 0.0\n",
    "    except:\n",
    "        faithfulness = 0.0\n",
    "\n",
    "    prompt_relevancy = f\"\"\"\n",
    "    Avalie se a resposta atende à pergunta original, sendo util e direta.\n",
    "    Pergunta: {pergunta}\n",
    "    Resposta: {resposta_llm}\n",
    "    A resposta é relevante para a pergunta? Responda apenas \"SIM\" ou \"NAO\".\n",
    "    \"\"\"\n",
    "    try:\n",
    "        resultado_ar = llm.predict(prompt_relevancy)\n",
    "        answer_relevancy = 1.0 if \"SIM\" in resultado_ar.upper() else 0.0\n",
    "    except:\n",
    "        answer_relevancy = 0.0\n",
    "\n",
    "    context_precision = 1.0 if ground_truth[:10].lower() in contexto.lower() else 0.5\n",
    "\n",
    "    return context_precision, faithfulness, answer_relevancy\n",
    "\n",
    "print(\"\\n## Rodando Avaliação RAGAS via LLM-as-a-judge (Simulada)...\\n\")\n",
    "scores = {\"context_precision\": [], \"faithfulness\": [], \"answer_relevancy\": []}\n",
    "\n",
    "for qa in qa_list:\n",
    "    p = qa['pergunta']\n",
    "    gt = qa['ground_truth']\n",
    "\n",
    "    alerta_neutro = \"Estado Operacional Normal\"\n",
    "    contexto, top_res = buscar_contexto_com_rerank(p, alerta_neutro, top_k=2)\n",
    "\n",
    "    historico = memory.buffer if memory else \"\"\n",
    "    if chain:\n",
    "        try:\n",
    "            resp = chain.run(alerta_atual=alerta_neutro, contexto=contexto, chat_history=historico, pergunta=p)\n",
    "        except Exception:\n",
    "            resp = \"Erro\"\n",
    "    else:\n",
    "        resp = \"Simulação sem LLM\"\n",
    "\n",
    "    cp, f, ar = calcular_metricas_rag(p, gt, resp, contexto)\n",
    "    scores[\"context_precision\"].append(cp)\n",
    "    scores[\"faithfulness\"].append(f)\n",
    "    scores[\"answer_relevancy\"].append(ar)\n",
    "\n",
    "media_cp = sum(scores[\"context_precision\"]) / len(qa_list) if len(qa_list) > 0 else 0\n",
    "media_f = sum(scores[\"faithfulness\"]) / len(qa_list) if len(qa_list) > 0 else 0\n",
    "media_ar = sum(scores[\"answer_relevancy\"]) / len(qa_list) if len(qa_list) > 0 else 0\n",
    "\n",
    "print(\"===\" * 15)\n",
    "print(\"🏆 RESULTADO FINAL DA AVALIAÇÃO RAG (LLM Judge)\")\n",
    "print(\"===\" * 15)\n",
    "print(f\"-> Context Precision : {media_cp:.2f}\")\n",
    "print(f\"-> Faithfulness      : {media_f:.2f}\")\n",
    "print(f\"-> Answer Relevancy  : {media_ar:.2f}\")\n",
    "print(\"===\" * 15)"
]

def process_file(filepath, updates):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    changed = False
    for cell in nb.get('cells', []):
        if cell.get('cell_type') == 'code':
            source = "".join(cell.get('source', []))
            for key, new_src in updates:
                if key in source:
                    cell['source'] = new_src
                    changed = True
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
        print(f"Updated {filepath}")

for filepath in files_to_update_alerta:
    process_file(filepath, [
        ("def gerar_alerta(", cell_alerta_source),
        ("def gerar_relatorio(", cell_relatorio_source)
    ])

for filepath in files_to_update_rag:
    process_file(filepath, [
        ("def buscar_contexto_com_rerank(", cell_rerank_source),
        ("def chat_troubleshooting(", cell_chat_source),
        ("def calcular_metricas_rag(", cell_metrics_source)
    ])

print("All notebooks processed.")
