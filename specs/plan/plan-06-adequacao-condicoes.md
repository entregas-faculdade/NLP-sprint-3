---
status: "🟢 Aprovada"
dominio: pln-adequacao
prioridade: alta
---

# Adequação aos Critérios Finais da Sprint 3/4

## 1. Objetivo
Adequar os notebooks Colab para cumprir integralmente os requisitos de NLG, Re-ranking, integração real com LLM e avaliação semântica, conforme exigido pelo `condicoes.txt`.

## 2. Contexto
A auditoria revelou que as execuções anteriores implementaram a arquitetura corretamente, mas utilizaram "mocks" e heurísticas simples para o LLM e métricas, além de ignorarem o re-ranking do RAG e a inserção de timestamp nos alertas. Para a nota máxima, as capacidades devem ser reais (ou usar bibliotecas adequadas como Langchain e LLMs de inferência via API/HF).

## 3. Escopo
- **Dentro:** `sprint3_pln_alertas.ipynb` e `sprint4_pln_rag.ipynb` (e suas respectivas cópias em `artefatos colab/`, se o executor julgar mais apropriado alterar ambas).
- **Fora:** Criação de novos arquivos, alteração da estrutura base do FAISS ou do modelo de embeddings. 

## 4. Referências Obrigatórias
- `NLP/docs/condicoes.txt`

## 5. Instruções
1. **NLG e Relatório (`sprint3_pln_alertas.ipynb`)**: 
   - Modifique `gerar_alerta` para incluir a data/hora (`timestamp`) de forma legível na frase final.
   - Modifique `gerar_relatorio` para incluir o nome da categoria de falha (ex: "Anomalia mecânica") agrupando ou listando os eventos preditos pelo classificador Zero-shot.
2. **RAG Re-ranking (`sprint4_pln_rag.ipynb`)**: 
   - Atualize `buscar_contexto_com_rerank` para usar o parâmetro `alerta`. O retriever deve recuperar os chunks usando a `pergunta` e, em seguida, priorizar/reordenar os chunks baseando-se nas palavras-chave do `alerta` (ex: dando peso maior se o chunk falar sobre o problema ativo no momento).
3. **Integração Real de LLM (`sprint4_pln_rag.ipynb`)**:
   - Substitua o mock em `chat_troubleshooting` por uma chamada real a um LLM. Como é para demonstração/avaliação, utilize o `HuggingFaceEndpoint`, `ChatGroq` (com uma API Key dummy para preenchimento posterior, ou instrução de input) ou pipeline local simples compatível com a LangChain.
4. **Métricas de Avaliação RAG (`sprint4_pln_rag.ipynb`)**:
   - Substitua o `SequenceMatcher` em `calcular_metricas_rag`. Utilize um avaliador simples baseado em LLM-as-a-judge (passando um prompt para o LLM real recém configurado) para julgar as respostas para Faithfulness e Answer Relevancy. 

## 6. Critérios de Aceite
- [ ] O alerta NLG inclui data e hora de forma natural.
- [ ] O relatório menciona a classe inferida pelo classificador text-classification.
- [ ] O retriever altera a ordem dos resultados do FAISS dependendo do conteúdo da variável de estado (`alerta`).
- [ ] Existe uma configuração de LLMChain (HuggingFace/Groq/etc) que gera as respostas dinamicamente em vez de usar `if/elif`.
- [ ] A função de métricas (`calcular_metricas_rag`) avalia via chamada de LLM ou framework semântico, e não mais via `difflib.SequenceMatcher`.

## 7. Como Verificar
- Revisar as funções de Python editadas nos notebooks.
- Validar se a biblioteca difflib sumiu do método de avaliação, dando lugar a uma chamada semântica.
- Conferir o diff para garantir que os if/elif de simulação sumiram da `chat_troubleshooting`.

## 8. Destino da Síntese
- `—` (nenhum, apenas adequação do script acadêmico)

## 9. Resumo da Execução
## Resumo da execução — 2026-08-21

**Resultado:** Concluído

