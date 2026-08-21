---
status: "🔴 A executar"
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
<!-- PREENCHER (executor) -->

## 10. Veredito
<!-- PREENCHER (revisor) -->

## 11. Síntese
<!-- PREENCHER (revisor) -->