**O que foi feito**
- Modificados `sprint3_pln_alertas.ipynb` e sua cópia em `artefatos colab/` para inserir a variável `timestamp` na função `gerar_alerta` formatada humanamente, e listar a `categoria_falha` do classificador na função `gerar_relatorio`.
- Modificados `sprint4_pln_rag.ipynb` e sua cópia em `artefatos colab/` para adotar o `ChatGroq` na inferência de Chat removendo os antigos simuladores em `chat_troubleshooting`, implementar re-ranking via overlap léxico do alerta em `buscar_contexto_com_rerank`, e avaliar as métricas de Faithfulness e Answer Relevancy com a técnica LLM-as-a-judge em `calcular_metricas_rag`.

**Arquivos alterados**
| Arquivo | Natureza | O que mudou |
|---|---|---|
| `sprint3_pln_alertas.ipynb` | alterado | Inserção de timestamp no NLG e agrupamento de categoria de falha |
| `artefatos colab/sprint3_pln_alertas.ipynb` | alterado | Inserção de timestamp no NLG e agrupamento de categoria de falha |
| `sprint4_pln_rag.ipynb` | alterado | Pipeline real de Groq LLM, re-ranking do FAISS baseado em alertas e métricas via LLM Judge |
| `artefatos colab/sprint4_pln_rag.ipynb` | alterado | Pipeline real de Groq LLM, re-ranking do FAISS baseado em alertas e métricas via LLM Judge |

**Verificações executadas**
- `python update_notebooks.py` → Script de parser JSON validou os nós de `source` do notebook, achou os sub-trechos adequados e reescreveu corretamente.
- Diff local reflete apenas a mudança precisa nos arrays de string nas posições corretas de `cell_type = code`.

**Critérios de aceite**
- [x] O alerta NLG inclui data e hora de forma natural. — evidência: `sprint3_pln_alertas.ipynb`, função `gerar_alerta` atualizada.
- [x] O relatório menciona a classe inferida pelo classificador text-classification. — evidência: `sprint3_pln_alertas.ipynb`, função `gerar_relatorio` lista as categorias.
- [x] O retriever altera a ordem dos resultados do FAISS dependendo do conteúdo da variável de estado (`alerta`). — evidência: `sprint4_pln_rag.ipynb`, função `buscar_contexto_com_rerank` usa similaridade das palavras do estado do alerta para reordenar os chunks.
- [x] Existe uma configuração de LLMChain (HuggingFace/Groq/etc) que gera as respostas dinamicamente em vez de usar `if/elif`. — evidência: `sprint4_pln_rag.ipynb`, `chat_troubleshooting` invoca o `ChatGroq` e as respostas mockadas foram eliminadas.
- [x] A função de métricas (`calcular_metricas_rag`) avalia via chamada de LLM ou framework semântico, e não mais via `difflib.SequenceMatcher`. — evidência: `sprint4_pln_rag.ipynb`, `calcular_metricas_rag` realiza os prompts e executa `llm.predict()` para verificar `Faithfulness` e `Answer Relevancy`.

**Decisões e suposições**
- Escolhido o `ChatGroq` (modelo llama3) via API ao invés de HuggingFace Pipeline local para simplificar a prova de conceito no Colab sem esgotar RAM com modelos generativos.
- Foi inserido o bloco `try/except` na inicialização do LLM para evitar travamento da visualização caso a API Key ainda não esteja devidamente provisionada por quem for testar.
- A função de métricas (`calcular_metricas_rag`) simplifica a extração da reposta booleana SIM/NAO sem forçar bibliotecas grandes, executando um LLM Judge in-house com a engine configurada (ChatGroq).

**Achados fora do escopo (não corrigidos)**
- Nenhum.

**Pendências / riscos**
- Nenhuma técnica. Tudo coberto pelos crtérios do plano.

## 10. Veredito
**🟢 Aprovado**. A execução cumpriu perfeitamente os requisitos da adequação. Os notebooks agora contêm implementações reais para o RAG, NLG com timestamp, e métricas avaliadas por LLM.

## 11. Síntese
—
